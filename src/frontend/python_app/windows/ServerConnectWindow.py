import dearpygui.dearpygui as dpg
from windows import Window

class ServerConnectWindow(Window):
    def __init__(self, app_controller):
        super().__init__("server_connect_window", app_controller)
        
        self.app_controller.register_message_listener(self, "connection")
        
        with dpg.window(label="Server", 
                        tag=self.tag, on_close=self.on_close,
                        width=450, height=150):
            with dpg.group(horizontal=True):
                dpg.add_text("Server IP:")  
                dpg.add_input_text(tag="server_ip", default_value="127.0.0.1")
            with dpg.group(horizontal=True):
                dpg.add_text("Server port:")  
                dpg.add_input_text(tag="server_port",  default_value="10789")
            with dpg.group(horizontal=True):
                self.button = dpg.add_button(label="Connect", callback=self.connect_button_clicked)
                self.status = dpg.add_text("", tag="connection_status")

        

    def set_button_label(self, s : str):
        dpg.set_item_label(self.button, s)

    def set_status_text(self, s: str):
        dpg.set_value(self.status, s)
    
    def connect_button_clicked(self):
        ip = str(dpg.get_value("server_ip"))
        try:
            port = int(dpg.get_value("server_port"))
            self.app_controller.app_communicator.toggle_server_connection(ip, port)
        except Exception as e:
            print(f"Port must be integer, you entered {dpg.get_value('server_port')}")
            raise e
        
    def receive_message(self, data: dict):
        if("connected" in data.keys()):            
            self.set_button_label("Disconnect")
            self.set_status_text("Connected!")
            self.app_controller.popup_box("Success", "Successfully connected to server. Loaded server's state variables.")
        if("disconnected" in data.keys()):
            self.set_button_label("Connect")
            self.set_status_text("")
            self.app_controller.popup_box("Success", "Successfully disconnected from server.")