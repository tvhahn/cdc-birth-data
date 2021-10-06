#!/bin/bash
PROJECT_DIR=$1
cd $PROJECT_DIR

# move to raw data folder
cd $PROJECT_DIR/data/raw

# select years
years=($(seq 1968 2019))

for i in $(seq 0 14); do
   wget https://data.nber.org/natality/"${years[$i]}"/natl"${years[$i]}".csv.zip 
done
