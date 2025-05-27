from rdkit import Chem

def process_pdb_frames(pdb_file, output_sdf):
    with open(pdb_file, 'r') as file:
        lines = file.readlines()
    
    frames = []
    current_frame = []
    
    for line in lines:
        if line.startswith("END") or line.startswith("ENDMDL"):  # Marks end of a frame
            if current_frame:
                frames.append(current_frame)
                current_frame = []
        else:
            current_frame.append(line)
    
    # Catch last frame if no END is present
    if current_frame:
        frames.append(current_frame)
    
    print(f"Total configurations found: {len(frames)}")
    
    # Write each frame to an SDF
    writer = Chem.SDWriter(output_sdf)
    for i, frame in enumerate(frames):
        pdb_string = "".join(frame)
        mol = Chem.MolFromPDBBlock(pdb_string, removeHs=False)
        if mol is not None:
            writer.write(mol)
        else:
            print(f"Skipping frame {i+1}: Invalid molecule.")
    
    writer.close()
    print(f"All configurations processed. Output written to {output_sdf}")

# Usage
process_pdb_frames('frames.pdb', 'output.sdf')

