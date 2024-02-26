import dearpygui.dearpygui as dpg
from windows import Window

from windows.EditTools.AddPointsWindow import AddPointsWindow
from windows.EditTools.RemovePointsWindow import RemovePointsWindow

class EditToolsWindow(Window):

    def __init__(self, app_controller):
        super().__init__("edit_tools_window", app_controller)
        
        add_points_tool = {
            "texture_tag": "plus-circle",
            "tag": "add_points_tool",
            "callback": self.add_points_clicked
        } 
        remove_points_tool = {
            "texture_tag": "minus-circle",
            "tag": "remove_points_tool",
            "callback": self.remove_points_clicked
        } 

        layout = [
            [ add_points_tool, remove_points_tool ]
        ]
        
        with dpg.window(label="Edit tools", tag=self.tag, on_close=self.on_close, no_title_bar=True):
            for row in layout:                
                with dpg.group(horizontal=True):
                    for item in row:                  
                        with dpg.item_handler_registry(tag=f"{item['tag']}_handler") as handler:
                            dpg.add_item_clicked_handler(callback=item['callback']) 
                        dpg.add_image(item['texture_tag'], tag=item['tag'])
                        dpg.bind_item_handler_registry(item['tag'], f"{item['tag']}_handler")

    def add_points_clicked(self):
        AddPointsWindow(self.app_controller)

    def remove_points_clicked(self):
        RemovePointsWindow(self.app_controller)