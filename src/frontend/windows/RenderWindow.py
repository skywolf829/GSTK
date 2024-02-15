import dearpygui.dearpygui as dpg
from windows import Window
import numpy as np
import time
from simplejpeg import decode_jpeg

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
        self.modifiers = []

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
            dpg.add_mouse_release_handler(callback=self.on_mouse_left_release, button=dpg.mvMouseButton_Left)
            dpg.add_mouse_click_handler(callback=self.on_mouse_left_click, button=dpg.mvMouseButton_Left)
            dpg.add_mouse_drag_handler(callback=self.on_mouse_left_drag, button=dpg.mvMouseButton_Left, threshold=5)

            dpg.add_key_down_handler(callback=self.on_key_down)
            dpg.add_key_release_handler(callback=self.on_key_release)

            dpg.add_mouse_wheel_handler(callback=self.on_mouse_wheel)
            
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
        data = decode_jpeg(data, fastdct=False, fastupsample=False)
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
    
    def on_mouse_left_click(self):
        pass

    def on_mouse_left_drag(self, usr_data, direction):
        if(not dpg.is_item_focused(self.tag)):
            return
        dx = direction[1] - self.last_dx
        dy = -(direction[2] - self.last_dy)
        self.app_controller.app_communicator.send_message(
            {"camera_move":
                {
                "mouse_move": {
                    "dx": dx,
                    "dy": dy,
                    "modifiers": self.modifiers
                }}
             }
        )
        self.last_dx = direction[1]
        self.last_dy = direction[2]

    def on_mouse_left_release(self):
        self.update_window_size()
        self.last_dx=0
        self.last_dy=0
        
    def on_resize_viewport(self):
        pass

    def on_key_down(self, user_data, key_code_data):
        if(not dpg.is_item_focused(self.tag)):
            return
        key_code = key_code_data[0]
        t = key_code_data[1]
        right = 0
        up = 0
        if(key_code == dpg.mvKey_Left):
            right -= 1
        if(key_code == dpg.mvKey_Right):
            right += 1
        if(key_code == dpg.mvKey_Up):
            up += 1
        if(key_code == dpg.mvKey_Down):
            up -= 1
            
        if(key_code == dpg.mvKey_Control and "control" not in self.modifiers):
            self.modifiers.append("control")
        if(key_code == dpg.mvKey_Shift and "shift" not in self.modifiers):
            self.modifiers.append("shift")
        if(key_code == dpg.mvKey_Alt and "alt" not in self.modifiers):
            self.modifiers.append("alt")


        if(up != 0 or right != 0):
            self.app_controller.app_communicator.send_message(
                {"camera_move":
                    {
                    "key_pressed": {
                        "up": up,
                        "right": right
                    }}
                }
            )

    def on_key_release(self, user_data, key_code):
        if(key_code == dpg.mvKey_Control and "control" in self.modifiers):
            self.modifiers.remove("control")
        if(key_code == dpg.mvKey_Shift and "shift" in self.modifiers):
            self.modifiers.remove("shift")
        if(key_code == dpg.mvKey_Alt and "alt" in self.modifiers):
            self.modifiers.remove("alt")

    def on_mouse_wheel(self, user_data, data):
        self.app_controller.app_communicator.send_message(
            {"camera_move":
                {
                "scrollwheel": {
                    "val": data
                }
                }
             }
        )

    def receive_message(self, data: dict):
        if("image" in data.keys()):
            img = data['image']
            self.on_new_image(img)