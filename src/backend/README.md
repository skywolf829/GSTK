# GSTK backend
Backend code for the gaussian model, training, datasets, and communicating with GUI.

# Installation

Requires CUDA Toolkit installed on system previously, we use v11.8.

From `/src/backend`, invoke:

`conda env create -f env.yml`
`conda activate GSTK_backend`

## Debug backend
If you would like run the backend for testing on a non-CUDA device, install a limited backend:

`conda env create -f env_no_CUDA.yml`
`conda activate GSTK_backend_no_CUDA`