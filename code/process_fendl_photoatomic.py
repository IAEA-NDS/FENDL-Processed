############################################################
#
# This script produces the processed files of the FENDL
# photo-atomic sublibrary in OpenMC HDF5 format.
#
# Usage:
#     Run from the root directory of the
#     FENDL-processed directory:
#
#     python process_fendl_photoatomic.py
#
############################################################

import os

from process_fendl_base import (
    process_fendl_sublib,
    get_njoy_version,
    get_fendl_version,
    get_creation_date,
)


def run_fendl_njoy(pardic):
    """Produce HDF5 photo-atomic file from ENDF (no NJOY needed)."""
    import warnings
    import openmc.data
    inputs = pardic['inputs']
    outputs = pardic['outputs']
    os.makedirs(os.path.dirname(outputs['h5']), exist_ok=True)
    with warnings.catch_warnings():
        warnings.simplefilter('ignore', UserWarning)
        data = openmc.data.IncidentPhoton.from_endf(inputs['ph_endf'])
    data.export_to_hdf5(outputs['h5'], 'w')
    return


def determine_fendl_paths(info, repodir, njoyexe, njoylib):
    """Return dictionary with paths to photo-atomic FENDL outputs."""
    if info['incpart'] != 'ph':
        raise ValueError('The info dic should be for photo-atomic data')
    ph_endf_file = 'ph_%04d_%d-%s.endf' % (
        info['matnr'], info['charge'], info['symb']
    )
    h5_file = '%s.h5' % info['symb']
    track_file = '%s.json' % info['symb']
    fendl_paths = {}
    fendl_paths['inputs'] = {
        'config': os.path.join(repodir, 'config.py'),
        'ph_endf': os.path.join(
            repodir, 'fendl-endf/general-purpose/atom', ph_endf_file
        ),
    }
    fendl_paths['outputs'] = {
        'h5': os.path.join(repodir, 'general-purpose/photon/hdf5', h5_file),
    }
    fendl_paths['trackfile'] = os.path.join(
        repodir, 'trackdb/trackdb_photon', track_file
    )
    return fendl_paths


def process_fendl_photoatomic_lib(
    repodir, njoyexe, njoylib, njoyvers, fendlvers, cdate, endf_file=None
):
    """Process all photo-atomic ENDF files in FENDL library."""
    endf_sublib = os.path.join('fendl-endf', 'general-purpose/atom')
    process_fendl_sublib(repodir, endf_sublib, run_fendl_njoy,
                         determine_fendl_paths, njoyexe, njoylib,
                         njoyvers, fendlvers, cdate, endf_file=endf_file)


if __name__ == '__main__':
    njoyvers = get_njoy_version('/opt/NJOY2016')
    fendlvers = get_fendl_version()
    cdate = get_creation_date()
    process_fendl_photoatomic_lib(
        '.', '/opt/NJOY2016/bin/njoy', '/opt/NJOY2016/bin/libnjoy.so',
        njoyvers, fendlvers, cdate
    )
