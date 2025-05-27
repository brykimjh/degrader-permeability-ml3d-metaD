import os
import csv

output_file = "3d_features.csv"
header = [
    "Index",
    "Ensemble_Average_PSA_Chloroform_ANI",
    "Ensemble_Average_Num_IMHB_Chloroform_ANI",
    "Ensemble_Average_RadiusOfGyration_Chloroform_ANI"
]

number_of_molecules = 32
base_dir = "../ani_exec"
rows = []

def extract_value(path):
    with open(path) as f:
        line = f.read().strip()
        return float(line.split(":")[1].strip())

for i in range(1, number_of_molecules + 1):
    mol_dir = os.path.join(base_dir, f"mol_{i}")
    if not os.path.isdir(mol_dir):
        print(f"❌ Skipping mol_{i}: directory not found.")
        continue

    try:
        psa = extract_value(os.path.join(mol_dir, "ensemble_avg_psa.txt"))
        imhb = extract_value(os.path.join(mol_dir, "ensemble_avg_num_imhb.txt"))
        rgyr = extract_value(os.path.join(mol_dir, "ensemble_avg_rgyr.txt"))
        rows.append([i, psa, imhb, rgyr])
    except Exception as e:
        print(f"⚠️  Failed to parse mol_{i}: {e}")

# Write the CSV
with open(output_file, "w", newline="") as f:
    writer = csv.writer(f)
    writer.writerow(header)
    writer.writerows(rows)

print(f"✅ 3D descriptor summary saved to {output_file}")

