import os
import sys
import dearpygui.dearpygui as dpg

def restart_app():
    dpg.stop_dearpygui()
    os.execv(sys.executable, ['python'] + sys.argv)