import dearpygui.dearpygui as dpg

class Window:
    def __init__(self, tag, app_controller):
        self.tag = tag
        self.app_controller = app_controller
        self.app_controller.windows_params[tag] = {}
        self.app_controller.windows[tag] = self
        app_controller.update_view_menu(self.tag, True)

    def receive_message(self, data : dict):
        pass

    def on_close(self):
        self.app_controller.update_view_menu(self.tag, False)
        dpg.configure_item(self.tag, show=False)
        #dpg.delete_item(self.tag)

    def sync_status(self, data=None):
        """
        Sync with the saved status of the window
        """
        if data is not None:
            for key in data.keys():
                try:
                    dpg.set_value(key, data[key])
                except Exception as e:
                    print(f"Could not set value {data[key]} to item {key}. Error: {e}")
                    pass

    def save_status(self, data=None):
        """
        Save the status of the window
        """
        if data is not None:
            self.app_controller.windows_params[self.tag] = data
        