#!/bin/bash
PROJECT_DIR=$1
cd $PROJECT_DIR

mkdir -p $PROJECT_DIR/data/raw

# move to raw data folder
cd $PROJECT_DIR/data/raw

# select years
years=($(seq 1968 2019))

for i in $(seq 0 52); do
   wget https://data.nber.org/natality/"${years[$i]}"/natl"${years[$i]}".csv.zip 
done

wget http://data.nber.org/natality/2019/nber_output/birth_2019_nber_us_v2.csv


