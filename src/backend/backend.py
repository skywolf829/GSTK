import os
import sys
from dataset import Dataset
from model import GaussianModel
from trainer import Trainer
from argparse import ArgumentParser
from utils.system_utils import mkdir_p
from settings import Settings
import threading
import multiprocessing.connection as connection
import signal 
import torch

def signal_handler(sig, frame):
    pid = os.getpid()
    print('Exiting')
    global server_communicator
    server_communicator.stop = True
    # This is required otherwise the ServerCommunicator will stay listening
    os.kill(pid, 9)
    sys.exit(0)
    
signal.signal(signal.SIGINT, signal_handler)


class ServerController:
    def __init__(self, ip, port):
        # Create the settings
        self.ip = ip
        self.port = port
        self.settings = Settings()
        self.dataset = None
        self.model = None
        self.trainer = None

        self.debug_for_frontend = False

        self.loading = False

        global server_communicator
        server_communicator = ServerCommunicator(self, ip, port)
        server_communicator.start()
        
    def process_message(self,data):
        global server_communicator
        print("Received message")
        print(data)
        if(self.loading):
            data = {"other" : {"error": "Please wait until the current operation is completed"}}
            server_communicator.send_message(data)
            return
        
        
        if("initialize_dataset" in data.keys()):
            t = threading.Thread(target=self.initialize_dataset, 
                                 args=[data['initialize_dataset']])
            self.loading = True
            t.start()
            #threading.self.initialize_dataset(data['initialize_dataset'])
        if("initialize_trainer" in data.keys()):
            t :threading.Thread  = threading.Thread(target=self.initialize_model_and_trainer, 
                                 args=[data['initialize_trainer']])
            self.loading = True
            t.start()
            
    def initialize_dataset(self, data):
        global server_communicator

        # Just load all key data to settings
        for k in data.keys():
            # Check if the keys line up
            if k not in self.settings.keys():
                data = {
                    "dataset": {"dataset_error": f"Key {k} from client not present in Settings"}
                }
                server_communicator.send_message(data)
                self.loading = False
                return
            else:
                self.settings.params[k] = data[k]
        

        # Check to make sure dataset path exists
        if not (os.path.exists(data["dataset_path"])):
            data = {
                "dataset": {"dataset_error": f"Dataset path does not exist: {data['dataset_path']}"}
            }
            server_communicator.send_message(data)
            self.loading = False
            return
        
        # Check if the data device exists
        try:
            a = torch.empty([32], dtype=torch.float32, device=data['data_device'])
            del a
        except Exception as e:
            data = {
                "dataset": {"dataset_error": f"Dataset device does not exist: {data['data_device']}"}
            }
            server_communicator.send_message(data)
            self.loading = False
            return
        
        # Create dataset
        try:
            data = {"dataset": {"dataset_loading": f""}}
            server_communicator.send_message(data)
            self.dataset = Dataset(self.settings)
        except Exception as e:
            data = {
                "dataset": {"dataset_error": f"Dataset failed to initialize, likely doesn't recognize dataset type."}
            }
            server_communicator.send_message(data)
            self.loading = False
            return
        
        data = {
            "dataset": {"dataset_initialized": f"Dataset was initialized."}
        }
        server_communicator.send_message(data)
        self.loading = False
        
    def initialize_model_and_trainer(self, data):
        global server_communicator

        if(self.dataset is None):
            data = {
                "trainer": {"trainer_error": f"Must initialize dataset before the model"}
            }
            server_communicator.send_message(data)
            self.loading = False
            return
        
        # Just load all key data to settings
        for k in data.keys():
            # Check if the keys line up
            if k not in self.settings.keys():
                data = {
                    "trainer": {"trainer_error": f"Key {k} from client not present in Settings"}
                }
                server_communicator.send_message(data)
                self.loading = False
                return
            else:
                self.settings.params[k] = data[k]
        
        # Check if the data device exists
        try:
            a = torch.empty([32], dtype=torch.float32, device=data['device'])
            del a
        except Exception as e:
            data = {
                "model": {"model_error": f"Dataset device does not exist: {data['device']}"}
            }
            server_communicator.send_message(data)
            self.loading = False
            return
        '''
        if("cuda" not in data['device']):
            data = {
                "model": {"model_error": f"Backend requires cuda device (eg. 'cuda', 'cuda:3')"}
            }
            server_communicator.send_message(data)
            self.loading = False
            return
        '''
        
        try:
            self.model = GaussianModel(self.settings)
        except Exception as e:
            data = {
                "model": {"model_error": f"Failed to setup GaussianModel"}
            }
            server_communicator.send_message(data)
            self.loading = False
            return
    
        try:
            self.trainer = Trainer(self.model, self.dataset, self.settings)
        except Exception as e:
            data = {
                "trainer": {"trainer_error": f"Failed to setup Trainer"}
            }
            server_communicator.send_message(data)
            self.loading = False
            return
        
        data = {
            "model": {"model_initialized": f"Model was initialized"}
        }
        server_communicator.send_message(data)
        print("Initialized model and trainer")
        self.loading = False

        


class ServerCommunicator(threading.Thread):

    def __init__(self, server_controller : ServerController, ip : str, port: int, *args, **kwargs): 
        super().__init__().__init__(*args, **kwargs)

        self.state = "uninitialized"        
        self.server_controller = server_controller
        self.ip = ip
        self.port = port
        self.listener : connection.Listener = None
        self.conn : connection.Connection = None
        self.stop = False

    def run(self):
        while not self.stop:
            if(self.state == "uninitialized"):
                # https://stackoverflow.com/questions/27428936/python-size-of-message-to-send-via-socket
                self.listener : connection.Listener = connection.Listener((self.ip, self.port), authkey=b"GRAVITY")
                self.state : str = "listening"
                print(f"Listening on {self.ip}:{self.port}")   

            elif(self.state == "listening"):
                # Blocking accept call - waits here until app connects
                self.conn : connection.Connection = self.listener.accept()
                print(f'Connection accepted from {self.listener.last_accepted}')
                self.state = "connected"

            elif(self.state == "connected"):
                # blocking call, see check_for_msg
                data = self.check_for_msg()
                if data is not None:
                    self.server_controller.process_message(data)

        print("Stop signal detected")
        # clean up
        if(self.conn):
            self.conn.close()
        if(self.listener):
            self.listener.close()

        self.conn = None
        self.listener = None
        self.stop()
            
    def check_for_msg(self):
        try:
            # poll tells us if there is a message ready
            if(self.conn.poll()):
                # Blocking call, will wait here
                item = self.conn.recv()
            else:
                item = None
        except Exception:
            print(f"Connection closed")
            self.state = "uninitialized"
            self.conn.close()
            self.listener.close()
            item = None
        return item

    def send_message(self, data):
        if(self.state == "connected"):
            try:
                self.conn.send(data)
            except Exception:
                print("Failed to send data.")


# global communicator so the thread can be shut down with ctrl-c
server_communicator = None

if __name__ == "__main__":
    # Set up command line argument parser
    parser = ArgumentParser(description="Backend server script")
    parser.add_argument('--ip', type=str, default="127.0.0.1")
    parser.add_argument('--port', type=int, default=10789)
    args = parser.parse_args()

    s = ServerController(args.ip, args.port)

    # infinite loop until ctrl-c
    while True:
        pass
    
