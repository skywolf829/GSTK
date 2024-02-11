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
from utils.loss_utils import l1_loss, ssim
import sys
import numpy as np
from torch import nn
import time
from dataset import Dataset
from model import GaussianModel
from utils.general_utils import get_expon_lr_func, inverse_sigmoid, build_rotation
from settings import Settings
from tqdm import tqdm

class Trainer:
    def __init__(self, model : GaussianModel, settings : Settings, debug=False):
        self.model : GaussianModel = model
        self.settings = settings

        self.optimizer = None
        self.xyz_scheduler_args = None

        self._iteration = 0
        self.ema_loss = 0.0
        self.last_loss = 0.0
        self.training = False
        self.loss_values_each_iter = []
        self.step_times_each_iter = []

        self.DEBUG = debug
        self.percent_dense = self.settings.percent_dense
        self.xyz_gradient_accum = torch.zeros((self.model.get_num_gaussians, 1), device=self.settings.device)
        self.denom = torch.zeros((self.model.get_num_gaussians, 1), device=self.settings.device)

        l = [
            {'params': [self.model._xyz], 'lr': self.settings.position_lr_init * self.settings.spatial_lr_scale, "name": "xyz"},
            {'params': [self.model._features_dc], 'lr': self.settings.feature_lr, "name": "f_dc"},
            {'params': [self.model._features_rest], 'lr': self.settings.feature_lr / 20.0, "name": "f_rest"},
            {'params': [self.model._opacity], 'lr': self.settings.opacity_lr, "name": "opacity"},
            {'params': [self.model._scaling], 'lr': self.settings.scaling_lr, "name": "scaling"},
            {'params': [self.model._rotation], 'lr': self.settings.rotation_lr, "name": "rotation"}
        ]

        self.optimizer = torch.optim.Adam(l, lr=0.0, eps=1e-15)
        self.xyz_scheduler_args = get_expon_lr_func(lr_init=self.settings.position_lr_init*self.settings.spatial_lr_scale,
                                                    lr_final=self.settings.position_lr_final*self.settings.spatial_lr_scale,
                                                    lr_delay_mult=self.settings.position_lr_delay_mult,
                                                    max_steps=self.settings.position_lr_max_steps)
    
    def set_dataset(self, dataset : Dataset):
        self.dataset = dataset
    
    def set_model(self, model : GaussianModel):
        self.model = model
        self.xyz_gradient_accum = torch.zeros((self.model.get_num_gaussians, 1), device=self.settings.device)
        self.denom = torch.zeros((self.model.get_num_gaussians, 1), device=self.settings.device)
        l = [
            {'params': [self.model._xyz], 'lr': self.settings.position_lr_init * self.settings.spatial_lr_scale, "name": "xyz"},
            {'params': [self.model._features_dc], 'lr': self.settings.feature_lr, "name": "f_dc"},
            {'params': [self.model._features_rest], 'lr': self.settings.feature_lr / 20.0, "name": "f_rest"},
            {'params': [self.model._opacity], 'lr': self.settings.opacity_lr, "name": "opacity"},
            {'params': [self.model._scaling], 'lr': self.settings.scaling_lr, "name": "scaling"},
            {'params': [self.model._rotation], 'lr': self.settings.rotation_lr, "name": "rotation"}
        ]

        self.optimizer = torch.optim.Adam(l, lr=0.0, eps=1e-15)
    
    def on_settings_update(self, new_settings: Settings):
        
        self.settings = new_settings 

        with torch.no_grad():
            if(self.xyz_gradient_accum.device.type not in self.settings.device):
                self.xyz_gradient_accum = self.xyz_gradient_accum.to(self.settings.device)
                self.denom = self.denom.to(self.settings.device)
                
            l = [
                {'params': [self.model._xyz], 'lr': self.settings.position_lr_init * self.settings.spatial_lr_scale, "name": "xyz"},
                {'params': [self.model._features_dc], 'lr': self.settings.feature_lr, "name": "f_dc"},
                {'params': [self.model._features_rest], 'lr': self.settings.feature_lr / 20.0, "name": "f_rest"},
                {'params': [self.model._opacity], 'lr': self.settings.opacity_lr, "name": "opacity"},
                {'params': [self.model._scaling], 'lr': self.settings.scaling_lr, "name": "scaling"},
                {'params': [self.model._rotation], 'lr': self.settings.rotation_lr, "name": "rotation"}
            ]

            self.optimizer = torch.optim.Adam(l, lr=0.0, eps=1e-15)
            self.xyz_scheduler_args = get_expon_lr_func(lr_init=self.settings.position_lr_init*self.settings.spatial_lr_scale,
                                                        lr_final=self.settings.position_lr_final*self.settings.spatial_lr_scale,
                                                        lr_delay_mult=self.settings.position_lr_delay_mult,
                                                        max_steps=self.settings.position_lr_max_steps)

    def update_learning_rate(self, iteration):
        ''' Learning rate scheduling per step '''
        for param_group in self.optimizer.param_groups:
            if param_group["name"] == "xyz":
                lr = self.xyz_scheduler_args(iteration)
                param_group['lr'] = lr
                return lr    
    
    def reset_opacity(self):
        opacities_new = inverse_sigmoid(torch.min(self.model.get_opacity, 
                        torch.ones_like(self.model.get_opacity)*0.01))
        optimizable_tensors = self.replace_tensor_to_optimizer(opacities_new, "opacity")
        self.model._opacity = optimizable_tensors["opacity"]

    def replace_tensor_to_optimizer(self, tensor, name):
        optimizable_tensors = {}
        for group in self.optimizer.param_groups:
            if group["name"] == name:
                stored_state = self.optimizer.state.get(group['params'][0], None)
                stored_state["exp_avg"] = torch.zeros_like(tensor)
                stored_state["exp_avg_sq"] = torch.zeros_like(tensor)

                del self.optimizer.state[group['params'][0]]
                group["params"][0] = nn.Parameter(tensor.requires_grad_(True))
                self.optimizer.state[group['params'][0]] = stored_state

                optimizable_tensors[group["name"]] = group["params"][0]
        return optimizable_tensors

    def _prune_optimizer(self, mask):
        optimizable_tensors = {}
        for group in self.optimizer.param_groups:
            stored_state = self.optimizer.state.get(group['params'][0], None)
            if stored_state is not None:
                stored_state["exp_avg"] = stored_state["exp_avg"][mask]
                stored_state["exp_avg_sq"] = stored_state["exp_avg_sq"][mask]

                del self.optimizer.state[group['params'][0]]
                group["params"][0] = nn.Parameter((group["params"][0][mask].requires_grad_(True)))
                self.optimizer.state[group['params'][0]] = stored_state

                optimizable_tensors[group["name"]] = group["params"][0]
            else:
                group["params"][0] = nn.Parameter(group["params"][0][mask].requires_grad_(True))
                optimizable_tensors[group["name"]] = group["params"][0]
        return optimizable_tensors

    def cat_tensors_to_optimizer(self, tensors_dict):
        optimizable_tensors = {}
        for group in self.optimizer.param_groups:
            assert len(group["params"]) == 1
            extension_tensor = tensors_dict[group["name"]]
            stored_state = self.optimizer.state.get(group['params'][0], None)
            if stored_state is not None:

                stored_state["exp_avg"] = torch.cat((stored_state["exp_avg"], torch.zeros_like(extension_tensor)), dim=0)
                stored_state["exp_avg_sq"] = torch.cat((stored_state["exp_avg_sq"], torch.zeros_like(extension_tensor)), dim=0)

                del self.optimizer.state[group['params'][0]]
                group["params"][0] = nn.Parameter(torch.cat((group["params"][0], extension_tensor), dim=0).requires_grad_(True))
                self.optimizer.state[group['params'][0]] = stored_state

                optimizable_tensors[group["name"]] = group["params"][0]
            else:
                group["params"][0] = nn.Parameter(torch.cat((group["params"][0], extension_tensor), dim=0).requires_grad_(True))
                optimizable_tensors[group["name"]] = group["params"][0]

        return optimizable_tensors

    def prune_points(self, mask):
        valid_points_mask = ~mask
        optimizable_tensors = self._prune_optimizer(valid_points_mask)

        self.model._xyz = optimizable_tensors["xyz"]
        self.model._features_dc = optimizable_tensors["f_dc"]
        self.model._features_rest = optimizable_tensors["f_rest"]
        self.model._opacity = optimizable_tensors["opacity"]
        self.model._scaling = optimizable_tensors["scaling"]
        self.model._rotation = optimizable_tensors["rotation"]
        self.xyz_gradient_accum = self.xyz_gradient_accum[valid_points_mask]
        self.denom = self.denom[valid_points_mask]
        self.model.max_radii2D = self.model.max_radii2D[valid_points_mask]

    def densification_postfix(self, new_xyz, new_features_dc, new_features_rest, new_opacities, new_scaling, new_rotation):
        d = {"xyz": new_xyz,
        "f_dc": new_features_dc,
        "f_rest": new_features_rest,
        "opacity": new_opacities,
        "scaling" : new_scaling,
        "rotation" : new_rotation}

        optimizable_tensors = self.cat_tensors_to_optimizer(d)
        self.model._xyz = optimizable_tensors["xyz"]
        self.model._features_dc = optimizable_tensors["f_dc"]
        self.model._features_rest = optimizable_tensors["f_rest"]
        self.model._opacity = optimizable_tensors["opacity"]
        self.model._scaling = optimizable_tensors["scaling"]
        self.model._rotation = optimizable_tensors["rotation"]
        self.xyz_gradient_accum = torch.zeros((self.model.get_num_gaussians, 1), device=self.settings.device)
        self.denom = torch.zeros((self.model.get_num_gaussians, 1), device=self.settings.device)
        self.model.max_radii2D = torch.zeros((self.model.get_num_gaussians), device=self.settings.device)

    def densify_and_split(self, grads : torch.Tensor, grad_threshold, scene_extent, N=2):
        n_init_points = self.model.get_num_gaussians
        # Extract points that satisfy the gradient condition
        padded_grad = torch.zeros((n_init_points), device=self.settings.device)
        padded_grad[:grads.shape[0]] = grads.squeeze()
        selected_pts_mask = torch.where(padded_grad >= grad_threshold, True, False)
        selected_pts_mask = torch.logical_and(selected_pts_mask,
                    torch.max(self.model.get_scaling, dim=1).values > self.percent_dense*scene_extent)

        stds = self.model.get_scaling[selected_pts_mask].repeat(N,1)
        means = torch.zeros((stds.size(0), 3),device=self.settings.device)
        samples = torch.normal(mean=means, std=stds)
        rots = build_rotation(self.model._rotation[selected_pts_mask]).repeat(N,1,1)
        new_xyz = torch.bmm(rots, samples.unsqueeze(-1)).squeeze(-1) + self.model.get_xyz[selected_pts_mask].repeat(N, 1)
        new_scaling = self.model.scaling_inverse_activation(self.model.get_scaling[selected_pts_mask].repeat(N,1) / (0.8*N))
        new_rotation = self.model._rotation[selected_pts_mask].repeat(N,1)
        new_features_dc = self.model._features_dc[selected_pts_mask].repeat(N,1,1)
        new_features_rest = self.model._features_rest[selected_pts_mask].repeat(N,1,1)
        new_opacity = self.model._opacity[selected_pts_mask].repeat(N,1)

        self.densification_postfix(new_xyz, new_features_dc, new_features_rest, new_opacity, new_scaling, new_rotation)

        prune_filter = torch.cat((selected_pts_mask, torch.zeros(N * selected_pts_mask.sum(), device=self.settings.device, dtype=bool)))
        self.prune_points(prune_filter)

    def densify_and_clone(self, grads : torch.Tensor, grad_threshold, scene_extent):
        # Extract points that satisfy the gradient condition
        selected_pts_mask = torch.where(torch.norm(grads, dim=-1) >= grad_threshold, True, False)
        selected_pts_mask = torch.logical_and(selected_pts_mask,
                    torch.max(self.model.get_scaling, dim=1).values <= self.percent_dense*scene_extent)
        
        new_xyz = self.model._xyz[selected_pts_mask]
        new_features_dc = self.model._features_dc[selected_pts_mask]
        new_features_rest = self.model._features_rest[selected_pts_mask]
        new_opacities = self.model._opacity[selected_pts_mask]
        new_scaling = self.model._scaling[selected_pts_mask]
        new_rotation = self.model._rotation[selected_pts_mask]

        self.densification_postfix(new_xyz, new_features_dc, new_features_rest, new_opacities, new_scaling, new_rotation)

    def densify_and_prune(self, max_grad : torch.Tensor, min_opacity, extent, max_screen_size):
        grads = self.xyz_gradient_accum / self.denom
        grads[grads.isnan()] = 0.0

        self.densify_and_clone(grads, max_grad, extent)
        self.densify_and_split(grads, max_grad, extent)

        prune_mask = (self.model.get_opacity < min_opacity).squeeze()
        if max_screen_size:
            big_points_vs = self.model.max_radii2D > max_screen_size
            big_points_ws = self.model.get_scaling.max(dim=1).values > 0.1 * extent
            prune_mask = torch.logical_or(torch.logical_or(prune_mask, big_points_vs), big_points_ws)
        self.prune_points(prune_mask)

        torch.cuda.empty_cache()

    def add_densification_stats(self, viewspace_point_tensor : torch.Tensor, update_filter):
        self.xyz_gradient_accum[update_filter] += torch.norm(viewspace_point_tensor.grad[update_filter,:2], dim=-1, keepdim=True)
        self.denom[update_filter] += 1

    def pre_iteration_checks(self, iteration): 
        self.update_learning_rate(iteration)
        if self._iteration % 1000 == 0:
            self.model.oneupSHdegree()

    def post_iteration_checks(self, iteration, viewspace_point_tensor, visibility_filter, radii):
        # Densification
        if iteration < self.settings.densify_until_iter:
            # Keep track of max radii in image-space for pruning
            self.model.max_radii2D[visibility_filter] = torch.max(self.model.max_radii2D[visibility_filter], radii[visibility_filter])
            self.add_densification_stats(viewspace_point_tensor, visibility_filter)

            if iteration > self.settings.densify_from_iter and iteration % self.settings.densification_interval == 0:
                size_threshold = 20 if iteration > self.settings.opacity_reset_interval else None
                self.densify_and_prune(self.settings.densify_grad_threshold, 0.005, self.dataset.cameras_extent, size_threshold)
            
            if iteration % self.settings.opacity_reset_interval == 0 or \
                (self.dataset.white_background and iteration == self.settings.densify_from_iter):
                self.reset_opacity()

    def step(self):
        if(self.DEBUG):
            #time.sleep(0.001)
            self.last_loss = np.random.rand()
            self.ema_loss = self.ema_loss * 0.6 + self.last_loss * 0.4
            self._iteration += 1
            return torch.rand([1024, 1024, 3], device=self.settings.device, dtype=torch.float32), \
                self.last_loss, self.ema_loss
        
        # Checks for the optimizer/model to update 
        self.pre_iteration_checks(self._iteration)

        # Get data for this iteration and render
        viewpoint_cam = self.dataset[self._iteration]
        render_pkg = self.model.render(viewpoint_cam)
        image, viewspace_point_tensor, visibility_filter, radii = render_pkg["render"], render_pkg["viewspace_points"], \
                        render_pkg["visibility_filter"], render_pkg["radii"]

        # Loss
        gt_image = viewpoint_cam.original_image.to(self.settings.device)
        Ll1 = l1_loss(image, gt_image)
        loss = (1.0 - self.settings.lambda_dssim) * Ll1 + \
            self.settings.lambda_dssim * (1.0 - ssim(image, gt_image))
        loss.backward()

        # Optimizer step
        self.optimizer.step()
        self.optimizer.zero_grad(set_to_none = True)

        with torch.no_grad():
            # Progress bar
            self.ema_loss = 0.4 * loss.item() + 0.6 * self.ema_loss
            self.post_iteration_checks(self._iteration, viewspace_point_tensor, visibility_filter, radii)

        self.loss_values_each_iter.append(loss.item())

        self._iteration += 1
        self.last_loss = loss.item()
        return self._iteration, image, self.last_loss, self.ema_loss
    
    def train_all(self):
        t = tqdm(range(self._iteration, self.settings.iterations))
        for _ in t:
            i, img, loss, ema_loss = self.step()
            t.set_description(f"[{self._iteration+1}/{self.settings.iterations}] loss: {ema_loss:0.04f}")
    
    def train_threaded(self, server_controller):
        t0 = time.time()
        while self.training:
            i, last_img, last_loss, ema_last_loss = self.step()
            server_controller.on_train_step(self._iteration, 
                                        last_img.detach().cpu().numpy(), 
                                        last_loss, ema_last_loss)
            