import os
import sys
from dataset import Dataset
from model import GaussianModel
from trainer import Trainer
from argparse import ArgumentParser
from utils.system_utils import mkdir_p
from primitive_renderer import WebGPU_renderer
from settings import Settings
import threading
import multiprocessing.connection as connection
import signal 
import time
import torch
import numpy as np
from dataset.cameras import cam_from_gfx
from simplejpeg import encode_jpeg
from utils.sh_utils import RGB2SH
import subprocess

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
        self.primitive_renderer = WebGPU_renderer()
        self.primitive_renderer.add_selector()
        self.primitive_renderer.activate_selector()
        self.dataset = None

        self.loading = False
        self.renderer_enabled = True
        self.editor_enabled = False
        self.editor_selection_mask = False
        self.edit_list = []
        self.DEBUG = False
        
        self.server_communicator = ServerCommunicator(self, ip, port)

        self.average_training_time = 0
        self.average_rendering_time = 0
        self.average_communication_time = 0
        self.average_step_time = 0
        self.average_message_listening_time = 0
        self.average_opengl_time = 0
        
        self.main_loop()
       
    def process_message(self,data):
               
        
        if("initialize_dataset" in data.keys() and not self.loading):
            t = threading.Thread(target=self.initialize_dataset, 
                                 args=[data['initialize_dataset']],
                                 daemon=True,
                                 name="InitializeDatasetThread")
            self.loading = True
            t.start()
            
        if("update_trainer_settings" in data.keys() and not self.loading):
            t = threading.Thread(target=self.update_trainer_settings, 
                                 args=[data['update_trainer_settings']],
                                 daemon=True,
                                 name="UpdateTrainerSettingsThread")
            self.loading = True            
            t.start()
        
        if("update_model_settings" in data.keys() and not self.loading):
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

        if("mouse" in data.keys() and self.renderer_enabled):
            self.primitive_renderer.simulate_mouse(data['mouse'])
        
        if("keyboard" in data.keys() and self.renderer_enabled):
            self.primitive_renderer.simulate_mouse(data['keyboard'])

        if("save_model" in data.keys()):
            self.on_save_model(data['save_model'])

        if("load_model" in data.keys()):
            self.on_load_model(data['load_model'])
        
        if("editor_enabled" in data.keys()):
            self.editor_enabled = data['editor_enabled'][0]
            self.editor_selection_mask = data['editor_enabled'][1]
            
        if("edit" in data.keys()):
            d = data['edit']
            if "add" in d['type']:
                self.process_edit_add(d['payload'])
            
            if "remove" in d['type']:
                self.process_edit_remove(d['payload'])

        if("load_default_model" in data.keys()):
            self.model.create_from_random_pcd()
            self.trainer.set_model(self.model)

    def process_edit_add(self, payload):
        num_points = payload[0]
        dist_type = payload[1]
        if(dist_type == "uniform"):
            samples = torch.rand([num_points, 3], device=self.settings.device, dtype=torch.float32)-0.5
        elif(dist_type == "normal"):
            samples = torch.randn([num_points, 3], device=self.settings.device, dtype=torch.float32).clamp(-1, 1)
        elif(dist_type == "inverse normal"):
            samples = torch.randn([num_points, 3], device=self.settings.device, dtype=torch.float32).clamp(-1, 1)
            samples[samples>0] = 1 - samples[samples>0]
            samples[samples<0] = -1 - samples[samples<0]

        samples = self.primitive_renderer.selector.transform_to_selector_world(samples)

        max_scale = (samples.amax(dim=0)-samples.amin(dim=0)) / (num_points**(1/3.))
        scales = torch.ones_like(samples) * max_scale
        scales = self.model.scaling_inverse_activation(scales)
        rots = torch.zeros([num_points, 4], device=self.settings.device, dtype=torch.float32)
        rots[:,0] = 1.
        opacities = self.model.inverse_opacity_activation(0.1 * torch.ones((num_points, 1), dtype=torch.float32, device=self.settings.device))
        features = np.zeros

        rgb = RGB2SH(0.5 * torch.ones([num_points, 3], dtype=torch.float32, device=self.settings.device))
        features = torch.zeros((num_points, 3, (self.settings.sh_degree + 1) ** 2)).float().to(self.settings.device)
        features[:, :3, 0 ] = rgb
        features[:, :3, 1:] = 0.0
        self.trainer.densification_postfix(samples, features[:,0:3,0:1].mT, features[:,:,1:].mT, opacities, scales, rots)

    def process_edit_remove(self, payload):
        remove_pct = payload[0]
        decimate_type = payload[1]
        redistribute = payload[2]

        mask = self.primitive_renderer.get_selection_mask(self.model.get_xyz).type(torch.bool)
        print(self.model.get_num_gaussians)
        print(mask.sum())        
        self.trainer.prune_points(mask)
        print(self.model.get_num_gaussians)
        


    def initialize_dataset(self, data):
        # relative dataset path
        datasets_path = os.path.abspath(os.path.join(os.path.abspath(__file__), "..", "..", "..", "data"))
        data['dataset_path'] = os.path.join(datasets_path, data['dataset_path'])

        # Just load all key data to settings
        for k in data.keys():
            # Check if the keys line up
            if k in self.settings.keys():
                self.settings.params[k] = data[k]

        # Check to make sure dataset path exists
        if not os.path.exists(data["dataset_path"]) and not self.DEBUG:
            self.server_communicator.send_message({
                "dataset": {"dataset_error": f"Dataset path does not exist: {data['dataset_path']}"}
            })
            self.loading = False
            return
        
        # Check if the data device exists
        try:
            a = torch.empty([32], dtype=torch.float32, device=data['data_device'])
            del a
        except Exception as e:
            self.server_communicator.send_message({
                "dataset": {"dataset_error": f"Dataset device does not exist: {data['data_device']}"}
            })
            self.loading = False
            return
        
        # Create dataset
        try:
            self.server_communicator.send_message({"dataset": {"dataset_loading": f"Attempting to load dataset..."}})
            self.dataset = Dataset(self.settings, debug=self.DEBUG)
            self.trainer.set_dataset(self.dataset)
            self.trainer.on_settings_update(self.settings)
            #if(self.dataset.scene_info.point_cloud is not None):
                #self.model.create_from_pcd(self.dataset.scene_info.point_cloud)
                #self.trainer.set_model(self.model)
        except Exception as e:
            # Doesn't recognize dataset, use COLMAP to turn it into a dataset from images
            self.server_communicator.send_message({"dataset": {"dataset_loading": f"Attempting to create dataset from COLMAP..."}})

            # move images in directory to an <input> folder
            if not os.path.exists(os.path.join(data['dataset_path'], "input")):
                mkdir_p(os.path.join(data['dataset_path'], "input"))
            for item in os.listdir(data['dataset_path']):
                if '.png' in item.lower() or ".jpg" in item.lower() or ".jpeg" in item.lower():
                    os.rename(os.path.join(data['dataset_path'], item), 
                              os.path.join(data['dataset_path'], "input", item))
            
            cmd = ["python", "convert.py", "-s", data['dataset_path']]
            if data['colmap_path'] != "":
                cmd.append("--colmap_executable")
                cmd.append(os.path.abspath(data['colmap_path']))
            if data['imagemagick_path'] != "":    
                cmd.append("--imagemagick_path")
                cmd.append(os.path.abspath(data['imagemagick_path']))      

            try:
                s = subprocess.Popen(cmd)
                s.wait()
                try:
                    self.server_communicator.send_message({"dataset": {"dataset_loading": f"COLMAP complete. Loading dataset..."}})
                    self.dataset = Dataset(self.settings, debug=self.DEBUG)
                    self.trainer.set_dataset(self.dataset)
                    self.trainer.on_settings_update(self.settings)
                except Exception as e:
                    # Doesn't recognize dataset still
                    self.server_communicator.send_message({"dataset": {"dataset_error": f"Error loading dataset."}})
                    return
            except Exception as e:
                self.server_communicator.send_message({
                    "dataset": {"dataset_error": f"Error running colmap on new dataset."}
                })
            

            

        self.server_communicator.send_message({
            "dataset": {"dataset_initialized": f"Dataset was initialized."}
        })
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
        self.primitive_renderer.resize(data['width'], data['height'])
        self.primitive_renderer.camera.fov = data['fov']
        self.primitive_renderer.camera.depth_range = [data['near_plane'],data['far_plane']]

    def on_train_start(self):
        
        if(self.dataset is None or self.model is None or self.trainer is None or self.loading):
            data = {
                "trainer": {"training_error": f"Cannot begin training until the dataset, model, and trainer are initialized."}
            }
            self.server_communicator.send_message(data)
            self.loading = False
            return
        
       
        self.loading = True
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
        self.server_communicator.send_message(
            {"connection": {
                "connected": True
                }
            }
        )

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
                    "fov": self.primitive_renderer.camera.fov,
                    "near_plane": self.primitive_renderer.camera.near,
                    "far_plane": self.primitive_renderer.camera.far
                }
            }                  
        }
        self.server_communicator.send_message(data)
        self.renderer_enabled = True

    def on_disconnect(self):
        #self.trainer.training = False
        self.renderer_enabled = False

    def render(self):
        t0 = time.time()
        
        if(self.editor_enabled):
            rgba_buffer, depth_buffer = self.primitive_renderer.render(self.settings)     
            selection_mask = self.primitive_renderer.get_selection_mask(self.model.get_xyz) if self.editor_selection_mask else None

        else:
            rgba_buffer = None
            depth_buffer = None
            selection_mask = None
            self.primitive_renderer.controller_tick()
        time_opengl = time.time() - t0
        self.average_opengl_time = self.average_opengl_time*0.8 + time_opengl*0.2


        render_package = self.model.render(
            cam_from_gfx(self.primitive_renderer.camera, self.primitive_renderer.canvas),
            rgba_buffer=rgba_buffer, depth_buffer = depth_buffer, selection_mask=selection_mask)
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
        
        t0 = time.time()

        if(self.model.initialized and self.renderer_enabled):
            img = self.render()
            img_jpg = self.encode_img(img)
            self.send_render_image(img_jpg)
            
        
        render_time = time.time() - t0
        self.average_rendering_time = self.average_rendering_time*0.8 + render_time*0.2

    def do_train_step(self):
        if(self.trainer.training):
            
            t0 = time.time()
            i, last_img, last_loss, ema_last_loss = self.trainer.step()
            
            t = time.time()
            train_time = t - t0
            self.average_training_time = self.average_training_time*0.8 + train_time*0.2

            if(i % 50 == 0):
                self.send_train_data(i, last_loss, ema_last_loss)
            if(i == self.settings.iterations):
                self.trainer.training = False

    def on_save_model(self, path):
        models_path = os.path.join(os.path.abspath(__file__), "..", "..", "..", "savedModels")
        
        if(".ply" not in path[-4:]):
            path = path + ".ply"

        path = os.path.join(models_path, path)
        path = os.path.abspath(path)
        if not self.model.initialized:
            data = {"other" : {"error": f"Model not initialized, cannot save."}}
            self.server_communicator.send_message(data)
            return
        self.model.save_ply(path)
        data = {"other" : {"popup": f"Model saved to \n {path}."}}
        self.server_communicator.send_message(data)

    def on_load_model(self, path):
        models_path = os.path.join(os.path.abspath(__file__), "..", "..", "..", "savedModels")
        path = os.path.join(models_path, path)
        
        if(not os.path.exists(path)):
            path2 = path + ".ply"
            if not os.path.exists(path2):
                data = {"other" : {"error": f"Location doesn't exist: {path}"}}
                self.server_communicator.send_message(data)
                return
            else:
                path = path2
        
        try:
            self.model.load_ply(path)
            self.trainer.set_model(self.model)
            data = {"other" : {"popup": f"Model loaded."}}
            self.server_communicator.send_message(data)
        except Exception as e:
            data = {"other" : {"error": f"Error loading the model."}}
            self.server_communicator.send_message(data)
            return

    def main_loop(self):
        

        t = time.time()
        while(True):
            
            t_start = time.time()

            self.process_messages()
            
            self.render_screen_image()
            
            self.do_train_step()
            
            if(not (self.model.initialized or self.renderer_enabled) and not self.trainer.training):
                time.sleep(0.01)

            
            self.average_step_time = self.average_step_time*0.8 + 0.2*(time.time()-t_start)

            if(time.time() > t + 1 and self.server_communicator.connected):
                #print(f"Render: {1/(1e-12+self.average_rendering_time):0.02f} FPS, \t " + \
                #    f"Train: {1/(1e-12+self.average_training_time) : 0.02f} FPS, \t " + \
                #    f"Send img: {self.average_communication_time * 1000 : 0.02f}ms, \t " + \
                #    f"Msg listen: {self.average_message_listening_time * 1000 : 0.02f}ms, \t " + \
                #    f"Full step: {self.average_step_time*1000:0.02f}ms")
                print(f"[{self.trainer._iteration}/{self.settings.iterations}] " + \
                      f"train: {self.average_training_time*1000:0.02f}ms, " + \
                      f"Render {self.average_rendering_time*1000:0.02f}ms")
                t = time.time()
            time.sleep(1/1000.)

            
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
        self.connected = True
        self.listening = False
        self.server_controller.on_connect()

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
    
