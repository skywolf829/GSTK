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

import os
import random
import json
from dataset.dataset_readers import sceneLoadTypeCallbacks
from settings import Settings
import numpy as np
from utils.camera_utils import cameraList_from_camInfos, camera_to_JSON

class Dataset:
    def __init__(self, settings : Settings, shuffle=True, resolution_scales=[1.0], debug=False):
        """b
        :param path: Path to colmap scene main folder.
        """
        self.model_path = settings.save_path
        self.loaded_iter = None
        self.white_background = settings.white_background
        self.train_cameras = {}
        self.test_cameras = {}
        self.settings = settings
        self.DEBUG = debug
        if(self.DEBUG):
            return
        
        if os.path.exists(os.path.join(settings.dataset_path, "sparse")):
            print("Found sparse folder, assuming COLMAP dataset.")
            scene_info = sceneLoadTypeCallbacks["Colmap"](settings.dataset_path, "images", False)
        elif os.path.exists(os.path.join(settings.dataset_path, "transforms_train.json")):
            print("Found transforms_train.json file, assuming Blender dataset.")
            scene_info = sceneLoadTypeCallbacks["Blender"](settings.dataset_path, settings.white_background, False)
        else:
            print("Could not recognize scene type!")
            assert False, "Could not recognize scene type!"

        if not self.loaded_iter:
            #with open(scene_info.ply_path, 'rb') as src_file, open(os.path.join(self.model_path, "input.ply") , 'wb') as dest_file:
            #    dest_file.write(src_file.read())
            json_cams = []
            camlist = []
            if scene_info.test_cameras:
                camlist.extend(scene_info.test_cameras)
            if scene_info.train_cameras:
                camlist.extend(scene_info.train_cameras)
            for id, cam in enumerate(camlist):
                json_cams.append(camera_to_JSON(id, cam))
            #with open(os.path.join(self.model_path, "cameras.json"), 'w') as file:
            #    json.dump(json_cams, file)


        if shuffle:
            random.shuffle(scene_info.train_cameras)  # Multi-res consistent random shuffling
            random.shuffle(scene_info.test_cameras)  # Multi-res consistent random shuffling


        self.cameras_extent = scene_info.nerf_normalization["radius"]


        for resolution_scale in resolution_scales:
            print("Loading Training Cameras")
            self.train_cameras[resolution_scale] = cameraList_from_camInfos(scene_info.train_cameras, resolution_scale, settings)
            print("Loading Test Cameras")
            self.test_cameras[resolution_scale] = cameraList_from_camInfos(scene_info.test_cameras, resolution_scale, settings)
        self.scene_info = scene_info

        min_pos = self.scene_info.point_cloud.points.min(axis=0)
        max_pos = self.scene_info.point_cloud.points.max(axis=0)
        max_diff = np.max(max_pos - min_pos)
        self.settings.spatial_lr_scale = max_diff.flatten()[0]
        print("Dataset loaded")

    def __getitem__(self, idx, scale=1.0):
        return self.train_cameras[scale][idx % len(self.train_cameras[scale])]

    def getTrainCameras(self, scale=1.0):
        return self.train_cameras[scale]

    def getTestCameras(self, scale=1.0):
        return self.test_cameras[scale]