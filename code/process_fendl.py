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
#     python process-fendl.py <sublib> [<endf_file>]
#
#     <sublib> can be: neutron, proton, deuteron, all
#     <endf_file> to process (optional). If none provided,
#                 all files of the sublibrary will be processed.
#
############################################################

import sys
from process_fendl_base import get_njoy_version
from process_fendl_neutron import process_fendl_neutron_lib
from process_fendl_proton import process_fendl_proton_lib
from process_fendl_deuteron import process_fendl_deuteron_lib
import argparse


parser = argparse.ArgumentParser()
parser.add_argument(
    'library_type', choices=['all', 'neutron', 'proton', 'deuteron'],
    default='all', nargs='?', help='sublibrary to process'
)
parser.add_argument(
    'endf_file', type=str, default=None, nargs='?',
    help='specific ENDF file of sublibrary to process'
)
args = parser.parse_args()

library_type = args.library_type
endf_file = args.endf_file

njoyexe = '/opt/NJOY2016/bin/njoy'
njoylib = '/opt/NJOY2016/bin/libnjoy.so'
njoyvers = get_njoy_version('/opt/NJOY2016')

if library_type in ('neutron', 'all'):
    print('--- processing neutron ENDF files ---')
    process_fendl_neutron_lib(
        '.', njoyexe, njoylib, njoyvers, endf_file=endf_file
    )

if library_type in ('proton', 'all'):
    print('--- processing proton ENDF files ---')
    process_fendl_proton_lib(
        '.', njoyexe, njoylib, njoyvers, endf_file=endf_file
    )

if library_type in ('deuteron', 'all'):
    print('--- processing deuteron ENDF files ---')
    process_fendl_deuteron_lib(
        '.', njoyexe, njoylib, njoyvers, endf_file=endf_file
    )
