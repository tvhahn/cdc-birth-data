#!/bin/bash
#SBATCH --time=00:30:00 # 10 minutes
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=16
#SBATCH --mem=64G
#SBATCH --account=rrg-mechefsk
#SBATCH --mail-type=ALL               # Type of email notification- BEGIN,END,F$
#SBATCH --mail-user=18tcvh@queensu.ca   # Email to which notifications will be $

module load python/3.8

source ~/cdcbirth/bin/activate

python src/data/make_dataset_geo.py --n_cores 16
# python src/data/make_dataset_no_geo.py
# python src/data/make_dataset_no_geo_extra.py