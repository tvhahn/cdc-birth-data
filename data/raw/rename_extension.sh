#!/bin/bash
# remove the extension from all the .trunc files
for file in ./*.trunc; do
    mv "$file" "${file%.trunc}"
done