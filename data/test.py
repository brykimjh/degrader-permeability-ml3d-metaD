import pandas as pd
from rdkit import Chem
from rdkit.Chem import Descriptors
import argparse
from rdkit import RDLogger

# ====================
# Optional: Disable RDKit warnings
# ====================
RDLogger.DisableLog('rdApp.*')

# ====================
# Dynamically load ALL RDKit descriptors
# ====================

descriptor_list = Descriptors.descList  # List of (name, function) pairs
descriptor_names = [name for name, func in descriptor_list]
descriptor_functions = {name: func for name, func in descriptor_list}

def calculate_all_descriptors(smiles):
    mol = Chem.MolFromSmiles(smiles)
    if mol is None:
        return {name: None for name in descriptor_names}

    result = {}
    for name, func in descriptor_functions.items():
        try:
            value = func(mol)
        except:
            value = None  # Some descriptors can fail
        result[name] = value
    return result

def clean_descriptors(df):
    """Remove constant and NaN columns."""
    # Drop constant columns
    nunique = df.nunique()
    constant_cols = nunique[nunique <= 1].index
    df_clean = df.drop(columns=constant_cols)

    # Drop columns with any NaN
    df_clean = df_clean.dropna(axis=1)

    return df_clean

def main():
    parser = argparse.ArgumentParser(description="Calculate all RDKit molecular descriptors from a CSV with a 'Smiles' column.")
    parser.add_argument("input_file", help="Path to the input CSV file with 'Smiles' column.")
    parser.add_argument("output_file", help="Path to the output CSV file.")
    args = parser.parse_args()

    smiles_df = pd.read_csv(args.input_file)

    if "Smiles" not in smiles_df.columns:
        raise ValueError("Input file must contain a column named 'Smiles'.")

    # Calculate descriptors
    descriptor_df = smiles_df["Smiles"].apply(calculate_all_descriptors).apply(pd.Series)

    # Clean descriptors
    descriptor_df_clean = clean_descriptors(descriptor_df)

    # Merge descriptors with original smiles
    result_df = pd.concat([smiles_df, descriptor_df_clean], axis=1)

    result_df.to_csv(args.output_file, index=False)
    print(f"✅ Molecular descriptors saved to {args.output_file}")
    print(f"🧹 Cleaned: Dropped {descriptor_df.shape[1] - descriptor_df_clean.shape[1]} constant/NaN descriptors.")

if __name__ == "__main__":
    main()

