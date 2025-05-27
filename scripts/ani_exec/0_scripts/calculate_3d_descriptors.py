import pandas as pd
from rdkit import Chem
from rdkit.Chem import Descriptors3D
import argparse

DESCRIPTOR_FAIL_VALUE = -1  # Default value for failed descriptor calculations

def calculate_3D_descriptors(mol):
    """
    Calculate all 3D descriptors for a given molecule.
    Returns a list of descriptor values or fail values if the calculation fails.
    """
    if mol is None:
        return [DESCRIPTOR_FAIL_VALUE] * len(descriptor3D_names)
    descriptor_values = []
    for desc_name in descriptor3D_names:
        desc_func = getattr(Descriptors3D, desc_name, None)
        if desc_func:
            try:
                descriptor_values.append(desc_func(mol))
            except:
                descriptor_values.append(DESCRIPTOR_FAIL_VALUE)
    return descriptor_values

# Get the list of all available 3D descriptors in RDKit
descriptor3D_names = [
    desc for desc in dir(Descriptors3D)
    if callable(getattr(Descriptors3D, desc)) and not desc.startswith("__")
]

def main():
    # Parse command-line arguments
    parser = argparse.ArgumentParser(description="Calculate 3D descriptors from an SDF file and save to CSV.")
    parser.add_argument("-i", "--input", required=True, help="Path to the input SDF file.")
    parser.add_argument("-o", "--output", required=True, help="Path to the output CSV file.")
    args = parser.parse_args()

    # Load molecules from the SDF file
    supplier = Chem.SDMolSupplier(args.input, sanitize=False)
    molecules_data = []

    print(f"Calculating 3D descriptors for molecules in {args.input}...")

    # Process each molecule and calculate descriptors
    molecule_names = []
    for mol in supplier:
        if mol is not None:
            try:
                Chem.SanitizeMol(mol)
                descriptors = calculate_3D_descriptors(mol)
                molecule_names.append(mol.GetProp("_Name") if mol.HasProp("_Name") else "N/A")
                molecules_data.append(descriptors)
            except Exception as e:
                print(f"Error processing a molecule: {e}")
                molecule_names.append("Failed")
                molecules_data.append([DESCRIPTOR_FAIL_VALUE] * len(descriptor3D_names))

    # Save results to a DataFrame
    descriptor_df = pd.DataFrame(molecules_data, columns=descriptor3D_names)
    descriptor_df.insert(0, "Molecule_Name", molecule_names)
    
    # Write the results to a CSV file
    descriptor_df.to_csv(args.output, index=False)
    print(f"Saved 3D descriptors to {args.output}")

if __name__ == "__main__":
    main()

