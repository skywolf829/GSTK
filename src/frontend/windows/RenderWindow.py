import dearpygui.dearpygui as dpg
from windows import Window
import numpy as np

class RenderWindow(Window):
    def __init__(self, app_controller):
        self.app_controller = app_controller
        self.tag = "render_window"
        if(dpg.does_item_exist(self.tag)):
            self.on_close()
            del self
            return
        default_width = 400
        default_height = 400
        self.max_tex_width = 2000
        self.max_tex_height = 2000
        self.resizing = True

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
            dpg.add_image("render_view_texture", tag="render_view_image")


        with dpg.item_handler_registry(tag="render_window_resize_handler", show=False):
            dpg.add_item_resize_handler(callback=self.on_resize)
        
        with dpg.handler_registry(show=True):
            dpg.add_mouse_release_handler(callback=self.mouse_released)

        dpg.bind_item_handler_registry(self.tag, "render_window_resize_handler")
        dpg.set_viewport_resize_callback(self.on_resize)
        #app_controller.update_view_menu(self.tag, True)
    
    def mouse_released(self, sender, app_data):
        if(self.resizing):
            h = min(dpg.get_item_height(self.tag), self.max_tex_height)
            w = min(dpg.get_item_width(self.tag), self.max_tex_width)

            print(f"Resizing to {h}x{w}")
            dpg.configure_item("render_view_image", width=w, height=h,
                               uv_max = (w/self.max_tex_width, h/self.max_tex_height))
            #dpg.configure_item("render_view_texture", width=w, height=h)
            r = np.random.random([h, w, 4]).astype(np.float32)
            self.tex[0:h, 0:w, 0:4] = r
            dpg.set_value("render_view_texture", self.tex)
            '''
            data = {
                "render_resolution": {
                    "width": w,
                    "height": h
                }
            }
            self.app_controller.app_communicator.send_message(data)
            '''
            self.resizing = False

    def update_dynamic_texture(self, data):
        print("Updating texture")
        self.tex[0:min(self.tex.shape[0], data.shape[0]),
                 0:min(self.tex.shape[1], data.shape[1]),
                 0:min(self.tex.shape[2], data.shape[2])] = data
        dpg.set_value("render_view_texture", self.tex)

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
    