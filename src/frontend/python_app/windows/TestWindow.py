import dearpygui.dearpygui as dpg
from windows import Window

class TestWindow(Window):
    def __init__(self, tag : str):
        if(dpg.does_item_exist(tag)):
            print(f"{tag} window already exists! Cannot add another.")
            return
        with dpg.window(label=tag, tag=tag, no_saved_settings=True):
            pass