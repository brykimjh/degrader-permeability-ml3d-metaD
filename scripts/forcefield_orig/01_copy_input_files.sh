#!/bin/bash

# Ensure the script is called with an argument
if [ "$#" -ne 1 ]; then
    echo "Usage: $0 <mol_name>"
    exit 1
fi

# Grab the ligand from the full molecule .pdb file
grep HETATM ../../../data/"$1".pdb > lig.pdb

