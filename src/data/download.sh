#!/bin/bash
years=($(seq 1968 1980))

for i in $(seq 0 14); do
   wget https://data.nber.org/natality/"${years[$i]}"/natl"${years[$i]}".csv.zip 
done
