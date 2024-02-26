import dearpygui.dearpygui as dpg
from windows import Window

class RemovePointsWindow(Window):

    def __init__(self, app_controller):
        super().__init__("remove_points_window", app_controller)
        
        if(dpg.does_item_exist(self.tag)):
            app_controller.unregister_edit_window(self.tag)
            dpg.delete_item(self.tag)
            return None

        with dpg.window(label="Remove points", tag=self.tag, on_close=self.on_close):
            dpg.add_input_int(label="Percentage of points", tag="remove_points_percent", 
                              min_value=0, max_value=100, min_clamped=True, max_clamped=True,
                              default_value=100)
            dpg.add_listbox(["To", "be", "implemented"], 
                    label="Decimation type", tag='decimate_type')
            dpg.add_checkbox(label="Re-distribute remaining points", tag='delete_redistribute')
            dpg.add_button(label="Remove", callback=self.button_clicked)

        app_controller.register_edit_window(self.tag, True)

    def button_clicked(self):
        self.app_controller.app_communicator.send_message(
            {
                "edit":
                {
                    "type": "remove",
                    "payload": [dpg.get_value('remove_points_percent'), dpg.get_value('decimate_type'), dpg.get_value('delete_redistribute')]
                }
            }
        )

    def on_close(self):
        self.app_controller.unregister_edit_window(self.tag)
        dpg.delete_item(self.tag)
