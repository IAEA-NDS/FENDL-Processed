# Fusion Evaluated Nuclear Data Library

This repository keeps track of updates to the
processed files of the Fusion Evaluated Nuclear Data Library (FENDL)
whose different versions are published on the
IAEA-NDS website at <https://www-nds.iaea.org/fendl/>.

The ENDF files associated with the processed files in this repository
are located at <https://github.com/IAEA-NDS/FENDL-ENDF>.

Please note that large files are not directly stored
in this repository but rather symlinks to them. The targets
of the symlinks contain cryptographic hashes that can be
used to verify whether a given file is indeed the correct
target of a symlink.

The command line tool
[git-annex](https://git-annex.branchable.com/) can be used
to download individually or in bulk current or previous
versions of files in this repository. For more information
on the data management, please
visit the [fendl-code](https://github.com/iaea-nds/fendl-code)
repository.

