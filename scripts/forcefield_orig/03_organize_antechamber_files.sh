#!/bin/bash

# Create a directory for the initial Antechamber files if it doesn't exist
mkdir -p antechamber_initial_files

# Move all Antechamber-generated files and ligand-related files into this directory using wildcards
mv ANTECHAMBER_* ATOMTYPE.INF lig.* antechamber_initial_files/

echo "All Antechamber and ligand files moved to antechamber_initial_files directory."

