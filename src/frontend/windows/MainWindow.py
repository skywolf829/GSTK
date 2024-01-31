import dearpygui.dearpygui as dpg

class MainWindow:
    def __init__(self):
        if(dpg.does_item_exist('main_window')):
            print(f"Main window already exists! Cannot add another.")
            return
        with dpg.window(label="Main Window", tag="main_window", no_close=True):
            pass

        