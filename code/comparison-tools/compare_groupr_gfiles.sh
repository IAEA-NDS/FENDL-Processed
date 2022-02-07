#!/bin/sh
############################################################
#
# Author:       Georg Schnabel
# Email:        g.schnabel@iaea.org
# Date:         2022/02/07
# Institution:  IAEA
#
# Compare most recent version of a GROUPR produced
# file in a git-annex repository to the previous version.
# Small numerical differences are ignored.
#
# Usage:
#     compare_groupr_gfiles.sh <filename>
#
#     <filename>: Name of the file that should be compared.
#
############################################################
fname="$1"
fname1="$(git show HEAD~:./$fname)"
fname2="$(git show HEAD:./$fname)"
tmpdir=$(mktemp -d)
tmpfile1=$tmpdir/file1
tmpfile2=$tmpdir/file2

# space apart the fields to make sure that
# numbers are separated by spaces
cut -c1-11,12-22,23-33,34-44,45-55,56-66,67- --output-delimiter='   ' $fname1 > $tmpfile1
cut -c1-11,12-22,23-33,34-44,45-55,56-66,67- --output-delimiter='   ' $fname2 > $tmpfile2
# introduce the E into the fortran number format, e.g., 0.23+3 to 0.23E+3
sed -i 's/\([0-9]\)\([+-][0-9]\)/\1E\2/g' $tmpfile1
sed -i 's/\([0-9]\)\([+-][0-9]\)/\1E\2/g' $tmpfile2

numdiff -q -r 1e-4 -a 1e-10 $tmpfile1 $tmpfile2 > /dev/null
if [ "$?" != 0 ]; then
    echo Difference in $fname
    echo $tmpdir
else
    rm -rf $tmpdir
fi
