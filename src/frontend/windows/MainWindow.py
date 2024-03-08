import dearpygui.dearpygui as dpg
from windows import Window

class MainWindow(Window):
    def __init__(self, app_controller):
        self.tag = "main_window"
        self.app_controller = app_controller
        
        with dpg.window(label="Main Window", tag=self.tag, no_close=True):
            pass

        