#!/bin/sh
############################################################
#
# Author:       Georg Schnabel
# Email:        g.schnabel@iaea.org
# Date:         2022/02/07
# Institution:  IAEA
#
# Compare most recent version of the output file
# produced by NJOY2016 with the previous verson.
# stored in a git-annex repository.
# Small numerical differences are ignored.
#
# Usage:
#     compare_njoy_output.sh <filename> 
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

# remove the header
tail $fname1 -n+11 > $tmpfile1
tail $fname2 -n+11 > $tmpfile2
# remove the dates
sed -i 's/[0-9][0-9]\/[0-9][0-9]\/[0-9][0-9]//' $tmpfile1
sed -i 's/[0-9][0-9]\/[0-9][0-9]\/[0-9][0-9]//' $tmpfile2
# remove trailing whitespace
sed -i 's/ *$//' $tmpfile1
sed -i 's/ *$//' $tmpfile2
# convert fortran number format
sed -i 's/\([0-9]\)\([+-][0-9]\)/\1E\2/g' $tmpfile1
sed -i 's/\([0-9]\)\([+-][0-9]\)/\1E\2/g' $tmpfile2
# remove the timings because system-dependent
sed -i 's/ *[0-9]\+.[0-9]\+s *$//' $tmpfile1
sed -i 's/ *[0-9]\+.[0-9]\+s *$//' $tmpfile2

numdiff -q -r 1e-4 -a 1e-10 $tmpfile1 $tmpfile2 > /dev/null
if [ "$?" != 0 ]; then
    echo Difference in $fname
    echo $tmpdir
else
    rm -rf $tmpdir
fi
