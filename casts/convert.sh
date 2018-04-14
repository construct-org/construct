#!/bin/bash

mkdir gifs

for filename in casts/*.cast; do

    output="gifs/$(basename "$filename" .cast).gif"

    echo "asciicast2gif -h 60 $filename $output"
    /app/asciicast2gif -h 60 $filename $output

done
