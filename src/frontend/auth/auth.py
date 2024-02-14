import os 
import json 
import requests
import firebase_admin

from firebase_admin import storage
from firebase_admin import auth
from firebase_admin import credentials
from requests.exceptions import HTTPError

import dearpygui.dearpygui as dpg

def raise_detailed_error(request_object):
    try:
        request_object.raise_for_status()
    except HTTPError as e:
        # raise detailed error message
        # TODO: Check if we get a { "error" : "Permission denied." } and handle automatically
        raise HTTPError(e, request_object.text)

def download_file(url, file_name):
    try:
        # Send a GET request to the URL
        response = requests.get(url, stream=True)
        # Check if the request was successful
        if response.status_code == 200:
            # Open a local file in binary write mode
            with open(file_name, 'wb') as file:
                for chunk in response.iter_content(chunk_size=8192):
                    # Write the content to the file in chunks to avoid using too much memory
                    file.write(chunk)
            print(f"File has been successfully downloaded and saved as {file_name}.")
        else:
            print(f"Failed to download the file. HTTP status code: {response.status_code}")
    except Exception as e:
        print(f"An error occurred: {e}")

class Auth: 
    def __init__(self, app_controller):
        self.app_controller = app_controller
        self.uid = None 
        self.username = None 
        self.signed_in_status = False 
        cred = credentials.Certificate('./auth/gstk-firebase.json')
        self.firebase_app = firebase_admin.initialize_app(cred)
        self.is_local_config_dirty = not self.check_signed_in_status()

    def signin(self, username: str, password: str) -> str:
        # check if the user is already signed in
        api_key = "AIzaSyCqZInCWoyXcmtl0gtqO9w1p9aGax4_iNc"
        request_ref = "https://www.googleapis.com/identitytoolkit/v3/relyingparty/verifyPassword?key={0}".format(api_key)
        headers = {"content-type": "application/json; charset=UTF-8"}
        data = json.dumps({"email": username, "password": password, "returnSecureToken": True})
        try: 
            request_object = requests.post(request_ref, headers=headers, data=data)
            raise_detailed_error(request_object)
            current_user = request_object.json()
            self.uid = current_user["localId"]
            self.username = current_user["displayName"] 
            self.signed_in_status = True
            self.download_documents()
            self.create_signin_cache()
            return True 
        except Exception as e:
            print(e)
            return False

    def signout(self):
        self.uid = None
        self.signed_in_status = False 
        self.username = None    
        # delete the auth.json file 
        self.delete_signin_cache()

    def check_signed_in_status(self):
        print("Checking signed in status.")
        try: 
            with open("./config/auth.json", "r") as f:
                data = json.load(f)
                self.uid = data["uid"]
                self.signed_in_status = True
                user = auth.get_user(self.uid)
                self.username = user.display_name
                self.download_documents()
                return True 
        except Exception as e:
            return False 
            pass
    
    def signup(self, username: str, password: str) -> str:
        cred = credentials.Certificate('./auth/gstk-firebase.json')
        try:
            user = auth.create_user(
                email=username,
                email_verified=True,
                password=password,
                display_name=username.split("@")[0],
                disabled=False
            )
            self.uid = user.uid
            self.username = username.split("@")[0]
            self.signed_in_status = True
            self.download_documents()
            self.create_signin_cache()
            return True 
        except Exception as e:
            print(e)
            return False


    def create_signin_cache(self):
        if self.uid is not None and self.signed_in_status is True: 
            with open("./config/auth.json", "w") as f:
                json.dump({"uid": self.uid}, f)

    def delete_signin_cache(self):
        if os.path.exists("./config/auth.json"):
            os.remove("./config/auth.json")

    def upload_documents(self, fileNames: list):
        print("uploading documents...")
        if self.signed_in_status:
            bucket = storage.bucket(name="gstk-73148.appspot.com")
            tmpstamp = self.get_next_latest_timestamp()
            print(f"Uploading documents with timestamp {tmpstamp}...")
            for file in fileNames:
                try:
                    file_path = f"./config/{self.uid}_{file}"
                    # check if the file exists
                    if not os.path.exists(file_path):
                        print(f"File {file} does not exist locally.")
                        continue
                    blob = bucket.blob(f"{self.uid}_{tmpstamp}_{file}")
                    blob.upload_from_filename(file_path)
                    blob.make_public()
                    print(f"File {file} uploaded to Firebase Storage.")
                except Exception as e:
                    print(e)
                    pass

    def download_documents(self):
        if self.signed_in_status:
            bucket = storage.bucket(name="gstk-73148.appspot.com")
            tmpstamp = self.get_latest_timestamp()
            print(f"Downloading documents with timestamp {tmpstamp}...")
            layout_file = f"window_layout.ini"
            window_state_file = f"window_state.json"
            app_params_file = f"app_params.json"
            fileNames = [layout_file, window_state_file, app_params_file] 
            for fileName in fileNames:
                blob = bucket.blob(f"{self.uid}_{tmpstamp}_{fileName}")
                if blob.exists():
                    print(f"File {fileName} downloaded from Firebase Storage.")
                    # check if local has such a file 
                    # TODO: version checks 
                    if os.path.exists(f"./config/{self.uid}_{fileName}"):
                        print(f"File {fileName} already exists locally.") 
                        continue
                    else:
                        print(f"File {fileName} does not exist locally.")
                        self.is_local_config_dirty = True 
                        blob.make_public()
                        download_file(blob.public_url, f"./config/{self.uid}_{fileName}")
            self.handle_dirty_update_check()

    def get_next_latest_timestamp(self): 
        if self.signed_in_status:
            bucket = storage.bucket(name="gstk-73148.appspot.com")
            i = 0 
            while True: 
                layout_file = f"{self.uid}_{i}_window_layout.ini"
                blob = bucket.blob(layout_file)
                if blob.exists():
                    i += 1
                else:
                    break
            return i
        else:
            return 0
    
    def get_latest_timestamp(self): 
        if self.signed_in_status:
            bucket = storage.bucket(name="gstk-73148.appspot.com")
            i = 0 
            while True: 
                layout_file = f"{self.uid}_{i}_window_layout.ini"
                blob = bucket.blob(layout_file)
                if blob.exists():
                    i += 1
                else:
                    break    
            return max(0, i - 1)
        else:
            return 0

    def handle_dirty_update_check(self):
        """
        Check with auth whether the view should be updated.
        """
        
        if self.is_local_config_dirty:
            self.is_local_config_dirty = False
            self.app_controller.popup_box_with_callback("Warning", "Local configuration is different from the online version. Do you want to update the view?", lambda: self.app_controller.restart_app(), lambda: None)