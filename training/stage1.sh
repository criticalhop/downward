#!/bin/bash
# mkdir -p runs_folder
# runs_folder is where the data is (first cmdline arg)
pypy3 ../src/subdominization-training/gen-subdom-rules.py --store_rules rules_file --runs $1 domain.pddl
