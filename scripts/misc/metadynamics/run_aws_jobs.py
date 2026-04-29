import os

nmol = 10
solv = 'chl_'
box_name = 'CHCL3BOX'

#solv = 'wat_'
#box_name = 'TIP3PBOX'

for i in range(nmol):
    ii = i+1
    dir0 = f'mol_{ii}'

    CC = f'''\
    cd {dir0}
    sed -i 's/mol_/{solv}/g' submit.pbs
    sed -i 's/CHCL3BOX/{box_name}/g' 01run.sh
    qsub submit.pbs
    '''
    print(CC)
    os.system(CC)
