# GSTK backend
Backend code for the gaussian model, training, datasets, and communicating with GUI.

# Installation

This section covers the installation procedure for just the backend code. 
Your system should have a CUDA capable graphics card.

## Prerequisites
- [CUDA Toolkit](https://developer.nvidia.com/cuda-downloads).
We have tested with v11.8 on Windows 11.
Ensure the environment's `PATH` variable is updated to include the `bin` folder of the installed CUDA toolkit.
- [Conda](https://docs.anaconda.com/free/miniconda/) package manager.
This will install Python and the required Python packages to run the server.
We use Miniconda on Windows 11.
- [COLMAP](https://colmap.github.io/index.html) (optional). 
Required if you'd like to process your own images into a dataset to train a model with.
We highly recommend installing with CUDA support for quicker processing times.


## Conda installation
From a terminal at `/src/backend`, invoke:

```
conda env create -f env.yml
conda activate GSTK_backend
```

It may take some time to download all packages, install, and compile the CUDA code.
 

# Running the code
From a terminal at `/src/backend`, invoke:

```
python backend.py --ip <your.ip.address.here> --port <open_port_number>
```

If you are running both the server and application on the same machine, you can use the default localhost and port:

```
python backend.py
```

If your server is another device in your network, you can use the devices local IP address on your LAN.
If your server is remote, find the servers public IP address and ensure a port is forwarded properly.
Then, use that specific IP and port for connection.