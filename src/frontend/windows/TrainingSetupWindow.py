import dearpygui.dearpygui as dpg
from windows import Window

class TrainingSetupWindow(Window):
    def __init__(self, app_controller):
        self.tag = "training_setup_window"
        self.app_controller = app_controller
        self.app_controller.register_message_listener(self, "dataset")
        self.app_controller.register_message_listener(self, "trainer")
        self.app_controller.register_message_listener(self, "model")
        if(dpg.does_item_exist(self.tag)):
            print(f"{self.tag} window already exists! Cannot add another.")
            return
        with dpg.window(label="Training Setup", tag=self.tag):
            
            # Dataset entries
            dpg.add_text("Dataset settings")
            dpg.add_input_text(label="Dataset Path", 
                               tag="dataset_path", 
                               default_value="../../data/mic")
            with dpg.group(horizontal=True):
                dpg.add_radio_button(["1", "2", "4", "8", "-1"],
                            default_value="1", 
                            label="Resolution scale", tag='resolution_scale',
                            horizontal=True)
                dpg.add_text("Resolution scale")
            dpg.add_input_text(label="Data device", 
                            hint="Where to host dataset (e.g. cpu, cuda)",
                            tag="data_device", 
                            default_value="cuda")
            dpg.add_checkbox(label="White background",
                            tag="white_background",
                            default_value=False)
            with dpg.group(horizontal=True):
                dpg.add_button(label="Initialize dataset",
                            callback=self.initialize_dataset_pressed)
                self.dataset_status = dpg.add_text("", tag="dataset_status")
            dpg.add_spacer()

            # Model entries
            dpg.add_text("Model settings")
            dpg.add_slider_int(label="SH degree",
                               tag="sh_degree",
                               default_value=3,
                               min_value=0,
                               max_value=3)
            dpg.add_input_text(label="Device", 
                               hint="Where to host model (e.g. cuda, cuda:3)",
                               tag="device", 
                               default_value="cuda")
            
            dpg.add_spacer()

            # Trainer settings
            dpg.add_text("Training settings")
            dpg.add_slider_int(label="Total iterations", 
                               tag="iterations", 
                               default_value=30000,
                               min_value=100,
                               max_value=100000
                               )
            dpg.add_slider_float(label="Initial position learning rate", 
                               tag="position_lr_init", 
                               default_value=0.00016,
                               min_value=0.0,
                               max_value=0.1,
                               format= '%.6f'
                               )
            dpg.add_slider_float(label="Final position learning rate", 
                               tag="position_lr_final", 
                               default_value=0.0000016,
                               min_value=0.0,
                               max_value=0.001,
                               format= '%.8f'
                               )
            dpg.add_slider_float(label="Position learning rate delay multiplier",
                               tag="position_lr_delay_mult", 
                               default_value=0.01,
                               min_value=0.0,
                               max_value=0.2,
                               format= '%.6f'
                               )
            dpg.add_slider_int(label="Position learning rate scheduler max steps", 
                               tag="position_lr_max_steps", 
                               default_value=30000,
                               min_value=0,
                               max_value=100000
                               )
            dpg.add_slider_float(label="Feature learning rate", 
                               tag="feature_lr", 
                               default_value=0.0025,
                               min_value=0.0,
                               max_value=0.2,
                               format= '%.6f'
                               )
            dpg.add_slider_float(label="Opacity learning rate", 
                               tag="opacity_lr", 
                               default_value=0.05,
                               min_value=0.0,
                               max_value=1.0,
                               format= '%.6f'
                               )
            dpg.add_slider_float(label="Scaling learning rate", 
                               tag="scaling_lr", 
                               default_value=0.005,
                               min_value=0.0,
                               max_value=0.2,
                               format= '%.6f'
                               )
            dpg.add_slider_float(label="Rotation learning rate", 
                               tag="rotation_lr", 
                               default_value=0.001,
                               min_value=0.0,
                               max_value=0.2,
                               format= '%.6f'
                               )
            dpg.add_slider_float(label="Percent dense", 
                               tag="percent_dense", 
                               default_value=0.01,
                               min_value=0.0,
                               max_value=1.0,
                               format= '%.6f'
                               )
            dpg.add_slider_float(label="SSIM loss weight", 
                               tag="lambda_dssim", 
                               default_value=0.2,
                               min_value=0.0,
                               max_value=10.0,
                               format= '%.6f'
                               )
            dpg.add_slider_float(label="Densification interval", 
                               tag="densification_interval", 
                               default_value=100,
                               min_value=-1,
                               max_value=100000
                               )
            dpg.add_slider_int(label="Opacity reset interval", 
                               tag="opacity_reset_interval", 
                               default_value=3000,
                               min_value=-1,
                               max_value=100000
                               )
            dpg.add_slider_int(label="Densify from iteration", 
                               tag="densify_from_iter", 
                               default_value=500,
                               min_value=0,
                               max_value=100000
                               )
            dpg.add_slider_int(label="Densify until iteration", 
                               tag="densify_until_iter", 
                               default_value=15000,
                               min_value=-1,
                               max_value=100000
                               )
            dpg.add_slider_float(label="Densify gradient threshold", 
                               tag="densify_grad_threshold", 
                               default_value=0.0002,
                               min_value=0.00001,
                               max_value=0.01,
                               format= '%.6f'
                               )
            with dpg.group(horizontal=True):
                dpg.add_button(label="Initialize model and trainer",
                            callback=self.initialize_model_and_trainer_pressed)            
                self.trainer_status = dpg.add_text("", tag="trainer_status")

    def initialize_dataset_pressed(self):
        dpg.set_value(self.dataset_status, "")
        dataset_data = {
            "dataset_path" : dpg.get_value("dataset_path"),
            "resolution_scale" : int(dpg.get_value("resolution_scale")),
            "white_background" : dpg.get_value("white_background"),
            "data_device": dpg.get_value("data_device")
        }
        data_to_send = {
            "initialize_dataset" : dataset_data
        }
        self.app_controller.app_communicator.send_message(data_to_send)

    def initialize_model_and_trainer_pressed(self):
        dpg.set_value(self.trainer_status, "")
        model_and_trainer_data = {
            "iterations" : dpg.get_value("iterations"),
            "position_lr_init" : dpg.get_value("position_lr_init"),
            "position_lr_final" : dpg.get_value("position_lr_final"),
            "position_lr_delay_mult" : dpg.get_value("position_lr_delay_mult"),
            "position_lr_max_steps" : dpg.get_value("position_lr_max_steps"),
            "feature_lr" : dpg.get_value("feature_lr"),
            "opacity_lr" : dpg.get_value("opacity_lr"),
            "scaling_lr" : dpg.get_value("scaling_lr"),
            "rotation_lr" : dpg.get_value("rotation_lr"),
            "percent_dense" : dpg.get_value("percent_dense"),
            "lambda_dssim" : dpg.get_value("lambda_dssim"),
            "densification_interval" : dpg.get_value("densification_interval"),
            "opacity_reset_interval" : dpg.get_value("opacity_reset_interval"),
            "densify_from_iter" : dpg.get_value("densify_from_iter"),
            "densify_until_iter" : dpg.get_value("densify_until_iter"),
            "densify_grad_threshold" : dpg.get_value("densify_grad_threshold"),
            "sh_degree" : dpg.get_value("sh_degree"),
            "device": dpg.get_value("device")
        }
        data_to_send = {
            "initialize_trainer" : model_and_trainer_data
        }
        self.app_controller.app_communicator.send_message(data_to_send)

    def on_dataset_initialized(self, data):
        dpg.set_value(self.dataset_status, "Dataset loaded.")
    
    def on_dataset_loading(self, data):
        dpg.set_value(self.dataset_status, "Dataset loading...")

    def on_dataset_error(self, data):
        dpg.set_value(self.dataset_status, "")
        self.app_controller.popup_box("Dataset initialization error", data)

    def on_model_initialized(self, data):
        dpg.set_value(self.trainer_status, "Trainer and model initialized")

    def on_model_error(self, data):
        self.app_controller.popup_box("Model initialization error", data)

    def receive_message(self, data):
        if "dataset_initialized" in data.keys():
            self.on_dataset_initialized(data['dataset_initialized'])
        if "dataset_loading" in data.keys():
            self.on_dataset_loading(data['dataset_loading'])
        if "dataset_error" in data.keys():
            self.on_dataset_error(data['dataset_error'])

        if "trainer_initialized" in data.keys():
            self.on_model_initialized(data['trainer_initialized'])
        if "trainer_error" in data.keys():
            self.on_model_error(data['trainer_error'])

        if "model_initialized" in data.keys():
            self.on_model_initialized(data['model_initialized'])
        if "model_error" in data.keys():
            self.on_model_error(data['model_error'])
