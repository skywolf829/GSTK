import dearpygui.dearpygui as dpg
import multiprocessing.connection as connection
import uuid
import threading
import multiprocessing

from windows.MainWindow import MainWindow
from windows.ServerConnectWindow import ServerConnectWindow
from windows.DatasetSetupWindow import DatasetSetupWindow
from windows.RenderWindow import RenderWindow
from windows.TrainingSettingsWindow import TrainingSettingsWindow
from windows.ModelSettingsWindow import ModelSettingsWindow
from windows.TrainerWindow import TrainerWindow
from windows.DebugWindow import DebugWindow
from windows.RenderSettingsWindow import RenderSettingsWindow

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
        dpg.create_viewport(title='GSTK', width=1200, height=800)

        self.menubar_setup()

        self.main_window = MainWindow(self)
        self.server_connect_window = ServerConnectWindow(self)
        self.render_window = RenderWindow(self)
        self.training_settings_window = TrainingSettingsWindow(self)
        self.model_settings_window = ModelSettingsWindow(self)
        self.trainer_window = TrainerWindow(self)
        self.dataset_window = DatasetSetupWindow(self)
        self.debug_window = DebugWindow(self)
        self.renderer_settings_window = RenderSettingsWindow(self)


        self.register_message_listener(self, "other")

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
                    tag="server_connect_window_menu_item", 
                    callback=lambda:self.menu_button_click(ServerConnectWindow, "server_connect_window"),
                    check=True)
                dpg.add_menu_item(label="Render view", 
                    tag="render_window_menu_item", 
                    callback=lambda:self.menu_button_click(RenderWindow, "render_window"),
                    check=True)
                dpg.add_menu_item(label="Render settings", 
                    tag="render_settings_window_menu_item", 
                    callback=lambda:self.menu_button_click(RenderSettingsWindow, "render_settings_window"),
                    check=True)
                dpg.add_menu_item(label="Dataset setup", 
                    tag="dataset_setup_window_menu_item", 
                    callback=lambda:self.menu_button_click(DatasetSetupWindow, "dataset_setup_window"),
                    check=True)
                dpg.add_menu_item(label="Training settings", 
                    tag="trainer_settings_window_menu_item", 
                    callback=lambda:self.menu_button_click(TrainingSettingsWindow, "training_settings_window"),
                    check=True)
                dpg.add_menu_item(label="Model settings", 
                    tag="model_settings_window_menu_item", 
                    callback=lambda:self.menu_button_click(ModelSettingsWindow, "model_settings_window"),
                    check=True)
                dpg.add_menu_item(label="Trainer window", 
                    tag="trainer_window_menu_item", 
                    callback=lambda:self.menu_button_click(TrainerWindow, "trainer_window"),
                    check=True)
                dpg.add_menu_item(label="Debug window", 
                    tag="debug_window_menu_item", 
                    callback=lambda:self.menu_button_click(DebugWindow, "debug_window"),
                    check=True)

    # Properly closes down the connection and threaded communicator
    def on_app_close(self):
        print("Closing")
        self.app_communicator.stop = True
        self.app_communicator.stop()
        try:
            self.conn.close()
        except Exception:
            pass
    
    def menu_button_click(self, window, tag):
        if(dpg.does_item_exist(tag)):
            dpg.configure_item(tag, show=not dpg.is_item_shown(tag))
        else:
            window(self)
        
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
    Takes new message data (in JSON/dict format) and distributes
    it to the registered listeners
    '''
    def distribute_message_data(self, data):
        #print(data)
        for tag in data.keys():
            if(tag not in self.listened_tags.keys()):
                print(f"No listeners for tag {tag}")
            else:
                for window in self.listened_tags[tag]:
                    window.receive_message(data[tag])

    def popup_box(self, title, message):
        # https://github.com/hoffstadt/DearPyGui/discussions/1002
        # guarantee these commands happen in the same frame
        with dpg.mutex():

            viewport_width = dpg.get_viewport_client_width()
            viewport_height = dpg.get_viewport_client_height()

            with dpg.window(label=title, modal=True, no_close=True, tag="popup_window") as modal_id:
                dpg.add_text(message)
                dpg.add_button(label="Ok", width=75, 
                               user_data=(modal_id, True), 
                               callback=lambda:dpg.delete_item("popup_window"))
                #dpg.add_same_line()
                #dpg.add_button(label="Cancel", width=75, user_data=(modal_id, False), callback=selection_callback)

        # guarantee these commands happen in another frame
        dpg.split_frame()
        width = dpg.get_item_width(modal_id)
        height = dpg.get_item_height(modal_id)
        dpg.set_item_pos(modal_id, [viewport_width // 2 - width // 2, viewport_height // 2 - height // 2])
        
    def receive_message(self, data):
        # Handles all "other" messages, usually global or state-related
        
        if("error" in data.keys()):
            self.popup_box("Error", data['error'])
        if("settings_state" in data.keys()):
            for k in data['settings_state'].keys():
                if(dpg.does_item_exist(k)):
                    dpg.set_value(k, data['settings_state'][k])
        if("debug" in data.keys()):
            self.debug_window.update_debug_val(data['debug'])
        if('dataset_loaded' in data.keys()):
            self.dataset_window.update_dataset_loaded_val(data['dataset_loaded'])
        if("render" in data.keys()):
            self.renderer_settings_window.update_renderer_settings(data['renderer_settings'])


class AppCommunicator(threading.Thread):
    def __init__(self, app_controller : AppController, *args, **kwargs): 
        super().__init__().__init__(*args, **kwargs)

        self.connected = False      
        self.app_controller = app_controller
        self.stop = False
        self.conn = None
        self.lock = multiprocessing.Lock()
    
    # Toggles server connection. Connects if not connected, otherwise disconnects
    def toggle_server_connection(self, ip:str=None, port:int=None):
        if(self.connected):
            self.disconnect_from_server()
        else:
            self.try_server_connect(ip, port)

    # Tries to connect to server and updates app controller if necessary
    def try_server_connect(self, ip:str, port:int):
        with self.lock:
            if(self.connected):
                print("Already connected, cannot connect again!")
                return
            try:
                self.conn = connection.Client((ip, port), authkey=b"GRAVITY")
                print(f"Successfully connected to {ip}:{port}")
                self.connected = True
                self.app_controller.distribute_message_data(
                    {"connection": {"connected": True}}
                )
            except:
                print(f"WARNING: {ip}:{port} is not available.")
                self.connected = False
    
    # Runs infinitely to listen for messages (until close)
    def run(self):
        while not self.stop:
            if self.conn is not None and self.connected:
                try:                    
                    with self.lock:
                        if(self.conn.poll()):
                            data = self.conn.recv()
                            self.app_controller.distribute_message_data(data)
                except Exception as e:
                    print(e)
                    self.disconnect_from_server()

        self.stop()

    # Disconnects and updates the app controller
    def disconnect_from_server(self, popup=True):        
        if(self.conn is not None):
            with self.lock:
                print(f"Disconnecting")
                self.conn.close()
                self.conn = None
                self.connected = False
                if(popup):
                    self.app_controller.distribute_message_data(
                            {"connection": {"disconnected": True}}
                    )

    def send_message(self, data):
        if(self.conn is not None and self.connected):
            try:
                with self.lock:
                    self.conn.send(data)
            except Exception as e:
                print("Could not send data")
                self.disconnect_from_server(popup=False)
                self.app_controller.popup_box("Error", "Server disconnected.")
        else:
            self.app_controller.popup_box("Error", 
                "Attempted to send message before connecting to server.")

if __name__ == "__main__":
    a = AppController()