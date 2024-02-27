import dearpygui.dearpygui as dpg
from windows import Window

class DatasetSetupWindow(Window):
    def __init__(self, app_controller):
        super().__init__("dataset_setup_window", app_controller)

        self.app_controller.register_message_listener(self, "dataset")
        
        with dpg.window(label="Dataset Setup", tag=self.tag, on_close=self.on_close):
            
            # Dataset entries
            dpg.add_text("Dataset settings")
            with dpg.group(horizontal=True):
                dpg.add_text("Dataset path:")
                dpg.add_input_text(tag="dataset_path",
                                   hint="Path relative to /data folder on server")
            #with dpg.group(horizontal=True):
            #    dpg.add_radio_button(["1", "2", "4", "8", "-1"],
            #                default_value="1", 
            #                label="Resolution scale", tag='resolution_scale',
            #                horizontal=True)
            #    dpg.add_text("Resolution scale")
            with dpg.group(horizontal=True):
                dpg.add_text("Data device:")
                dpg.add_input_text(hint="Where to host dataset (e.g. cpu, cuda)",
                            tag="data_device", 
                            default_value="cuda")
            with dpg.group(horizontal=True):
                dpg.add_text("White background:")    
                dpg.add_checkbox(tag="white_background",
                            default_value=False)
            with dpg.group(horizontal=True):
                dpg.add_button(label="Initialize dataset",
                            callback=self.initialize_dataset_pressed)
                self.dataset_status = dpg.add_text("", tag="dataset_status")
            dpg.add_spacer()


    def initialize_dataset_pressed(self):
        dpg.set_value(self.dataset_status, "")
        dataset_data = {
            "dataset_path" : dpg.get_value("dataset_path"),
            #"resolution_scale" : int(dpg.get_value("resolution_scale")),
            "white_background" : dpg.get_value("white_background"),
            "data_device": dpg.get_value("data_device")
        }
        data_to_send = {
            "initialize_dataset" : dataset_data
        }
        self.app_controller.app_communicator.send_message(data_to_send)

    def on_dataset_initialized(self, data):
        dpg.set_value(self.dataset_status, "Dataset loaded.")
        self.app_controller.popup_box("Dataset was initialized", data)
 
    def on_dataset_loading(self, data):
        dpg.set_value(self.dataset_status, "Dataset loading...")

    def on_dataset_error(self, data):
        dpg.set_value(self.dataset_status, "")
        self.app_controller.popup_box("Dataset initialization error", data)

    def update_dataset_loaded_val(self, val):
        if(val):
            dpg.set_value(self.dataset_status, "Dataset loaded.")
        else:
            dpg.set_value(self.dataset_status, "")

    def receive_message(self, data):
        if "dataset_initialized" in data.keys():
            self.on_dataset_initialized(data['dataset_initialized'])
        if "dataset_loading" in data.keys():
            self.on_dataset_loading(data['dataset_loading'])
        if "dataset_error" in data.keys():
            self.on_dataset_error(data['dataset_error'])
