
import cv2
import numpy as np
import argparse
import os

def iterate_through_folder(read_fold, scale_fold, max_res):
    for im_path in os.listdir(read_fold):        
        if(".jpg" in im_path.lower() or ".jpeg" in im_path.lower() or ".png" in im_path.lower()):
            im = cv2.imread(os.path.join(read_fold, im_path), 1)
            max_dim = max(im.shape[0], im.shape[1])
            if(max_dim > max_res):
                factor = max_res / max_dim
                im = cv2.resize(im, (int(im.shape[1]*factor), int(im.shape[0]*factor)))
            cv2.imwrite(os.path.join(scale_fold, im_path), im)


parser = argparse.ArgumentParser("Resize images")
parser.add_argument("--load_folder", required=True)
parser.add_argument("--save_folder", required=True)
parser.add_argument("--max_dim", type=int, default=1920)
args = parser.parse_args()

if(not os.path.exists(args.save_folder)):
    os.makedirs(args.save_folder)

iterate_through_folder(args.load_folder, args.save_folder, args.max_dim)