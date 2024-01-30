import dearpygui.dearpygui as dpg

# Creating a window  
# This is labeled as the "primary window".
# Will fill whole viewport even on resizing and always render behind other windows
# https://dearpygui.readthedocs.io/en/latest/documentation/primary-window.html
def create_main_window():
    if(dpg.does_item_exist('main_window')):
        print(f"Main window already exists! Cannot add another.")
        return
    with dpg.window(label="Main Window", tag="main_window", no_close=True):
        pass

def create_test_window(tag):
    if(dpg.does_item_exist(tag)):
        print(f"{tag} window already exists! Cannot add another.")
        return
    with dpg.window(label=tag, tag=tag, no_saved_settings=True):
        pass