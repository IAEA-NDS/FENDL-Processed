############################################################
#
# This script converts photo-atomic ENDF files from the
# FENDL library into OpenMC HDF5 format.
#
# Usage:
#     Run from the root directory of the
#     FENDL-processed directory:
#
#     python code/process_fendl_photon_hdf5.py
#
############################################################

import os
from pathlib import Path

import openmc.data


def process_fendl_photon_hdf5(repodir, destination, endf_file=None):
    """Convert all photo-atomic ENDF files to OpenMC HDF5 format."""
    repodir = Path(repodir).resolve()
    endf_dir = repodir / 'fendl-endf' / 'general-purpose' / 'atom'
    destination = Path(destination)
    destination.mkdir(parents=True, exist_ok=True)

    library = openmc.data.DataLibrary()

    endf_files = sorted(endf_dir.glob('*.endf'))
    for endf_path in endf_files:
        if endf_file is not None and endf_path.name != endf_file:
            continue

        print(f'Converting: {endf_path.name}')
        data = openmc.data.IncidentPhoton.from_endf(endf_path)

        h5_file = destination / f'{data.name}.h5'
        print(f'Writing {h5_file}...')
        data.export_to_hdf5(h5_file, 'w')

        library.register_file(h5_file)

    return library
