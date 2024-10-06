#!/bin/bash

input_dir="./soccerserver"
output_dir="./soccerserver"

if [ ! -d "$output_dir" ]; then
    mkdir -p "$output_dir"  
fi

for rst_file in "$input_dir"/*.rst; do

    filename=$(basename "$rst_file" .rst)

    md_file="$rst_file.md"
    
    rst2myst convert $rst_file
    
    echo "Converted $rst_file to $md_file"

    rm "$rst_file"
    echo "Removed original file: $rst_file"
done

echo "All files have been converted and original .rst files have been removed!"
