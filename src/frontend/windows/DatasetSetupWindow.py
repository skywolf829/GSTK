import dearpygui.dearpygui as dpg
from windows import Window

class DatasetSetupWindow(Window):
    def __init__(self, app_controller):
        super().__init__("dataset_setup_window", app_controller)

        self.app_controller.register_message_listener(self, "dataset")
        self.app_controller.register_message_listener(self, "connection")
        
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
            
            dpg.add_spacer()
            dpg.add_text("Paths if you need to process your dataset first:")
            with dpg.group(horizontal=True):
                dpg.add_text("COLMAP executable:")
                dpg.add_input_text(tag="colmap_path",
                                   hint="Path to colmap executable (if not in environment path already)")
            with dpg.group(horizontal=True):
                dpg.add_text("ImageMagick executable:")
                dpg.add_input_text(tag="imagemagick_path",
                                   hint="Path to ImageMagick executable (if not in environment path already)")
            dpg.add_spacer()

            with dpg.group(horizontal=True):
                dpg.add_button(label="Initialize dataset",
                            callback=self.initialize_dataset_pressed)
                #self.dataset_status = dpg.add_text("", tag="dataset_status")                
                self.point_cloud_button = dpg.add_button(label="Load point cloud",
                        callback=self.point_cloud_button_pressed)
            dpg.add_spacer()


    def initialize_dataset_pressed(self):
        #dpg.set_value(self.dataset_status, "")
        dataset_data = {
            "dataset_path" : dpg.get_value("dataset_path"),
            #"resolution_scale" : int(dpg.get_value("resolution_scale")),
            "white_background" : dpg.get_value("white_background"),
            "data_device": dpg.get_value("data_device"),
            "colmap_path": dpg.get_value("colmap_path"),
            "imagemagick_path": dpg.get_value("imagemagick_path")

        }
        data_to_send = {
            "initialize_dataset" : dataset_data
        }
        self.app_controller.app_communicator.send_message(data_to_send)

    def point_cloud_button_pressed(self):
        self.app_controller.app_communicator.send_message({
            "load_point_cloud": True
        })

    def on_dataset_initialized(self, data):
        #dpg.set_value(self.dataset_status, "Dataset loaded.")
        dpg.delete_item("dataset_loading_wait")
        #self.app_controller.popup_box("Dataset was initialized", data)
 
    def on_dataset_loading(self, data):
        #dpg.set_value(self.dataset_status, data)        
        if(dpg.does_item_exist("dataset_loading_wait")):
            dpg.set_value("dataset_loading_text", data)
        else:
            with dpg.window(label="Loading dataset...", modal=True, no_close=True, tag="dataset_loading_wait"):
                dpg.add_text(data, tag="dataset_loading_text")
                with dpg.group(horizontal=True):
                    dpg.add_spacer(width=80)
                    dpg.add_loading_indicator()
        dpg.split_frame()
        viewport_width = dpg.get_viewport_client_width()
        viewport_height = dpg.get_viewport_client_height()
        width = dpg.get_item_width('dataset_loading_wait')
        height = dpg.get_item_height('dataset_loading_wait')
        dpg.set_item_pos('dataset_loading_wait', [viewport_width // 2 - width // 2, viewport_height // 2 - height // 2])

    def on_dataset_error(self, data):
        #dpg.set_value(self.dataset_status, "")
        dpg.delete_item("dataset_loading_wait")
        self.app_controller.popup_box("Dataset initialization error", data)

    def update_dataset_loaded_val(self, val):
        #if(val):
        #    dpg.set_value(self.dataset_status, "Dataset loaded.")
        #else:
        #    dpg.set_value(self.dataset_status, "")
        pass

    def receive_message(self, data):
        if "dataset_initialized" in data.keys():
            self.on_dataset_initialized(data['dataset_initialized'])
        if "dataset_loading" in data.keys():
            self.on_dataset_loading(data['dataset_loading'])
        if "dataset_error" in data.keys():
            self.on_dataset_error(data['dataset_error'])
        if("disconnected" in data.keys()):
            dpg.delete_item("dataset_loading_wait")

        
