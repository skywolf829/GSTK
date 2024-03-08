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
from pygfx import PerspectiveCamera

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

def cam_from_gfx(cam: PerspectiveCamera, canvas):  
    d = "cuda" if torch.cuda.is_available() else "cpu"
    wv = cam.view_matrix.copy()
    p = cam.projection_matrix.copy()
    #p[1,:] *= -1
    wv[1,:] *= -1
    world_view = torch.tensor(wv, dtype=torch.float32, device=d).T
    full_proj = torch.tensor(p @ wv, dtype=torch.float32, device=d).T
    #world_view[0:3,1] *= -1
    #full_proj[0:3,1] *= -1
    #full_proj = torch.tensor(cam.camera_matrix, dtype=torch.float32, device=d).T
    #print(world_view)
    #print(full_proj)
    return MiniCam(
        canvas.get_logical_size()[0], canvas.get_logical_size()[1], 
        np.deg2rad(cam.fov), np.deg2rad(cam.fov),
        cam.near, cam.far, 
        world_view, full_proj
    )

class RenderCam:
    def __init__(self, 
                 width=800, height=800, 
                 fovy=np.pi*(120/180), fovx=np.pi*(120/180), 
                 znear=0.01, zfar=100.0,
                 T=np.array([00.,00.,2.], dtype=np.float32),
                 R=np.eye(3, dtype=np.float32),
                 device = "cuda" if torch.cuda.is_available() else "cpu"):
        self.data_device = device
        self.image_width : int = width
        self.image_height : int  = height    
        self.FoVy : float = fovy
        self.FoVx : float = fovx
        self.znear : float = znear
        self.zfar : float = zfar
        self.T : np.ndarray = T
        self.R : np.ndarray = R
        self.COI : np.ndarray = np.zeros([3], dtype=np.float32)
        self.mode = "arcball"

    @property
    def world_view_transform(self):
        t = np.zeros([4,4], dtype=np.float32)
        t[:3, :3] = self.R
        COI_local = (np.linalg.inv(self.R) @ self.COI[:,None])[:,0]
        t[3, :3] = self.T + COI_local
        t[3, 3] = 1.
        return torch.tensor(t, device=self.data_device)
        
    @property
    def up(self):
        return self.R[:3, 1] / np.linalg.norm(self.R[:3, 1])
    
    @property
    def right(self):
        return -self.R[:3, 0] / np.linalg.norm(self.R[:3, 0])
    
    @property
    def forward(self):
        return -self.R[:3, 2] / np.linalg.norm(self.R[:3, 2])
    
    @property 
    def projection_matrix(self):
        return getProjectionMatrix(znear=self.znear, 
                            zfar=self.zfar, 
                            fovX=self.FoVx, 
                            fovY=self.FoVy,
                            device=self.data_device,
                            z_sign=1.0).T
    @property 
    def projection_matrix_openGL(self):
        return getProjectionMatrix(znear=self.znear, 
                            zfar=self.zfar, 
                            fovX=self.FoVx, 
                            fovY=self.FoVy,
                            device=self.data_device,
                            z_sign=-1.0).T
    
    @property
    def full_proj_transform(self):
        return self.world_view_transform @ \
                self.projection_matrix
    
    @property
    def camera_center(self):
        return self.world_view_transform.inverse()[3, :3]
    
    def move_forward(self, d):
        f = np.linalg.norm(self.T)
        world_space_change = f*d*self.forward
        self.COI += world_space_change
    
    def move_right(self, d):
        f = np.linalg.norm(self.T)
        world_space_change = f*d*self.right
        self.COI += world_space_change

    def move_up(self, d):
        f = np.linalg.norm(self.T)
        world_space_change = f*d*self.up
        self.COI += world_space_change

    def process_camera_move(self, data):
        if(self.mode == "arcball"):
            if("mouse_move" in data.keys()):
                self.process_mouse_input_arcball(
                    data['mouse_move']['dx'], data['mouse_move']['dy'], data['mouse_move']['modifiers']
                    )
            if("key_pressed" in data.keys()):
                self.process_key_input_test(data['key_pressed']['right'], data['key_pressed']['up'])
            if("scrollwheel" in data.keys()):
                self.process_scrollwheel(data["scrollwheel"]["val"])

    def process_scrollwheel(self, val):
        r = 1 - (val/10.)
        self.T *= r

    def process_key_input_test(self, right, up):
        world_space_change = 0.2 * right * self.right + 0.2 * up * self.up
        self.COI += world_space_change

    def process_mouse_input_arcball(self, dx, dy, modifiers=[]):

        if len(modifiers) == 0:
            # rotation

            angle1 = 2 * np.pi * dx / self.image_width
            angle2 = 2 * np.pi * dy / self.image_height
            r1 = rotate_axis_angle(self.up, angle1)
            r2 = rotate_axis_angle(-self.right, angle2)

            self.R = (r1 @ r2 @ self.R)
            #self.T = (r1 @ r2 @ (self.T[:,None] - self.COI))[:,0] + self.COI
        if (len(modifiers) == 1 and "shift" in modifiers):
            # pan
            f = np.linalg.norm(self.T)
            world_space_change = 2.5*f*(-dx/self.image_width)*self.right + \
                2.5*f*(-dy/self.image_height)*self.up
            self.COI += world_space_change

        