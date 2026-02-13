#!/bin/bash

# Define input PDB file
ligand_pdb="lig.pdb"

# Step 1: Run antechamber to generate .mol2 file with specified charge and GAFF2 atom types
# Update the charge method to Gasteiger
antechamber -i $ligand_pdb -fi pdb -o lig.mol2 -fo mol2 -c gas -s 2 -rn LIG -at gaff2

# Check if the .mol2 file was generated successfully
if [ ! -f lig.mol2 ]; then
    echo "Error: Failed to generate lig.mol2 file. Exiting."
    exit 1
fi

