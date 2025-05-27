# degrader-permeability-ml3d-metaD

This repository provides a modular pipeline for predicting passive permeability of bifunctional degraders using a combination of 2D and 3D molecular descriptors. It integrates conformational sampling (via metadynamics), descriptor extraction (including ANI-based quantum descriptors), and supervised machine learning classification. The full workflow is automated and includes molecular preparation, force field generation, metadynamics simulation, descriptor extraction, dataset assembly, and model training.

---

## 📁 DProject Structure

```
degrader-permeability-ml3d-metaD/
├── 01_run_forcefield.py              # Step 1: Launch force field jobs
├── 02_run_metadynamics.py           # Step 2: Launch WT-MetaD simulations
├── 03_run_trajectory_processing.py  # Step 3: Extract ligand-only SDF
├── 04_run_ani_exec.py               # Step 4: Run ANI-based descriptor jobs
├── 05_run_ml_models.py              # Step 5: Generate datasets & train models
├── data/                            # Input molecular data and descriptor scripts
│   ├── 2d_features.csv              # Computed 2D descriptors
│   ├── calculate_2d_properties.py   # Script to generate 2D descriptors
│   ├── mol_1.pdb                    # Protonated 3D structure
│   └── mol_data.csv                 # Metadata (optional)
├── README.md                        # Documentation
├── reset.sh                         # Cleanup script
└── scripts/                         # Modular workflow components
    ├── ani_exec/                    # ANI-based descriptor workflow
    │   ├── 0_scripts/
    │   │   ├── ani_job_setup.py
    │   │   ├── calculate_3d_descriptors.py
    │   │   ├── calculate_boltzmann_weights.py
    │   │   ├── calculate_ensemble_avg.py
    │   │   ├── calculate_imhb.py
    │   │   ├── calculate_psa.py
    │   │   ├── concatenate_sdf.sh
    │   │   ├── extract_lowest_energy.py
    │   │   ├── run_ani_batch.sh
    │   │   └── template_submit_array.pbs
    │   └── ani/
    │       ├── prep.sh
    │       ├── run_ani.sh
    │       └── submit_ani.pbs
    ├── forcefield/                  # AMBER parameterization workflow
    │   ├── 01_copy_input_files.sh
    │   ├── 02_generate_gasteiger_charges.sh
    │   ├── 03_organize_antechamber_files.sh
    │   ├── 04_compute_total_charge.sh
    │   ├── 05_run_antechamber_with_total_charge.sh
    │   ├── 06_generate_amber_inputs.sh
    │   └── submit.pbs
    ├── metadynamics/                # Metadynamics job templates
    │   ├── 01run.sh
    │   ├── min.in
    │   ├── plumed.dat
    │   └── submit.pbs
    ├── ml_models/                   # ML pipeline components
    │   ├── generate_ml_datasets.py
    │   ├── get_3d_properties.py
    │   ├── run_all_models.sh
    │   └── run_model.py
    └── trajectory_processing/       # Post-MetaD ligand cleanup
        ├── env_modules.txt
        ├── extract_sdf_from_md.sh
        └── frames_to_sdf.py

```

---

## 🧪 Input Data

- `mol_data.csv`: Primary input file containing SMILES strings and any associated compound metadata.
- `calculate_2d_properties.py`: Python script that computes 2D molecular descriptors using RDKit from `mol_data.csv`. Run with:

  ```bash
  python calculate_2d_properties.py mol_data.csv 2d_features.csv
  ```

- `2d_features.csv`: Generated 2D descriptor table (used in downstream ML modeling).
- `mol_1.pdb`: Example protonated 3D structure, prepared externally (e.g., Schrödinger Epik at pH 7.4). These serve as input for force field parameterization and metadynamics setup.

---

## ⚙️ Step 1: Force Field Generation (AMBER)

⚠️ **Note:** You must manually edit the `submit.pbs` file in `scripts/forcefield/` to match your HPC environment (e.g., job name, queue, and modules).

To generate AMBER-compatible force field parameters for all molecules:

```bash
python 01_run_forcefield.py
```

This script:

- Copies a self-contained job template (from `scripts/forcefield/`) to a new directory for each molecule
- Replaces placeholders (e.g., `mol_INDEX`) in the job script (`submit.pbs`)
- Submits the job using `qsub` on your HPC system

Each job executes the following scripts in order:

1. **Ligand Extraction** – `01_copy_input_files.sh`: Copies the input `.pdb` file and sets up the molecule-specific directory  
2. **Gasteiger Charge Calculation** – `02_generate_gasteiger_charges.sh`: Uses Antechamber for initial charge estimation  
3. **Intermediate File Organization** – `03_organize_antechamber_files.sh`: Prepares inputs for total charge calculation  
4. **Charge Validation** – `04_compute_total_charge.sh`: Computes and logs total molecular charge for later use  
5. **AM1-BCC Charge Assignment** – `05_run_antechamber_with_total_charge.sh`: Reruns Antechamber with specified total charge  
6. **Topology Building** – `06_generate_amber_inputs.sh`: Generates AMBER-compatible topology (`.prmtop`) and coordinate (`.inpcrd`) files using `tleap`

---

## 🔄 Step 2: Metadynamics Simulation (External)

After generating force field parameters, metadynamics simulations are performed externally using AMBER and PLUMED (e.g., on AWS cloud infrastructure).

The following files are transferred from each `outputs/forcefield/mol_X/` directory:

- `system_1.prmtop`
- `system_1.inpcrd`
- `system_1.frcmod`
- `system_1.mol2`
- `natoms.txt`
- `total_charge.txt`

Metadynamics jobs are launched using:

```bash
python run_metadynamics.py
```

Each job directory is initialized from `scripts/metadynamics/` and includes:

- `01run.sh`: Full metadynamics workflow including tleap, minimization, simulated annealing, and equilibration
- `plumed.dat`: Defines the radius of gyration (Rgyr) as the collective variable
- `submit.pbs`: Submission script for qsub, with job name customized per molecule

**WTMetaD Parameters**:
- CV: Radius of gyration (Rgyr)
- Temperature: 300 K
- Hill Height: 1.2 kcal/mol
- Hill Sigma: 0.1 Å
- Bias Factor: 6
- Pace: 500 steps

Trajectory files are saved and postprocessed using cpptraj.

### ⚠️ Notes for Users

- You **must manually edit** the `submit.pbs` file in both `scripts/forcefield/` and `scripts/metadynamics/` to suit your compute environment (e.g., queue names, resources, and module loads).
- If you are using PLUMED and it is not on your system path, ensure it is properly referenced. For example, the following may be necessary in `01run.sh`:

```bash
unset LD_LIBRARY_PATH
export LD_LIBRARY_PATH=$LD_LIBRARY_PATH:/home/YOUR_USERNAME/.conda/envs/lapack_env/lib
```

---

## 📊 Step 3: Trajectory Processing (Extract SDF from MetaD)

After metadynamics simulations are complete, we extract ligand-only structures and convert them to `.sdf` files for descriptor calculations.

Run:

```bash
python run_trajectory_processing.py
```

This script does the following for each molecule:

- Creates a new folder in `outputs/trajectory_processing/mol_X/`
- Copies in the trajectory processing template from `scripts/trajectory_processing/`
- Loads the `system_2.pdb` and `system_2.prmtop` from `outputs/metadynamics/mol_X/`
- Dynamically generates an `amber_script.in` file to extract ligand-only trajectory (`frames.pdb`)
- Converts the resulting `frames.pdb` into `output.sdf` using RDKit

You will find the final SDF file here:

```
outputs/trajectory_processing/mol_X/output.sdf
```

These are used as input for ANI-based 3D descriptor extraction in the next step.

### ⚠️ Notes for Users

- Ensure you have `cpptraj` and `RDKit` installed and available in your environment.
- If `cpptraj` requires additional shared libraries (e.g., LAPACK, OpenBLAS) that are not in standard system paths, you may need to manually set `LD_LIBRARY_PATH` in `extract_sdf_from_md.sh`. For example:

  ```bash
  export LD_LIBRARY_PATH=$LD_LIBRARY_PATH:/home/your_user/.conda/envs/your_env/lib
  ```
---

## 🥚 Step 4: ANI-Based Descriptor Execution

To perform ANI energy minimization and descriptor calculations using the `.sdf` files generated above:

```bash
python run_ani_exec.py 1  # Step 1: Setup and submit jobs
python run_ani_exec.py 2  # Step 2: Run descriptor property extraction
```

This will:

- Copy `scripts/ani_exec/` into a new `outputs/ani_exec/mol_X/` directory
- Replace solvent placeholders in PBS templates
- Run `prep.sh` with your configuration (`output.sdf`, frame count, jobs)
- Submit ANI property extraction jobs to your cluster

All scripts are portable and modular to work per molecule.

### ⚠️ Notes for Users

- You **must manually edit** the following PBS submission templates:

  - `scripts/ani_exec/ani/submit_ani.pbs`
  - `scripts/ani_exec/0_scripts/template_submit_array.pbs`

  Make sure they reflect your cluster's queue, module environment, and conda setup.

- RDKit, OpenEye, and Schrödinger modules must be available and configured properly.

- Check `env_modules.txt` in `scripts/ani_exec/` for example module loads.

- Verify that the `run_ani_batch.sh` script points to the correct path for `run_ANI.py`:

  ```bash
  ANI_PYTHON_SCRIPT="/SFS/project/kw/kimbry/rklake/smiles_to_ff/git/mrl-mi-ssf-torchani/scripts/run_ANI.py"
  ```

  If you move or clone the repo elsewhere, this path must be updated manually.

---

## 🧱 Step 5: Machine Learning Model Generation

After calculating both 2D and 3D descriptors, we build classification models to predict passive permeability classes (Low, Moderate, High).

### 🎓 Descriptor and Target Dataset Generation
To assemble the final input datasets for machine learning, run:

```bash
python run_ml_models.py
```

This will:
- Copy all scripts from `scripts/ml_models/` to `outputs/ml_models/`
- Execute `get_3d_properties.py` to collect ANI-derived 3D descriptors from each molecule folder
- Run `generate_ml_datasets.py` to merge 2D and 3D descriptors and perform k-means classification on −log(Papp)
- Create and save the following dataset variants:
  - `datasets_classified/`: 2D-only, 3D-only, and combined descriptors, each labeled with class index (target = 0, 1, 2)
  - `datasets_papp/`: 2D-only and combined descriptors using raw Papp values as the target
  - `datasets_neglog/`: 2D-only and combined descriptors using −log(Papp) as the target
  - `datasets_full/`: Combined descriptors with all original metadata (Index, Compound, Smiles, Papp, −log(Papp), class index, and label)

Each variant includes properly aligned descriptors and targets for modeling.

### 🎯 Model Training and Evaluation

Once datasets are generated, the following command trains models:

```bash
bash run_all_models.sh
```

This script:
- Trains a model using `run_model.py` for each `*_classified.csv` file
- Uses Random Forest with:
  - 5-fold cross-validation
  - Feature selection via ANOVA F-score (`SelectKBest`)
  - Top-k features specified per dataset
- Logs the following to `outputs/ml_models/model_outputs/`:
  - Model parameters (folds, seed, feature count)
  - Accuracy metrics (mean and std of CV accuracy)
  - CV predictions per fold
  - Feature importance rankings
  - Trained model (`.joblib` format)

### ⚠️ Notes for Users
- Ensure descriptor generation steps (1–4) are completed first.
- Targets are created via k-means clustering on −log(Papp) to assign Low, Moderate, and High labels.
- You may customize seeds, folds, or feature count (`k`) in `run_all_models.sh`.

The machine learning workflow is fully automated and integrates directly with the descriptor generation pipeline.

---

