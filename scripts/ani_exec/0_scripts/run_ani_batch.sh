#!/bin/bash

# Check if the required arguments are provided
if [[ $# -lt 2 ]]; then
  echo "Usage: $0 <input_index> <solvent>"
  echo "Example: $0 56 water"
  exit 1
fi

# Input arguments
INPUT_INDEX=$1
SOLVENT=$2

# Input file
INPUT_FILE="chunk_${INPUT_INDEX}.sdf"

# Validate input file exists
if [[ ! -f "$INPUT_FILE" ]]; then
  echo "Error: Input file '$INPUT_FILE' not found."
  exit 1
fi

echo "Processing input file: $INPUT_FILE"
echo "Using solvent: $SOLVENT"

# Output directories
SPLIT_DIR="split_sdf"
OUTPUT_DIR="ani_results"
FINAL_CSV="../../csv/optimized_${INPUT_INDEX}.csv"
FINAL_SDF="../../sdf/optimized_${INPUT_INDEX}.sdf"

# Create directories if they don't exist
mkdir -p "$SPLIT_DIR" "$OUTPUT_DIR" "$(dirname "$FINAL_CSV")" "$(dirname "$FINAL_SDF")"

# Get line numbers of the delimiters and store them in an array
mapfile -t line_numbers < <(grep -n '\$\$\$\$' "$INPUT_FILE" | cut -d: -f1)

# Split the file based on the line numbers
start=1
count=1 # Start counting from 1
for end in "${line_numbers[@]}"; do
  sed -n "${start},${end}p" "$INPUT_FILE" > "$SPLIT_DIR/molecule_$count.sdf"
  echo "Saved molecule $count from line $start to $end."
  start=$((end + 1))
  count=$((count + 1))
done

echo "Split completed. $((count - 1)) molecules saved to '$SPLIT_DIR'."

# Python script and model for ANI processing
ANI_PYTHON_SCRIPT="/SFS/project/kw/kimbry/rklake/smiles_to_ff/git/mrl-mi-ssf-torchani/scripts/run_ANI.py"
MODEL="ANI2x_${SOLVENT}"

# Loop through each SDF file in the input directory
for input_file in "$SPLIT_DIR"/*.sdf; do
  # Extract base filename without extension
  base_name=$(basename "$input_file" .sdf)

  # Set output filenames
  output_sdf="$OUTPUT_DIR/${base_name}_optimized.sdf"
  output_csv="$OUTPUT_DIR/${base_name}_optimized.csv"
  log_file="$OUTPUT_DIR/${base_name}_run.log"

  # Run the Python command
  echo "Processing $input_file..."
  python "$ANI_PYTHON_SCRIPT" \
    -model "$MODEL" \
    -input "$input_file" \
    -output_sdf "$output_sdf" \
    -output_csv "$output_csv" \
    > "$log_file" 2>&1

  # Check if the Python script ran successfully
  if [[ $? -eq 0 ]]; then
    echo "Successfully processed $input_file. Results saved to $output_sdf and $output_csv."
  else
    echo "Error processing $input_file. Running single-point optimization on original SDF file..."
    python "$ANI_PYTHON_SCRIPT" \
      -model "$MODEL" \
      -input "$input_file" \
      -output_sdf "$output_sdf" \
      -output_csv "$output_csv" \
      -single_point \
      > "$log_file" 2>&1

    if [[ $? -eq 0 ]]; then
      echo "Single-point optimization successful for $input_file. Results saved to $output_sdf and $output_csv."
    else
      echo "Single-point optimization also failed for $input_file. Check log file: $log_file"
    fi
  fi
done

echo "All files processed."

# Concatenate all CSV files in order
echo "Concatenating all CSV files into $FINAL_CSV..."
head -n 1 $(find "$OUTPUT_DIR" -type f -name "*.csv" | sort | head -n 1) > "$FINAL_CSV" # Add header from the first file
for file in $(find "$OUTPUT_DIR" -type f -name "*.csv" | sort); do
  tail -n +2 "$file" >> "$FINAL_CSV" # Skip header lines from subsequent files
done
echo "CSV concatenation complete. Saved to $FINAL_CSV."

# Concatenate all SDF files in order
echo "Concatenating all SDF files into $FINAL_SDF..."
cat $(find "$OUTPUT_DIR" -type f -name "*.sdf" | sort) > "$FINAL_SDF"
echo "SDF concatenation complete. Saved to $FINAL_SDF."

echo "All tasks completed successfully."

