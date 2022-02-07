#!/bin/sh
############################################################
#
# Author:       Georg Schnabel
# Email:        g.schnabel@iaea.org
# Date:         2022/02/07
# Institution:  IAEA
#
# This script compares different versions
# of an ace file in the git-annex repository
# to check if numerically significant differences
# are present.
#
# Usage:
#     compare_ace.sh <commit1> <commit2> <filename>
#
#     <commit1>:  Commit id with the earlier version
#     <commit2>:  Commit id with the later version
#     <filename>: The name of the file for comparison
#
############################################################

commit1="$1"
commit2="$2"
fpath="$3"
fname=$(basename $fpath)
fdir=$(dirname $fpath)

file1=$(git show ${commit1}:./$fdir/$fname)
file2=$(git show ${commit2}:./$fdir/$fname)

mytmp=$(mktemp -d)
tmpfile1="$mytmp/file1"
tmpfile2="$mytmp/file2"

cp $fdir/$file1 $tmpfile1
cp $fdir/$file2 $tmpfile2

regex='1s/[0-9][0-9]\/[0-9][0-9]\/[0-9][0-9]//'
sed -i $regex $tmpfile1
sed -i $regex $tmpfile2

numdiff -q -r 1e-5 -a 1e-10 $tmpfile1 $tmpfile2
if [ "$?" != 0 ]; then
    echo difference for $filename
fi

rm -rf $mytmp
