#!/bin/sh

mkdir -p casts

for filename in scripts/*.yaml; do

    output="casts/$(basename "$filename" .yaml).cast"

    echo "spielbash --script $filename --output $output $@"
    spielbash --script $filename --output $output "$@"
    echo

done
