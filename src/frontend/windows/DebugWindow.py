import dearpygui.dearpygui as dpg
from windows import Window

class DebugWindow(Window):
    def __init__(self, app_controller):
        self.tag = "debug_window"
        self.app_controller = app_controller
        self.app_controller.register_message_listener(self, "debug")
        if(dpg.does_item_exist(self.tag)):
            self.on_close()
            del self
            return
        with dpg.window(label="Debug", tag=self.tag):
            self.button = dpg.add_button(label="Enable debug",
                        callback=self.button_pressed)
        self.debug = False
    
    def on_debug_true(self):
        dpg.set_item_label(self.button, "Disable debug")
        self.debug = True

    def on_debug_false(self):
        dpg.set_item_label(self.button, "Enable debug")
        self.debug = False

    def on_close(self):
        self.app_controller.update_view_menu(self.tag, False)
        dpg.delete_item(self.tag)

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
    
    def receive_message(self, data):
        if "debug_enabled" in data.keys():
            self.on_debug_true()
        if "debug_disabled" in data.keys():
            self.on_debug_false()
        if "debug_error" in data.keys():
            self.on_debug_error(data['debug_error'])
