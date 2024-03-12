# Gaussian Splatting Toolkit

This is the code for Gaussian Splatting Toolkit (GSTK), an application to help you create a dataset, train a gaussian splatting model, edit it to your liking, and export it for use in other applications!

The application for this codebase is live at https://skywolf829.github.io/GSTK/.

## Why GSTK?
Many [great 3DGS tools exist](https://github.com/MrNeRF/awesome-3D-gaussian-splatting) for editing a trained [3DGS model](https://repo-sam.inria.fr/fungraph/3d-gaussian-splatting/) for use in other rendering software such as Blender, Unity, Unreal, or on the web.
However, some of these edits can reduce the final quality.
In our toolkit, you can perform these edits at any point during or after training, and continue training afterward to fine-tune the model once the edits are complete.
This way, quality can be preserved.

Conversely, we can help the 3DGS model perform better with a human-in-the-loop training routine! 
3DGS will often create floaters placed inconveniently to reduce training loss, or make surfaces that aren't flat due to lack of training viewpoints.
As a human with an innate understanding of the scene, we can help models perform better (and create better geometry) by adjusting gaussians during training.

## How does GSTK work?
Our toolkit uses a backend-frontend framework.
All of the training and rendering is hosted on a CUDA-accelerated backend (using our [backend code](https://github.com/skywolf829/GSTK_backend)), while the viewing, interacting, and editing is handled from a webapp (this codebase).
Since we cannot provide free GPUs to everyone, we require that you install the backend yourself on a machine with a CUDA-enabled GPU; please see the backend code repository above.
Once your backend is running, you can connect to it from any device (the same PC, a laptop, or a tablet) and start your training!

## How do I use it?
To install the backend and start using our application, please see our [backend code's](https://github.com/skywolf829/GSTK_backend) installation instructions.

When thats installed and running, visit https://skywolf829.github.io/GSTK/ and begin this process:

### 1. Connecting to the backend
Once you start the application (while the backend server is running), the first thing you need to do is connect to the server.

![Server connection window](figures/ServerConnection.jpg)

In the server connection window (in the middle of the image above), enter the IP and port that the server is running on (more information in the README in `src/backend`).
If you do not see the server connection window, open it by clicking on the plug icon from the icon bar above.

Once verifying the IP and port are correct, hit connect.
If you successfully connect, the plug icon should turn green.

![Server connected](figures/ServerConnected.jpg)

### 2. Loading your dataset
Now that you've connected to the server, the next step is to load your dataset!
Place your dataset in the `data` folder on the backend.

We support 3 kinds of datasets:

1. COLMAP datasets. 
These are datasets created with [COLMAP](https://colmap.github.io/index.html). 
The result is a set of images, camera positions, a point cloud, and colors for the points. 
These are used as the tools to initialize and train the model.
You can create your own with `src/backend/convert.py` after installing COLMAP with only a directory of images.
The (important parts of the) directory structure is assumed to look like this:
```
<dataset_name>
    |images
        |im1.jpg
        |im2.jpg
        |...
    |sparse
        |0
            |cameras.bin
            |images.bin
            |points3D.bin
            |project.ini
```
2. Blender datasets. 
These are datasets similar to those created for some NeRF models. 
The directory structure is assumed to look like this:
```
<dataset_name>
    |test
        |test_im1.jpg
        |test_im2.jpg
        |...
    |train
        |train_im1.jpg
        |train_im2.jpg
        |...
    |val
        |val_im1.jpg
        |val_im2.jpg
        |...
    |transforms_test.json
    |transforms_train.json
    |transforms_val.json
```
3. Image folder. 
In the case you've captured your own images for a dataset and haven't processed them with COLMAP yet, we also support doing this in GSTK so long as you have installed COLMAP on the server machine.
Organize all images into a single folder like so, and our app will process it using COLMAP into the colmap dataset:
```
<dataset_name>
    |im1.jpg
    |im2.jpg
    |...
```

While loading your dataset (which may take between 15 seconds and up to 10 minutes if running COLMAP), you will see a loading sign.

![Dataset loading](figures/DatasetLoading.jpg)

Once it is loaded properly, the sign will disappear and you are ready to train!

### 3. Training your model

Finally, you can begin training your model.
Find the training window, and click "Start training".

![Training window](figures/Trainer.jpg)

As you train, the gaussian model will refine itself in the viewing window.
At any point, you can click "Stop training" to pause the model training so you may make edits if necessary.

![Training example](figures/TrainingExample.jpg)

### 4. Editing your model

At any point during training, you may pause model training and perform edits to the model.
These are accessed through the edit toolbar, shown below outlined in red.

![Edit window](figures/EditWindow.jpg)

When clicking on one of the edit operations, a window will pop up related to that operations settings.
At the same time, a selector cube may appear in the scene.
Depending on the edit operation, you can move the selector cube to the area you'd like to apply the edit, and scale/rotate the selector as necessary.

![Deleting points example](figures/DeletePointsExample.jpg)

Training can seamlessly resume after editing, or you may be happy and can save the model by clicking on the settings icon and selecting `Model > Save model`, which will create `<model_name>.ply` in the `savedModels` folder on the server.

## Acknowledgements

Many thanks to the authors of 3DGS who have created a great work!
We borrow and adapt a majority of [their code](https://github.com/graphdeco-inria/gaussian-splatting) to fit in this application.
Since we do make numerous changes to their code's structure and CUDA API for the model, we do ship our own version of their model and training code, but acknowledge that a large chunk of our code is unchanged from the original implementation.

# Developers

If interested in running this webapp locally, use the following instructions:

## Prerequisites

This project uses Node.js.
Ensure you have node package manager available. 

## Project setup

In the project directory, run:

`npm install`

On some machines, you may need to add `sudo` before that to run in administrator mode.

Once everything is installed, you can start the project locally with

`npm start`

This runs the app in the development mode.
Open [http://localhost:3000](http://localhost:3000) to view it in your browser.

The page will reload when you make changes.

