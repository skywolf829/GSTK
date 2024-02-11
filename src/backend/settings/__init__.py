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

from argparse import ArgumentParser, Namespace
import sys
import os
from typing import Any
import torch

# Global settings class
class Settings():
    def __init__(self):
        self.params = {
            
            # from old ModelParams 
            "sh_degree" : 3,
            "dataset_path" : "",
            "save_path" : "",
            "resolution_scale" : -1,
            "white_background" : False,
            "device": "cuda" if torch.cuda.is_available() else "cpu",
            "data_device": "cuda" if torch.cuda.is_available() else "cpu",

            # from old OptimizationParams
            "iterations" : 30_000,
            "position_lr_init" : 0.00016,
            "position_lr_final" : 0.0000016,
            "position_lr_delay_mult" : 0.01,
            "position_lr_max_steps" : 30_000,
            "feature_lr" : 0.0025,
            "opacity_lr" : 0.05,
            "scaling_lr" : 0.005,
            "rotation_lr" : 0.001,
            "percent_dense" : 0.01,
            "lambda_dssim" : 0.2,
            "densification_interval" : 100,
            "opacity_reset_interval" : 3000,
            "densify_from_iter" : 500,
            "densify_until_iter" : 15_000,
            "densify_grad_threshold" : 0.0002,
            "spatial_lr_scale" : 1.0,
            "random_background" : False
        }

    def keys(self):
        return self.params.keys()
    
    def update_argparse(self, parser = None):
        if parser is None:
            parser = ArgumentParser("Gaussian model and training parameters")
            
        for key in self.params:
            parser.add_argument(f"--{key}", default=self.params[key])
        
        return parser
    
    # Takes all arguments from the argparser and updates them in the
    # internal params object
    def update_settings_from_argparse(self, parser : ArgumentParser):
        args = parser.parse_args()
        for k in args.__dict__:
            if args.__dict__[k] is not None:
                self.params[k] = args.__dict__[k]

    # Python default calls __getattribute__ to instance of objects when attributes
    # (such as member variables or methods) are trying to be accessed.
    # __getattr__ is only called if __getattribute__ fails. Here,
    # we use it to catch the rest in case the attribute is in our param dict.
    def __getattr__(self, __name: str) -> Any:
        try:
            return self.params[__name]
        except:
            raise Exception(f"Settings does not have attribute {__name}.")

    def __setattr__(self, __name: str, __value: Any) -> None:
        if(__name == "params"):
            super().__setattr__(__name, __value)
        else:
            try:
                self.params[__name] = __value
            except:
                raise Exception(f"Settings does not have attribute {__name}.")
