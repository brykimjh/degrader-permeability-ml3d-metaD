import os

nmol = 17

for i in range(nmol):
    ii = i+1
    dir0 = f'mol_{ii}'

    CC = f'''\
    rm -rf {dir0}
    cp -r tmp {dir0}
    cd {dir0}
    sed -i 's/INDEX/{ii}/' copy.pbs
    qsub copy.pbs
    '''
    print(CC)
    os.system(CC)
