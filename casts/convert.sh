#!/bin/bash

mkdir -p gifs

for filename in casts/*.cast; do

    output="gifs/$(basename "$filename" .cast).gif"

    echo "asciicast2gif $@ $filename $output"
    /app/asciicast2gif "$@" $filename $output
    echo

done
