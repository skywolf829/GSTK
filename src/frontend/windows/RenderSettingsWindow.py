import dearpygui.dearpygui as dpg
from windows import Window

class RenderSettingsWindow(Window):
    def __init__(self, app_controller):
        super().__init__("render_settings_window", app_controller)

        self.app_controller.register_message_listener(self, "renderer")
        self.app_controller.register_message_listener(self, "connection")
        
        with dpg.window(label="Render settings", tag=self.tag, on_close=self.on_close):
        
            # Trainer settings
            dpg.add_text("Rendering settings")
            dpg.add_checkbox(label="Renderer enabled", 
                               tag='renderer_enabled',
                               default_value=True)
            dpg.add_slider_float(label="Resolution scaling",
                                 tag="resolution_scaling",
                                 default_value=1.0,
                                 min_value = 0.1,
                                 max_value = 1.0,
                                 format='%.2f')
            dpg.add_text("Resolution: ", tag="effective_resolution")
            
            dpg.add_slider_float(label="Field of view", 
                               tag="fov", 
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
        scaling = dpg.get_value("resolution_scaling")

        max_width = dpg.get_item_width("render_view_texture")
        max_height = dpg.get_item_height("render_view_texture")
        fov = dpg.get_value("fov")
        w = int(scaling*min(max_width,dpg.get_item_width("render_window")))
        h = int(scaling*min(max_height,dpg.get_item_height("render_window")))

        dpg.set_value("effective_resolution", f"Resolution: {w}x{h}")

        render_settings = {
            'renderer_enabled': dpg.get_value('renderer_enabled'),
            "width" : w,
            "height" : h,
            "fov" : fov,
            "near_plane" : dpg.get_value("near_plane"),
            "far_plane" : dpg.get_value("far_plane")
        }
        if(self.app_controller.app_communicator.connected):
            data_to_send = {
                "update_renderer_settings" : render_settings
            }
            self.app_controller.app_communicator.send_message(data_to_send)

    def on_update(self, data):
        self.app_controller.popup_box("Updated renderer settings", data)

    def on_update_error(self, data):
        self.app_controller.popup_box("Error updating renderer settings", data)

    def on_receive_state(self, data):

        dpg.set_value('renderer_enabled', data['renderer_enabled'])
        dpg.set_value("fov", data['fov'])
        dpg.set_value("near_plane", data['near_plane'])
        dpg.set_value("far_plane", data['far_plane'])

    def receive_message(self, data):
        if "renderer_settings_updated" in data.keys():
            self.on_update(data['renderer_settings_updated'])
        if "renderer_settings_updated_error" in data.keys():
            self.on_update_error(data['renderer_settings_updated_error'])
        if("settings_state" in data.keys()):
            self.on_receive_state(data['settings_state'])
        if "connected" in data.keys():
            if data['connected']:
                self.update_renderer_settings()