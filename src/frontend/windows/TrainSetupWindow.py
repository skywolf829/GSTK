import dearpygui.dearpygui as dpg

class TrainSetupWindow:
  
    def __init__(self, tag : str):
        
        if(dpg.does_item_exist(tag)):
            print(f"{tag} window already exists! Cannot add another.")
            return
        with dpg.window(label=tag, tag=tag, no_saved_settings=True):
            
            with dpg.collapsing_header(label="Dataset Loading"):
                dpg.add_input_text(label="Path to dataset")
                dpg.add_button(label="Load Dataset")
                dpg.add_input_float(label="Resolution Scale", min_value=0.0, max_value=1.0)
                dpg.add_checkbox(label="White Background")
            
            with dpg.collapsing_header(label="Trainer/Model Setup"):
                dpg.add_input_int(label="Iterations", default_value=30_000)
                dpg.add_input_float(label="Position Learning Rate Initialization", default_value=0.00016)
                dpg.add_input_float(label="Position Learning Rate Final", default_value=0.0000016)
                dpg.add_input_int(label="Position Learning Rate Max Steps", default_value=30_000)
                dpg.add_input_float(label="Feature Learning Rate", default_value=0.0025)
                dpg.add_input_float(label="Opacity Learning Rate", default_value=0.05)
                dpg.add_input_float(label="Scaling Learning Rate", default_value=0.005)
                dpg.add_input_float(label="Rotation Learning rate", default_value=0.001)
                dpg.add_input_float(label="Percent Dense", default_value=0.01)
                dpg.add_input_float(label="Lambda DSSIM", default_value=0.2)
                dpg.add_input_int(label="Densification Interval", default_value=100)
                dpg.add_input_int(label="Opacity Reset Interval", default_value=3000)
                dpg.add_input_int(label="Density From Iterations", default_value=500)
                dpg.add_input_int(label="Density Until Iterations", default_value=15_000)
                dpg.add_input_float(label="Density Grad Threshold", default_value=0.0002)
                dpg.add_checkbox(label="Random Background")
                dpg.add_button(label="Initialize Model")
            
            with dpg.collapsing_header(label="Start Training"):
                dpg.add_button(label="Start Training")
                dpg.add_button(label="Stop Training")
                dpg.add_button(label="Pause Training")