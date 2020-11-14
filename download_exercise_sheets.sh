#!/bin/bash

BASE_URL="https://com402.epfl.ch/handouts/"
for counter in `seq 0 9`;
do
    file_name="hw${counter}.pdf"
    output_path="homework${counter}/${file_name}"
    curl "${BASE_URL}${file_name}" --output $output_path -f
done