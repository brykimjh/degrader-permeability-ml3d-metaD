import os
import shutil
import subprocess

# Number of molecules
nmol = 1

TEMPLATE_DIR = "scripts/metadynamics"
INPUT_ROOT = "outputs/forcefield"
OUTPUT_ROOT = "outputs/metadynamics"

for i in range(1, nmol + 1):
    mol_name = f"mol_{i}"
    mol_dir = os.path.join(OUTPUT_ROOT, mol_name)
    input_dir = os.path.join(INPUT_ROOT, mol_name)

    print(f"Preparing metadynamics job for {mol_name}...")

    # Remove existing directory if it exists
    if os.path.exists(mol_dir):
        shutil.rmtree(mol_dir)

    # Copy template
    shutil.copytree(TEMPLATE_DIR, mol_dir)

    # Copy required input files from numbered folder
    for filename in [
        "system_1.frcmod", "system_1.inpcrd", "system_1.mol2",
        "system_1.prmtop", "natoms.txt", "total_charge.txt"
    ]:
        shutil.copy(os.path.join(input_dir, filename), os.path.join(mol_dir, filename))

    # Replace mol_INDEX in submit.pbs
    submit_path = os.path.join(mol_dir, "submit.pbs")
    subprocess.run(["sed", "-i", f"s/mol_INDEX/{mol_name}/g", submit_path])

    # Submit the job
    print(f"Submitting job for {mol_name}")
    subprocess.run(["qsub", "submit.pbs"], cwd=mol_dir)

