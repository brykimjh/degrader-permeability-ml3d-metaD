#!/bin/bash

# Setup environment
export LD_LIBRARY_PATH=$LD_LIBRARY_PATH:/home/kimbry/.conda/envs/lapack_env/lib

# Get molecule name from folder name
MOLNAME=$(basename "$PWD")
META_DIR="../../metadynamics/${MOLNAME}"

cd "$META_DIR/eq_1"
bash 02_combine_dcd.sh

cd "../../../trajectory_processing/${MOLNAME}"

# Copy required files
cp "${META_DIR}/system_2.pdb" mol.pdb
cp "${META_DIR}/system_2.prmtop" mol.prmtop

# Fix residue name
sed -i 's/UNK/MOL/g' mol.*

# Dynamically write amber_script.in
cat > amber_script.in <<EOF
parm mol.prmtop
trajin ${META_DIR}/eq_1/md.dcd
trajin ${META_DIR}/eq_2/md.dcd
reference mol.pdb [ref]
center :MOL mass origin
image origin center familiar
strip !:MOL
trajout frames.pdb pdb
EOF

# Run cpptraj
cpptraj amber_script.in > amber_script.log

# Convert to SDF
python frames_to_sdf.py

# Clean up
rm -f mol.pdb mol.prmtop frames.pdb amber_script.in

echo "✅ output.sdf created in $(pwd)"

