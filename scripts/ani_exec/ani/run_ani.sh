#!/bin/bash

# Check if a solvent argument is provided
if [ -z "$1" ]; then
    echo "Usage: $0 <solvent>"
    exit 1
fi

# Configuration
SOLVENT="$1"  # Solvent passed as an argument (e.g., "chloroform" or "water")

# Setup environment (commented out for PBS execution)
# module purge
# module load merck_csc
# module load csc/python
# conda activate torchani
# module load openeye
# module load schrodinger

# Prepare output directory
rm -rf analysis
mkdir analysis

# Run ANI single-point calculations
python /SFS/project/kw/kimbry/rklake/smiles_to_ff/git/mrl-mi-ssf-torchani/scripts/run_ANI.py \
    -model ANI2x_${SOLVENT} \
    -input optimized/concatenated_output.sdf \
    -output_sdf analysis/output_sp.sdf \
    -output_csv analysis/output_sp.csv \
    -single_point

# Extract lowest energy conformers
python ../0_scripts/extract_lowest_energy.py \
    -s analysis/output_sp.sdf \
    -c analysis/output_sp.csv \
    -o analysis/lowest_conformer.sdf \
    -n 10

# Calculate molecular properties
$SCHRODINGER/run python3 ../0_scripts/calculate_psa.py -i analysis/output_sp.sdf -o analysis/psa_values.csv
$SCHRODINGER/run python3 ../0_scripts/calculate_imhb.py -i analysis/output_sp.sdf -o analysis/imhb_results.csv
python ../0_scripts/calculate_3d_descriptors.py -i analysis/output_sp.sdf -o analysis/3d_descriptors.csv

# Perform ensemble averaging
python ../0_scripts/calculate_boltzmann_weights.py -i analysis/output_sp.csv -o analysis/boltzmann_weights.csv
python ../0_scripts/calculate_ensemble_avg.py -w analysis/boltzmann_weights.csv -p analysis/psa_values.csv -o analysis/ensemble_avg_psa.txt -c PSA
python ../0_scripts/calculate_ensemble_avg.py -w analysis/boltzmann_weights.csv -p analysis/imhb_results.csv -o analysis/ensemble_avg_num_imhb.txt -c Num_IMHB
python ../0_scripts/calculate_ensemble_avg.py -w analysis/boltzmann_weights.csv -p analysis/3d_descriptors.csv -o analysis/ensemble_avg_rgyr.txt -c RadiusOfGyration

