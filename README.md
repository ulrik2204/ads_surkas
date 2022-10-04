# E-Commerce Data Science
Applied Data Science project for group 11.
Here we discover the [largest e-commerce dataset from Pakistan](https://www.kaggle.com/datasets/zusmani/pakistans-largest-ecommerce-dataset).

## Development

### First time setup
Install conda (miniconda): [Linux/WSL and Mac](https://educe-ubc.github.io/conda.html) or [Windows](https://docs.conda.io/en/latest/miniconda.html).
Ensure that `conda` is in path by typing `conda --version` in the terminal.

Create and activate conda environment from `env.yml`
```bash
conda env create -f env.yml   # create environment
conda activate ads_surkas   # activate environment
```

Each time you enter the project you only have to activate the environment

### Updating environment

```
conda env update --file env.yml --prune
```