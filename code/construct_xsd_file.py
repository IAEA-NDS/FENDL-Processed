############################################################
#
# Author:       Georg Schnabel
# Email:        g.schnabel@iaea.org
# Date:         2022/02/15
# Institution:  IAEA
#
# Reads the header from an ace file and writes the
# relevant fields to an xsd file required by MCNP
#
# Usage:
#     python construct_xsd_file.py <ace-file> <xsd-file>
#
#     <ace-file>: An ACE file as used for MCNP calculations
#     <xsd-file>: Directory file for MCNP
#
############################################################

import os
import sys

fpath = sys.argv[1]
xsdpath = sys.argv[2]
fname = os.path.basename(fpath)

try:
    with open(fpath, 'r') as f:
        ace_header = f.readline()
        za_field = ace_header[0:10]
        mass_field = ace_header[10:22]
        temp_field = ace_header[22:34]
        for i in range(6):
            ace_line = f.readline()
        numel_field = ace_line[0:9]
        for i in range(4):
            ace_line = f.readline()
        has_ptable = int(ace_line[54:63]) > 0
        ptablestr = ' ptable' if has_ptable else ''
except IOError:
    print('Cannot read from file {}\n'.format(fpath), file=sys.stderr)

if len(fname) > 8:
    raise ValueError('filename of ace file must not exceed seven characters')

try:
    with open(xsdpath, 'w') as f:
        f.write('%s%s %s%2d%2d%9d%s%2d%2d%s%s\n' %
                (za_field, mass_field, fname, 0, 1, 1,
                 numel_field, 0, 0, temp_field, ptablestr))
except IOError:
    print('Cannot write to file {}\n'.format(xsdpath), file=sys.stderr)
