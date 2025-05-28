#!/bin/bash

# Define directories and output file
SDF_DIR="files/sdf"
CSV_DIR="files/csv"
OUTPUT_DIR="optimized"
OUTPUT_FILE="$OUTPUT_DIR/concatenated_output.sdf"

# Create or recreate the output directory
rm -rf "$OUTPUT_DIR"
mkdir -p "$OUTPUT_DIR"

# Count the number of SDF and CSV files
NUM_SDF_FILES=$(find "$SDF_DIR" -type f -name "optimized_*.sdf" | wc -l)
NUM_CSV_FILES=$(find "$CSV_DIR" -type f -name "*.csv" | wc -l)

# Print the number of files
echo "Number of SDF files: $NUM_SDF_FILES"
echo "Number of CSV files: $NUM_CSV_FILES"

# Check if the number of SDF files matches the number of CSV files
if [[ "$NUM_SDF_FILES" -ne "$NUM_CSV_FILES" ]]; then
    echo "Error: The number of SDF files ($NUM_SDF_FILES) does not match the number of CSV files ($NUM_CSV_FILES)."
    exit 1
fi

# Loop through the SDF files and concatenate them into the output file
for i in $(seq 1 "$NUM_SDF_FILES"); do
    file="$SDF_DIR/optimized_${i}.sdf"
    if [[ -f "$file" ]]; then
        cat "$file" >> "$OUTPUT_FILE"
    else
        echo "File $file does not exist, skipping..."
    fi
done

echo "Concatenation complete. Output saved to $OUTPUT_FILE."

