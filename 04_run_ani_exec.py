import os
import argparse

# Define configurable parameters
solvent = 'chloroform'
nmol = 1
output_file = "../data/output.sdf"
frames_per_job = 15
num_jobs = 3
output_dir = "files"
template_script = "../0_scripts/template_submit_array.pbs"

# Define the argument parser
parser = argparse.ArgumentParser(description="Run job scripts with different steps.")
parser.add_argument("step", type=int, choices=[1, 2], help="Step to execute (1 or 2).")
args = parser.parse_args()

# Verify the step before proceeding
if args.step not in [1, 2]:
    print("Invalid step. Please specify 1 for single-point energy calculations or 2 for ANI-based property calculations.")
    exit(1)

# Display the loaded modules
print("Checking loaded modules...")
os.system("module list")

# Step 1: Single-point energy calculations and ANI minimization
if args.step == 1:
    # Prompt the user to verify if RDKit is loaded
    rdkit_loaded = input("Is the RDKit module loaded? (yes/no): ").strip().lower()
    if rdkit_loaded != 'yes':
        print("RDKit module is not loaded. Exiting...")
        exit(1)

    for i in range(nmol):
        mol_ii = i + 1
        dir0 = f'outputs/ani_exec/mol_{mol_ii}'

        # Prepare configurations for single-point energy calculations and property calculations
        CC = f'''\
        rm -rf {dir0}
        cp -r scripts/ani_exec {dir0}
        cd {dir0}
        mkdir data
        cp ../../trajectory_processing/mol_{mol_ii}/output.sdf data/output.sdf
        cd ani
        sed -i "s/__SOLVENT__/{solvent}/g" submit_ani.pbs
        bash prep.sh {solvent} "{output_file}" {frames_per_job} {num_jobs} "{output_dir}" "{template_script}"
        '''
        print(CC)
        os.system(CC)

# Step 2: Property calculations on ANI-minimized conformations
elif args.step == 2:
    for i in range(nmol):
        mol_ii = i + 1
        dir0 = f'outputs/ani_exec/mol_{mol_ii}'

        # Check if the directory {dir0}/ani exists
        if not os.path.exists(f"{dir0}/ani"):
            print(f"Directory {dir0}/ani does not exist. Skipping...")
            continue

        # Perform property calculations on ANI-minimized conformations
        CC = f'''\
        cd {dir0}/ani
        sed -i "s/__SOLVENT__/{solvent}/g" submit_ani.pbs
        qsub submit_ani.pbs
        '''
        print(CC)
        os.system(CC)

