# todo: if we have per-vertex coloring, we can paint on the mesh instead :D

from wgpu.gui.glfw import WgpuCanvas, run
from wgpu.gui.offscreen import WgpuCanvas as WgpuCanvas_offscreen
from pygfx.renderers.wgpu._blender import *
import pygfx as gfx
import numpy as np
from tqdm import tqdm
from wgpu.backends.wgpu_native import GPUTexture
import imageio.v3 as iio
import wgpu

class WGPU_renderer():
    def __init__(self, offscreen=True):
        self.offscreen = offscreen
        self.simulated_mouse_pos = [0,0]
        self.modifiers = []
        self.buttons = []

        self.init_renderer()

    def init_renderer(self):
        if(self.offscreen):
            self.canvas = WgpuCanvas_offscreen()
        else:
            self.canvas = WgpuCanvas()
        self.renderer = gfx.renderers.WgpuRenderer(
            self.canvas, 
            #self.rgba_texture,
            blend_mode='ordered2',
            pixel_ratio=1.0)
        self.viewport = gfx.Viewport(self.renderer)

        self.camera = gfx.PerspectiveCamera(50, depth_range=[0.01, 100])

        self.scene = gfx.Scene()        
        self.scene.add(gfx.Background(None, gfx.BackgroundMaterial("#000")))

        #self.camera.show_object(self.scene)

        self.canvas.request_draw(self.draw)
        self.controller = gfx.OrbitController(self.camera, register_events=self.renderer)

    def add_test_scene(self):

        self.cube = gfx.BoxHelper(size=1, thickness=4)
        self.gizmo = gfx.TransformGizmo(self.cube)
        self.gizmo.add_default_event_handlers(self.viewport, self.camera)

        self.scene.add(self.cube)
        self.scene.add(self.gizmo)
        self.scene.add(gfx.AmbientLight())
        self.camera.show_object(self.scene)

    def draw(self):
        self.renderer.render(self.scene, self.camera)
        #self.viewport.render(self.gizmo, self.camera)
        self.renderer.flush()

    def render(self):
        
        # Render the scene
        rgba = np.asarray(self.canvas.draw())

        
        # Get the blender, which has a reference to the depth dexture
        b : Ordered2FragmentBlender = self.renderer._blender
        # Get the GPUTexture from the final pass
        t : GPUTexture = b.get_depth_attachment(b.get_pass_count()-1)['view'].texture 
        # Grab the canvas's GPUDevice through the context to grab the queue instance
        q : wgpu.GPUQueue = self.canvas.get_context()._config['device'].queue
        # Get the number of bytes per pixel (generally 4 bytes for 32-bit float depth)
        bytes_per_element = int(t._nbytes / (t.width*t.height))
        
        # Use the queue to read the texture to a memoryview, and grab it with numpy
        # Reshape it at the end not to t.size, but height x width.
        depth = np.frombuffer(
            q.read_texture(
                {"texture": t, "origin":(0,0,0), "mip_level": 0},
                {"offset": 0, "bytes_per_row": bytes_per_element*t.width, "rows_per_image": t.height},
            t.size), dtype=np.float32
        ).reshape(t.height, t.width)
        
        return rgba, depth

    def resize(self, w, h):
        self.canvas.set_logical_size(w, h)

    def simulate_mouse(self, data):

        if("mouse_click" in data):
            self.simulate_pointer_click(data['mouse_click']['button'])
        if("mouse_release" in data):
            self.simulate_pointer_release(data['mouse_release']['button'])
        if("mouse_move" in data):
            self.simulate_pointer_move(data['mouse_move']['x'], data['mouse_move']['y'])
        if("wheel" in data):
            self.simulate_scroll(data['wheel']['dy'])

    def handle_event(self, ev):
        #self.gizmo.handle_event(ev)
        #self.camera.handle_event(ev)
        #self.renderer.handle_event(ev)
        self.canvas._handle_event_and_flush(ev)

    def simulate_keyboard(self, data):
        print(data)
        pass

    def simulate_pointer_move(self, x, y):
        self.simulated_mouse_pos = [x, y]
        ev = {
            "event_type": "pointer_move",
            "x": self.simulated_mouse_pos[0],
            "y": self.simulated_mouse_pos[1],
            "button": 0,
            "buttons": self.buttons,
            "modifiers": self.modifiers,
            "ntouches": 0,  # glfw dows not have touch support
            "touches": {},
        }
        self.handle_event(ev)
    
    def simulate_pointer_click(self, button:int):

        if(button not in self.buttons):
            self.buttons.append(button)
        
        ev = {
            "event_type": "pointer_down",
            "x": self.simulated_mouse_pos[0],
            "y": self.simulated_mouse_pos[1],
            "button": button,
            "buttons": self.buttons,
            "modifiers": self.modifiers,
            "ntouches": 0,  # glfw dows not have touch support
            "touches": {},
        }
        self.handle_event(ev)

    def simulate_pointer_release(self, button:int):

        if(button in self.buttons):
            self.buttons.append(button)
        ev = {
            "event_type": "pointer_up",
            "x": self.simulated_mouse_pos[0],
            "y": self.simulated_mouse_pos[1],
            "button": button,
            "buttons": self.buttons,
            "modifiers": self.modifiers,
            "ntouches": 0,  # glfw dows not have touch support
            "touches": {},
        }
        self.handle_event(ev)

    def simulate_scroll(self, dy:float):
        # wheel is 1 or -1 in glfw, in jupyter_rfb this is ~100
        ev = {
            "event_type": "wheel",
            "dx": 0,
            "dy": -100.0 * dy,
            "x": self.simulated_mouse_pos[0],
            "y": self.simulated_mouse_pos[1],
            "buttons": self.buttons,
            "modifiers": self.modifiers,
        }
        self.handle_event(ev)

    def simulate_key_down(self, key):
        ev = {
            "event_type": "key_down",
            "key": key,
            "modifiers": self.modifiers,
        }
        self.handle_event(ev)

    def simulate_key_up(self, key):
        
        ev = {
            "event_type": "key_up",
            "key": key,
            "modifiers": self.modifiers,
        }
        self.handle_event(ev)

    def get_camera_matrix(self):
        return self.camera.camera_matrix
    
    def get_view_matrix(self):
        return self.camera.view_matrix
    
    def get_projection_matrix(self):
        return self.camera.projection_matrix
    
    def get_inverse_projection_matrix(self):
        return self.camera.projection_matrix_inverse


if __name__ == "__main__":
    r = WGPU_renderer(offscreen=False)
    r.add_test_scene()
    print(r.canvas.get_logical_size())
    run()
