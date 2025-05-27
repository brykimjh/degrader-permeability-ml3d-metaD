#!/bin/bash

# Check if the correct number of arguments is provided
if [ "$#" -ne 6 ]; then
    echo "Usage: $0 <solvent> <sdf_file> <total_configurations> <chunk_size> <files_dir> <template_pbs>"
    exit 1
fi

# Assign arguments to variables
SOLVENT=$1
SDF_FILE=$2
TOTAL_CONFIGURATIONS=$3
CHUNK_SIZE=$4
FILES_DIR=$5
TEMPLATE_PBS=$6

# Run the Python script with the provided arguments
python ../0_scripts/ani_job_setup.py "$SOLVENT" "$SDF_FILE" "$TOTAL_CONFIGURATIONS" "$CHUNK_SIZE" "$FILES_DIR" "$TEMPLATE_PBS"

