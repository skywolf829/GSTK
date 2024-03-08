
import os
import numpy as np
import imageio.v3 as iio
import dearpygui.dearpygui as dpg
'''
Loads and holds all icons, since DPG doesn't support SVG, we 
need to load them and convert to PNG first
'''
def load_icons():
    this_dir = os.path.join(os.path.abspath(__file__), "..", "icons", "png")
    for file in os.listdir(this_dir):
        name = file.split(".png")[0]
        full_file = os.path.join(this_dir, file)
        im = iio.imread(full_file,pilmode='RGBA')
        
        im[:,:,0] = 255 # Can change this to theme color when we figure that out
        im[:,:,1] = 255
        im[:,:,2] = 255
        with dpg.texture_registry(show=False):
            dpg.add_static_texture(width=im.shape[0], 
                height=im.shape[1], default_value=im, tag=name)
        

