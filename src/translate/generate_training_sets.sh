
RUNS_FOLDER=~/Desktop/subdominization/subdominization_data/hiking/runs/
RULES_FILE=~/Desktop/subdominization/subdominization_data/hiking/rules/all_rules_size_one
TARGET_DIR=~/Desktop/subdominization/subdominization_data/hiking/training_sets/


rm "$TARGET_DIR/training_data_*.csv"

for a in `ls "$RUNS_FOLDER"`; do
    RUN_FOLDER="$RUNS_FOLDER/$a";
    if [ -e "$RUN_FOLDER/sas_plan" ]
    then
	echo ./gen-subdom-training.py "$RUN_FOLDER"/domain.pddl "$RUN_FOLDER"/problem.pddl --training-rules "$RULES_FILE" --training-plan "$RUN_FOLDER/sas_plan" --store-training-data "$TARGET_DIR";
    fi
done
