#!/bin/bash
PROJECT_DIR=$1
cd $PROJECT_DIR

# move to raw data folder
cd $PROJECT_DIR/data/raw

# extract all zip files
unzip '*.zip'

# rename 2018 and 2019 files so that they fit standard naming convention
mv $PROJECT_DIR/data/natl2018us.csv $PROJECT_DIR/data/natl2018.csv
mv $PROJECT_DIR/data/rawbirth_2019_nber_us_v2.csv $PROJECT_DIR/data/natl2019.csv
