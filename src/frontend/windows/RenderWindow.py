import dearpygui.dearpygui as dpg
from windows import Window
import numpy as np
import time
import cv2

class RenderWindow(Window):
    def __init__(self, app_controller):
        super().__init__("render_window", app_controller)

        default_width = 800
        default_height = 800
        self.max_tex_width = 2000
        self.max_tex_height = 2000
        self.resizing = True
        self.app_controller.register_message_listener(self, "render")

        self.tex = np.zeros([self.max_tex_height, self.max_tex_width, 4], 
                           dtype=np.float32)
        self.tex[:,:,-1] = 1


        with dpg.texture_registry(show=False):
            dpg.add_raw_texture(width=self.max_tex_width, 
                        height=self.max_tex_height, 
                        default_value=self.tex, 
                        format=dpg.mvFormat_Float_rgba,
                        tag="render_view_texture")
                
        with dpg.window(label="Render View", tag=self.tag, 
                        width=default_width, height=default_height,
                        on_close=self.on_close, no_scrollbar=True,
                        no_scroll_with_mouse=True):
            self.fps = dpg.add_text("FPS: -")
            dpg.add_image("render_view_texture", tag="render_view_image")

        self.last_fps_update = time.time()
        self.frames_this_update : int = 0

        with dpg.item_handler_registry(tag="render_window_resize_handler", show=False):
            dpg.add_item_resize_handler(callback=self.on_resize)
        
        with dpg.handler_registry(show=True):
            dpg.add_mouse_release_handler(callback=self.on_mouse_release)
            dpg.add_mouse_click_handler(callback=self.on_mouse_click)
            dpg.add_mouse_drag_handler(callback=self.on_mouse_drag, threshold=5)

        dpg.bind_item_handler_registry(self.tag, "render_window_resize_handler")
        dpg.set_viewport_resize_callback(self.on_resize_viewport)

        self.last_dx = 0
        self.last_dy = 0
  
    def update_window_size(self, force=False):
        if(self.resizing or force):
            h = min(dpg.get_item_height(self.tag), self.max_tex_height)
            w = min(dpg.get_item_width(self.tag), self.max_tex_width)

            #print(f"Resizing to {h}x{w}")
            dpg.configure_item("render_view_image", width=w, height=h,
                uv_max = (w/self.max_tex_width, h/self.max_tex_height))
            self.resizing = False
            #if(self.app_controller.renderer_settings_window is not None):
            #    self.app_controller.renderer_settings_window.update_renderer_settings()
            
    def on_new_image(self, data):
        #print("Updating texture")
        data = np.frombuffer(data, dtype=np.byte)
        data = cv2.imdecode(data, cv2.IMREAD_COLOR)
        data = data.astype(np.float32) / 255.

        x_dim = min(self.tex.shape[0], data.shape[0])
        y_dim = min(self.tex.shape[1], data.shape[1])
        z_dim = min(self.tex.shape[2], data.shape[2])
        self.tex[0:x_dim,0:y_dim,0:z_dim] = data[0:x_dim,0:y_dim,0:z_dim]
        dpg.set_value("render_view_texture", self.tex)
        
        dpg.configure_item("render_view_image",
            uv_max = (y_dim/self.max_tex_width, x_dim/self.max_tex_height))
        
        self.frames_this_update += 1
        t = time.time() - self.last_fps_update
        if (t > 1.0):
            fps = self.frames_this_update / t
            dpg.set_value(self.fps, f"FPS: {fps:0.02f}")
            self.frames_this_update = 0
            self.last_fps_update = time.time()

    def on_resize(self):
        self.resizing = True
    
    def on_mouse_click(self):
        pass

    def on_mouse_drag(self, button, direction):
        dx = direction[1] - self.last_dx
        dy = -(direction[2] - self.last_dy)
        modifiers = []
        
        self.app_controller.app_communicator.send_message(
            {"camera_move":
                {
                    "dx": dx,
                    "dy": dy,
                    "modifiers": modifiers
                }
             }
        )
        self.last_dx = direction[1]
        self.last_dy = direction[2]

    def on_mouse_release(self):
        self.update_window_size()
        self.last_dx=0
        self.last_dy=0
        
    def on_resize_viewport(self):
        pass

    def receive_message(self, data: dict):
        if("image" in data.keys()):
            img = data['image']
            self.on_new_image(img)