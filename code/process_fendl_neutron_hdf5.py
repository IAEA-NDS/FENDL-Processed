############################################################
#
# This script converts neutron ENDF files from the FENDL
# library into OpenMC HDF5 format using NJOY.
#
# Usage:
#     Run from the root directory of the
#     FENDL-processed directory:
#
#     python code/process_fendl_neutron_hdf5.py
#
############################################################

import os
import warnings
from pathlib import Path

import openmc.data

from process_fendl_base import (
    is_endf_file,
    get_endf_info,
)


def process_fendl_neutron_hdf5(repodir, destination, endf_file=None):
    """Convert all neutron ENDF files to OpenMC HDF5 format."""
    repodir = Path(repodir).resolve()
    endf_dir = repodir / 'fendl-endf' / 'general-purpose' / 'neutron'
    destination = Path(destination)
    destination.mkdir(parents=True, exist_ok=True)

    library = openmc.data.DataLibrary()

    endf_files = sorted(endf_dir.glob('*.endf'))
    for endf_path in endf_files:
        if endf_file is not None and endf_path.name != endf_file:
            continue
        if not is_endf_file(str(endf_path)):
            continue
        info = get_endf_info(str(endf_path))
        if info['incpart'] != 'n':
            continue

        print(f'Converting: {endf_path.name}')
        try:
            with warnings.catch_warnings():
                warnings.simplefilter('ignore', UserWarning)
                data = openmc.data.IncidentNeutron.from_njoy(
                    endf_path, njoy_exec='/opt/NJOY2016/bin/njoy'
                )
        except Exception as e:
            print(f'Error converting {endf_path.name}: {e}')
            raise

        h5_file = destination / f'{data.name}.h5'
        print(f'Writing {h5_file}...')
        data.export_to_hdf5(h5_file, 'w')

        library.register_file(h5_file)

    return library
