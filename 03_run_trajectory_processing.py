import os
import shutil
import subprocess

nmol = 1  # Set this to however many molecules you have

TEMPLATE_DIR = "scripts/trajectory_processing"
OUTPUT_ROOT = "outputs/trajectory_processing"

for i in range(1, nmol + 1):
    mol_name = f"mol_{i}"
    mol_dir = os.path.join(OUTPUT_ROOT, mol_name)

    print(f"\n🧬 Setting up and extracting descriptor input for {mol_name}...")

    # Ensure the output directory exists
    os.makedirs(mol_dir, exist_ok=True)

    # Copy all files and subdirs from TEMPLATE_DIR into mol_X
    for item in os.listdir(TEMPLATE_DIR):
        src = os.path.join(TEMPLATE_DIR, item)
        dest = os.path.join(mol_dir, item)

        if os.path.isdir(src):
            if os.path.exists(dest):
                shutil.rmtree(dest)
            shutil.copytree(src, dest)
        else:
            shutil.copy2(src, dest)

    try:
        # Original local execution (kept but commented out)
#        subprocess.run(["bash", "extract_sdf_from_md.sh"], cwd=mol_dir, check=True)
#        print(f"✅ output.sdf created in {mol_dir}")

        # Replace INDEX inside submit.pbs
        subprocess.run(
            ["sed", "-i", f"s/INDEX/{i}/", "submit.pbs"],
            cwd=mol_dir,
            check=True
        )

        # Submit via PBS
        subprocess.run(["qsub", "submit.pbs"], cwd=mol_dir, check=True)
        print(f"✅ Job submitted for {mol_name}")

    except subprocess.CalledProcessError:
        print(f"❌ Failed for {mol_name}")
