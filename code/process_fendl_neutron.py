############################################################
#
# Author:       Georg Schnabel
# Email:        g.schnabel@iaea.org
# Date:         2023/11/10
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
#     python process-fendl-neutron.py
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
    shutil.copy(inputs['n_endf'], os.path.join(tmpdir.name, 'tape20'))
    shutil.copy(inputs['ph_endf'], os.path.join(tmpdir.name, 'tape40'))
    shutil.copy(inputs['njoyinp'], os.path.join(tmpdir.name, 'input'))

    njoyinp = open(os.path.join(tmpdir.name, 'input'))
    ret = subprocess.run([inputs['njoyexe']], stdin=njoyinp,
                         text=True, cwd = tmpdir.name)
    njoyinp.close()
    ret.check_returncode()

    shutil.copy(os.path.join(tmpdir.name, 'tape29'), outputs['ace'])
    write_xsd_file(outputs['ace'], outputs['xsd'])
    shutil.copy(os.path.join(tmpdir.name, 'tape35'), outputs['aceplot'])
    shutil.copy(os.path.join(tmpdir.name, 'tape31'), outputs['g'])
    shutil.copy(os.path.join(tmpdir.name, 'tape32'), outputs['htrplot'])
    shutil.copy(os.path.join(tmpdir.name, 'tape43'), outputs['gam'])
    shutil.copy(os.path.join(tmpdir.name, 'tape44'), outputs['m'])
    shutil.copy(os.path.join(tmpdir.name, 'output'), outputs['njoyout'])
    tmpdir.cleanup()

    ret = subprocess.run(['ps2pdf', outputs['aceplot'], outputs['aceplotpdf']])
    ret.check_returncode()
    ret = subprocess.run(['ps2pdf', outputs['htrplot'], outputs['htrplotpdf']])
    ret.check_returncode()
    return


def determine_fendl_paths(info, repodir, njoyexe, njoylib):
    """Return dictionary with paths to FENDL paths (ace, plots, etc.)."""
    if info['incpart'] != 'n':
        raise ValueError('The info dic should be for incident neutrons')
    n_endf_file = '%s_%04d_%d-%s-%s%s.endf' % (info['incpart'], info['matnr'],
                                           info['charge'], info['symb'],
                                           info['mass'], info['meta'])
    ph_endf_file = 'ph_%02d00_%d-%s.endf' % (info['charge'], info['charge'], info['symb'])
    padsymb = ('%-2s' % info['symb']).replace(' ','_')
    ace_file = '%02d%s%03d%s' % (info['charge'], padsymb, info['mass'], info['meta'])
    xsd_file = ace_file + '.xsd'
    g_file = ace_file + '.g'
    m_file = ace_file + '.m'
    gam_file = ace_file + '.gam'
    njoyout_file = ace_file + '.out'
    njoyinp_file = ace_file + '.nji'
    htrplot_file = ace_file + '_htr.ps'
    htrplot_pdffile = ace_file + '_htr.pdf'
    aceplot_file = ace_file + '_ace.ps'
    aceplot_pdffile = ace_file + '_ace.pdf'
    track_file = ace_file + '.json'
    fendl_paths = {}
    fendl_paths['inputs'] = {
        'config': os.path.join(repodir, 'config.py'),
        'n_endf': os.path.join(repodir, 'fendl-endf/general-purpose/neutron', n_endf_file),
        'ph_endf': os.path.join(repodir, 'fendl-endf/general-purpose/atom', ph_endf_file),
        'njoyinp': os.path.join(repodir, 'general-purpose/neutron/njoy', njoyinp_file),
        'njoyexe': njoyexe,
        'njoylib': njoylib
    }
    fendl_paths['outputs'] = {
        'gam': os.path.join(repodir, 'general-purpose/atom/group', gam_file),
        'g': os.path.join(repodir, 'general-purpose/neutron/group', g_file),
        'm': os.path.join(repodir, 'general-purpose/neutron/group', m_file),
        'ace': os.path.join(repodir, 'general-purpose/neutron/ace', ace_file),
        'xsd': os.path.join(repodir, 'general-purpose/neutron/ace', xsd_file),
        'aceplot': os.path.join(repodir, 'general-purpose/neutron/plot', aceplot_file),
        'aceplotpdf': os.path.join(repodir, 'general-purpose/neutron/plot', aceplot_pdffile),
        'htrplot': os.path.join(repodir, 'general-purpose/neutron/plot', htrplot_file),
        'htrplotpdf': os.path.join(repodir, 'general-purpose/neutron/plot', htrplot_pdffile),
        'njoyout': os.path.join(repodir, 'general-purpose/neutron/njoy', njoyout_file),
    }
    fendl_paths['trackfile'] = os.path.join(repodir, 'trackdb/trackdb_neutron', track_file)
    return fendl_paths


def process_fendl_neutron_lib(
    repodir, njoyexe, njoylib, njoyvers, fendlvers, cdate, endf_file=None
):
    """Process all neutron ENDF files in FENDL library."""
    endf_sublib = os.path.join('fendl-endf', 'general-purpose/neutron')
    process_fendl_sublib(repodir, endf_sublib, run_fendl_njoy,
                         determine_fendl_paths, njoyexe, njoylib,
                         njoyvers, fendlvers, cdate, endf_file=endf_file)


if __name__ == '__main__':
    njoyvers = get_njoy_version('/opt/NJOY2016')
    fendlvers = get_fendl_version()
    cdate = get_creation_date()
    process_fendl_neutron_lib('.', '/opt/NJOY2016/bin/njoy', njoyvers, fendlvers, cdate)
