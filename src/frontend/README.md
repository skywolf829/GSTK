# GSTK
Frontend application for GSTK.

# Installation

Installation instructions for the application.
Can be ran on any machine that supports Python.

## Prerequisites
- [Conda](https://docs.anaconda.com/free/miniconda/) package manager.
This will install Python and the required Python packages to run the server.
We use Miniconda on Windows 11.

## Installation

From a terminal at `/src/frontend`, invoke:

```
conda env create -f env.yml
conda activate GSTK
```

It may take some time to create the environment.

# Running the frontend

From a terminal at `/src/frontend`, invoke:

```
python app.py
```

Alternatively, you can double click on `GSTK.sh` or `/src/frontend/app.sh`.