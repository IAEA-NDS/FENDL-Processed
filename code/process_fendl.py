############################################################
#
# Author:       Georg Schnabel
# Email:        g.schnabel@iaea.org
# Date:         2022/02/06
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
#     python process-fendl.py
#
############################################################

import sys
from process_fendl_neutron import process_fendl_neutron_lib
from process_fendl_proton import process_fendl_proton_lib


if len(sys.argv) != 2:
    raise ValueError('please provide type of sublibrary: proton / neutron / all')

library_type = sys.argv[1]
njoyexe = '/opt/NJOY2016/bin/njoy'
njoylib = '/opt/NJOY2016/bin/libnjoy.so'

if library_type in ('neutron', 'all'):
    print('--- processing neutron ENDF files ---')
    process_fendl_neutron_lib('.', njoyexe, njoylib)

if library_type in ('proton', 'all'):
    print('--- processing proton ENDF files ---')
    process_fendl_proton_lib('.', njoyexe, njoylib)
