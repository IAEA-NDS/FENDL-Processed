############################################################
#
# This script converts FENDL ENDF files into OpenMC HDF5
# format. It processes neutron and photo-atomic sublibraries
# and produces a cross_sections.xml file.
#
# Usage:
#     Run from the root directory of the
#     FENDL-processed directory:
#
#     python code/process_fendl_hdf5.py [<sublib>] [<endf_file>]
#
#     <sublib> can be: neutron, photon, all (default: all)
#     <endf_file> specific ENDF file to process (optional)
#
############################################################

import argparse
from pathlib import Path

import openmc.data

from process_fendl_neutron_hdf5 import process_fendl_neutron_hdf5
from process_fendl_photon_hdf5 import process_fendl_photon_hdf5


parser = argparse.ArgumentParser()
parser.add_argument(
    'library_type', choices=['all', 'neutron', 'photon'],
    default='all', nargs='?', help='sublibrary to process'
)
parser.add_argument(
    'endf_file', type=str, default=None, nargs='?',
    help='specific ENDF file of sublibrary to process'
)
args = parser.parse_args()

library_type = args.library_type
endf_file = args.endf_file

repodir = '.'
destination = Path('general-purpose/hdf5')

library = openmc.data.DataLibrary()

if library_type in ('neutron', 'all'):
    print('--- converting neutron ENDF files to HDF5 ---')
    neutron_dest = destination / 'neutron'
    neutron_lib = process_fendl_neutron_hdf5(
        repodir, neutron_dest, endf_file=endf_file
    )
    for h5_file in sorted(neutron_dest.glob('*.h5')):
        library.register_file(h5_file)

if library_type in ('photon', 'all'):
    print('--- converting photon ENDF files to HDF5 ---')
    photon_dest = destination / 'photon'
    photon_lib = process_fendl_photon_hdf5(
        repodir, photon_dest, endf_file=endf_file
    )
    for h5_file in sorted(photon_dest.glob('*.h5')):
        library.register_file(h5_file)

# Write cross_sections.xml
print('Writing', destination / 'cross_sections.xml')
library.export_to_xml(destination / 'cross_sections.xml')
