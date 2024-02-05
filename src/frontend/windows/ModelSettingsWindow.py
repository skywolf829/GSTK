import dearpygui.dearpygui as dpg
from windows import Window

class ModelSettingsWindow(Window):
    def __init__(self, app_controller):
        super().__init__("model_settings_window", app_controller)

        self.app_controller.register_message_listener(self, "model")
        
        with dpg.window(label="Model settings", tag=self.tag, on_close=self.on_close):
            
            # Model entries
            dpg.add_text("Model settings")
            dpg.add_slider_int(label="SH degree",
                               tag="sh_degree",
                               default_value=3,
                               min_value=0,
                               max_value=3)
            dpg.add_input_text(label="Device", 
                               hint="Where to host model (e.g. cuda, cuda:3)",
                               tag="device", 
                               default_value="cuda")
            dpg.add_button(label="Update model settings",
                        callback=self.updated_pressed)  


    def updated_pressed(self):
        model_settings = {
            "sh_degree" : dpg.get_value("sh_degree"),
            "device": dpg.get_value("device")
        }
        data_to_send = {
            "update_model_settings" : model_settings
        }
        self.app_controller.app_communicator.send_message(data_to_send)

    def on_update(self, data):
        self.app_controller.popup_box("Model settings updated", data)

    def on_update_error(self, data):
        self.app_controller.popup_box("Model initialization error", data)

    def on_receive_state(self, data):
        for k in data.keys():
            dpg.set_value(k, data[k])

    def receive_message(self, data):
        
        if "model_settings_updated" in data.keys():
            self.on_update(data['model_settings_updated'])
        if "model_settings_updated_error" in data.keys():
            self.on_update_error(data['model_settings_updated_error'])
