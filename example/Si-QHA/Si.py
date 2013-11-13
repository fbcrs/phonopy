from phonopy import Phonopy
from phonopy.interface.vasp import read_vasp
from phonopy.file_IO import parse_FORCE_SETS
import numpy as np

def get_frequency(poscar_filename, force_sets_filename):
    bulk = read_vasp(poscar_filename)
    volume = bulk.get_volume()
    phonon = Phonopy(bulk, [[2, 0, 0], [0, 2, 0], [0, 0, 2]],
                     is_auto_displacements=False)
    force_sets = parse_FORCE_SETS(phonon.get_supercell().get_number_of_atoms(),
                                  filename=force_sets_filename)
    set_of_forces = [x.get_forces() for x in force_sets]
    displacements = [[x.get_atom_number()] + list(x.get_displacement())
                     for x in force_sets]
    phonon.set_displacements(displacements)
    phonon.set_post_process([[0, 0.5, 0.5], [0.5, 0, 0.5], [0.5, 0.5, 0]],
                            set_of_forces)
    return phonon.get_frequencies([0.5, 0.5, 0]), volume

frequencies = []
volumes = []
for i in range(-10, 6):
    poscar_filename = "POSCAR-%d" % i
    force_sets_filename = "FORCE_SETS-%d" % i
    fs, v = get_frequency(poscar_filename, force_sets_filename)
    frequencies.append(fs)
    volumes.append(v)

import matplotlib.pyplot as plt
for curve in np.array(frequencies).T:
    plt.plot(volumes, curve**2 * np.sign(curve))
    for v, f2 in zip(volumes, curve ** 2 * np.sign(curve)):
         print v, f2
    print
    print
plt.show()


