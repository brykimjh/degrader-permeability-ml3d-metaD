#!/bin/bash

# Define input PDB files and ligand name
ligand_pdb="antechamber_initial_files/lig.pdb"
ligand_name="UNK"

# Step 0.5: Read the total charge from total_charge.txt
echo "Reading total charge from total_charge.txt..."
charge=$(grep "Total partial charge (integer part):" total_charge.txt | awk '{print $6}')

if [ -z "$charge" ]; then
    echo "Error: Could not read charge from total_charge.txt. Exiting."
    exit 1
fi

echo "Total charge read successfully: Charge=$charge."

# Step 1: Re-generate ligand files using Antechamber and Parmchk2
echo "Re-generating ligand files using Antechamber and Parmchk2..."
antechamber -i $ligand_pdb -fi pdb -o lig.mol2 -fo mol2 -c bcc -s 2 -nc $charge -rn $ligand_name -at gaff2
#antechamber -i $ligand_pdb -fi pdb -o lig.mol2 -fo mol2 -c gas -s 2 -nc $charge -rn $ligand_name -at gaff2
parmchk2 -i lig.mol2 -f mol2 -o lig.frcmod

if [ $? -ne 0 ]; then
    echo "Error: Antechamber or Parmchk2 failed. Exiting."
    exit 1
fi

echo "Ligand files re-generated successfully."

