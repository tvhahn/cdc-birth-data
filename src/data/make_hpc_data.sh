#!/bin/bash
#SBATCH --time=00:20:00 # 20 minutes
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=8
#SBATCH --mem=32G
#SBATCH --account=rrg-mechefsk
#SBATCH --mail-type=ALL               # Type of email notification- BEGIN,END,F$
#SBATCH --mail-user=18tcvh@queensu.ca   # Email to which notifications will be $

module load python/3.8

source ~/cdcbirth/bin/activate

python src/data/make_dataset_geo.py
python src/data/make_dataset_no_geo.py