#!/bin/bash

stem_1="system_1"

cp lig.mol2 ${stem_1}.mol2

parmchk2 -i ${stem_1}.mol2 -f mol2 -o ${stem_1}.frcmod -s gaff2
cat <<EOF > "leap_${stem_1}.in"
source leaprc.protein.ff14SB
source leaprc.gaff2
loadamberparams ${stem_1}.frcmod
mol = loadmol2 ${stem_1}.mol2
charge mol
check mol
saveamberparm mol ${stem_1}.prmtop ${stem_1}.inpcrd
quit
EOF
tleap -f "leap_${stem_1}.in"

awk 'NR==2{print $1}' system_1.inpcrd > natoms.txt

