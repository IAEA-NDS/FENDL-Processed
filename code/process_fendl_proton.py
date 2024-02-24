############################################################
#
# Author:       Georg Schnabel
# Email:        g.schnabel@iaea.org
# Date:         2023/11/10
# Institution:  IAEA
#
# This script is a driver for NJOY2016 to
# produce the processed files of the FENDL
# proton sublibrary.
#
# Usage:
#     Run from the root directory of the
#     FENDL-processed directory:
#
#     python process-fendl-proton.py
#
############################################################

import subprocess
import tempfile
import shutil
import os

from construct_xsd_file import write_xsd_file
from process_fendl_base import (
    process_fendl_sublib,
    get_njoy_version,
    get_fendl_version,
    get_creation_date,
)


def run_fendl_njoy(pardic):
    """Invoke NJOY for ENDF files in FENDL library."""
    inputs = pardic['inputs']
    outputs = pardic['outputs']
    tmpdir = tempfile.TemporaryDirectory()
    shutil.copy(inputs['p_endf'], os.path.join(tmpdir.name, 'tape20'))
    shutil.copy(inputs['njoyinp'], os.path.join(tmpdir.name, 'input'))

    njoyinp = open(os.path.join(tmpdir.name, 'input'))
    ret = subprocess.run([inputs['njoyexe']], stdin=njoyinp,
                         text=True, cwd = tmpdir.name)
    njoyinp.close()
    ret.check_returncode()

    shutil.copy(os.path.join(tmpdir.name, 'tape29'), outputs['ace'])
    write_xsd_file(outputs['ace'], outputs['xsd'])
    shutil.copy(os.path.join(tmpdir.name, 'tape35'), outputs['aceplot'])
    shutil.copy(os.path.join(tmpdir.name, 'output'), outputs['njoyout'])
    tmpdir.cleanup()

    ret = subprocess.run(['ps2pdf', outputs['aceplot'], outputs['aceplotpdf']])
    ret.check_returncode()
    return


def determine_fendl_paths(info, repodir, njoyexe, njoylib):
    """Return dictionary with paths to FENDL paths (ace, plots, etc.)."""
    if info['incpart'] != 'p':
        raise ValueError('The info dic should be for incident protons')
    p_endf_file = '%s_%04d_%d-%s-%s%s.endf' % (info['incpart'], info['matnr'],
                                           info['charge'], info['symb'],
                                           info['mass'], info['meta'])
    padsymb = ('%-2s' % info['symb']).replace(' ','_')
    ace_file = '%02d%s%03d%s' % (info['charge'], padsymb, info['mass'], info['meta'])
    xsd_file = ace_file + '.xsd'
    njoyout_file = ace_file + '.out'
    njoyinp_file = ace_file + '.nji'
    aceplot_file = ace_file + '_ace.ps'
    aceplot_pdffile = ace_file + '_ace.pdf'
    track_file = ace_file + '.json'
    fendl_paths = {}
    fendl_paths['inputs'] = {
        'p_endf': os.path.join(repodir, 'fendl-endf/general-purpose/proton', p_endf_file),
        'njoyinp': os.path.join(repodir, 'general-purpose/proton/njoy', njoyinp_file),
        'njoyexe': njoyexe,
        'njoylib': njoylib
    }
    fendl_paths['outputs'] = {
        'ace': os.path.join(repodir, 'general-purpose/proton/ace', ace_file),
        'xsd': os.path.join(repodir, 'general-purpose/proton/ace', xsd_file),
        'aceplot': os.path.join(repodir, 'general-purpose/proton/plot', aceplot_file),
        'aceplotpdf': os.path.join(repodir, 'general-purpose/proton/plot', aceplot_pdffile),
        'njoyout': os.path.join(repodir, 'general-purpose/proton/njoy', njoyout_file),
    }
    fendl_paths['trackfile'] = os.path.join(repodir, 'trackdb/trackdb_proton', track_file)
    return fendl_paths


def process_fendl_proton_lib(
    repodir, njoyexe, njoylib, njoyvers, fendlvers, cdate, endf_file=None
):
    """Process all deuteron ENDF files in FENDL library."""
    endf_sublib = os.path.join('fendl-endf', 'general-purpose/proton')
    process_fendl_sublib(repodir, endf_sublib, run_fendl_njoy,
                         determine_fendl_paths, njoyexe, njoylib,
                         njoyvers, fendlvers, cdate, endf_file=endf_file)


if __name__ == '__main__':
    njoyvers = get_njoy_version('/opt/NJOY2016')
    fendlvers = get_fendl_version()
    cdate = get_creation_date()
    process_fendl_proton_lib('.', '/opt/NJOY2016/bin/njoy', njoyvers, fendlvers, cdate)
