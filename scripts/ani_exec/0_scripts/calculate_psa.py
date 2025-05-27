import csv
import argparse
from schrodinger import structure
from schrodinger.structutils.analyze import calculate_sasa_by_atom

# Parse command-line arguments
parser = argparse.ArgumentParser(description="Calculate Polar Surface Area (PSA) from an SDF file.")
parser.add_argument("-i", "--input", required=True, help="Path to the input SDF file.")
parser.add_argument("-o", "--output", required=True, help="Path to the output CSV file.")
args = parser.parse_args()

# Input and output file paths
input_file = args.input  # SDF file
output_file = args.output  # Output CSV file

# Atomic numbers for polar atoms
polar_atoms = [7, 8]  # Nitrogen (N) and Oxygen (O)

# Open the SDF file and process conformations
with open(output_file, "w", newline="") as csvfile:
    csv_writer = csv.writer(csvfile)
    csv_writer.writerow(["Conformation_ID", "PSA"])  # Write header

    # Process each conformation in the SDF file
    for conf_id, conf in enumerate(structure.StructureReader(input_file), start=1):
        polar_atom_ids = [atom.index for atom in conf.atom if atom.atomic_number in polar_atoms]

        # Add hydrogens bonded to polar atoms
        for atom in conf.atom:
            if atom.atomic_number == 1:  # Hydrogen
                bonded_atoms = [bond.atom1 if bond.atom2 == atom else bond.atom2 for bond in atom.bond]
                if any(ba.atomic_number in polar_atoms for ba in bonded_atoms):
                    polar_atom_ids.append(atom.index)

        # Calculate PSA for the selected atoms
        psa_values = calculate_sasa_by_atom(conf, atoms=polar_atom_ids)
        total_psa = sum(psa_values)

        # Write the results
        csv_writer.writerow([conf_id, f"{total_psa:.2f}"])

print(f"PSA calculation completed! Results saved to {output_file}")

