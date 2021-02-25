#!/bin/bash
mkdir training_data_merged_r2
FLIST=`cat ./domain.pddl | grep ":action" | cut -d' ' -f6`

for F in $FLIST; do
    BF="${F}.csv"
    for i in `seq 2 24`; do
        cat ./training_data_r2${i}/training/$BF >> ./training_data_merged_r2/$BF
    done
done
