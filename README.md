# Fusion Evaluated Nuclear Data Library

This repository keeps track of updates to
files derived from the ENDF files of the
Fusion Evaluated Nuclear Data Library (FENDL)
whose different versions are published on the
IAEA-NDS website at <https://nds.iaea.org/fendl/>.
These types of derived files are included
(n, p, d indicates their presence for neutrons, protons,
and deuterons respectively):

- NJOY input and output files (n, p, d)
- ACE files for Monte Carlo codes (n, p, d)
- MATXS for deterministic transport calculations (n)
- GENDF files for sensitivity studies (n)
- Plots to visualize cross sections (n, p, d)
- Plots to visualize heating (n)

Please note that these files are not directly stored
in this repository but symlinks to them. The
command line tool [git-annex] can be used to download
the files. Alternatively, you can download them from the [IAEA-NDS website].
Please take note of the [terms of use] for this repository.

[terms of use]: TERMS_OF_USE.md
[IAEA-NDS website]: https://nds.iaea.org/fendl/


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
using the command
```
git annex get --jobs=4 general-purpose/neutron
```
This command works recursively, so running `git annex get .`
at the root will download all derived files in this repository.
The `--jobs` argument enables the download of files in parallel.
It is also possible to download individual files, e.g.
```
git annex get general-purpose/neutron/n_0831_8-O-18.endf
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
as a git submodule), and download the required ENDF files:
```
cd fendl-endf
git annex get --jobs=4 general-purpose
```
For regenerating processed files only for one of the sublibraries,
use the sublibrary path instead, e.g. `general-purpose/neutron`
for the neutron sublibrary.

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

To re-process only a specific sublibrary (neutron, proton or deuteron),
provide the sublibrary name as argument, e.g.
```
apptainer run code/process_fendl.sif neutron
```

To re-process only a single ENDF file from a sublibrary, provide
the ENDF filename as second argument, e.g.
```
apptainer run code/process_fendl.sif neutron n_0728_7-N-15.endf
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
