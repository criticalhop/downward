#!/bin/bash
# python2.7 ../src/subdominization-training/gen-subdom-training.py runs_folder ./rules_file training_data
# runs_folder is where the data is (first cmdline arg)
# --num-test-instances NUM_TEST_INSTANCES
pypy3 ../src/subdominization-training/gen-subdom-training.py --num-test-instances 2000 $1 ./relevant_rules training_data
