import argparse
import csv
from rdkit import Chem

def parse_csv(csv_path):
    """
    Parse a CSV file containing energy values.
    Returns a list of dictionaries with molecule names and energy values.
    """
    energies = []
    with open(csv_path, mode='r') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            energies.append({
                "name": row["mol"],  # Assuming molecule names match
                "energy_hartree": float(row["ANI_energy(hartree)"]),
                "energy_kcal": float(row["ANI_energy(kcal/mol)"])
            })
    return energies


def process_sdf(sdf_path, energies, output_path, num_conformations):
    """
    Process an SDF file, attach energy values, and save the lowest-energy conformations.
    """
    supplier = Chem.SDMolSupplier(sdf_path, removeHs=False)  # Preserve explicit hydrogens
    molecules = []

    for mol, energy in zip(supplier, energies):
        if mol is None:
            continue
#        mol = Chem.AddHs(mol)  # Ensure hydrogens are added
        mol.SetProp("ANI_energy(hartree)", str(energy["energy_hartree"]))
        mol.SetProp("ANI_energy(kcal/mol)", str(energy["energy_kcal"]))
        molecules.append((mol, energy["energy_kcal"]))

    # Sort by energy
    molecules.sort(key=lambda x: x[1])

    # Select top conformations
    top_molecules = molecules[:num_conformations]

    # Write to output
    writer = Chem.SDWriter(output_path)
    for mol, _ in top_molecules:
        writer.write(mol)
    writer.close()

    print(f"Top {num_conformations} conformations saved to {output_path}")


def main():
    parser = argparse.ArgumentParser(
        description="Extract the lowest-energy conformations from an SDF file using energy values from a CSV file."
    )
    parser.add_argument('-s', '--sdf', required=True, help="Path to the input SDF file")
    parser.add_argument('-c', '--csv', required=True, help="Path to the CSV file with energy values")
    parser.add_argument('-o', '--output', required=True, help="Path to the output SDF file")
    parser.add_argument('-n', '--num', type=int, default=3, help="Number of lowest-energy conformations to extract (default: 3)")
    args = parser.parse_args()

    # Load energy data
    energies = parse_csv(args.csv)

    # Process SDF and save output
    process_sdf(args.sdf, energies, args.output, args.num)


if __name__ == "__main__":
    main()

