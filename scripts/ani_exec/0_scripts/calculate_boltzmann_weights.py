import pandas as pd
import numpy as np
import argparse

# Constants
T = 298  # Temperature in Kelvin
k_B = 0.001987204259  # Boltzmann constant in kcal/(mol·K)
beta = 1 / (k_B * T)

# Parse command-line arguments
parser = argparse.ArgumentParser(description="Calculate Boltzmann weights from energy data.")
parser.add_argument("-i", "--input", required=True, help="Path to the input CSV file containing energy data.")
parser.add_argument("-o", "--output", required=True, help="Path to the output CSV file to save results.")
args = parser.parse_args()

# File paths
input_file = args.input  # Input CSV file
output_file = args.output  # Output CSV file

# Read energy data
energy_df = pd.read_csv(input_file)

# Extract energies (in kcal/mol)
energies = energy_df['ANI_energy(kcal/mol)'].values

# Apply energy shift to prevent overflow
min_energy = np.min(energies)
shifted_energies = energies - min_energy

# Calculate Boltzmann factors
boltzmann_factors = np.exp(-beta * shifted_energies)

# Normalize to get weights
partition_function = np.sum(boltzmann_factors)
boltzmann_weights = boltzmann_factors / partition_function

# Add Boltzmann weights to the dataframe
energy_df['Boltzmann Weight'] = boltzmann_weights

# Save results to a CSV file
energy_df.to_csv(output_file, index=False)

print(f"Boltzmann weights saved to {output_file}")

