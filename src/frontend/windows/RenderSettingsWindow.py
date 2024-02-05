import dearpygui.dearpygui as dpg
from windows import Window

class RenderSettingsWindow(Window):
    def __init__(self, app_controller):
        super().__init__("render_settings_window", app_controller)

        self.app_controller.register_message_listener(self, "renderer")
        
        with dpg.window(label="Render settings", tag=self.tag, on_close=self.on_close):
        
            # Trainer settings
            dpg.add_text("Rendering settings")
            
            dpg.add_input_int(label="width", default_value=800, min_value=100, max_value = 2000, tag="res_x")
            dpg.add_input_int(label='height', default_value= 800, min_value=100, max_value = 2000, tag="res_y")
            
            dpg.add_slider_float(label="FoV x", 
                               tag="fov_x", 
                               default_value=70,
                               min_value=30,
                               max_value=120,
                               format= '%.2f'
                               )
            dpg.add_slider_float(label="FoV y", 
                               tag="fov_y", 
                               default_value=70,
                               min_value=30,
                               max_value=120,
                               format= '%.2f'
                               )
            dpg.add_slider_float(label="Near plane", 
                               tag="near_plane", 
                               default_value=0.01,
                               min_value=0.0001,
                               max_value=0.1,
                               format= '%.5f'
                               )
            dpg.add_slider_float(label="Far plane", 
                               tag="far_plane", 
                               default_value=100,
                               min_value=1,
                               max_value=10000,
                               format= '%.1f'
                               )
            
            dpg.add_button(label="Update renderer settings",
                        callback=self.update_renderer_settings)    
      
    def update_renderer_settings(self):
        trainer_settings = {
            "width" : dpg.get_value("res_x"),
            "height" : dpg.get_value("res_y"),
            "fov_x" : dpg.get_value("fov_x"),
            "fov_y" : dpg.get_value("fov_y"),
            "near_plane" : dpg.get_value("near_plane"),
            "far_plane" : dpg.get_value("far_plane")
        }
        data_to_send = {
            "update_renderer_settings" : trainer_settings
        }
        self.app_controller.app_communicator.send_message(data_to_send)

    def on_update(self, data):
        self.app_controller.popup_box("Updated renderer settings", data)

    def on_update_error(self, data):
        self.app_controller.popup_box("Error updating renderer settings", data)

    def on_receive_state(self, data):
        dpg.set_value("res_x", data['image_width'])
        dpg.set_value("res_y", data['image_width'])
        dpg.set_value("fov_x", data['fov_x'])
        dpg.set_value("fov_y", data['fov_y'])
        dpg.set_value("near_plane", data['near_plane'])
        dpg.set_value("far_plane", data['far_plane'])

    def receive_message(self, data):
        if "renderer_settings_updated" in data.keys():
            self.on_update(data['renderer_settings_updated'])
        if "renderer_settings_updated_error" in data.keys():
            self.on_update_error(data['renderer_settings_updated_error'])