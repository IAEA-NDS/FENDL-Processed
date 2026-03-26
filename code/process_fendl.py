############################################################
#
# Author:       Georg Schnabel
# Email:        g.schnabel@iaea.org
# Date:         2023/11/09
# Institution:  IAEA
#
# This script is a driver for NJOY2016 to
# produce the processed files of the FENDL library
# based on the neutron and photo-atomic ENDF files.
#
# Usage:
#     Run from the root directory of the
#     FENDL-processed directory:
#
#     python process-fendl.py <sublib> [<endf_file>] [--formats ace hdf5]
#
#     <sublib> can be: neutron, proton, deuteron, photon, all
#     <endf_file> to process (optional). If none provided,
#                 all files of the sublibrary will be processed.
#     --formats: ace (includes plots), hdf5, or both (default: both)
#
############################################################

import sys
from pathlib import Path
from process_fendl_base import (
    get_njoy_version,
    get_fendl_version,
    get_creation_date
)
from process_fendl_neutron import process_fendl_neutron_lib
from process_fendl_proton import process_fendl_proton_lib
from process_fendl_deuteron import process_fendl_deuteron_lib
import argparse


parser = argparse.ArgumentParser()
parser.add_argument(
    'library_type', choices=['all', 'neutron', 'proton', 'deuteron', 'photon'],
    default='all', nargs='?', help='sublibrary to process'
)
parser.add_argument(
    'endf_file', type=str, default=None, nargs='?',
    help='specific ENDF file of sublibrary to process'
)
parser.add_argument(
    '--formats', nargs='+', choices=['ace', 'hdf5'],
    default=['ace', 'hdf5'], help='output formats to produce (default: both)'
)
args = parser.parse_args()

library_type = args.library_type
endf_file = args.endf_file
formats = args.formats

njoyexe = '/opt/NJOY2016/bin/njoy'
njoylib = '/opt/NJOY2016/bin/libnjoy.so'
njoyvers = get_njoy_version('/opt/NJOY2016')
fendlvers = get_fendl_version()
cdate = get_creation_date()

basedir = Path('general-purpose')

if 'ace' in formats:
    if library_type in ('neutron', 'all'):
        print('--- processing neutron ENDF files ---')
        process_fendl_neutron_lib(
            '.', njoyexe, njoylib, njoyvers, fendlvers, cdate, endf_file=endf_file
        )

    if library_type in ('proton', 'all'):
        print('--- processing proton ENDF files ---')
        process_fendl_proton_lib(
            '.', njoyexe, njoylib, njoyvers, fendlvers, cdate, endf_file=endf_file
        )

    if library_type in ('deuteron', 'all'):
        print('--- processing deuteron ENDF files ---')
        process_fendl_deuteron_lib(
            '.', njoyexe, njoylib, njoyvers, fendlvers, cdate, endf_file=endf_file
        )

if 'hdf5' in formats:
    # Lazy import to avoid requiring openmc when only producing ACE files
    import openmc.data
    from process_fendl_neutron_hdf5 import process_fendl_neutron_hdf5
    from process_fendl_photon_hdf5 import process_fendl_photon_hdf5

    hdf5_library = openmc.data.DataLibrary()

    if library_type in ('neutron', 'all'):
        print('--- converting neutron ENDF files to HDF5 ---')
        neutron_dest = basedir / 'neutron' / 'hdf5'
        process_fendl_neutron_hdf5('.', neutron_dest, endf_file=endf_file)
        for h5_file in sorted(neutron_dest.glob('*.h5')):
            hdf5_library.register_file(h5_file)

    if library_type in ('photon', 'all'):
        print('--- converting photon ENDF files to HDF5 ---')
        photon_dest = basedir / 'photon' / 'hdf5'
        process_fendl_photon_hdf5('.', photon_dest, endf_file=endf_file)
        for h5_file in sorted(photon_dest.glob('*.h5')):
            hdf5_library.register_file(h5_file)

    print('Writing', basedir / 'cross_sections.xml')
    hdf5_library.export_to_xml(basedir / 'cross_sections.xml')
