import dearpygui.dearpygui as dpg
import socket
import multiprocessing
import multiprocessing.connection as connection
import uuid

from windows.MainWindow import MainWindow
from windows.ServerConnectWindow import ServerConnectWindow
from windows.TestWindow import TestWindow
from windows.TrainSetupWindow import TrainSetupWindow

class AppController:
    def __init__(self):
        # Setup GUI
        self.conn : connection.Client = None

        dpg.create_context()
        dpg.configure_app(docking=True, docking_space=True, init_file="window_layout.ini", load_init_file=True)
        dpg.create_viewport(title='GSTK', width=600, height=600)

        self.menubar_setup()

        MainWindow()
        self.server_connect_window = ServerConnectWindow(self)
        TrainSetupWindow('Training Setup Window')
        dpg.setup_dearpygui()
        dpg.show_viewport()
        dpg.set_primary_window("main_window", True)
        dpg.start_dearpygui()
        dpg.destroy_context()
        #dpg.set_exit_callback(self.on_app_close)
    
    # Top menu bar for whole application
    def menubar_setup(self):
        with dpg.viewport_menu_bar():
            with dpg.menu(label="File"):
                dpg.add_menu_item(label="Save", callback=None)
                dpg.add_menu_item(label="Save As")
                
            with dpg.menu(label="Edit"):
                dpg.add_menu_item(label="Save window layout", 
                    callback=lambda: dpg.save_init_file("window_layout.ini"))
                
            with dpg.menu(label="View"):
                dpg.add_menu_item(label="Server connection", 
                    tag="server_connector_menu_item", 
                    callback=lambda:ServerConnectWindow(self),
                    check=True, default_value=True)
                dpg.add_menu_item(label="New test window", 
                    callback=lambda: self.create_test_window())

    def on_app_close(self):
        print("Closing")
        try:
            self.conn.close()
        except Exception:
            pass

    def try_server_connect(self):
        if(self.conn is not None):
            print(f"Disconnecting")
            self.conn.close()
            self.conn = None
            self.server_connect_window.set_button_label("Connect")
            self.server_connect_window.set_status_text("")
            return
        
        self.server_connect_window.set_button_label("Connecting...")
        
        ip = str(dpg.get_value("server_ip"))
        try:
            port = int(dpg.get_value("server_port"))
        except Exception:
            print(f"Port must be integer, you entered {dpg.get_value('server_port')}")
            self.server_connect_window.set_button_label("Connect")
            return
        try:
            self.conn = connection.Client((ip, port), authkey=b"GRAVITY")
            print(f"Successfully connected to {ip}:{port}")
            self.server_connect_window.set_button_label("Disconnect")
            self.server_connect_window.set_status_text("Connected!")
        except:
            print(f"WARNING: {ip}:{port} is not available.")
            self.server_connect_window.set_button_label("Connect")
    
    def create_test_window(self):
        TestWindow(str(uuid.uuid4()))

    def update_view_menu(self, tag, enabled):
        if(dpg.does_item_exist('main_window')):
            #print(f"Checking {tag}_menu_item : {enabled}.")
            dpg.set_value(f"{tag}_menu_item", enabled)
            #dpg.configure_item(f"{tag}_menu_item", value=enabled)
        else:
            print(f"{tag}_menu_item does not exist.")

if __name__ == "__main__":
    a = AppController()