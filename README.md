# Fusion Evaluated Nuclear Data Library

This repository keeps track of updates to
files derived from the ENDF files of the
Fusion Evaluated Nuclear Data Library (FENDL)
whose different versions are published on the
IAEA-NDS website at <https://nds.iaea.org/fendl/>.
These types of derived files are included
(n, p, d, ph indicates their presence for neutrons, protons,
deuterons, and photons respectively):

- NJOY input and output files (n, p, d)
- ACE files for Monte Carlo codes (n, p, d)
- MATXS for deterministic transport calculations (n)
- GENDF files for sensitivity studies (n)
- Plots to visualize cross sections (n, p, d)
- Plots to visualize heating (n)
- HDF5 files for OpenMC (n, ph)

The photo-atomic HDF5 files are stored in the `general-purpose/atom`
directory. The photo-atomic sublibrary is referred to as `photon`
on the command line of the processing pipeline, but its derived
files are placed under the `atom` directory for historic continuity
with the naming used for the photo-atomic ENDF source files and on
the IAEA-NDS website.

Please note that these files are not directly stored
in this repository but symlinks to them. The
command line tool [git-annex] is used to download
the files, most easily with the [FENDL-Get] tool described
[below](#quick-start-downloading-files-with-fendl-get), which takes
care of installing and setting up git-annex for you.
Alternatively, you can download the files from the [IAEA-NDS website].
Please take note of the [terms of use] for this repository.

[terms of use]: TERMS_OF_USE.md
[IAEA-NDS website]: https://nds.iaea.org/fendl/


## Quick start: downloading files with FENDL-Get

**The current development version to be tested by collaborators is
`FENDL-3.2d-T4`.**

The easiest way to download files of this repository is [FENDL-Get].
It installs git-annex in an isolated Python environment, clones the
repository, checks out the requested version and downloads the
selected files with a single command, on Linux, macOS and Windows.
For example, the ACE files of the neutron sublibrary of FENDL-3.2d-T4
are downloaded on Linux and macOS with
```
curl -LO https://raw.githubusercontent.com/iaea-nds/fendl-get/v1.0.0/fendl-get.sh
chmod +x fendl-get.sh
./fendl-get.sh -r FENDL-3.2d-T4 -t ace -p neutron
```
On Windows (PowerShell):
```
curl.exe -LO https://raw.githubusercontent.com/iaea-nds/fendl-get/v1.0.0/fendl-get.ps1
powershell -ExecutionPolicy Bypass -File .\fendl-get.ps1 -Release FENDL-3.2d-T4 -Type ace -Particle neutron
```
See [FENDL-Get] for all file types and options. The following
sections explain how to use git and git-annex directly instead.

[FENDL-Get]: https://github.com/iaea-nds/fendl-get


## Installation of git-annex

The command line tool [git-annex] must be installed on your system
(not needed if you use [FENDL-Get], which installs it for you).
The easiest way is to install it with `pip` into a Python virtual
environment. On Linux and macOS:
```
python3 -m venv ~/git-annex-venv
~/git-annex-venv/bin/pip install --upgrade pip
~/git-annex-venv/bin/pip install git-annex
export PATH="$HOME/git-annex-venv/bin:$PATH"
```
The last line lets `git annex` find the program; add it to your
shell's startup file (e.g. `~/.bashrc` or `~/.zshrc`) to make it
permanent. Updating pip first is needed with older Python versions,
e.g. the Python 3.9 of the macOS Command Line Tools, whose pip does
not recognise the binaries of the git-annex package.

The [git-annex package on PyPI][git-annex-pypi] provides binaries for
Linux with glibc 2.34 or newer (e.g. Ubuntu 22.04, Debian 12, RHEL 9
and newer) on x86_64 and aarch64, for macOS 15 or newer, and for
Windows. On Windows, git-annex is easiest to use through
[FENDL-Get], which sets up the repository as needed. Installation
instructions for other systems can be found [here][git-annex-install].

[git-annex]: https://git-annex.branchable.com/
[git-annex-install]: https://git-annex.branchable.com/install/
[git-annex-pypi]: https://pypi.org/project/git-annex/


## Downloading files with git and git-annex

The command line tool `git` can be used in the usual way to
browse different versions of the repository. First,
download the repository to your local computer:
```
git clone --recurse-submodules https://github.com/iaea-nds/fendl-processed
```
The argument `--recurse-submodules` ensures that also
the source ENDF files in the `fendl-endf` subfolder are downloaded.
After changing into the directory of the repository,
check out the specific version of FENDL you
are interested in. For instance, to use FENDL-3.2d-T4:
```
git checkout FENDL-3.2d-T4
git submodule update
```
The second instruction makes sure that the ENDF files in the
`fendl-endf` directory are indeed the versions used as source
files to generate the derived files.

### Enabling the storage locations

The files of the FENDL-3.2d test versions are stored in public
Amazon S3 buckets. Before the first download, tell git-annex where
to find them (once per clone). In the root directory of the repository:
```
git annex enableremote 4737e67e-3733-4035-8715-a2747c323879 \
    public=yes publicurl=https://fendl-processing-storage.s3.eu-north-1.amazonaws.com/
```
and for the ENDF files in the `fendl-endf` submodule:
```
cd fendl-endf
git annex enableremote 2cf4d611-eca6-4062-9bb9-ac099534b9e3 \
    public=yes publicurl=https://fendl-endf-storage.s3.eu-north-1.amazonaws.com/
cd ..
```
The long identifiers select the storage locations unambiguously.
No account or credentials are needed, the files are downloaded
anonymously. (If you have AWS credentials in your environment, e.g.
`AWS_ACCESS_KEY_ID`, unset them first: git-annex would otherwise use
them, fail on the public storage and store them in the clone.)

git-annex 10.20261026 and later additionally ask you to confirm the
configuration of a storage location before using it. Run
```
git annex verifyremote fendl-proc-aws-s3
```
check that the configuration it shows contains
`bucket=fendl-processing-storage`, and then run the command
`git annex verifyremote fendl-proc-aws-s3 --safe ...` that it prints.
Do the same in the `fendl-endf` directory with `fendl-endf-aws-s3`
(`bucket=fendl-endf-storage`). Older versions of git-annex do not
have this command and need no confirmation.

Files of older FENDL versions are also available from the IAEA-NDS
web server, which git-annex uses without these steps.

git-annex records its state in git commits. If git reports that it
does not know who you are (e.g. "Please tell me who you are" or
"empty ident name"), set your name and email address once:
```
git config --global user.name "Your Name"
git config --global user.email "you@example.org"
```

### Downloading

All derived files are available as (broken) symbolic links.
In order to download their content, you need to use `git-annex`.
For instance, being at the root directory of the repository,
you can download all the processed files of the neutron transport sublibrary
using the command
```
git annex get --jobs=4 general-purpose/neutron
```
This command works recursively, so running `git annex get .`
at the root will download all derived files in this repository.
The `--jobs` argument enables the download of files in parallel.
It is also possible to download individual files, e.g.
```
git annex get general-purpose/neutron/ace/08O_018
```

After running `git annex get`, the symbolic links will not
be broken anymore and point to the files that store the
file contents. These files are stored in the
`.git/annex` directory but you should not directly
interact with this directory and instead use the functionality
of `git-annex`.

If you want to remove dowloaded files, e.g., because you
are running out of space, you can use `git-annex-drop`:
```
git annex drop general-purpose/neutron
```
It will remove the files from the annex and symlinks
in the repository will be broken again.
You can re-download them whenever needed
using the `git annex get` command explained above.

## Re-generating derived files

A [customized version][NJOY2016-iaea] of [NJOY2016]
has been used to generate the derived files. 
If you make changes to the ENDF source
files or for any other reason, you can re-generate the
processed files of the sublibraries yourself using exactly
the same processing pipeline used at the IAEA-NDS.
Make sure [Apptainer] is available on your system.

For the following, it is assumed that you have already
checked out the specific version of the FENDL library
using the instructions of the previous section.

First, you need to download all relevant ENDF files.
Change into the `fendl-endf` directory (which is registered
as a git submodule), and download the required ENDF files
(for the FENDL-3.2d test versions, enable the storage locations
first, see [above](#enabling-the-storage-locations)):
```
cd fendl-endf
git annex get --jobs=4 general-purpose
```
For regenerating processed files only for one of the sublibraries,
use the sublibrary path instead, e.g. `general-purpose/neutron`
for the neutron sublibrary. Processing the neutron sublibrary also
needs the photo-atomic ENDF files, so download those as well:
```
git annex get --jobs=4 general-purpose/neutron general-purpose/atom
```

Change again into the root folder of the
`FENDL-Processed` repo and download the required
NJOY2016 input files:
```
cd ..
git annex get --jobs=4 general-purpose/*/njoy/*.nji
```
You also need to download the Apptainer image
that contains the processing pipeline:
```
git annex get code/process_fendl.sif
```
As an aside, the Apptainer image file
(sif) was created from an Apptainer definition
file (def), see the next section.

Finally, launch the Apptainer image to
generate all derived files using
NJOY2016 with patches from the IAEA-NDS:
```
apptainer run code/process_fendl.sif
```
You can execute this command several
times in parallel to speed up the re-creation
of derived files.

To re-process only a specific sublibrary (neutron, proton, deuteron,
or photon), provide the sublibrary name as argument, e.g.
```
apptainer run code/process_fendl.sif neutron
```

To re-process only a single ENDF file from a sublibrary, provide
the ENDF filename as second argument, e.g.
```
apptainer run code/process_fendl.sif neutron n_0728_7-N-15.endf
```
The last step of the processing writes the `cross_sections.xml` file
for OpenMC, which requires the HDF5 files of all nuclides of the
sublibrary. If you re-process only a single file, the run therefore
ends with an error message about a missing `.h5` file (e.g.
`general-purpose/neutron/hdf5/Ag107.h5`). The derived files of the
selected ENDF file have been created at that point.

To produce only specific output formats, use the `--formats` flag
with `ace` and/or `hdf5` (default: both), e.g.
```
apptainer run code/process_fendl.sif neutron --formats hdf5
```

If you haven't modified any of the NJOY input files
and ENDF files, the re-created output files (ace, pdf, etc.)
should be identical to the files registered in
this repository. You can check whether this is true by executing
```
git annex lock general-purpose
```
Locking (moving the files into the annex and
replacing them by symlinks to the annex) will
only succeed if the files are identical to the
registered ones.


[NJOY2016-iaea]: https://github.com/IAEA-NDS/NJOY2016
[Apptainer]: https://apptainer.org
[NJOY2016]: https://github.com/njoy/NJOY2016


## Creating the Apptainer image

The Apptainer image file `code/process_fendl.sif`
can be created from the Apptainer definition file
`code/process_fendl.def` in the following way:
```
cd code
apptainer build process_fendl.sif process_fendl.def
```

This needs to be done if you want to perform the
processing with another NJOY2016 version and
changed the NJOY2016 commit id in the `process_fendl.def`
file.
