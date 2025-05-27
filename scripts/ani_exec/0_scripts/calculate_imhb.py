import argparse
from schrodinger import structure
from schrodinger.structutils.interactions import hbond
import csv

def calculate_imhb(sdf_path):
    """
    Calculate intramolecular hydrogen bonds (IMHB) for each conformation in the input SDF file.
    """
    imhb_data = []  # List to store IMHB results for each conformation
    
    # Read conformations from the SDF file
    for conf_id, conf in enumerate(structure.StructureReader(sdf_path), start=1):
        # Identify hydrogen bonds
        hbonds = hbond.get_hydrogen_bonds(conf)
        
        # Filter for intramolecular hydrogen bonds
        imhb_pairs = [
            (hb[0].index, hb[1].index) 
            for hb in hbonds 
            if conf.atom[hb[0].index].molecule_number == conf.atom[hb[1].index].molecule_number
        ]
        
        # Store the results for this conformation
        imhb_data.append({
            'conf_id': conf_id,
            'num_imhb': len(imhb_pairs),
            'imhb_pairs': imhb_pairs
        })
    
    return imhb_data

def save_results(output_path, results):
    """
    Save IMHB results to a CSV file.
    """
    with open(output_path, mode='w', newline='') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(['Conformation_ID', 'Num_IMHB', 'IMHB_Pairs'])  # Header
        for result in results:
            writer.writerow([result['conf_id'], result['num_imhb'], result['imhb_pairs']])

def main():
    # Parse command-line arguments
    parser = argparse.ArgumentParser(description="Calculate intramolecular hydrogen bonds (IMHB) from an SDF file.")
    parser.add_argument('-i', '--input', required=True, help="Path to the input SDF file")
    parser.add_argument('-o', '--output', required=True, help="Path to the output CSV file")
    args = parser.parse_args()

    # Calculate IMHB
    results = calculate_imhb(args.input)

    # Save results to the specified output file
    save_results(args.output, results)

    print(f"IMHB calculation completed. Results saved to {args.output}")

if __name__ == "__main__":
    main()

