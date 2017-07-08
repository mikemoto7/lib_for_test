#!/bin/bash


\ls *.actual | \
while read source_file; do
   file_basename=$(echo $source_file | sed 's/\.actual//')
   target_file=${file_basename}.expected
   cp $source_file $target_file
done









