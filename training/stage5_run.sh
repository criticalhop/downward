#!/bin/bash

# ./fast-downward.py problem.pddl --translate-options --grounding-action-queue-ordering noveltyfifo --termination-condition goal-relaxed-reachable min-number 10000 --search-options --search "astar(blind)"
./fast-downward.py problem.pddl --translate-options --grounding-action-queue-ordering trained --trained-model-folder "" --termination-condition goal-relaxed-reachable min-number 10000 --search-options --search "astar(blind)"

exit 0

# This is for translate only

python ./translate.py domain.pddl  problem.pddl --grounding-action-queue-ordering trained --trained-model-folder "learned_model" --termination-condition goal-relaxed-reachable min-number 10000 
# matplotlib is required to run this

python ./translate.py --sas-file ./OUT.SAS --grounding-action-queue-ordering trained --termination-condition goal-relaxed-reachable --trained-model-folder /home/grandrew/sandbox/downward_ch/training/learning_m /home/grandrew/sandbox/downward_ch/training/runs_folder/1602629308_YIY5D/domain.pddl /home/grandrew/sandbox/downward_ch/training/runs_folder/1602629308_YIY5D/problem.pddl
