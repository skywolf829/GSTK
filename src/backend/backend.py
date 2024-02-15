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
from simplejpeg import encode_jpeg
#from torchvision.io import encode_jpeg as encode_jpeg_torch
#import yappi

def signal_handler(sig, frame):
    pid = os.getpid()
    print('Closing')
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
        
        self.server_communicator = ServerCommunicator(self, ip, port)

        #self.main_thread = threading.Thread(target=self.main_loop, 
        #                                      args=(), 
        #                                      daemon=True,
        #                                      name="TrainRenderThread")
        #self.main_thread.start()

        self.average_training_time = 0
        self.average_rendering_time = 0
        self.average_communication_time = 0
        self.average_step_time = 0
        self.average_message_listening_time = 0
        #self.main_thread.join()
        self.main_loop()
       
    def process_message(self,data):
        #print("Received message")
        #print(data)
        if(self.loading):
            data = {"other" : {"error": "Please wait until the current operation is completed"}}
            self.server_communicator.send_message(data)
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

        if("camera_move" in data.keys() and self.renderer_enabled):
            self.render_cam.process_camera_move(
                data['camera_move'])
            
    def initialize_dataset(self, data):
        # Just load all key data to settings
        for k in data.keys():
            # Check if the keys line up
            if k not in self.settings.keys():
                data = {
                    "dataset": {"dataset_error": f"Key {k} from client not present in Settings"}
                }
                self.server_communicator.send_message(data)
                self.loading = False
                return
            else:
                self.settings.params[k] = data[k]
        

        # Check to make sure dataset path exists
        if not os.path.exists(data["dataset_path"]) and not self.DEBUG:
            data = {
                "dataset": {"dataset_error": f"Dataset path does not exist: {data['dataset_path']}"}
            }
            self.server_communicator.send_message(data)
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
            self.server_communicator.send_message(data)
            self.loading = False
            return
        
        # Create dataset
        try:
            data = {"dataset": {"dataset_loading": f""}}
            self.server_communicator.send_message(data)
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
            self.server_communicator.send_message(data)
            self.loading = False
            return
        
        data = {
            "dataset": {"dataset_initialized": f"Dataset was initialized."}
        }
        self.server_communicator.send_message(data)
        self.loading = False
        
    def update_trainer_settings(self, data):
        # Just load all key data to settings
        for k in data.keys():
            # Check if the keys line up
            if k not in self.settings.keys():
                data = {
                    "trainer": {"trainer_settings_updated_error": f"Key {k} from client not present in Settings"}
                }
                self.server_communicator.send_message(data)
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
            self.server_communicator.send_message(data)
            self.loading = False
            return
        
        data = {
            "trainer": {"trainer_settings_updated": f"Trainer settings successfully updated."}
        }
        self.server_communicator.send_message(data)
        print("Initialized model and trainer")
        self.loading = False

    def update_model_settings(self, data):

        self.loading = True
        # Check if the data device exists
        try:
            a = torch.empty([32], dtype=torch.float32, device=data['device'])
            del a
        except Exception as e:
            data = {
                "model": {"model_settings_updated_error": f"Device does not exist: {data['device']}"}
            }
            self.server_communicator.send_message(data)
            self.loading = False
            return
        
        if(data['sh_degree'] < 0 or data['sh_degree'] > 3):
            data = {
                "model": {"model_settings_updated_error": f"SH degree is invalid: {data['device']}"}
            }
            self.server_communicator.send_message(data)
            self.loading = False
            return
        
        self.settings.params['sh_degree'] = data['sh_degree']
        self.settings.params['device'] = data['device']
        self.model.on_settings_update(self.settings)
        self.trainer.on_settings_update(self.settings)
        
        data = {
            "model": {"model_settings_updated": f"Model settings were updated"}
        }
        self.server_communicator.send_message(data)
        print("Updated model settings")
        self.loading = False

    def update_renderer_settings(self, data):
        self.renderer_enabled = data['renderer_enabled']
        self.render_cam.image_width = data['width']
        self.render_cam.image_height = data['height']
        self.render_cam.FoVx = np.deg2rad(data['fov_x'])
        self.render_cam.FoVy = np.deg2rad(data['fov_y'])
        self.render_cam.znear = data['near_plane']
        self.render_cam.zfar = data['far_plane']

    def on_train_start(self):
        
        self.loading = True
        if(self.dataset is None or self.model is None or self.trainer is None):
            data = {
                "trainer": {"training_error": f"Cannot begin training until the dataset, model, and trainer are initialized."}
            }
            self.server_communicator.send_message(data)
            self.loading = False
            return
        
       
        self.trainer.training = True
        data = {
            "trainer": {"training_started": True}
        }
        self.server_communicator.send_message(data)
        self.loading = False

    def on_train_pause(self):
        
        self.loading = True
        if(self.dataset is None or self.model is None or self.trainer is None):
            data = {
                "trainer": {"training_error": f"Cannot end training until the dataset, model, and trainer are initialized."}
            }
            self.server_communicator.send_message(data)
            self.loading = False
            return
        
        self.trainer.training = False
        
        data = {
            "trainer": {"training_paused": True}
        }
        self.server_communicator.send_message(data)
        self.loading = False

    def on_debug_toggle(self, val):
        
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
        self.server_communicator.send_message(data)
        self.loading = False

    def on_connect(self):
        
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
                    'renderer_enabled': self.renderer_enabled,
                    "fov": max(self.render_cam.FoVx, self.render_cam.FoVy) * 180. / np.pi,
                    "near_plane": self.render_cam.znear,
                    "far_plane": self.render_cam.zfar
                }
            }                  
        }
        self.server_communicator.send_message(data)
        self.renderer_enabled = True

    def on_disconnect(self):
        #self.trainer.training = False
        self.renderer_enabled = False

    def render(self):
        #rgba_buffer, depth_buffer = self.opengl_renderer.render(self.render_cam)
        #rgba_buffer = torch.tensor(rgba_buffer, dtype=torch.float32, device=self.settings.device) / 255.
        #depth_buffer = torch.tensor(depth_buffer, dtype=torch.float32, device=self.settings.device)*2 - 1
        
        render_package = self.model.render(self.render_cam) 
            #rgba_buffer=rgba_buffer, depth_buffer = depth_buffer)
        img = torch.clamp(render_package['render'], min=0, max=1.0) * 255
        return img
        
    def encode_img(self, img:torch.Tensor):
        
        img_npy = img.byte().permute(1, 2, 0).contiguous().cpu().numpy()
        img_jpeg = encode_jpeg(img_npy, quality=85, fastdct=True)
        return img_jpeg
    
    def send_render_image(self, img_jpeg):
        
        self.server_communicator.send_message(
            { "render": {
                "image" : img_jpeg,
                "update_time": self.average_step_time
                }
            }
        )

    def send_train_data(self, i, last_loss, ema_last_loss):
        
        data = {"trainer": 
                {
                    "step": {
                        "iteration": i,
                        "max_iteration": self.settings.iterations,
                        "loss": last_loss,
                        "ema_loss": ema_last_loss,
                        "update_time": self.average_step_time
                    }
                }
            }
        self.server_communicator.send_message(data)

    def process_messages(self):
        t0 = time.time()
        self.server_communicator.step()
        for msg in self.server_communicator.data_to_process:
            self.process_message(msg)
        self.server_communicator.data_to_process.clear()
        t_messages = time.time() - t0
        self.average_message_listening_time = self.average_message_listening_time*0.8 + t_messages*0.2

    def render_screen_image(self):
        if(self.model.initialized and self.renderer_enabled):
            
            t0 = time.time()
            img = self.render()
            render_time = time.time() - t0
            self.average_rendering_time = self.average_rendering_time*0.8 + render_time*0.2
            t0 = time.time()
            img_jpg = self.encode_img(img)
            self.send_render_image(img_jpg)
            comm_this_step = time.time() - t0
            self.average_communication_time = self.average_communication_time*0.8 + comm_this_step*0.2

    def do_train_step(self):
        if(self.trainer.training):
            
            t0 = time.time()
            i, last_img, last_loss, ema_last_loss = self.trainer.step()
            
            t = time.time()
            train_time = t - t0
            self.average_training_time = self.average_training_time*0.8 + train_time*0.2

            if(i % 50 == 0):
                self.send_train_data(i, last_loss, ema_last_loss)

    def main_loop(self):
        self.opengl_renderer = OpenGL_renderer()
        self.opengl_renderer.add_item(Cube())

        t = time.time()
        while(True):
            
            t_start = time.time()

            self.process_messages()
            
            self.render_screen_image()
            
            self.do_train_step()
            
            if(not (self.model.initialized or self.renderer_enabled) and not self.trainer.training):
                time.sleep(0.01)

            
            self.average_step_time = self.average_step_time*0.8 + 0.2*(time.time()-t_start)

            if(time.time() > t + 1):
                #print(f"Render: {1/(1e-12+self.average_rendering_time):0.02f} FPS, \t " + \
                #    f"Train: {1/(1e-12+self.average_training_time) : 0.02f} FPS, \t " + \
                #    f"Send img: {self.average_communication_time * 1000 : 0.02f}ms, \t " + \
                #    f"Msg listen: {self.average_message_listening_time * 1000 : 0.02f}ms, \t " + \
                #    f"Full step: {self.average_step_time*1000:0.02f}ms")
                t = time.time()

            
class ServerCommunicator():

    def __init__(self, server_controller : ServerController, ip : str, port: int, *args, **kwargs): 
   
        self.server_controller = server_controller
        self.ip = ip
        self.port = port

        self.connected = False
        self.listening = False
        self.listener : connection.Listener = None
        self.conn : connection.Connection = None


        self.data_to_process = []

    def wait_for_connection(self):
        self.listener : connection.Listener = connection.Listener((self.ip, self.port), authkey=b"GRAVITY")
        print(f"Listening on {self.ip}:{self.port}")
        
        self.conn : connection.Connection = self.listener.accept()
        print(f'Connection accepted from {self.listener.last_accepted}')
        self.server_controller.on_connect()
        self.connected = True
        self.listening = False

    def step(self):
        if self.listening:
            return
        
        if not self.connected:
            self.listening = True
            # Threaded so cntl+c works
            t = threading.Thread(target=self.wait_for_connection,
                                 args=(),
                                 daemon=True)
            t.start()

        else:
            # blocking call, see check_for_msg
            self.gather_messages()

    def disconnect(self):
        self.connected = False
        self.conn.close()
        self.listener.close()
        self.server_controller.on_disconnect()

    def gather_messages(self):
        try:
            # poll tells us if there is a message ready
            # read all messages available
            while(self.conn.poll()):
                # Blocking call, will wait here
                data = self.conn.recv()
                self.data_to_process.append(data)

        except Exception:
            print(f"Connection closed")
            self.disconnect()

    def send_message(self, data):
        if(self.connected):
            try:
                #print(f"Sending {data}")
                self.conn.send(data)
            except Exception as e:
                print("Failed to send data.")

if __name__ == "__main__":
    # Set up command line argument parser
    parser = ArgumentParser(description="Backend server script")
    parser.add_argument('--ip', type=str, default="127.0.0.1")
    parser.add_argument('--port', type=int, default=10789)
    args = parser.parse_args()
    #yappi.start()

    s = ServerController(args.ip, args.port)

    # infinite loop until ctrl-c
    #while True:
    #    time.sleep(1.0)
    
