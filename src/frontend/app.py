import dearpygui.dearpygui as dpg
import multiprocessing.connection as connection
import uuid
import threading

from windows.MainWindow import MainWindow
from windows.ServerConnectWindow import ServerConnectWindow
from windows.TestWindow import TestWindow


class AppController:
    def __init__(self):
        
        self.app_communicator : AppCommunicator = AppCommunicator(self, daemon=True)
        self.app_communicator.start()
        # each specific tag is linked to the window(s) intersted in 
        # hearing about new data. i.e. "loss_data" tag may be useful
        # for a window displaying the loss over time, so in this 
        # dict, listened_tags['loss_data'] = [loss_curve_window]
        self.listened_tags = {}

        # Setup GUI
        dpg.create_context()
        dpg.configure_app(docking=True, docking_space=True, init_file="window_layout.ini", load_init_file=True)
        dpg.create_viewport(title='GSTK', width=600, height=600)

        self.menubar_setup()

        MainWindow()
        self.server_connect_window = ServerConnectWindow(self)

        dpg.setup_dearpygui()
        dpg.show_viewport()
        dpg.set_primary_window("main_window", True)
        dpg.start_dearpygui()
        dpg.destroy_context()
        # Causes seg fault on exit but it works
        dpg.set_exit_callback(self.on_app_close)
    
    '''
    Registers window as a listener for message_tag when that
    data comes from the server.
    '''
    def register_message_listener(self, window, message_tag):
        if(message_tag not in self.listened_tags):
            self.listened_tags[message_tag] = []
        self.listened_tags[message_tag].append(window)
        
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

    # Properly closes down the connection and threaded communicator
    def on_app_close(self):
        print("Closing")
        self.app_communicator.stop = True
        self.app_communicator.stop()
        try:
            self.conn.close()
        except Exception:
            pass
    
    # Creates a test window with a random name
    def create_test_window(self):
        TestWindow(str(uuid.uuid1()))

    '''
    Enables or disables the checkmark next to the window on the view menu
    '''
    def update_view_menu(self, tag, enabled):
        if(dpg.does_item_exist(f"{tag}_menu_item")):
            #print(f"Checking {tag}_menu_item : {enabled}.")
            dpg.set_value(f"{tag}_menu_item", enabled)
            #dpg.configure_item(f"{tag}_menu_item", value=enabled)
        else:
            print(f"{tag}_menu_item does not exist.")

    '''
    Changes the server connection window text based on the current connection status
    '''
    def update_connection(self, connected : bool):
        if(connected):
            
            self.server_connect_window.set_button_label("Disconnect")
            self.server_connect_window.set_status_text("Connected!")
        else:
            self.server_connect_window.set_button_label("Connect")
            self.server_connect_window.set_status_text("")
    
    '''
    Takes new message data (in JSON/dict format) and distributes
    it to the registered listeners
    '''
    def distribute_message_data(self, data):
        for tag in data.keys():
            if(tag not in self.listened_tags.keys()):
                print(f"No listeners for tag {tag}")
            else:
                for window in self.listened_tags[tag]:
                    window.receive_message(data[tag])

class AppCommunicator(threading.Thread):
    def __init__(self, app_controller : AppController, *args, **kwargs): 
        super().__init__().__init__(*args, **kwargs)

        self.connected = False      
        self.app_controller = app_controller
        self.stop = False
        self.conn = None
    
    # Toggles server connection. Connects if not connected, otherwise disconnects
    def toggle_server_connection(self, ip:str=None, port:int=None):
        if(self.connected):
            self.disconnect_from_server()
        else:
            self.try_server_connect(ip, port)

    # Tries to connect to server and updates app controller if necessary
    def try_server_connect(self, ip:str, port:int):
        if(self.connected):
            print("Already connected, cannot connect again!")
            return
        try:
            self.conn = connection.Client((ip, port), authkey=b"GRAVITY")
            print(f"Successfully connected to {ip}:{port}")
            self.connected = True
        except:
            print(f"WARNING: {ip}:{port} is not available.")
            self.connected = False

        self.app_controller.update_connection(self.connected)
    
    # Runs infinitely to listen for messages (until close)
    def run(self):
        while not self.stop:
            if self.conn is not None and self.connected:
                try:
                    if(self.conn.poll()):
                        data = self.conn.recv()
                        self.app_controller.distribute_message_data(data)
                except Exception as e:
                    # Likely just disconnected
                    pass

        self.stop()

    # Disconnects and updates the app controller
    def disconnect_from_server(self):        
        if(self.conn is not None):
            print(f"Disconnecting")
            self.conn.close()
            self.conn = None
            self.connected = False
            self.app_controller.update_connection(self.connected)

if __name__ == "__main__":
    a = AppController()