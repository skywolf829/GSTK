import dearpygui.dearpygui as dpg
from windows import Window

class TrainingSettingsWindow(Window):
    def __init__(self, app_controller):
        super().__init__("trainer_settings_window", app_controller)

        self.app_controller.register_message_listener(self, "trainer")
        
        with dpg.window(label="Training settings", tag=self.tag, on_close=self.on_close):
        
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
            
            dpg.add_button(label="Update trainer settings",
                        callback=self.update_trainer_settings)    

        

    def update_trainer_settings(self):
        
        trainer_settings = {
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
            "densify_grad_threshold" : dpg.get_value("densify_grad_threshold")
        }
        data_to_send = {
            "update_trainer_settings" : trainer_settings
        }
        
        self.app_controller.app_communicator.send_message(data_to_send)

    def on_update(self, data):
        self.app_controller.popup_box("Updated trainer settings", data)

    def on_update_error(self, data):
        self.app_controller.popup_box("Error updating trainer settings", data)

    def on_receive_state(self, data):
        for k in data.keys():
            dpg.set_value(k, data[k])

    def receive_message(self, data):
        if "trainer_settings_updated" in data.keys():
            self.on_update(data['trainer_settings_updated'])
        if "trainer_settings_updated_error" in data.keys():
            self.on_update_error(data['trainer_settings_updated_error'])

    def save_status(self, data=None):
        if data is None: 
            data = {
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
                "densify_grad_threshold" : dpg.get_value("densify_grad_threshold")
            }
        super().save_status(data)