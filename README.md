# Fusion Evaluated Nuclear Data Library

This repository keeps track of updates to
files derived from the ENDF files of the
Fusion Evaluated Nuclear Data Library (FENDL)
whose different versions are published on the
IAEA-NDS website at <https://nds.iaea.org/fendl/>.
These types of derived files are included
(n, p, d indicates their presence for neutrons, protons,
and deuterons respectively):

- NJOY input and output files (n, p)
- ACE files for Monte Carlo codes (n, p, d)
- MATXS for deterministic transport calculations (n)
- GENDF files for sensitivity studies (n)
- Plots to visualize cross sections (n, p)
- Plots to visualize heating (n)

Please note that these files are not directly stored
in this repository but symlinks to them. The
command line tool [git-annex] can be used to download
the files. Alternatively, you can download them from the IAEA-NDS website.
Please take note of the [terms of use] for this repository.

[terms of use]: TERMS_OF_USE.md


## Installation of git-annex

The command line tool [git-annex] must be installed on your system.
Installation instructions for various operating systems
can be found [here][git-annex-install]. Windows is for the time being
not well supported. If you are using [conda], you can install
`git-annex` by
```
conda install -c conda-forge git-annex
```

[git-annex]: https://git-annex.branchable.com/
[git-annex-install]: https://git-annex.branchable.com/install/
[conda]: https://docs.conda.io/en/latest/


## Downloading files in this repository

The command line tool `git` can be used in the usual way to
browse different versions of the repository. First,
download the repository to your local computer:
```
git clone --recurse-submodules https://github.com/iaea-nds/fendl-processed
```
The argument `---recurse-submodules` ensures that also
the source ENDF files in the `fendl-endf` subfolder are downloaded.
After changing into the directory of the repository,
check out the specific version of FENDL you
are interested in. For instance, to use FENDL-3.2b:
```
git checkout FENDL-3.2b
git submodule update
```
The second instruction makes sure that the ENDF files in the
`fendl-endf` directory are indeed the versions used as source
files to generate the derived files.

All derived files are available as (broken) symbolic links.
In order to download their content, you need to use `git-annex`.
For instance, being at the root directory of the repository,
you can download all the processed files of the neutron transport sublibrary
by
```
git annex get --jobs=4 general-purpose/neutron
```
This command works recursively so running `git annex get .`
at the root will download all derived files in this repository.
It is also possible to download individual
files. The `--jobs` argument enables the download of files
in parallel.

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

A [customized version][NJOY2016-iaea] of [NJOY2016] has been used to generate
the derived files. 
If you make changes to the ENDF source
files or for any other reason, you can re-generate the
processed files of the neutron sublibrary yourself using exactly
the same processing pipeline used at the IAEA-NDS.
Make sure [Apptainer] is available on your system.

For the following, it is assumed that you have already
checked out the specific version of the FENDL library
using the instructions of the previous section.

First, you need to download all relevant ENDF files.
Change into the `fendl-endf` directory (which is registered
as a git submodule), and download the required ENDF files:
```
cd fendl-endf
git annex get --jobs=4 \
  general-purpose/neutron \
  general-purpose/atom
```

Change again into the root folder of the
`FENDL-Processed` repo and download the required
NJOY2016 input files:
```
cd ..
git annex get --jobs=4 \
  general-purpose/neutron/njoy/*.nji \
  general-purpose/neutron/ace/*.xsd
```
You also need to download the Apptainer image
that contains the processing pipeline:
```
git annex get code/process-fendl.sif
```

Finally, launch the Apptainer image to
generate all derived files using
NJOY2016 with patches from the IAEA-NDS:
```
apptainer run code/process-fendl.sif
```

Please note that not all generated files
will be completly identical to the
files already provided in this repository
even when they are based on the same
ENDF source files.
The reason being that in some generated
files, the date of execution is stored.
Apart from differences related to different
dates, however, the files are expected to be
identical to the ones provided in this
repository due to using exactly the same 
software stack bundled in the Apptainer image.

[NJOY2016-iaea]: https://github.com/IAEA-NDS/NJOY2016
[Apptainer]: https://apptainer.org
[NJOY2016]: https://github.com/njoy/NJOY2016
