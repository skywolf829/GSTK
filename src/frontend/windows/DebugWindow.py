import dearpygui.dearpygui as dpg
from windows import Window

class DebugWindow(Window):
    def __init__(self, app_controller):
        super().__init__("debug_window", app_controller)
        
        self.app_controller.register_message_listener(self, "debug")

        
        with dpg.window(label="Debug", tag=self.tag, on_close=self.on_close):
            self.button = dpg.add_button(label="Enable debug",
                        callback=self.button_pressed)
        self.debug = False
        
    
    def on_debug_true(self):
        dpg.set_item_label(self.button, "Disable debug")
        self.debug = True

    def on_debug_false(self):
        dpg.set_item_label(self.button, "Enable debug")
        self.debug = False

    def button_pressed(self):
        if(self.debug):
            data_to_send = {
                "debug" : False
            }
        else:
            data_to_send = {
                "debug" : True
            }
        
        self.app_controller.app_communicator.send_message(data_to_send)

    def on_debug_error(self, data):
        self.app_controller.popup_box("Error", data)
        pass

    def update_debug_val(self, val):
        if val:
            self.on_debug_true()
        else:
            self.on_debug_false()
    
    def receive_message(self, data):
        if "debug_enabled" in data.keys():
            self.on_debug_true()
        if "debug_disabled" in data.keys():
            self.on_debug_false()
        if "debug_error" in data.keys():
            self.on_debug_error(data['debug_error'])
    
    def save_status(self, data=None):
        if data is None: 
            data = {
                "debug" : self.debug
            }
        super().save_status(data)

    def sync_status(self, data=None):
        if data is not None:
            self.update_debug_val(data["debug"])
        else:
            super().sync_status(data)
