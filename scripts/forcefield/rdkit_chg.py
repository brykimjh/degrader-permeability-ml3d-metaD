from rdkit import Chem

# load PDB
mol = Chem.MolFromPDBFile("ligand.pdb", sanitize=False, removeHs=False)
if mol is None:
    raise ValueError("Failed to load PDB")

# write MOL
Chem.MolToMolFile(mol, "ligand_fixed.mol", includeStereo=False)
print("Wrote ligand_fixed.mol")

# compute charge safely
total = 0

with open("ligand_fixed.mol") as f:
    for line in f:
        if line.startswith("M  CHG"):
            parts = line.split()
            # expected: M CHG <n> <atom1> <chg1> <atom2> <chg2> ...
            n = int(parts[2])
            fields = parts[3:]
            # fields should contain 2*n integers
            for i in range(0, len(fields), 2):
                try:
                    charge = int(fields[i+1])
                    total += charge
                except (IndexError, ValueError):
                    pass  # skip malformed pairs

# write charge file
with open("total_charge.txt", "w") as out:
    out.write(f"Total partial charge (rounded): {total}\n")
    out.write(f"Total partial charge (exact): {total:.6f}\n")

