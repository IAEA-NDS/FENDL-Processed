import os
import json
import hashlib
import re
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), os.pardir))
from config import CREATION_DATE, FENDL_VERSION


def get_fendl_version():
    return FENDL_VERSION


def get_creation_date():
    return CREATION_DATE


def get_njoy_version(njoy_path):
    version_file = os.path.join(njoy_path, 'src', 'vers.f90')
    with open(version_file, 'r') as f:
        lines = f.readlines()
    for line in lines:
        m = re.search(r"public::vers='(.*)'", line)
        if m:
            njoy_version = m.group(1).strip()
            return njoy_version
    raise ValueError('unable to determine NJOY version')


def update_njoy_version_in_njoy_inputfile(njoyinp, njoyvers):
    with open(njoyinp, 'r') as fin:
        lines = fin.readlines()
    lines = [re.sub('NJOY[0-9+.]+', f'NJOY{njoyvers}', ln) for ln in lines]
    os.unlink(njoyinp)
    with open(njoyinp, 'w') as fout:
        fout.writelines(lines)


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


def check_input_files_available(fendl_paths):
    fendl_paths = fendl_paths['inputs']
    for fname in fendl_paths.values():
        if not os.path.isfile(fname):
            raise FileNotFoundError(f'required input file `{fname}` was not found')
    return


def should_reprocess(fendl_paths):
    """Return boolean indicating whether running NJOY is necessary"""
    for k, f in fendl_paths['outputs'].items():
        if not os.path.isfile(f):
            return True
    trackfile = fendl_paths['trackfile']
    if not os.path.isfile(trackfile):
        return True
    with open(trackfile, 'r') as f:
        storedhashes = json.load(f)
    curhashes = {k: filehash(f) for k, f in fendl_paths['outputs'].items()}
    for k in curhashes:
        if curhashes[k] != storedhashes['outputs'][k]:
            raise ValueError(
                'Hashes of output files do not match those in trackdb!\n'
                'maybe files were reprocessed without using this script?'
            )

    curhashes = {k: filehash(f) for k, f in fendl_paths['inputs'].items()}
    for k in curhashes:
        if curhashes[k] != storedhashes['inputs'][k]:
            return True
    return False


def process_fendl_endf(run_fendl_njoy, fendl_paths, njoyvers, fendlvers, cdate):
    """Process one neutron ENDF file in FENDL library."""
    check_input_files_available(fendl_paths)
    njoyinp = fendl_paths['inputs']['njoyinp']
    update_njoy_version_in_njoy_inputfile(njoyinp, njoyvers)
    if should_reprocess(fendl_paths):
        for k, curpath in fendl_paths['outputs'].items():
            if os.path.isfile(curpath) or os.path.islink(curpath):
                os.unlink(curpath)
        trackfile = fendl_paths['trackfile']
        run_fendl_njoy(fendl_paths)
        curhashes_inputs = {k: filehash(f) for k, f in fendl_paths['inputs'].items()}
        curhashes_outputs = {k: filehash(f) for k, f in fendl_paths['outputs'].items()}
        curhashes = {'inputs': curhashes_inputs, 'outputs': curhashes_outputs}
        with open(trackfile, 'w') as outf:
            json.dump(curhashes, outf, indent=4)
    return


def process_fendl_sublib(
    repodir, sublib_path, run_njoy, determine_fendl_paths,
    njoyexe, njoylib, njoyvers, fendlvers, cdate, endf_file=None
):
    endf_sublib = os.path.join(repodir, sublib_path)
    endf_files = os.listdir(endf_sublib)
    for cur_endf_file in endf_files:
        if endf_file is not None and endf_file != cur_endf_file:
            continue
        fendl_endf_file = os.path.join(endf_sublib, cur_endf_file)
        info = get_endf_info(fendl_endf_file)
        fendl_paths = determine_fendl_paths(info, repodir, njoyexe, njoylib)
        process_fendl_endf(run_njoy, fendl_paths, njoyvers, fendlvers, cdate)
