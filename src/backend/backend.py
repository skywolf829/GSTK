import os
import sys
from dataset import Dataset
from model import GaussianModel
from trainer import Trainer
from argparse import ArgumentParser
from utils.system_utils import mkdir_p
from opengl_renderer import OpenGL_renderer, Cube
from settings import Settings
import threading
import multiprocessing.connection as connection
import signal 
import time
import torch
import numpy as np
from dataset.cameras import RenderCam
import multiprocessing
import cv2
#import yappi

def signal_handler(sig, frame):
    pid = os.getpid()
    print('Exiting')
    global server_communicator
    server_communicator.stop = True
    # This is required otherwise the ServerCommunicator will stay listening
    #yappi.stop()
    #yappi.get_func_stats(ctx_id=1).print_all()
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
        self.opengl_renderer = None
        self.dataset = None
        self.render_cam = RenderCam()

        self.loading = False
        self.renderer_enabled = True
        self.DEBUG = False

        # < 0.5 is more preference to rendering, > 0.5 is more preference to training
        self.render_balance = 0.5 
        self.training_balance = 0.5

        global server_communicator
        server_communicator = ServerCommunicator(self, ip, port)
        server_communicator.start()

        self.render_thread = threading.Thread(target=self.render_loop, 
                                              args=(), 
                                              daemon=True,
                                              name="RenderThread")
        self.render_thread.start()

        self.average_training_time = 0
        self.average_rendering_time = 0
        self.last_train_step_time = 0
       
    def process_message(self,data):
        global server_communicator
        #print("Received message")
        #print(data)
        if(self.loading):
            data = {"other" : {"error": "Please wait until the current operation is completed"}}
            server_communicator.send_message(data)
            return
        
        
        if("initialize_dataset" in data.keys()):
            t = threading.Thread(target=self.initialize_dataset, 
                                 args=[data['initialize_dataset']],
                                 daemon=True,
                                 name="InitializeDatasetThread")
            self.loading = True
            t.start()
            
        if("update_trainer_settings" in data.keys()):
            t = threading.Thread(target=self.update_trainer_settings, 
                                 args=[data['update_trainer_settings']],
                                 daemon=True,
                                 name="UpdateTrainerSettingsThread")
            self.loading = True            
            t.start()
        
        if("update_model_settings" in data.keys()):
            t = threading.Thread(target=self.update_model_settings, 
                                 args=[data['update_model_settings']],
                                 daemon=True,
                                 name="UpdateModelSettingsThread")
            self.loading = True            
            t.start()
        
        if("update_renderer_settings" in data.keys()):
           self.update_renderer_settings(data['update_renderer_settings'])

        if("training_start" in data.keys()):
            self.on_train_start()
        
        if("training_pause" in data.keys()):
            self.on_train_pause()

        if("debug" in data.keys()):
            self.on_debug_toggle(data['debug'])

        if("camera_move" in data.keys()):
            self.render_cam.process_camera_move(
                data['camera_move'])
            
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
            self.trainer.set_dataset(self.dataset)
            self.trainer.on_settings_update(self.settings)
            if not self.model.initialized:
                self.model.create_from_pcd(self.dataset.scene_info.point_cloud)
                self.trainer.set_model(self.model)
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
            self.trainer.on_settings_update(self.settings)
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
        self.trainer.on_settings_update(self.settings)
        
        data = {
            "model": {"model_settings_updated": f"Model settings were updated"}
        }
        server_communicator.send_message(data)
        print("Updated model settings")
        self.loading = False

    def update_renderer_settings(self, data):
        self.render_cam.image_width = data['width']
        self.render_cam.image_height = data['height']
        self.render_cam.FoVx = np.deg2rad(data['fov_x'])
        self.render_cam.FoVy = np.deg2rad(data['fov_y'])
        self.render_cam.znear = data['near_plane']
        self.render_cam.zfar = data['far_plane']
        self.render_balance = np.clip(data['balance'], 0., 1.)
        self.training_balance = 1 - self.render_balance

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
        
        self.training_thread = threading.Thread(target = self.train_loop,
                                args=(), daemon=True, name="TrainingThread")
        self.trainer.training = True
        self.last_train_step_time = time.time()
        self.training_thread.start()
        data = {
            "trainer": {"training_started": True}
        }
        server_communicator.send_message(data)
        self.loading = False
        #server_communicator.disconnect()

    def train_loop(self):
        global server_communicator
        while self.trainer.training:
            t0 = time.time()
            i, last_img, last_loss, ema_last_loss = self.trainer.step()
            t = time.time()
            t_passed = t - self.last_train_step_time
            self.average_training_time = self.average_training_time*0.8 + t_passed*0.2

            if(i % 50 == 0):
                data = {"trainer": 
                            {
                                "step": {
                                    "iteration": i,
                                    "max_iteration": self.settings.iterations,
                                    "loss": last_loss,
                                    "ema_loss": ema_last_loss,
                                    "update_time": self.average_training_time
                                }
                            }
                        }
                server_communicator.send_message(data)

            self.last_train_step_time = time.time()
            update_render_time = self.average_rendering_time + self.average_training_time
            p_step = self.average_training_time / update_render_time
            diff = self.training_balance - p_step
            if(diff > 0):
                time.sleep(diff * update_render_time)

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
        data =  {
            "other": {
                "settings_state": self.settings.params, 
                "debug": self.DEBUG,
                "dataset_loaded": self.dataset is not None,
            },
            "trainer": {
                "step": {
                    "iteration": self.trainer._iteration,
                    "max_iteration": self.settings.iterations,
                    "loss": self.trainer.last_loss,
                    "ema_loss": self.trainer.ema_loss
                }
            },
            "renderer": {
                "settings_state":{
                    "fov": max(self.render_cam.FoVx, self.render_cam.FoVy) * 180. / np.pi,
                    "near_plane": self.render_cam.znear,
                    "far_plane": self.render_cam.zfar,
                    "balance": self.render_balance
                }
            }                  
        }
        server_communicator.send_message(data)
        
    def render_loop(self):
        global server_communicator

        # Have to use same thread for opengl rendering
        self.opengl_renderer = OpenGL_renderer()
        self.opengl_renderer.add_item(Cube())

        while self.renderer_enabled:
            if(server_communicator.state == "connected" and not self.loading):
                if(self.model.initialized):
                    t0 = time.time()
                    rgba_buffer, depth_buffer = self.opengl_renderer.render(self.render_cam)
                    rgba_buffer = torch.tensor(rgba_buffer, dtype=torch.float32, device=self.settings.device) / 255.
                    depth_buffer = torch.tensor(depth_buffer, dtype=torch.float32, device=self.settings.device)*2 - 1
                    #print(rgba_buffer)
                    
                    render_package = self.model.render(self.render_cam, 
                        rgba_buffer=rgba_buffer, depth_buffer = depth_buffer)
                    img = torch.clamp(render_package['render'], min=0, max=1.0) * 255
                    #img = torch.clamp(rgba_buffer[:,:,0:3], min=0, max=1.0).permute(2, 0, 1) * 255

                    img_npy = img.byte().permute(1, 2, 0).contiguous().cpu().numpy()
                    _, img_jpeg = cv2.imencode(".jpeg", img_npy)
                    t = time.time() - t0
                    self.average_rendering_time = self.average_rendering_time*0.8 + t*0.2
                    server_communicator.send_message(
                        { "render": {
                            "image" : img_jpeg.tobytes(),
                            "update_time": self.average_rendering_time
                            }
                        }
                    )
                    update_render_time = self.average_rendering_time + self.average_training_time
                    p_render = self.average_rendering_time / update_render_time
                    diff = self.render_balance -  p_render
                    if(diff > 0 and self.trainer.training):
                        time.sleep(diff * update_render_time)

            else:
                time.sleep(1.0)


class ServerCommunicator(threading.Thread):

    def __init__(self, server_controller : ServerController, ip : str, port: int, *args, **kwargs): 
        super().__init__(*args, **kwargs, daemon=True, name="ServerCommunicatorThread")

        self.state = "uninitialized"        
        self.server_controller = server_controller
        self.ip = ip
        self.port = port
        self.listener : connection.Listener = None
        self.conn : connection.Connection = None
        self.stop = False
        self.lock = multiprocessing.Lock()

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
            #time.sleep(0.0001)
            
        print("Stop signal detected")
        # clean up
        if(self.conn):
            self.conn.close()
        if(self.listener):
            self.listener.close()

        self.conn = None
        self.listener = None

    def disconnect(self):
        self.state = "uninitialized"
        self.conn.close()
        self.listener.close()

    def check_for_msg(self):
        item = None
        try:
            # poll tells us if there is a message ready
            if(self.conn.poll()):
                # Blocking call, will wait here
                item = self.conn.recv()
        except Exception:
            print(f"Connection closed")
            self.disconnect()
            item = None
        return item

    def send_message(self, data):
        with self.lock:
            if(self.state == "connected"):
                try:
                    #print(f"Sending {data}")
                    self.conn.send(data)
                except Exception as e:
                    print("Failed to send data.")


# global communicator so the thread can be shut down with ctrl-c
server_communicator = None

if __name__ == "__main__":
    # Set up command line argument parser
    parser = ArgumentParser(description="Backend server script")
    parser.add_argument('--ip', type=str, default="127.0.0.1")
    parser.add_argument('--port', type=int, default=10789)
    args = parser.parse_args()
    #yappi.start()

    s = ServerController(args.ip, args.port)

    # infinite loop until ctrl-c
    while True:
        time.sleep(1.0)
    
