import pandas as pd
from rdkit import Chem
from rdkit.Chem import Descriptors
from rdkit.Chem import rdMolDescriptors
from rdkit.Chem import AllChem
import argparse

# Define the desired properties and their corresponding RDKit descriptor functions
descriptor_functions = {
    "MolecularWeight": Descriptors.MolWt,
    "ExactMass": Descriptors.ExactMolWt,
    "XLogP3": Descriptors.MolLogP,
    "HeavyAtomCount": Descriptors.HeavyAtomCount,
    "RingCount": Descriptors.RingCount,
    "HydrogenBondAcceptorCount": Descriptors.NumHAcceptors,
    "HydrogenBondDonorCount": Descriptors.NumHDonors,
    "RotatableBondCount": Descriptors.NumRotatableBonds,
    "TopologicalPolarSurfaceArea": Descriptors.TPSA,
    "FractionCSP3": lambda mol: Descriptors.FractionCSP3(mol),
    "NumStereoCenters": lambda mol: Chem.FindMolChiralCenters(mol, includeUnassigned=True)
}

def calculate_tnsa(mol):
    """Calculate Total Non-Polar Surface Area (TNSA)."""
    tpsa = rdMolDescriptors.CalcTPSA(mol)
    total_surface_area = sum(20 if atom.GetAtomicNum() == 6 else 0 for atom in mol.GetAtoms())
    tnsa = total_surface_area - tpsa
    return max(tnsa, 0)

def calculate_charvol(mol):
    """Calculate Characteristic Volume (CharVol)."""
    mol = Chem.AddHs(mol)
    AllChem.EmbedMolecule(mol)
    try:
        return AllChem.ComputeMolVolume(mol)
    except:
        return None

def calculate_properties(smiles):
    mol = Chem.MolFromSmiles(smiles)
    if mol is None:
        return {key: None for key in descriptor_functions.keys()}
    result = {key: func(mol) for key, func in descriptor_functions.items()}
    result["NumStereoCenters"] = len(result["NumStereoCenters"])
    result["AllBonds"] = mol.GetNumBonds()
    result["RingAtoms"] = sum(len(ring) for ring in mol.GetRingInfo().AtomRings())
    result["Halogens"] = sum(1 for atom in mol.GetAtoms() if atom.GetAtomicNum() in [9, 17, 35, 53])
    result["HeteroAtoms"] = sum(1 for atom in mol.GetAtoms() if atom.GetAtomicNum() not in [1, 6])
    result["TNSA"] = calculate_tnsa(mol)
    result["CharVol"] = calculate_charvol(mol)
    result["SizeShape"] = result["AllBonds"] + result["RingAtoms"]
    try:
        result["Flexibility"] = result["RotatableBondCount"] / result["AllBonds"] if result["AllBonds"] > 0 else None
    except ZeroDivisionError:
        result["Flexibility"] = None

    return {
        "Molecular Weight (MW)": result.get("MolecularWeight"),
        "CharVol (characteristic volume)": result.get("CharVol"),
        "Flexibility (number of rotatable bonds / number of bonds)": result.get("Flexibility"),
        "Number of Heavy Atoms (HA)": result.get("HeavyAtomCount"),
        "RingAtoms": result.get("RingAtoms"),
        "Halogens": result.get("Halogens"),
        "HeteroAtoms": result.get("HeteroAtoms"),
        "RotBonds (NRotB)": result.get("RotatableBondCount"),
        "AllBonds": result.get("AllBonds"),
        "RingCount": result.get("RingCount"),
        "NumStereo": result.get("NumStereoCenters"),
        "Fraction of sp3 Carbon Atoms (FSP3)": result.get("FractionCSP3"),
        "Hydrogen Bond Donors (HBD)": result.get("HydrogenBondDonorCount"),
        "Hydrogen Bond Acceptors (HBA)": result.get("HydrogenBondAcceptorCount"),
        "cLogD^7.4": result.get("XLogP3"),
        "Topological polar surface area (TPSA)": result.get("TopologicalPolarSurfaceArea"),
        "Total non-polar surface area (TNSA)": result.get("TNSA"),
    }

def main():
    parser = argparse.ArgumentParser(description="Calculate molecular properties from a CSV with a 'Smiles' column.")
    parser.add_argument("input_file", help="Path to the input CSV file with 'Smiles' column.")
    parser.add_argument("output_file", help="Path to the output CSV file.")
    args = parser.parse_args()

    smiles_df = pd.read_csv(args.input_file)

    if "Smiles" not in smiles_df.columns:
        raise ValueError("Input file must contain a column named 'Smiles'.")

    smiles_df = smiles_df.assign(**smiles_df["Smiles"].apply(calculate_properties).apply(pd.Series))
    smiles_df.to_csv(args.output_file, index=False)
    print(f"Molecular properties saved to {args.output_file}")

if __name__ == "__main__":
    main()

