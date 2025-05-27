#!/bin/bash

number=$(cat natoms.txt)
sed -i "s/NATOMS/${number}/g" plumed.dat

############
# SYSTEM-1 #
############

unset LD_LIBRARY_PATH
export LD_LIBRARY_PATH=$LD_LIBRARY_PATH:/home/kimbry/.conda/envs/lapack_env/lib

stem_1="system_1"

############
# SYSTEM-2 #
############

stem_2="system_2"
cat <<EOF > leap_${stem_2}.in
source leaprc.protein.ff14SB
source leaprc.gaff2
source leaprc.water.tip3p

loadamberparams ${stem_1}.frcmod
loadamberparams frcmod.chcl3

mol = loadmol2 ${stem_1}.mol2

solvateBox mol CHCL3BOX 10.0

addIons2 mol Na+ 0  # Add enough sodium ions to neutralize the system
addIons2 mol Cl- 0  # Add enough chloride ions to neutralize, if needed

saveamberparm mol ${stem_2}.prmtop ${stem_2}.inpcrd
savepdb mol ${stem_2}.pdb
savemol2 mol ${stem_2}.mol2 1
quit
EOF
tleap -f "leap_${stem_2}.in"

pmemd.cuda -AllowSmallBox -O -i min.in -o min.out -p ${stem_2}.prmtop -c ${stem_2}.inpcrd -r min.rst -x md.nc -inf md.info 2>error.log

# MD - Explicit solvent molecular dynamics constant pressure
cat <<EOF > md.in
&cntrl
  ! =======================
  ! Run control parameters
  ! =======================

  imin = 0,          ! Run type: 0 indicates molecular dynamics (MD) simulation
  nstlim = ISTEP     ! Total number of MD steps to be performed
  dt = 0.002,        ! Time step size for each MD step in picoseconds (ps)

  ! =======================
  ! Initial Configuration
  ! =======================

  ntx = INTX,        ! Specifies how the initial coordinates are to be read. INTX is a placeholder.
  irest = IREST,     ! Restart option. 0 means starting from an initial structure, 1 means restart from a previous simulation
  tempi = ITEMP,     ! Initial temperature of the system in Kelvin (K). ITEMP is a placeholder.
  temp0 = JTEMP,     ! Desired/target temperature for the simulation in Kelvin (K). JTEMP is a placeholder.

  ! ==========================
  ! Output & File Management
  ! ==========================

  ntpr = ISAVE,      ! Print frequency: Output is printed to the mdout file every ntrp steps.
  ntwx = ISAVE,      ! Coordinates write frequency: Atomic coordinates are written to the trajectory file every ntwx steps.
  ntwe = ISAVE,      ! Energies write frequency: Energies are written to the mdend file every ntwe steps.
  ntwr = ISTEP,      ! Restart write frequency: Restart file is written every ntwr steps.
  ioutfm = 1,        ! Format for the trajectory output file. 1 indicates ASCII format.

  ! ====================
  ! Molecular Mechanics
  ! ====================

  ntc = 2,           ! Specifies bond constraints. 2 indicates SHAKE will be applied to bonds involving hydrogen.
  ntf = 2,           ! Specifies which kind of force field terms to be used. 2 indicates the standard Amber force field.
  cut = 8.0,         ! Cutoff radius for nonbonded interactions in angstroms (Å).

  ! ===============
  ! Thermodynamics
  ! ===============

  ntt = 3            ! Specifies temperature scaling method. 3 indicates the Langevin dynamics thermostat is in use.
  gamma_ln = 1.0,    ! Collision frequency for Langevin thermostat in ps^-1.

  ! =======================
  ! Periodic Boundary Conditions and Pressure Control
  ! =======================

  ntp = 1,           ! Flag for constant pressure dynamics. 1 means isotropic position scaling.
  ntb = 2,           ! Defines boundary conditions. 2 indicates periodic boundaries in use.
  iwrap = 1,         ! If set to 1, coordinates are wrapped back into primary box. Helps in avoiding large translations.

  ! =======================
  ! Random Number Generation
  ! =======================

  ig = -1,           ! Seed for random number generator. -1 lets the system provide a unique seed.

  ! =======================
  ! Metadynamics
  ! =======================

  !!PLUMED!!plumed=1, plumedfile='../plumed.dat',
  /
EOF

############################
# SIMULATED ANNEALING (SA) #
############################

istep0=10000
isave0=500
istep=100000
isave=5000

# Define the temperature ranges
temperatures0=("0.0" "0.0"   "300.0" "300.0" "315.0" "315.0" "300.0" "300.0" "300.0" "300.0" "300.0")
temperatures1=("0.0" "300.0" "300.0" "315.0" "315.0" "300.0" "300.0" "300.0" "300.0" "300.0" "300.0")

# Iterate over the temperature ranges
for i in "${!temperatures0[@]}"; do
  md_iter="sa_${i}"
  sa_ind=${i}
  itemp=${temperatures0[$i]}
  jtemp=${temperatures1[$i]}

  rm -rf ${md_iter}
  mkdir ${md_iter}
  cd ${md_iter}

  # Modify the script file with the current temperature settings
  sed "s/ITEMP/${itemp}/" ../md.in > md.in
  sed -i "s/JTEMP/${jtemp}/" md.in

  if [[ $i -ne 0 ]]; then
    echo "Not the first SA iteration. Number: $i"
    iter0=$((i - 1))
    md_iter0="sa_${iter0}"
    echo "cp from ${md_iter0}"
    sed -i "s/INTX/5/" md.in
    sed -i "s/IREST/1/" md.in
    sed -i "s/ISTEP/${istep}/" md.in
    sed -i "s/ISAVE/${isave}/" md.in
    pmemd.cuda -AllowSmallBox -O -i md.in -o md.out -p ../${stem_2}.prmtop -c ../${md_iter0}/md.rst -r md.rst -x md.nc -inf md.info 2>error.log
    [[ $? -ne 0 ]] && echo "Error occurred during pmemd.cuda -AllowSmallBox execution. Exiting script." > RUN_ERROR.TXT && exit 1
    sleep 2
    cpptraj -p ../${stem_2}.prmtop -y md.nc -x md.dcd

  else
    echo "First SA iteration. Number: $i"
    sed -i "s/INTX/1/" md.in
    sed -i "s/IREST/0/" md.in
    sed -i "s/ISTEP/${istep0}/" md.in
    sed -i "s/ISAVE/${isave0}/" md.in
    pmemd -O -i md.in -o md.out -p ../${stem_2}.prmtop -c ..//min.rst -r md.rst -x md.nc -inf md.info 2>error.log
    [[ $? -ne 0 ]] && echo "Error occurred during pmemd.cuda -AllowSmallBox execution. Exiting script." > RUN_ERROR.TXT && exit 1
    sleep 2
    cpptraj -p ../${stem_2}.prmtop -y md.nc -x md.dcd
  fi

  cd ..

done

#######################
# MD EQUILIBRATE (EQ) #
#######################

istep=25000000
isave=5000

# Define the equilibration temperature
eq_temp=300.0

for i in {1..2}; do
  md_iter="eq_${i}"

  rm -rf ${md_iter}
  mkdir ${md_iter}
  cd ${md_iter}

  # Modify the script file with the current temperature settings
  sed "s/ITEMP/${eq_temp}/" ../md.in > md.in
  sed -i "s/JTEMP/${eq_temp}/" md.in
  sed -i "s/ISTEP/${istep}/" md.in
  sed -i "s/ISAVE/${isave}/" md.in
  sed -i "s/INTX/5/" md.in
  sed -i "s/IREST/1/" md.in
  sed -i "s/!!PLUMED!!//" md.in

  if [[ $i -ne 1 ]]; then
    echo "Not the first EQ iteration. Number: $i"
    iter0=$((i - 1))
    md_iter0="eq_${iter0}"
    echo "cp from ${md_iter0}"
    sed -i "s/RESTART=NO/RESTART=YES/" ../plumed.dat
    pmemd.cuda -AllowSmallBox -O -i md.in -o md.out -p ../${stem_2}.prmtop -c ../${md_iter0}/md.rst -r md.rst -x md.nc -inf md.info 2>error.log
    [[ $? -ne 0 ]] && echo "Error occurred during pmemd.cuda -AllowSmallBox execution. Exiting script." > RUN_ERROR.TXT && exit 1
    sleep 2
    cpptraj -p ../${stem_2}.prmtop -y md.nc -x md.dcd

  else
    echo "First EQ iteration. Number: $i"
    md_iter0="sa_${sa_ind}"
    echo "cp from ${md_iter0}"
    pmemd.cuda -AllowSmallBox -O -i md.in -o md.out -p ../${stem_2}.prmtop -c ../${md_iter0}/md.rst -r md.rst -x md.nc -inf md.info 2>error.log
    [[ $? -ne 0 ]] && echo "Error occurred during pmemd.cuda -AllowSmallBox execution. Exiting script." > RUN_ERROR.TXT && exit 1
    sleep 2
    cpptraj -p ../${stem_2}.prmtop -y md.nc -x md.dcd

  fi

  cd ..

done

