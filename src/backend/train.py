import os
import sys
from dataset import Dataset
from model import GaussianModel
from trainer import Trainer
from argparse import ArgumentParser
import torch
from utils.system_utils import mkdir_p
from settings import Settings
from utils.general_utils import safe_state


if __name__ == "__main__":
    # Set up command line argument parser
    parser = ArgumentParser(description="Backend server controller script")
    parser.add_argument('--ip', type=str, default="127.0.0.1")
    parser.add_argument('--port', type=int, default=6009)
    parser.add_argument('--debug_from', type=int, default=-1)
    parser.add_argument('--detect_anomaly', action='store_true', default=False)
    parser.add_argument("--test_iterations", nargs="+", type=int, default=[7_000, 30_000])
    parser.add_argument("--save_iterations", nargs="+", type=int, default=[7_000, 30_000])
    parser.add_argument("--quiet", action="store_true")
    parser.add_argument("--checkpoint_iterations", nargs="+", type=int, default=[])
    parser.add_argument("--start_checkpoint", type=str, default = None)

    # Create the settings
    settings = Settings()
    # Update the argparse to have all the settings necessary with default values
    settings.update_argparse(parser)
    # Finally parses the argparse and updates the settings object
    settings.update_settings_from_argparse(parser)

    if(settings.dataset_path is None):
        print(f"--dataset_path argument is required")
        quit()
    if(settings.save_path is None):
        fp = os.path.dirname(os.path.abspath(__file__))
        save_path = os.path.abspath(os.path.join(fp, "..", "savedModels"))
        mkdir_p(save_path)
        print(f"Saving model to {save_path}")
        settings.save_path = save_path

    # Initialize system state (RNG)
    #safe_state(settings.quiet)

    dataset = Dataset(settings)
    settings.spatial_lr_scale = dataset.cameras_extent

    gaussians = GaussianModel(settings)
    gaussians.create_from_pcd(dataset.scene_info.point_cloud)
    
    trainer = Trainer(gaussians, settings)
    trainer.set_dataset(dataset)


    trainer.train_all()

    # All done
    print("\nTraining complete.")
