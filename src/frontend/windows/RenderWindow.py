import dearpygui.dearpygui as dpg
from windows import Window
import numpy as np
import time

class RenderWindow(Window):
    def __init__(self, app_controller):
        super().__init__("render_window", app_controller)

        default_width = 400
        default_height = 400
        self.max_tex_width = 2000
        self.max_tex_height = 2000
        self.resizing = True
        self.app_controller.register_message_listener(self, "render")

        self.tex = np.ones([self.max_tex_height, self.max_tex_width, 4], 
                           dtype=np.float32)


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
            dpg.add_mouse_release_handler(callback=self.mouse_released)

        dpg.bind_item_handler_registry(self.tag, "render_window_resize_handler")
        dpg.set_viewport_resize_callback(self.on_resize)
        
    
    def mouse_released(self, sender, app_data):
        if(self.resizing):
            h = min(dpg.get_item_height(self.tag), self.max_tex_height)
            w = min(dpg.get_item_width(self.tag), self.max_tex_width)

            print(f"Resizing to {h}x{w}")
            dpg.configure_item("render_view_image", width=w, height=h,
                               uv_max = (w/self.max_tex_width, h/self.max_tex_height))
            #dpg.configure_item("render_view_texture", width=w, height=h)
            #r = np.random.random([h, w, 4]).astype(np.float32)
            #self.on_new_image(r)
            self.resizing = False
            

    def update_dynamic_texture(self, data):
        #print("Updating texture")
        self.tex[0:min(self.tex.shape[0], data.shape[0]),
                 0:min(self.tex.shape[1], data.shape[1]),
                 0:min(self.tex.shape[2], data.shape[2])] = data
        dpg.set_value("render_view_texture", self.tex)
        
        self.frames_this_update += 1
        t = time.time() - self.last_fps_update
        if (t > 1.0):
            fps = self.frames_this_update / t
            dpg.set_value(self.fps, f"FPS: {fps:0.02f}")
            self.frames_this_update = 0
            self.last_fps_update = time.time()


    def on_new_image(self, data):
        self.update_dynamic_texture(data)

    def on_resize(self):
        self.resizing = True

    def on_close(self):
        self.app_controller.update_view_menu(self.tag, False)
        dpg.delete_item("render_view_texture")
        dpg.delete_item("render_view_image")
        dpg.delete_item("render_window_resize_handler")
        dpg.delete_item(self.tag)
    
    def receive_message(self, data: dict):
        if("image" in data.keys()):
            img = data['image'].astype(np.float32) / 255.
            self.on_new_image(img)