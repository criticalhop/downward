#!/bin/bash
# python2.7 ../src/subdominization-training/gen-subdom-training.py runs_folder ./rules_file training_data
# runs_folder is where the data is (first cmdline arg)
# --num-test-instances NUM_TEST_INSTANCES
for procid in `seq 2 24`; do
	pypy3 ../src/subdominization-training/gen-subdom-training.py --num-test-instances 30 /var/data/userdata/flat_training${procid} ./relevant_rules_file_r2_all training_data_r2${procid} &
done
wait
