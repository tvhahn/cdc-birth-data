#!/bin/bash
PROJECT_DIR=$1
cd $PROJECT_DIR

mkdir -p $PROJECT_DIR/data/raw/desc

# move to raw data folder
cd $PROJECT_DIR/data/raw/desc

# select years
years=($(seq 1968 2019))

for i in $(seq 0 52); do
   wget -O "${years[$i]}".txt https://data.nber.org/natality/"${years[$i]}"/desc/natl"${years[$i]}"/desc.txt
done


