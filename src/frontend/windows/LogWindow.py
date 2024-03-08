import dearpygui.dearpygui as dpg
from windows import Window

class LogWindow(Window):
    def __init__(self, tag, app_controller):
        super().__init__(tag, app_controller)

        with dpg.window(label=tag, tag=tag, no_saved_settings=True):
            pass