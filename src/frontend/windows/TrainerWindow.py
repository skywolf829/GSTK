import dearpygui.dearpygui as dpg
from windows import Window

class TrainerWindow(Window):
    def __init__(self, app_controller):
        self.tag = "trainer_window"
        self.app_controller = app_controller
        self.app_controller.register_message_listener(self, "trainer")
        if(dpg.does_item_exist(self.tag)):
            print(f"{self.tag} window already exists! Cannot add another.")
            return
        with dpg.window(label="Trainer window", tag=self.tag):
            self.iteration_text = dpg.add_text("", tag="iteration_text")
            self.loss_text = dpg.add_text("", tag="loss_test")
            self.button = dpg.add_button(label="Start training",
                        callback=self.button_pressed)
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
        dpg.set_value(self.iteration_text, f"{data['iteration']}/{data['max_iteration']}")

    def receive_message(self, data):
        if "training_started" in data.keys():
            self.on_train_true()
        if "training_paused" in data.keys():
            self.on_train_false()
        if "training_error" in data.keys():
            self.on_train_error(data['training_error'])
        if "step" in data.keys():
            self.on_step(data['step'])
