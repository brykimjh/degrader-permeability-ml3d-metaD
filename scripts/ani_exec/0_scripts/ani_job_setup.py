import os
import math
import argparse
from rdkit import Chem

def split_sdf(input_file, output_dir, chunk_size):
    # Check if output directory exists, create it if not
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    # Read the input SDF
    supplier = Chem.SDMolSupplier(input_file, removeHs=False)
    if not supplier:
        raise ValueError(f"Failed to read the input SDF file: {input_file}")

    # Split the file
    current_chunk = []
    chunk_count = 0

    for i, mol in enumerate(supplier):
        if mol is None:
            continue  # Skip invalid molecules

        current_chunk.append(mol)

        # Write to a new file when the chunk size is reached
        if len(current_chunk) == chunk_size:
            chunk_dir = os.path.join(output_dir, f"chunk_{chunk_count + 1}")
            os.makedirs(chunk_dir, exist_ok=True)

            output_file = os.path.join(chunk_dir, f"chunk_{chunk_count + 1}.sdf")
            writer = Chem.SDWriter(output_file)
            for m in current_chunk:
                writer.write(m)
            writer.close()

            current_chunk = []
            chunk_count += 1

    # Write any remaining molecules to a final chunk
    if current_chunk:
        chunk_dir = os.path.join(output_dir, f"chunk_{chunk_count + 1}")
        os.makedirs(chunk_dir, exist_ok=True)

        output_file = os.path.join(chunk_dir, f"chunk_{chunk_count + 1}.sdf")
        writer = Chem.SDWriter(output_file)
        for m in current_chunk:
            writer.write(m)
        writer.close()

    print(f"SDF split into {chunk_count} files in separate directories under: {output_dir}")
    return chunk_count

def setup_jobs(solvent, total_configurations, chunk_size, sdf_file, files_dir, template_pbs):
    # Calculate number of jobs
    num_jobs = math.ceil(total_configurations / chunk_size)
    
    # Directory structure setup
    chunks_dir = os.path.join(files_dir, "chunks")
    jobs_dir = os.path.join(files_dir, "jobs")
    os.makedirs(chunks_dir, exist_ok=True)
    os.makedirs(jobs_dir, exist_ok=True)
    os.makedirs(os.path.join(files_dir, "sdf"), exist_ok=True)
    os.makedirs(os.path.join(files_dir, "csv"), exist_ok=True)

    # Split SDF into chunks
    chunk_count = split_sdf(sdf_file, chunks_dir, chunk_size)

    # Generate PBS job file
    pbs_output_path = os.path.join(jobs_dir, "submit_array.pbs")
    with open(template_pbs, "r") as template, open(pbs_output_path, "w") as output:
        for line in template:
            output.write(line.replace("ANI2x_SOLVENT", f"{solvent}"))

    # Generate runs.txt
    runs_txt_path = os.path.join(files_dir, "runs.txt")
    with open(runs_txt_path, "w") as runs_file:
        for i in range(chunk_count):
            chunk_path = f"chunks/chunk_{i + 1}/chunk_{i + 1}.sdf"
            runs_file.write(f"{chunk_path}\n")

    # Submit jobs
    job_array_command = f"cd {jobs_dir} && qsub -J 1-{chunk_count} submit_array.pbs"
    os.system(job_array_command)

    print(f"Setup complete for solvent '{solvent}'. Generated {chunk_count} jobs with chunk size {chunk_size}.")

def main():
    parser = argparse.ArgumentParser(description="Set up and submit jobs for ANI computation.")
    parser.add_argument("solvent", type=str, help="Solvent type (e.g., chloroform, water).")
    parser.add_argument("sdf_file", type=str, help="Path to the input SDF file.")
    parser.add_argument("total_configurations", type=int, help="Total number of configurations (required).")
    parser.add_argument("chunk_size", type=int, help="Number of configurations per chunk (required).")
    parser.add_argument("files_dir", type=str, help="Base directory for generated files.")
    parser.add_argument("template_pbs", type=str, help="Path to the PBS template file.")

    args = parser.parse_args()

    setup_jobs(args.solvent, args.total_configurations, args.chunk_size, args.sdf_file, args.files_dir, args.template_pbs)

if __name__ == "__main__":
    main()

