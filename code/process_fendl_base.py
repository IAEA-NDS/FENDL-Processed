import os
import json
import hashlib
import re
import sys
from njoy_file_manipulation import (
    set_ace_comment,
    set_g_comment,
    set_gam_comment,
    set_m_comment,
    get_m_long_comments,
    set_m_long_comments,
    set_reconr_comments1,
    set_reconr_comments2,
    set_moder_comment,
    set_acefile_date,
    zero_njoy_outfile_durations,
    set_njoy_outfile_date
)
from pdf_manipulation import remove_metadata_from_pdf
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
            return njoy_version + 'NDS'
    raise ValueError('unable to determine NJOY version')


def extract_isotope_info(njoyinp):
    m = re.match(r'([0-9]+)([a-zA-Z]+)_?([0-9]+m?)', njoyinp)
    if not m:
        raise ValueError('regular expression did not match')
    charge = m.group(1)
    sym = m.group(2).title()
    mass = m.group(3).lstrip('0')
    return charge, sym, mass


def update_njoy_inputfile(njoyinp, njoyvers, fendlvers, cdate):
    with open(njoyinp, 'r') as fin:
        lines = fin.readlines()
    lines = [s.rstrip('\n') for s in lines]
    njoyinp_basename = os.path.basename(njoyinp)
    osd = os.path.dirname
    particle = os.path.basename(osd(osd(njoyinp)))
    if particle not in ('neutron', 'proton', 'deuteron'):
        raise ValueError('first letter of nji filename must be n,p or d')
    charge, sym, mass = extract_isotope_info(njoyinp_basename)
    fullsym = f"{charge}-{sym}-{mass}"
    comment = f"{fullsym} {fendlvers} (NJOY{njoyvers})"
    moder_comment = f"{fullsym} {fendlvers}"
    set_moder_comment(lines, moder_comment)
    reconr_comments1 = [
        f"PENDF for {fullsym}",
        f"{fullsym} {fendlvers}",
        f"Processed by NJOY{njoyvers}"
    ]
    set_reconr_comments1(lines, reconr_comments1)
    set_ace_comment(lines, comment)
    if particle == 'n':
        set_g_comment(lines, comment)
        set_gam_comment(lines, comment)
        m_comment = (' '*8 + sym.lower() + mass).ljust(16)
        set_m_comment(lines, m_comment)
        long_m_comments = get_m_long_comments(lines)
        long_m_comments[0] = f"{fullsym} {fendlvers}"
        long_m_comments[2] = f"Processed by NJOY{njoyvers}"
        set_m_long_comments(lines, long_m_comments)
        reconr_comments2 = [
            f"PENDF photo-atomic data for {fullsym}",
            f"{fullsym} {fendlvers}",
            f"Processed by NJOY{njoyvers}"
        ]
        set_reconr_comments2(lines, reconr_comments1)
    os.unlink(njoyinp)
    lines = [s + '\n' for s in lines]
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
    update_njoy_inputfile(njoyinp, njoyvers, fendlvers, cdate)
    if should_reprocess(fendl_paths):
        for k, curpath in fendl_paths['outputs'].items():
            if os.path.isfile(curpath) or os.path.islink(curpath):
                os.unlink(curpath)
        trackfile = fendl_paths['trackfile']
        run_fendl_njoy(fendl_paths)
        # specify dates and remove metadata of pdfs for reproducibility
        for p in fendl_paths['outputs'].values():
            if p.endswith('.pdf'):
                remove_metadata_from_pdf(p, cdate)
        ace_file = fendl_paths['outputs']['ace']
        set_acefile_date(ace_file, cdate)
        njoy_outfile = fendl_paths['outputs']['njoyout']
        set_njoy_outfile_date(njoy_outfile, cdate)
        zero_njoy_outfile_durations(njoy_outfile)
        # record checksums
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
