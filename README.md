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
    - <domain>: A PDDL domain file that is shared accross all training and testing instances.
    - <runs>: A directory containing the training data. It should contain a sub-directory for each instance, which should contain the following files:
        * domain.pddl
        * problem.pddl
        * sas_plan/good_operators: file containing the list of "good" operators, one per line. 
        * all_operators.bz2: file containing a list of all grounded (good and bad) operators, one per line. Compressed with bz2 format to use less space.

* The learning phase consists of 4 steps. They require executing an script located in src/subdominization-training.py.
  There is no master script because some of the steps can be parallelized, so we are running everything manually in the cluster.


 1) ./gen-subdom-rules.py: Generates an initial set of rules

 2) ./gen-relevant-rules.py: ??? I'm confused, is this an alternative to 1) or an additional step? 

 3) ./gen-subdom-training.py

 4) ./select-features.py

 5) learn models
 

Alternatively, steps 3-5 can be substituted by:

3bis) gen-aleph-training.py


4bis) run aleph




Planning phase:

The planner is run exactly the same as Fast Downward, but providing additional options for
the translation phase that specify the stopping condition, and the priority queue.

