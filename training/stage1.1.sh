#!/bin/bash
# mkdir -p runs_folder
# runs_folder is where the data (sas_plan, all_operators.bz2) is (first cmdline arg)
# !!! IMPORTANT supply correct domain file
# ./gen-subdom-rules.py --store_rules <output_rule_file> --rule_size RULE_SIZE --num_rules NUM_RULES --runs <runs> <domain>
# pypy3 ../src/subdominization-training/gen-subdom-rules.py --store_rules rules_file --rule_size 10 --num_rules 5000 --runs $1 domain.pddl
# pypy3 ../src/subdominization-training/gen-relevant-rules.py  [--instances-relevant-rules INSTANCES_RELEVANT_RULES] [--max-training-examples MAX_TRAINING_EXAMPLES] <runs> <training_rules> <output>
pypy3 ../src/subdominization-training/gen-relevant-rules.py  /var/data/userdata/flat_training rules_file relevant_rules_file

