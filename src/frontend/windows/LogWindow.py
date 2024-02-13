import dearpygui.dearpygui as dpg
from windows import Window
from utils.status_maintain import restart_app

class LogWindow(Window):
    def __init__(self, app_controller):
        super().__init__("login_user_account_window", app_controller)

        self._default_user_name = ""

        self.app_controller.register_message_listener(self, "login")

        with dpg.window(label="User Account", tag=self.tag, on_close=self.on_close):
            width, height, channels, data = dpg.load_image("windows/avatar.png")
            with dpg.texture_registry(show=False):
                dpg.add_static_texture(width=width, height=height, default_value=data, tag="avatar_texture")
            # Use a group to align the image and text widgets horizontally
            with dpg.group(horizontal=True):
                # Add image widget
                dpg.add_image("avatar_texture", width=30, height=30)    
                # Adjust the vertical alignment of the text
                text_height = 30  # Approximate height of the text widget
                vertical_padding = (30 - text_height) / 2
                with dpg.group(horizontal=False):
                    dpg.add_spacer(height=vertical_padding)
                    dpg.add_text(self._default_user_name, tag="user_name")
                    dpg.hide_item("user_name")
                    dpg.add_button(label="Signin/Signup", callback=self.signin_signup_pressed, tag="signin_signup_button")
        
        self.check_signed_in_status()
              
    def check_signed_in_status(self):
        if self.app_controller.auth.signed_in_status:
            dpg.hide_item("signin_signup_button")
            dpg.set_value("user_name", self.app_controller.auth.username)
            dpg.show_item("user_name")
        else:
            dpg.show_item("signin_signup_button")

    def signin_signup_pressed(self):
        self.popup_login_signup_window()
        # dpg.hide_item("signin_signup_button")
        # dpg.set_value("user_name", "Rui Qiu")
        # dpg.show_item("user_name")
        # self.simulate_file_download()
        # print(self.app_controller.get_windows_state(save_to_file=True))
        # self.app_controller.popup_box_with_callback("Reload Warning", "App needs to restart to load", lambda: (self.simulate_file_download(), restart_app(dpg)), lambda: None)
        # restart_app()

    def popup_login_signup_window(self):
        if dpg.does_item_exist("Signin/Signup_window"):
            return 

        with dpg.mutex(): 
            viewport_width = dpg.get_viewport_client_width()
            viewport_height = dpg.get_viewport_client_height()
            with dpg.window(label="Signin/Signup", tag="Signin/Signup_window", width=viewport_width / 3, no_close=True) as modal_id:
                dpg.add_input_text(label="User name", tag="user_name_input", default_value=self._default_user_name)
                dpg.add_input_text(label="Password", tag="password_input", default_value="", password=True)
                dpg.add_input_text(label="Repeat password", tag="password_repeat_input", default_value="",  password=True)
                dpg.hide_item("password_repeat_input")
                with dpg.group(horizontal=True):
                    dpg.add_button(label="Signin", tag="signin_btn", user_data=(modal_id, True), callback=self.login_pressed)
                    dpg.add_button(label="Not Signup Yet", tag="signup_btn", user_data=(modal_id, True), callback=self.signup_pressed)
                    dpg.add_button(label="Cancel", user_data=(modal_id, True), callback=self.cancel_pressed)
        dpg.split_frame()
        width = dpg.get_item_width(modal_id)
        height = dpg.get_item_height(modal_id)
        dpg.set_item_pos(modal_id, [viewport_width // 2 - width // 2, viewport_height // 2 - height // 2])

    def login_pressed(self):
        username = dpg.get_value("user_name_input")
        password = dpg.get_value("password_input")
        if username == "" or password == "":
            self.app_controller.popup_box("Error", "Username and password cannot be empty.")
            return
        
        signin_status = self.app_controller.auth.signin(username, password)
        if not signin_status:
            self.app_controller.popup_box("Error", "Username or password is incorrect.")
        else:
            dpg.hide_item("signin_signup_button")
            dpg.set_value("user_name", self.app_controller.auth.username)
            dpg.show_item("user_name")
            dpg.delete_item("Signin/Signup_window")
            self.app_controller.popup_box("Success", "Successfully signed in.")
          

    def signup_pressed(self):
        if not dpg.is_item_shown("password_repeat_input"):
            dpg.set_item_label("Signin/Signup_window", "Signup")
            dpg.set_item_label("signup_btn", "Signup")
            dpg.show_item("password_repeat_input")
            dpg.hide_item("signin_btn")
            current_height = dpg.get_item_height("Signin/Signup_window")
            dpg.set_item_height("Signin/Signup_window", current_height + 25)
        else: 
            username = dpg.get_value("user_name_input")
            password = dpg.get_value("password_input")
            password_repeat = dpg.get_value("password_repeat_input")
            if password != password_repeat:
                self.app_controller.popup_box("Error", "Password and repeated password do not match.")
                return
            else:
                signup_status = self.app_controller.auth.signup(username, password)
                if not signup_status:
                    self.app_controller.popup_box("Error", "Email already exists")
                else: 
                    dpg.hide_item("signin_signup_button")
                    dpg.set_value("user_name", self.app_controller.auth.username)
                    dpg.show_item("user_name")
                    dpg.delete_item("Signin/Signup_window")
                    self.app_controller.popup_box("Error", "Password and repeated password do not match.")
                    
    def sign_out(self):
        dpg.hide_item("user_name")
        dpg.show_item("signin_signup_button")
        self.app_controller.auth.signout()
        self.app_controller.popup_box("Success", "Successfully signed out.")              

    def cancel_pressed(self):
        dpg.delete_item("Signin/Signup_window")

    def simulate_file_download(self):
        import shutil
        source_file = "./config/window_layout_2.ini"
        destination_file = "./window_layout_2.ini"
        try:
            # Copy the file from source to destination
            shutil.copy(source_file, destination_file)
            print("File downloaded (copied) successfully.")
        except FileNotFoundError:
            print("Source file not found.")
        except Exception as e:
            print(f"An error occurred: {e}")


