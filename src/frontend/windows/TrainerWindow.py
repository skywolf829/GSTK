import dearpygui.dearpygui as dpg
from windows import Window

class TrainerWindow(Window):
    def __init__(self, app_controller):
        super().__init__("trainer_window", app_controller)

        self.app_controller.register_message_listener(self, "trainer")
        
        with dpg.window(label="Trainer window", tag=self.tag, on_close=self.on_close):
            self.iteration_text = dpg.add_text("Iteration: --/--", tag="iteration_text")
            self.loss_text = dpg.add_text("Loss: --", tag="loss_test")
            self.button = dpg.add_button(label="Start training",
                        callback=self.button_pressed)
            dpg.add_spacer()
            self.update_time = dpg.add_text(default_value="", tag="update_time")
        self.training = False
        
    
    def on_train_true(self):
        dpg.configure_item(self.button, label="Stop training")
        self.training = True

    def on_train_false(self):
        dpg.configure_item(self.button, label="Start training")
        self.training = False

    def button_pressed(self):
        if(self.training):
            data_to_send = {
                "training_pause" : True
            }
        else:
            data_to_send = {
                "training_start" : True
            }
        self.app_controller.app_communicator.send_message(data_to_send)

    def on_train_error(self, data):
        self.app_controller.popup_box("Error", data)
        pass
    
    def on_step(self, data):
        dpg.set_value(self.iteration_text, f"Iteration: {data['iteration']}/{data['max_iteration']}")
        dpg.set_value(self.loss_text, f"Loss: {data['ema_loss']:0.04f}")

    def on_update_time(self, data):
        dpg.set_value(self.update_time, f"{data / 1000 : 0.02f} ms per step / {1/data : 0.02f} FPS")
        
    def receive_message(self, data):
        if "training_started" in data.keys():
            self.on_train_true()
        if "training_paused" in data.keys():
            self.on_train_false()
        if "training_error" in data.keys():
            self.on_train_error(data['training_error'])
        if "step" in data.keys():
            self.on_step(data['step'])
        if "update_time" in data.keys():
            self.on_update_time(data['update_time'])
