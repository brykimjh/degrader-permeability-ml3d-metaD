import pandas as pd
import argparse

# Parse command-line arguments
parser = argparse.ArgumentParser(description="Calculate the ensemble average of a specified property using Boltzmann weights.")
parser.add_argument("-w", "--weights", required=True, help="Path to the input CSV file containing Boltzmann weights.")
parser.add_argument("-p", "--properties", required=True, help="Path to the input CSV file containing property values.")
parser.add_argument("-o", "--output", required=True, help="Path to the output text file to save the ensemble average.")
parser.add_argument("-c", "--column", required=True, help="The name of the property column to weight (e.g., PSA, energy).")
args = parser.parse_args()

# Input and output files
weights_file = args.weights  # File with Boltzmann weights
properties_file = args.properties  # File with property values
output_file = args.output  # Output file
property_column = args.column  # Column name of the property to weight

# Read data
weights_df = pd.read_csv(weights_file)
properties_df = pd.read_csv(properties_file)

# Check lengths match
if len(weights_df) != len(properties_df):
    raise ValueError("Mismatch in number of conformations between weights and properties files")

# Align property values with weights by order
if property_column not in properties_df.columns:
    raise ValueError(f"The specified column '{property_column}' does not exist in the properties file")

properties_df['Boltzmann Weight'] = weights_df['Boltzmann Weight'].values

# Calculate weighted property values
properties_df['Weighted Property'] = properties_df['Boltzmann Weight'] * properties_df[property_column]

# Calculate ensemble average of the property
ensemble_avg = properties_df['Weighted Property'].sum()

# Save ensemble average to a text file
with open(output_file, 'w') as f:
    f.write(f"Ensemble_Average_{property_column}: {ensemble_avg:.2f}\n")

print(f"Ensemble_Average_{property_column}: {ensemble_avg:.2f}")
print(f"Results saved to {output_file}")

