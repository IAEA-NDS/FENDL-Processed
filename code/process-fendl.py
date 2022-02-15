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
#     python fendl-processing.py
#
############################################################

import argparse
import subprocess
import tempfile
import shutil
import os
import sys
import json
import hashlib
import re

from construct_xsd_file import write_xsd_file


# auxiliary functions

def filehash(fname):
    """Calculate sha256 hash of file."""
    sha256 = hashlib.sha256()
    with open(fname, 'rb') as f:
        while True:
            data = f.read(65536)
            if not data:
                break
            sha256.update(data)
    return sha256.hexdigest()


def run_fendl_njoy(pardic):
    """Invoke NJOY for ENDF files in FENDL library."""
    tmpdir = tempfile.TemporaryDirectory()
    shutil.copy(pardic['n_endf'], os.path.join(tmpdir.name, 'tape20')) 
    shutil.copy(pardic['ph_endf'], os.path.join(tmpdir.name, 'tape40')) 
    shutil.copy(pardic['njoyinp'], os.path.join(tmpdir.name, 'input')) 

    njoyinp = open(os.path.join(tmpdir.name, 'input'))
    ret = subprocess.run([pardic['njoyexe']], stdin=njoyinp,
                         text=True, cwd = tmpdir.name)
    njoyinp.close()
    ret.check_returncode()

    shutil.copy(os.path.join(tmpdir.name, 'tape29'), pardic['ace'])
    write_xsd_file(pardic['ace'], pardic['xsd'])
    shutil.copy(os.path.join(tmpdir.name, 'tape35'), pardic['aceplot'])
    shutil.copy(os.path.join(tmpdir.name, 'tape31'), pardic['g'])
    shutil.copy(os.path.join(tmpdir.name, 'tape32'), pardic['htrplot'])
    shutil.copy(os.path.join(tmpdir.name, 'tape43'), pardic['gam'])
    shutil.copy(os.path.join(tmpdir.name, 'tape44'), pardic['m'])
    shutil.copy(os.path.join(tmpdir.name, 'output'), pardic['njoyout'])
    tmpdir.cleanup()

    ret = subprocess.run(['ps2pdf', pardic['aceplot'], pardic['aceplotpdf']])
    ret.check_returncode()
    ret = subprocess.run(['ps2pdf', pardic['htrplot'], pardic['htrplotpdf']])
    ret.check_returncode()
    return


# specific functions to process the endf files
# in FENDL as being organized in the GitHub repositories

def is_endf_file(fpath):
    """Return whether ENDF file is named according to FENDL convention."""
    p = re.compile('(?:^|.*/)([a-z][a-z]?)_([0-9]+)_([0-9]+)-([A-Z][a-z]?)(?:-([0-9]+m?))?\.endf$')
    return p.match(fpath) is not None


def get_endf_info(fpath):
    """Return a dictionary with information about an ENDF file"""
    p = re.compile('(?:^|.*/)([a-z][a-z]?)_([0-9]+)_([0-9]+)-([A-Z][a-z]?)(?:-([0-9]+)(m?))?\.endf$')
    m = p.match(fpath)
    if not m:
        raise ValueError('The file ' + fpath + ' is not an ENDF file following FENDL naming convention')
    info = {
            'incpart': m.group(1),
            'matnr': int(m.group(2)),
            'charge': int(m.group(3)),
            'symb': m.group(4),
            'mass': int(m.group(5)) if m.group(5) is not None else 0,
            'meta': m.group(6)
            }
    return info


def determine_fendl_paths(info, repodir, njoyexe):
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
    fendl_paths = {
        'n_endf': os.path.join(repodir, 'fendl-endf/general-purpose/neutron', n_endf_file),
        'ph_endf': os.path.join(repodir, 'fendl-endf/general-purpose/atom', ph_endf_file),
        'gam': os.path.join(repodir, 'general-purpose/atom/group', gam_file),
        'g': os.path.join(repodir, 'general-purpose/neutron/group', g_file),
        'm': os.path.join(repodir, 'general-purpose/neutron/group', m_file),
        'ace': os.path.join(repodir, 'general-purpose/neutron/ace', ace_file),
        'xsd': os.path.join(repodir, 'general-purpose/neutron/ace', xsd_file),
        'aceplot': os.path.join(repodir, 'general-purpose/neutron/plot', aceplot_file),
        'aceplotpdf': os.path.join(repodir, 'general-purpose/neutron/plot', aceplot_pdffile),
        'htrplot': os.path.join(repodir, 'general-purpose/neutron/plot', htrplot_file),
        'htrplotpdf': os.path.join(repodir, 'general-purpose/neutron/plot', htrplot_pdffile),
        'njoyinp': os.path.join(repodir, 'general-purpose/neutron/njoy', njoyinp_file),
        'njoyout': os.path.join(repodir, 'general-purpose/neutron/njoy', njoyout_file),
        'track': os.path.join(repodir, 'code/trackdb', track_file),
        'njoyexe': njoyexe
    }
    return fendl_paths


def check_input_files_available(fendl_paths):
    if not os.path.isfile(fendl_paths['njoyexe']):
        raise FileNotFoundError('NJOY2016 was not found at the specified path: ' + fendl_paths['njoyexe'])
    if not os.path.isfile(fendl_paths['njoyinp']):
        raise FileNotFoundError('NJOY2016 input file is missing: ' + fendl_paths['njoyinp'])
    if not os.path.isfile(fendl_paths['n_endf']):
        raise FileNotFoundError('neutron endf file is missing: ' + fendl_paths['n_endf'])
    if not os.path.isfile(fendl_paths['ph_endf']):
        raise FileNotFoundError('photo-atomic endf file is missing: ' + fendl_paths['ph_endf'])
    return


def should_reprocess(info, repodir, njoyexe):
    """Return boolean indicating whether running NJOY is necessary"""
    fendl_paths = determine_fendl_paths(info, repodir, njoyexe)
    for k,f in fendl_paths.items():
        if not os.path.isfile(f):
            return True
    trackfile = fendl_paths.pop('track')
    with open(trackfile, 'r') as f:
        storedhashes = json.load(f)

    curhashes = {k: filehash(f) for k,f in fendl_paths.items()}
    for k in curhashes:
        if curhashes[k] != storedhashes[k]:
            if k not in ('n_endf','ph_endf','njoyinp'):
                raise ValueError('Hashes of output files do not match those in trackdb')
            return True
    return False


def process_fendl_endf(info, repodir, njoyexe):
    """Process one neutron ENDF file in FENDL library."""
    fendl_paths = determine_fendl_paths(info, repodir, njoyexe)
    check_input_files_available(fendl_paths)
    if should_reprocess(info, repodir, njoyexe):
        for k in fendl_paths:
            if k in ('n_endf', 'ph_endf', 'njoyinp', 'njoyexe'):
                continue  # we do not delete input files!
            if os.path.isfile(fendl_paths[k]) or os.path.islink(fendl_paths[k]):
                os.unlink(fendl_paths[k])
        trackfile = fendl_paths.pop('track')
        run_fendl_njoy(fendl_paths)
        curhashes = {k: filehash(f) for k,f in fendl_paths.items()}
        with open(trackfile, 'w') as outf:
            json.dump(curhashes, outf, indent=4)
    return


def process_fendl_file(fname, repodir, njoyexe):
    endf_sublib = os.path.join(repodir, 'fendl-endf/general-purpose/neutron')
    info = get_endf_info(os.path.join(endf_sublib, fname))
    process_fendl_endf(info, repodir, njoyexe)
    return


def process_fendl_neutron_lib(repodir, njoyexe):
    """Process all neutron ENDF files in FENDL library."""
    endf_sublib = os.path.join(repodir, 'fendl-endf/general-purpose/neutron')
    endf_files = os.listdir(endf_sublib)
    for cur_endf_file in endf_files:
        process_fendl_file(cur_endf_file, repodir, njoyexe)
    return


if __name__ == '__main__':

    process_fendl_neutron_lib('.', '/opt/NJOY2016/bin/njoy')
