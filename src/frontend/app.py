'''
Frontend DearPyGUI-based app for interfacing with the backend trainer/editor.

Useful links/documentation:
Save a docking setup: https://github.com/hoffstadt/DearPyGui/discussions/1088
Set primary window: https://dearpygui.readthedocs.io/en/latest/documentation/primary-window.html

'''

import dearpygui.dearpygui as dpg
from window_creator import *
import uuid

dpg.create_context()
dpg.configure_app(docking=True, docking_space=True, init_file="window_layout.ini", load_init_file=True)
dpg.create_viewport(title='GSTK', width=600, height=600)

def test_callback(*args):
    print(f"Callback function called {args}")

# Top menu bar for whole application
with dpg.viewport_menu_bar():
    with dpg.menu(label="File"):
        dpg.add_menu_item(label="Save", callback=test_callback)
        dpg.add_menu_item(label="Save As", callback=test_callback)
        
    with dpg.menu(label="Edit"):
        dpg.add_menu_item(label="Temp A", callback=test_callback)
        dpg.add_menu_item(label="Temp B", callback=test_callback)

    with dpg.menu(label="Edit"):
        dpg.add_menu_item(label="Save window layout", callback=lambda: dpg.save_init_file("window_layout.ini"))
        
    with dpg.menu(label="View"):
        dpg.add_menu_item(label="Main window", callback=create_main_window)
        dpg.add_menu_item(label="New test window", callback=lambda: create_test_window(str(uuid.uuid4())))

    with dpg.menu(label="Help"):
        dpg.add_menu_item(label="Save", callback=test_callback)
        dpg.add_menu_item(label="Save As", callback=test_callback)
        
create_main_window()
create_test_window("A")
create_test_window("B")
create_test_window("C")

dpg.setup_dearpygui()
dpg.show_viewport()
dpg.set_primary_window("main_window", True)
dpg.start_dearpygui()
dpg.destroy_context()