#
# Copyright (C) 2023, Inria
# GRAPHDECO research group, https://team.inria.fr/graphdeco
# All rights reserved.
#
# This software is free for non-commercial, research and evaluation use 
# under the terms of the LICENSE.md file.
#
# For inquiries contact  george.drettakis@inria.fr
#

import torch
from torch import nn
import numpy as np
from utils.graphics_utils import getWorld2View2, getProjectionMatrix, rotate_axis_angle

class Camera(nn.Module):
    def __init__(self, colmap_id, 
                 R, T, 
                 FoVx, FoVy, 
                 image, gt_alpha_mask,
                 image_name, uid,
                 trans=np.array([0.0, 0.0, 0.0]), scale=1.0, data_device = "cuda"
                 ):
        super(Camera, self).__init__()

        self.uid = uid
        self.colmap_id = colmap_id
        self.R = R
        self.T = T
        self.FoVx = FoVx
        self.FoVy = FoVy
        self.image_name = image_name

        try:
            self.data_device = torch.device(data_device)
        except Exception as e:
            print(e)
            print(f"[Warning] Custom device {data_device} failed, fallback to default cuda device" )
            self.data_device = torch.device("cuda")

        self.original_image = image.clamp(0.0, 1.0).to(self.data_device)
        self.image_width = self.original_image.shape[2]
        self.image_height = self.original_image.shape[1]

        if gt_alpha_mask is not None:
            self.original_image *= gt_alpha_mask.to(self.data_device)
        else:
            self.original_image *= torch.ones((1, self.image_height, self.image_width), 
                                              device=self.data_device)
        self.zfar = 100.0
        self.znear = 0.01

        self.trans = trans
        self.scale = scale
        self.world_view_transform = torch.tensor(getWorld2View2(R, T, trans, scale), 
                                                 device=self.data_device).transpose(0, 1)
        self.projection_matrix = getProjectionMatrix(znear=self.znear, 
                            zfar=self.zfar, fovX=self.FoVx, fovY=self.FoVy).transpose(0,1).to(self.data_device)
        self.full_proj_transform = (self.world_view_transform.unsqueeze(0).bmm(self.projection_matrix.unsqueeze(0))).squeeze(0)
        self.camera_center = self.world_view_transform.inverse()[3, :3]

class MiniCam:
    def __init__(self, 
                 width, height, 
                 fovy, fovx, 
                 znear, zfar,
                 world_view_transform, full_proj_transform):
        self.image_width = width
        self.image_height = height    
        self.FoVy = fovy
        self.FoVx = fovx
        self.znear = znear
        self.zfar = zfar
        self.world_view_transform = world_view_transform
        self.full_proj_transform = full_proj_transform
        view_inv = torch.inverse(self.world_view_transform)
        self.camera_center = view_inv[3][:3]

class RenderCam:
    def __init__(self, 
                 width=800, height=800, 
                 fovy=65., fovx=65., 
                 znear=0.01, zfar=100.0,
                 T=np.array([0.,0.,0.], dtype=np.float32),
                 R=np.eye(3, dtype=np.float32),
                 device = "cuda" if torch.cuda.is_available() else "cpu"):
        self.data_device = device
        self.image_width : int = width
        self.image_height : int  = height    
        self.FoVy : float = fovy
        self.FoVx : float = fovx
        self.znear : float = znear
        self.zfar : float = zfar
        self.T = T
        self.R = R

        self.mode = "arcball"

    @property
    def world_view_transform(self):
        t = torch.empty([4,4], dtype=torch.float32, device=self.data_device)
        t[:3, :3] = self.R.T
        t[:3, 3] = self.T
        t[3, 3] = 1.
        return t.T
    
    @property
    def up(self):
        return self.R[:3, 1] / torch.norm(self.R[:3, 1])
    
    @property
    def right(self):
        return self.R[:3, 0] / torch.norm(self.R[:3, 0])
    
    @property
    def forward(self):
        return self.R[:3, 2] / torch.norm(self.R[:3, 2])
    
    @property
    def full_proj_transform(self):
        return getProjectionMatrix(znear=self.znear, 
                            zfar=self.zfar, 
                            fovX=self.FoVx, 
                            fovY=self.FoVy,
                            device=self.data_device).transpose(0,1)
    
    @property
    def camera_center(self):
        return torch.tensor(self.T, device=self.data_device)
    
    def process_mouse_input(self, dx, dy, modifiers = []):
        if(self.mode == "arcball"):
            self.process_mouse_input_arcball(dx, dy, modifiers)

    def process_mouse_input_arcball(self, dx, dy, modifiers=[]):

        if len(modifiers) == 0:
            # rotation

            # rotate from dx first (about y axis)
            angle = 2 * np.pi * dx / self.image_width
            self.R = rotate_axis_angle(self.up, angle)

            # rotate from dy about x axis
            angle = 2 * np.pi * dy / self.image_height
            self.R = rotate_axis_angle(self.right, angle)