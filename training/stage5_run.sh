#!/bin/bash

# ./fast-downward.py problem.pddl --translate-options --grounding-action-queue-ordering noveltyfifo --termination-condition goal-relaxed-reachable min-number 10000 --search-options --search "astar(blind)"
./fast-downward.py problem.pddl --translate-options --grounding-action-queue-ordering trained --trained-model-folder "" --termination-condition goal-relaxed-reachable min-number 10000 --search-options --search "astar(blind)"

exit 0

# This is for translate only

python ./translate.py domain.pddl  problem.pddl --grounding-action-queue-ordering trained --trained-model-folder "learned_model" --termination-condition goal-relaxed-reachable min-number 10000 