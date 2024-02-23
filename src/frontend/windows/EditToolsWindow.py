import dearpygui.dearpygui as dpg
from windows import Window

class EditToolsWindow(Window):
    def __init__(self, app_controller):
        super().__init__("edit_tools_window", app_controller)
        
        with dpg.window(label="Edit tools", tag=self.tag, on_close=self.on_close):
            
            dpg.add_spacer()

