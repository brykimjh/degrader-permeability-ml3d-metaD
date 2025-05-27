import os
import shutil
import subprocess

# Number of molecules
nmol = 1

TEMPLATE_DIR = "scripts/forcefield"
OUTPUT_ROOT = "outputs/forcefield"

for i in range(1, nmol + 1):
    mol_name = f"mol_{i}"
    mol_dir = os.path.join(OUTPUT_ROOT, mol_name)

    print(f"Preparing job for {mol_name}...")

    # Remove existing job dir if it exists
    if os.path.exists(mol_dir):
        shutil.rmtree(mol_dir)

    # Copy job template into output directory
    shutil.copytree(TEMPLATE_DIR, mol_dir)

    # Replace mol_INDEX in submit.pbs
    submit_path = os.path.join(mol_dir, "submit.pbs")
    subprocess.run(["sed", "-i", f"s/mol_INDEX/{mol_name}/g", submit_path])

    # Submit the PBS job
    print(f"Submitting job for {mol_name}")
    subprocess.run(["qsub", "submit.pbs"], cwd=mol_dir)

