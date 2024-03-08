import dearpygui.dearpygui as dpg
from windows import Window

class AddPointsWindow(Window):

    def __init__(self, app_controller):
        super().__init__("add_points_window", app_controller)
        
        if(dpg.does_item_exist(self.tag)):
            app_controller.unregister_edit_window(self.tag)
            dpg.delete_item(self.tag)
            return None

        with dpg.window(label="Add points", tag=self.tag, on_close=self.on_close, pos=dpg.get_mouse_pos(),
                        no_collapse=True):
            dpg.add_input_int(label="Number of points", tag="add_num_points", 
                              min_value=1, max_value=50000, min_clamped=True, max_clamped=True,
                              default_value=10000)
            dpg.add_listbox(["uniform", "normal", "inverse_normal"], 
                    label="Position distribution", tag='add_points_distribution')
            dpg.add_button(label="Add", callback=self.button_clicked)

        app_controller.register_edit_window(self.tag, False)

    def button_clicked(self):
        self.app_controller.app_communicator.send_message(
            {
                "edit":
                {
                    "type": "add",
                    "payload": [dpg.get_value('add_num_points'), dpg.get_value('add_points_distribution')]
                }
            }
        )
    
    def on_close(self):
        self.app_controller.unregister_edit_window(self.tag)
        dpg.delete_item(self.tag)