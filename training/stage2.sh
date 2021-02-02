#!/bin/bash
# python2.7 ../src/subdominization-training/gen-subdom-training.py runs_folder ./rules_file training_data
# runs_folder is where the data is (first cmdline arg)
pypy3 ../src/subdominization-training/gen-subdom-training.py $1 ./rules_file training_data
