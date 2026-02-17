import pandas as pd

# ---- Input files ----
file_2d = "../../data/2d_features.csv"
file_3d = "3d_features.csv"

# ---- Output file ----
outfile = "new_unknowns.csv"

# ----------------------

# Load
df_2d = pd.read_csv(file_2d)
df_3d = pd.read_csv(file_3d)

# Merge on Index
df = df_2d.merge(df_3d, on="Index", how="inner")

# Drop columns not needed for prediction
cols_to_drop = [
    "Index",
    "Compound",
    "Smiles",
    "P_app AB (nm/s)",
    "P_app BA (nm/s)",
    "P_app"
]

df = df.drop(columns=[c for c in cols_to_drop if c in df.columns])

# Save
df.to_csv(outfile, index=False)

print(f"Saved {outfile}")
