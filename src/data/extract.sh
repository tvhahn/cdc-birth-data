#!/bin/bash
PROJECT_DIR=$1
cd $PROJECT_DIR

# move to raw data folder
cd $PROJECT_DIR/data/raw

# extract all zip files
unzip '*.zip'

# rename 2018, 2019, 2020 files so that they fit standard naming convention
mv $PROJECT_DIR/data/raw/natl2018us.csv $PROJECT_DIR/data/raw/natl2018.csv
mv $PROJECT_DIR/data/raw/birth_2019_nber_us.csv $PROJECT_DIR/data/raw/natl2019.csv
mv $PROJECT_DIR/data/raw/birth_2020_nber_us.csv $PROJECT_DIR/data/raw/natl2020.csv
