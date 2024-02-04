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
from dataset.cameras import RenderCam

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
        self.DEBUG = False
        self.ip = ip
        self.port = port

        self.settings = Settings()
        self.model = GaussianModel(self.settings, debug=self.DEBUG)
        self.trainer = Trainer(self.model, self.settings, debug=self.DEBUG)
        self.dataset = None
        self.render_cam = RenderCam()

        self.loading = False
        self.DEBUG = False

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
            
        if("update_trainer_settings" in data.keys()):
            t = threading.Thread(target=self.update_trainer_settings, 
                                 args=[data['update_trainer_settings']])
            self.loading = True            
            t.start()
        
        if("update_model_settings" in data.keys()):
            t = threading.Thread(target=self.update_model_settings, 
                                 args=[data['update_model_settings']])
            self.loading = True            
            t.start()

        if("training_start" in data.keys()):
            self.on_train_start()
        
        if("training_pause" in data.keys()):
            self.on_train_pause()

        if("debug" in data.keys()):
            self.on_debug_toggle(data['debug'])
            
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
        if not os.path.exists(data["dataset_path"]) and not self.DEBUG:
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
            self.dataset = Dataset(self.settings, debug=self.DEBUG)
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
        
    def update_trainer_settings(self, data):
        global server_communicator

        # Just load all key data to settings
        for k in data.keys():
            # Check if the keys line up
            if k not in self.settings.keys():
                data = {
                    "trainer": {"trainer_settings_updated_error": f"Key {k} from client not present in Settings"}
                }
                server_communicator.send_message(data)
                self.loading = False
                return
            
        # Check all before commiting changed
        for k in data.keys():
            self.settings.params[k] = data[k]
            
        try:
            self.trainer.update_settings(self.settings)
            self.trainer.training_setup()
        except Exception as e:
            data = {
                "trainer": {"trainer_settings_updated_error": f"Failed to update trainer settings."}
            }
            server_communicator.send_message(data)
            self.loading = False
            return
        
        data = {
            "trainer": {"trainer_settings_updated": f"Trainer settings successfully updated."}
        }
        server_communicator.send_message(data)
        print("Initialized model and trainer")
        self.loading = False

    def update_model_settings(self, data):
        global server_communicator

        self.loading = True
        # Check if the data device exists
        try:
            a = torch.empty([32], dtype=torch.float32, device=data['device'])
            del a
        except Exception as e:
            data = {
                "model": {"model_settings_updated_error": f"Device does not exist: {data['device']}"}
            }
            server_communicator.send_message(data)
            self.loading = False
            return
        
        if(data['sh_degree'] < 0 or data['sh_degree'] > 3):
            data = {
                "model": {"model_settings_updated_error": f"SH degree is invalid: {data['device']}"}
            }
            server_communicator.send_message(data)
            self.loading = False
            return
        
        self.settings.params['sh_degree'] = data['sh_degree']
        self.settings.params['device'] = data['device']
        self.model.on_settings_update(self.settings)
        
        data = {
            "model": {"model_settings_updated": f"Model settings were updated"}
        }
        server_communicator.send_message(data)
        print("Updated model settings")
        self.loading = False

    def on_train_start(self):
        global server_communicator
        self.loading = True
        if(self.dataset is None or self.model is None or self.trainer is None):
            data = {
                "trainer": {"training_error": f"Cannot begin training until the dataset, model, and trainer are initialized."}
            }
            server_communicator.send_message(data)
            self.loading = False
            return
        
        t = threading.Thread(target = self.trainer.train_threaded,
                                args=(self,))
        self.trainer.training = True
        t.start()
        data = {
            "trainer": {"training_started": True}
        }
        server_communicator.send_message(data)
        self.loading = False
        
    def on_train_pause(self):
        global server_communicator
        self.loading = True
        if(self.dataset is None or self.model is None or self.trainer is None):
            data = {
                "trainer": {"training_error": f"Cannot begin training until the dataset, model, and trainer are initialized."}
            }
            server_communicator.send_message(data)
            self.loading = False
            return
        
        self.trainer.training = False
        data = {
            "trainer": {"training_paused": True}
        }
        server_communicator.send_message(data)
        self.loading = False

    def on_train_step(self, iteration, img, loss, ema_loss):
        global server_communicator
        if (iteration % 25 == 0):
            data = {"trainer": {"step": {
                "iteration": iteration,
                "max_iteration": self.settings.iterations,
                "loss": loss,
                "ema_loss": ema_loss
                }}
            }
            server_communicator.send_message(data)

    def on_debug_toggle(self, val):
        global server_communicator
        print(f"Setting debug to {val}")
        self.loading = True
        self.DEBUG = val
        if(self.dataset is not None):
            self.dataset.DEBUG = self.DEBUG
        if(self.trainer is not None):
            self.trainer.DEBUG = self.DEBUG
        if(self.model is not None):
            self.model.DEBUG = self.DEBUG
        data = {"debug": {"debug_enabled" if self.DEBUG else "debug_disabled": True}}
        server_communicator.send_message(data)
        self.loading = False

    def on_connect(self):
        global server_communicator
        # Send messages for each of the objects to send settings state for
        data = {"other": {"settings_state": self.settings.params, 
                          "debug": self.DEBUG,
                          "dataset_loaded": self.dataset is not None},
                "trainer": {"step": {"iteration": self.trainer._iteration,
                                     "max_iteration": self.settings.iterations,
                                     "loss": self.trainer.last_loss,
                                     "ema_loss": self.trainer.ema_loss}}}
        server_communicator.send_message(data)
        

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
                self.server_controller.on_connect()

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
                #print(f"Sending {data}")
                self.conn.send(data)
            except Exception as e:
                print("Failed to send data.")
                raise e


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
    
