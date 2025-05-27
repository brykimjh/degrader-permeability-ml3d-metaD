import os

ml_models_dir = "outputs/ml_models"
pbs_list_path = f"{ml_models_dir}/pbs_job_list.txt"

CC = f'''\
cp scripts/ml_models/* {ml_models_dir}
cd {ml_models_dir}
python get_3d_properties.py
rm -rf outputs pbs_jobs
mkdir outputs
python generate_pbs_jobs.py
'''
print(CC)
os.system(CC)

try:
    with open(pbs_list_path, "r") as f:
        job_names = [line.strip() for line in f if line.strip()]

    print("Jobs listed in pbs_job_list.txt:")
    for name in job_names:
        print(name)
        dir0 = f' outputs/{name}'
        pbs0 = f'{name}.pbs'

        CC = f'''\
        cd {ml_models_dir}
        rm -rf {dir0}
        mkdir {dir0}
        mv pbs_jobs/{pbs0} {dir0}/submit.pbs
        cd {dir0}
        qsub submit.pbs
        '''
        print(CC)
        os.system(CC)


except FileNotFoundError:
    print(f"Error: File '{pbs_list_path}' not found.")

CC = f'''\
rm -rf pbs_jobs
'''
print(CC)
os.system(CC)

