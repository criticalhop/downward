Fast Downward Partial Grounding is based on Fast Downward, which is a domain-independent planning system.

For instructions on how to use the Partial Grounding mechanism see below. 

For documentation about Fast Downward and contact information see http://www.fast-downward.org/.

The following directories are not part of Fast Downward as covered by this
license:

* ./src/search/ext

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

 This is divided in two phases: the training phase does offline learning of some models, and the planning phase uses the learned models during grounding.

Learning Phase:
* Prerequisites:
   - python3, with libraries: numpy, ...
   
   - <domain>: A PDDL domain file that is shared accross all training and testing instances.
   - <runs>: A directory containing the training data. It should contain a sub-directory for each instance, which should contain the following files:
        * domain.pddl
        * problem.pddl
        * sas_plan/good_operators: file containing the list of "good" operators, one per line. 
        * all_operators.bz2: file containing a list of all grounded (good and bad) operators, one per line. Compressed with bz2 format to use less space.

* The learning phase consists of several steps. They require executing an script located in src/subdominization-training.py.
  There is no master script because some of the steps can be parallelized, so we are running everything manually in the cluster.


 1) ./gen-subdom-rules.py: Generates an initial set of features (each feature correspond to a rule). It exhaustively generates many rules, and one can control the size by two parameters: (rule_size y num_rules).
If the training runs are provided, it'll extract data from them to avoid rules that check predicates in the initial state or goal if they never appeared there. This is recommended to avoid unnecessary rules that would be entirely uninformative.


Usage:

./gen-subdom-rules.py --store_rules <output_rule_file> --rule_size RULE_SIZE --num_rules NUM_RULES --runs <runs> <domain>

Recommended values for RULE_SIZE is 10, so that the number of features is controlled by NUM_RULES: Higher-values (100k) will require much longer training times than lower values (1K), but also can provide more accuracy in the end.


 2) ./gen-relevant-rules.py: This is an optional step, in order to filter features that have exactly the same value in all the cases in the training data (these rules are simply invariants, so they are not useful features for the learning algorithms), or there exists a shorter rule that is equivalent in the training set (they always evaluate to the same value).


Usage: 
./gen-relevant-rules.py  [--instances-relevant-rules INSTANCES_RELEVANT_RULES] [--max-training-examples MAX_TRAINING_EXAMPLES] <runs> <training_rules> <output>

<training_rules> is the file generated in step 1.

The two parameters are optional and make the rule filter approximate in exchange of a faster check, and to filter features that can be relevant but only in very few training examples.

3) ./gen-subdom-training.py: Generates the training data

Usage: gen-subdom-training.py [--debug-info] [--instances-relevant-rules INSTANCES_RELEVANT_RULES] [--op-file OP_FILE] [--num-test-instances NUM_TEST_INSTANCES]  [--max-training-examples MAX_TRAINING_EXAMPLES] <runs_folder> <training_rules> <output_path_to_store_training_data>

num test instances allows you to separate some instances to validate the model. --op-file allows you to control the name of the file that you want to use as "good_operators".
By default is sas_plan, but you can have different files with different operator subsets and use this to control which ones to use for training the models.


 4) ./select-features.py

 5) learn models
 

Alternatively, steps 3-5 can be substituted by:

3bis) gen-aleph-training.py


4bis) run aleph




Planning phase:

The planner is run exactly the same as Fast Downward, but providing additional options for
the translation phase that specify the stopping condition, and the priority queue.

