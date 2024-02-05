import dearpygui.dearpygui as dpg

class Window:
    def __init__(self, tag, app_controller):
        self.tag = tag
        self.app_controller = app_controller

        app_controller.update_view_menu(self.tag, True)

    def receive_message(self, data : dict):
        pass

    def on_close(self):
        self.app_controller.update_view_menu(self.tag, False)
        dpg.configure_item(self.tag, show=False)
        #dpg.delete_item(self.tag)