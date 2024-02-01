import dearpygui.dearpygui as dpg

class ServerConnectWindow:
    def __init__(self, app_controller):
        self.app_controller = app_controller
        self.button = None
        self.tag = "server_connector"
        if(dpg.does_item_exist(self.tag)):
            self.on_close()
            del self
            return
        with dpg.window(label="Server", tag=self.tag, on_close=self.on_close):
            dpg.add_input_text(label="Server IP", tag="server_ip", default_value="127.0.0.1")
            dpg.add_input_text(label="Server port",tag="server_port",  default_value="10789")
            with dpg.group(horizontal=True):
                self.button = dpg.add_button(label="Connect", callback=self.connect_button_clicked)
                self.status = dpg.add_text("", tag="connection_status")

        #app_controller.update_view_menu(self.tag, True)

    def set_button_label(self, s : str):
        dpg.set_item_label(self.button, s)
    
    def set_enabled(self, v : bool):
        dpg.configure_item(self.button, enabled=v)

    def set_status_text(self, s: str):
        dpg.set_value(self.status, s)
    
    def on_close(self):
        self.app_controller.update_view_menu(self.tag, False)
        dpg.delete_item(self.tag)
    
    def connect_button_clicked(self):
        ip = str(dpg.get_value("server_ip"))
        try:
            port = int(dpg.get_value("server_port"))
            self.app_controller.app_communicator.toggle_server_connection(ip, port)
        except Exception as e:
            print(f"Port must be integer, you entered {dpg.get_value('server_port')}")
            raise e