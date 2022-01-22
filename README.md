CDC Birth Data in Python
==============================

Exploring the CDC birth data files using Python.

The work can by broken into two parts:

1. Data prep and consolidation of all the records into several summary tables. The summary tables may be of use to others.

2. Analysis of the data, including production of several data visualizations

   

Note: **Still a work in progress!** I'll be updating as I go along. Here's a sample of the visualizations:

<p align="center">
  <img alt="face milling" src="./reports/figures/1990_births_by_month.png" width="200px">
&nbsp; &nbsp; &nbsp; &nbsp;
  <img alt="flank wear" src="./reports/figures/violin_births.png" width="200px">
&nbsp; &nbsp; &nbsp; &nbsp;
</p>

### Dataset
The data set is from the National Bureau of Economic Research (NBER), on their [Vital Statistics Natality Birth Data page](https://www.nber.org/research/data/vital-statistics-natality-birth-data). NBER has provided csv's of the birth data, by year, from 1968 to 2020. The data is originally sourced from the [CDC Vital Statistics](https://www.cdc.gov/nchs/data_access/vitalstatsonline.htm), and totals ~19 GB, uncompressed.

### Analysis Summary

<figure>
       <img src="./reports/figures/violin_births.png" alt="vioin plot showing the percent change in births per month" style="background:none; border:none; box-shadow:none; text-align:center" width="500px"/>
</figure>

...


## Setup

Project will work well in a Linux and on a HPC environment. It will also work with MacOS (although not tested). Windows may require some minor changes by the user.











Project Organization
------------

    ├── LICENSE
    ├── Makefile           <- Makefile with commands like `make data` or `make train`
    ├── README.md          <- The top-level README for developers using this project.
    ├── data
    │   ├── external       <- Data from third party sources. You'll find geocoding data here.
    │   ├── interim        <- Intermediate data that has been transformed.
    │   ├── processed      <- The final, canonical data sets for modeling.
    │   └── raw            <- The original, immutable data dump.
    │
    │
    ├── models             <- Models (don't have any at the moment)
    │
    ├── notebooks          <- Jupyter notebooks.
    │   └── scratch        <- Jupyter notebooks of questionable quality.
    
    │
    ├── references         <- Data dictionaries, manuals, and all other explanatory materials.
    │
    ├── reports            <- Generated analysis as HTML, PDF, LaTeX, etc.
    │   └── figures        <- Generated graphics and figures to be used in reporting
    │
    ├── requirements.txt   <- The requirements file for reproducing the analysis environment, e.g.
    │                         generated with `pip freeze > requirements.txt`
    │
    ├── setup.py           <- makes project pip installable (pip install -e .) so src can be imported
    ├── src                <- Source code for use in this project.
    │   ├── __init__.py    <- Makes src a Python module
    │   │
    │   ├── data           <- Scripts to download or generate data
    │   │
    │   ├── features       <- Not used at present
    │   │
    │   ├── models         <- Not used at present
    │   │
    │   └── visualization  <- Scripts to create exploratory and results oriented visualizations
    │       └── visualize.py
    │


## Future Work

Ideas to consider:

* Identify anomalies by geography (although geo data may not be fine enough)
* Allow user to select any number of columns, and spit out new consolidated data file

