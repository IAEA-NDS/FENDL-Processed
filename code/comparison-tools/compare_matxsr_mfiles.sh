#!/bin/sh
############################################################
#
# Author:       Georg Schnabel
# Email:        g.schnabel@iaea.org
# Date:         2022/02/07
# Institution:  IAEA
#
# Compare most recent version of a MATXSR produced file
# to the previous version in a git-annex repository.
# Small numerical differences are ignored.
#
# Usage:
#     compare_matxsr_mfiles.sh <filename> 
#
#     <filename>: Name of the file for comparison.
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
cut -c1-12,13-24,25-36,37-48,49-60,61-72,73- --output-delimiter='   ' $fname1 > $tmpfile1
cut -c1-12,13-24,25-36,37-48,49-60,61-72,73- --output-delimiter='   ' $fname2 > $tmpfile2
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
