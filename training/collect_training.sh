#!/bin/bash

FLIST=`cat ./domain.pddl | grep ":action" | cut -d' ' -f6`

for F in $FLIST; do
    BF="${F}.csv"
    for i in `seq 2 24`; do
        cat ./training_data${i}/training/$BF >> ./training_data_merged/$BF
    done
done