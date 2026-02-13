#!/bin/bash

# File containing the molecule data
mol2_file="antechamber_initial_files/lig.mol2"

# Output file for the total charge
output_file="total_charge.txt"

# Start processing from the line containing '@<TRIPOS>ATOM'
# and stop at the line containing '@<TRIPOS>BOND' or '@<TRIPOS>SUBSTRUCTURE'
# This ensures we only process the ATOM section
awk '/@<TRIPOS>ATOM/,/@<TRIPOS>BOND|@<TRIPOS>SUBSTRUCTURE/' $mol2_file |
grep -v '@<TRIPOS>' |  # Remove lines that contain section headers or footers
awk '{sum += $9} END {
    rounded = (sum >= 0) ? int(sum + 0.5) : int(sum - 0.5);
    printf "Total partial charge (integer part): %d\nTotal partial charge (exact): %.6f\n", rounded, sum
}' > $output_file

echo "Total partial charge has been saved to $output_file."

