Fast Downward Partial Grounding is based on Fast Downward, which is a domain-independent planning system.

For instructions on how to use the Partial Grounding mechanism see below. 

For documentation about Fast Downward and contact information see http://www.fast-downward.org/.

The following directories are not part of Fast Downward as covered by this
license:

* ./src/search/ext
* ./src/subdominization_data/aleph

For the rest, the following license applies:

```
Fast Downward is free software: you can redistribute it and/or modify it under
the terms of the GNU General Public License as published by the Free Software
Foundation, either version 3 of the License, or (at your option) any later
version.

Fast Downward is distributed in the hope that it will be useful, but WITHOUT ANY
WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A
PARTICULAR PURPOSE. See the GNU General Public License for more details.

You should have received a copy of the GNU General Public License along with
this program. If not, see <http://www.gnu.org/licenses/>.
```


**Instructions to run the partial grounding algorithms.**

There are two types of partial grounding algorithms: 
A) ad-hoc algorithms that work on any given problem without prerequisites,
B) algorithms based on learning a model for a specific domain.


## RUNNING PARTIAL GROUNDING WITH OR WITHOUT A TRAINED MODEL
For A) the following options are available:

- Sorting of actions during grounding (priority functions):
fifo => ground actions in first-in-first-out order; this is the default of fast downward
lifo => ground actions in last-in-first-out order
random => random action ordering
roundrobin => one FIFO priority queue per action schema, grounding on action per schema before proceeding to the next schema.
noveltyfifo => sorting actions in the queue by their "novelty" score
roundrobinnovelty => one noveltyfifo queue per action schema

For learning-based grounding as of B), there are additionally the following options:
trained => ordering of actions based on the priority learned by an ML model; requires the option "--trained-model-folder" to points to a directory that contains a file SCHEMA.model for each actions schema SCHEMA defined in the PDDL domain that it was trained on.
roundrobintrained => same as trained, with a separate priority queue per action schema
aleph => similar to the *trained queues, it requires an additional option "--aleph-model-file" that specifies a file that contains the model learned by aleph for the given domain
roundrobinaleph => same as aleph, with a separate priority queue per action schema

- Termination condition:
default     => perform full grounding; this is the default of fast downward
goal-relaxed-reachable  => stop the grounding process when the goal is delete-relaxed reachable
goal-relaxed-reachable [number NUMBER] 
=> stop the grounding process when the goal is delete-relaxed reachable and NUMBER actions have been grounded since the goal became delete-relaxed reachable

goal-relaxed-reachable [min-number NUMBER] 
=> stop the grounding process when the goal is delete-relaxed reachable and at least NUMBER actions have been grounded

goal-relaxed-reachable [percentage NUMBER] 
=> stop the grounding process when the goal is delete-relaxed reachable and, say X is the number of actions grounded when the goal becomes delete-relaxed reachable, (100 + NUMBER)% * X actions have been grounded.

goal-relaxed-reachable [percentage NUMBER1 min-increment NUMBER2] 
=> stop the grounding process when the goal is delete-relaxed reachable and at least max(#RS * NUMBER1%, NUMBER2) + #RS actions have been grounded, where #RS is the number of actions grounded when the goal becomes relaxed reachable.

goal-relaxed-reachable [min-number NUMBER1 percentage NUMBER2 max-increment NUMBER3] 
=> stop the grounding process when the goal is delete-relaxed reachable and at least max(NUMBER1, min(#RS * NUMBER2%, NUMBER3) + #RS) actions have been grounded, where #RS is the number of actions grounded when the goal becomes relaxed reachable.

All termination conditions can be combined arbitrarily with all grounding priority functions.

These options can be used by passing the options "--grounding-action-queue-ordering" and "--termination-condition" to the translator, for example:
./fast-downward.py problem.pddl --translate-options --grounding-action-queue-ordering noveltyfifo --termination-condition goal-relaxed-reachable min-number 10000 --search-options --search "astar(blind)"

Finally, in contrast to the one-shot option described so far, there is the option to run incremental grounding, iteratively increasing the number of grounded actions automatically until a plan is found or full grounding is performed.
The option "--incremental-grounding" is implemented in the driver and can be used as follows:
./fast-downward.py --incremental-grounding /mnt/Daten/Uni/Software/benchmarks-aibasel/nomystery-opt11-strips/p03.pddl --translate-options --grounding-action-queue-ordering noveltyfifo --search-options --search "astar(blind)"
It can be combined with arbitrary priority functions, but no termination condition must be specified. Additionally, the following options are available:
--incremental-grounding-search-time-limit NUMBER => limits the search time for each iteration of the incremental grounding process; given in seconds
--incremental-grounding-minimum NUMBER => minimum number of actions to ground in the first iteration
--incremental-grounding-increment NUMBER => absolute increment in number of actions from one iteration to the next; default is 10000
--incremental-grounding-increment-percentage NUMBER => relative increment in the number of grounded actions from one iteration to the next

If both absolute and relative increment are given, the maximum of both is taken.




## TRAINING A MODEL
The usage of learning algorithms B) is divided in two phases: 
the training phase does offline learning of some models, and the planning phase uses the learned models during grounding.
For the learning phase there are two alternatives: using 

Learning Phase:
* Prerequisites:
   - python3, with libraries: numpy, sklearn, matplotlib, pandas, pylab
   
   - <domain>: A PDDL domain file that is shared accross all training and testing instances.
   - <runs>: A directory containing the training data. It should contain a sub-directory for each instance, which should contain the following files:
        * domain.pddl
        * problem.pddl
        * sas_plan/good_operators: file containing the list of "good" operators, one per line. 
        * all_operators.bz2: file containing a list of all grounded (good and bad) operators, one per line. Compressed with bz2 format to use less space.

* The learning phase consists of several steps. They require executing python scripts located in src/subdominization-training.

1) ./gen-subdom-rules.py: Generates an initial set of features (each feature correspond to a rule). It exhaustively generates many rules, and one can control the size by two parameters: (rule_size y num_rules).
If the training runs are provided, it'll extract data from them to avoid rules that check predicates in the initial state or goal if they never appeared there. This is recommended to avoid unnecessary rules that would be entirely uninformative.


Usage:

./gen-subdom-rules.py --store_rules <output_rule_file> --rule_size RULE_SIZE --num_rules NUM_RULES --runs <runs> <domain>

Recommended values for RULE_SIZE is 10, so that the number of features is controlled by NUM_RULES: Higher-values (100k) will require much longer training times than lower values (1K), but also can provide more accuracy in the end.


2) ./gen-subdom-training.py: Generates the training data

Usage: gen-subdom-training.py [--debug-info] [--instances-relevant-rules INSTANCES_RELEVANT_RULES] [--op-file OP_FILE] [--num-test-instances NUM_TEST_INSTANCES]  [--max-training-examples MAX_TRAINING_EXAMPLES] <runs_folder> <training_rules> <output_path_to_store_training_data>

  - num test instances allows you to separate some instances to validate the model.

  - op-file allows you to control the name of the file that you want to use as "good_operators". By default is sas_plan, but you can have different files with different operator subsets and use this to control which ones to use for training the models.

  - instances-relevant-rules and max-training-examples allow you to filter the input features that are irrelevant (see step 1-prime below)


3) ./learning/select-features.py --training-folder FOLDER1 --selector-type TYPE [--keep-duplicate-features] [--mean-over-duplicates]

    --training-folder: path to training set files (must be *.csv, where last column is the class, also need relevant_rules file); this is the outcome of 2)
    --selector-type: the type of the learning model: can be one of 'LRCV', 'LG', 'RF' , 'SVMCV','NBB', 'NBG', 'DT'
    --keep-duplicate-features: elimination and aggregation of duplicate feature vectors, default is eliminate
    --mean-over-duplicates: aggregating eliminated duplicate feature vectors by taking max or mean (default is max)

4) ./learning/train_model_for_domain.py --training-set-folder FOLDER1 --model-folder FOLDER2 --model-type TYPE [--keep-duplicate-features] [--mean-over-duplicates]

    --training-set-folder:  path to training set files (must be *.csv, where last column is the class); this is the outcome of 2) or 3)
    --model-folder: path to folder where to store model files in
    --model-type: the type of the learning model: can be one of 'LRCV', 'LG', 'RF' , 'SVMCV','NBB', 'NBG', 'DT'
    --keep-duplicate-features: elimination and aggregation of duplicate feature vectors, default is eliminate
    --mean-over-duplicates: when --keep-duplicate-features is set, aggregating eliminated duplicate feature vectors by taking max or mean (default is max)


The result of step 4 is a folder containing the models that can be loaded into our version of FastDownward (see step A above)



 1-prime) Also, there is an extra step that can be executed between steps 1 and 2, but it is not strictly necessary:
 ./gen-relevant-rules.py: This is an optional step, after step 1 in order to filter features that have exactly the same value in all the cases in the training data (these rules are simply invariants, so they are not useful features for the learning algorithms), or there exists a shorter rule that is equivalent in the training set (they always evaluate to the same value). It can also be done 


Usage: 
./gen-relevant-rules.py  [--instances-relevant-rules INSTANCES_RELEVANT_RULES] [--max-training-examples MAX_TRAINING_EXAMPLES] <runs> <training_rules> <output>

<training_rules> is the file generated in step 1.

The two parameters are optional and make the rule filter approximate in exchange of a faster check, and to filter features that can be relevant but only in very few training examples.


* Alternatively, one can use Aleph for learning the models by using:
1) gen-aleph-training.py

2) run aleph scripts that are generated by gen-aleph-training and redírect the output to a file

3) run parse_aleph_theory.py on the output to generate the Aleph-based models that can be loaded into our version of Fast Downward (see step A above)