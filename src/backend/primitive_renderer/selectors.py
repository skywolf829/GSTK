

from wgpu.gui.glfw import WgpuCanvas, run
from wgpu.gui.offscreen import WgpuCanvas as WgpuCanvas_offscreen
from pygfx.renderers.wgpu._blender import *
import pygfx as gfx
import numpy as np
from wgpu.backends.wgpu_native import GPUTexture
import wgpu
import torch

class CustomGizmo(gfx.TransformGizmo):
    def __init__(object : any | None = None,
                 screen_size : int = 100):
        super().__init__(object, screen_size)

class Selector():
    def __init__(self, scene : gfx.Scene, mesh_type="cube"):
        self.is_active : bool = False
        self.scene = scene
        self.mesh_type = mesh_type
        if(mesh_type == "cube" or mesh_type == "box"):
            self.mesh = gfx.BoxHelper(size=1, thickness=4)    
    
        self.gizmo = gfx.TransformGizmo(self.mesh, 100)
        self.invert_selection : bool = False
    
    def set_active(self):
        if(self.mesh not in self.scene.children):
            self.scene.add(self.mesh)
        if(self.gizmo not in self.scene.children):
            self.scene.add(self.gizmo)
        self.is_active = True

    def set_inactive(self):
        if(self.mesh in self.scene.children):
            self.scene.remove(self.mesh)
        if(self.gizmo in self.scene.children):
            self.scene.remove(self.gizmo)
        self.is_active = False       

    def points_in_bounds(self, points : torch.Tensor) -> torch.Tensor:
        with torch.no_grad():
            if(self.mesh_type == "cube" or self.mesh_type == "box"):
                return self.points_in_bounds_box(points)

    def points_in_bounds_box(self, points : torch.Tensor) -> torch.Tensor:

        # Get the inverse transform matrix for the mesh
        t = torch.tensor(self.mesh.world.inverse_matrix, dtype=torch.float32, device=points.device).T
        # Create homogenous coords for the points
        points_h = torch.cat([points, torch.ones([points.shape[0], 1], dtype=torch.float32, device=points.device)], dim=1)
        # Transform the points and get new xyz
        points_t = points_h @ t

        # Since this is a unit cube with mesh corners [-1, 1]^3, anything out of those bounds is out.
        in_bounds = (points_t[:,0] < 0.5) * (points_t[:,0] > -0.5) * \
                        (points_t[:,1] < 0.5) * (points_t[:,1] > -0.5) * \
                        (points_t[:,2] < 0.5) * (points_t[:,2] > -0.5)
        # invert selection if needed
        if self.invert_selection:
            in_bounds *= -1
        # cast in_bounds to uint8 because torch doesnt support real 1-bit bools
        # and our kernel needs to interperet the data
        in_bounds = in_bounds.type(torch.uint8)
        return in_bounds
