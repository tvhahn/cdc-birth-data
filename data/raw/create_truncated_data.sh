#!/bin/bash
for file in ./*.csv; do
    head -n 1000 "$file" >"$file.trunc"
done

zip -r truncated *.trunc

rm -r *.trunc