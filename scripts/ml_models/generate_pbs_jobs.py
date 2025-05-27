import os

models = ["rf", "svr", "pls"]
features = ["2d", "3d", "combined"]
scrambled_opts = [False, True]

template_path = "model_template.pbs"
output_dir = "pbs_jobs"
pbs_list_path = "pbs_job_list.txt"

os.makedirs(output_dir, exist_ok=True)

with open(template_path, "r") as f:
    template = f.read()

job_names = []

for model in models:
    for feat in features:
        for scrambled in scrambled_opts:
            job_name = f"{model}_{feat}"
            if scrambled:
                job_name += "_scrambled"

            job_file = os.path.join(output_dir, f"{job_name}.pbs")

            replaced = (
                template.replace("__MODEL__", model)
                        .replace("__FEATURES__", feat)
                        .replace("__SCRAMBLED__", str(scrambled))
                        .replace("__JOB_NAME__", job_name)
            )

            with open(job_file, "w") as jf:
                jf.write(replaced)

            job_names.append(job_name)

# Save only job names (not paths) to list
with open(pbs_list_path, "w") as f:
    for name in job_names:
        f.write(name + "\n")

print(f"Generated {len(job_names)} PBS job files in: {output_dir}")
print(f"Saved job names to: {pbs_list_path}")

