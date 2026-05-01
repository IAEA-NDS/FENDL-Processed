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

import os
import sys
from pathlib import Path
from process_fendl_base import (
    get_njoy_version,
    get_fendl_version,
    get_creation_date,
    process_fendl_endf,
)
from process_fendl_neutron import process_fendl_neutron_lib
from process_fendl_proton import process_fendl_proton_lib
from process_fendl_deuteron import process_fendl_deuteron_lib
from process_fendl_photoatomic import process_fendl_photoatomic_lib
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
openmclib = '/opt/openmc/.git/HEAD'
njoyvers = get_njoy_version('/opt/NJOY2016')
fendlvers = get_fendl_version()
cdate = get_creation_date()

basedir = Path('general-purpose')


def process_cross_sections_xml(repodir, basedir, openmclib, njoyvers, fendlvers, cdate):
    """Reconcile general-purpose/cross_sections.xml with the neutron and
    photon HDF5 files currently on disk, using the same trackdb-hash
    machinery as the per-isotope outputs."""
    import openmc.data

    inputs = {'openmclib': openmclib}
    for sublib in ('neutron', 'photon'):
        h5_dir = basedir / sublib / 'hdf5'
        if h5_dir.is_dir():
            for h5 in sorted(h5_dir.glob('*.h5')):
                inputs[f'h5/{sublib}/{h5.name}'] = str(h5)

    fendl_paths = {
        'inputs': inputs,
        'outputs': {
            'cross_sections_xml': str(basedir / 'cross_sections.xml'),
        },
        'trackfile': os.path.join(repodir, 'trackdb', 'cross_sections.json'),
    }

    def run_xml_export(pardic):
        lib = openmc.data.DataLibrary()
        for key in sorted(pardic['inputs']):
            if key.startswith('h5/'):
                lib.register_file(pardic['inputs'][key])
        lib.export_to_xml(pardic['outputs']['cross_sections_xml'])

    process_fendl_endf(run_xml_export, fendl_paths, njoyvers, fendlvers, cdate)


if 'ace' in formats:
    if library_type in ('neutron', 'all'):
        print('--- processing neutron ENDF files ---')
        process_fendl_neutron_lib(
            '.', njoyexe, njoylib, openmclib, njoyvers, fendlvers, cdate, endf_file=endf_file
        )

    if library_type in ('proton', 'all'):
        print('--- processing proton ENDF files ---')
        process_fendl_proton_lib(
            '.', njoyexe, njoylib, openmclib, njoyvers, fendlvers, cdate, endf_file=endf_file
        )

    if library_type in ('deuteron', 'all'):
        print('--- processing deuteron ENDF files ---')
        process_fendl_deuteron_lib(
            '.', njoyexe, njoylib, openmclib, njoyvers, fendlvers, cdate, endf_file=endf_file
        )

if 'hdf5' in formats:
    if library_type in ('photon', 'all'):
        print('--- processing photo-atomic ENDF files ---')
        process_fendl_photoatomic_lib(
            '.', njoyexe, njoylib, openmclib, njoyvers, fendlvers, cdate, endf_file=endf_file
        )

    process_cross_sections_xml('.', basedir, openmclib, njoyvers, fendlvers, cdate)
