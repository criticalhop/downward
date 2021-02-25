#! /usr/bin/env python

import sys
sys.path.append("../src")
sys.path.append("../src/subdominization-training")
sys.path.append("../src/subdominization-training/learning")
sys.path.append("../src/translate")

import os
import numpy as np

from collections import defaultdict
from rule_training_evaluator import *
from subdominization.model import TrainedModel
import lisp_parser
import shutil
import bz2

from IPython import embed

try:
    # Python 3.x
    from builtins import open as file_open
except ImportError:
    # Python 2.x
    from codecs import open as file_open

import parsing_functions
import instantiate

def parse_pddl_file(type, filename):
    try:
        # The builtin open function is shadowed by this module's open function.
        # We use the Latin-1 encoding (which allows a superset of ASCII, of the
        # Latin-* encodings and of UTF-8) to allow special characters in
        # comments. In all other parts, we later validate that only ASCII is
        # used.
        return lisp_parser.parse_nested_list(file_open(filename,
                                                       encoding='ISO-8859-1'))
    except IOError as e:
        raise SystemExit("Error: Could not read file: %s\nReason: %s." %
                         (e.filename, e))
    except lisp_parser.ParseError as e:
        raise SystemExit("Error: Could not parse %s file: %s\nReason: %s." %
                         (type, filename, e))



if __name__ == "__main__":
    import argparse
    import os
    
    argparser = argparse.ArgumentParser()
    argparser.add_argument("runs_folder", help="path to task pddl file")
    argparser.add_argument("training_rules", type=argparse.FileType('r'), help="File that contains the rules used to generate training data by gen-subdominization-training")
    argparser.add_argument("--debug-info", help="Include action name in the file", action="store_true")    
    argparser.add_argument("--instances-relevant-rules", type=int, help="Number of instances for relevant rules", default=0)    
    argparser.add_argument("--op-file", default="sas_plan", help="File to store the training data by gen-subdominization-training")    
    argparser.add_argument("--num-test-instances", type=int,default=0, help="Number of instances reserved for the testing set")
    argparser.add_argument("--max-training-examples", type=int, help="Maximum number of training examples for action schema", default=1000000)    
    argparser.add_argument(
        "--trained-model-folder", type=str,
        help="The folder that should contain the trained model and relevant files if 'trained' is used as queue ordering")


    options = argparser.parse_args()

        
    relevant_rules = []

    operators_filename = options.op_file

    relevant_rules = sorted([l for l in options.training_rules.readlines()])

    training_lines = defaultdict(list)
    testing_lines = defaultdict(list)


    all_instances = sorted([d for d in os.listdir(options.runs_folder) if os.path.isfile('{}/{}/{}'.format(options.runs_folder, d, operators_filename))])
    np.random.seed(2018)
    testing_instances = np.random.choice(all_instances, int(options.num_test_instances), replace=False)

    model = None


    for task_run in all_instances:        
        try:
            print ("Processing ", task_run)
            is_test_instance = task_run in testing_instances
            domain_filename = '{}/{}/{}'.format(options.runs_folder, task_run, "domain.pddl")
            task_filename = '{}/{}/{}'.format(options.runs_folder, task_run, "problem.pddl")
            plan_filename = '{}/{}/{}'.format(options.runs_folder, task_run, operators_filename)

            domain_pddl = parse_pddl_file("domain", domain_filename)
            task_pddl = parse_pddl_file("task", task_filename)

            all_operators_filename = '{}/{}/{}'.format(options.runs_folder, task_run, "all_operators.bz2")
            
            task = parsing_functions.parse_task(domain_pddl, task_pddl)
            if model is None:
                model = TrainedModel(options.trained_model_folder, task)
            else:
                model.ruleEvaluator = RulesEvaluator(relevant_rules, task)

            # embed()
        
            re = RulesEvaluator(relevant_rules, task)

            #relaxed_reachable, atoms, actions, axioms, _ = instantiate.explore(task)
            
            with open(plan_filename) as plan_file:
                plan = set(map (lambda x : tuple(x.replace("\n", "").replace(")", "").replace("(", "").split(" ")), plan_file.readlines()))
                for step in plan:
                    # print(plan)
                    schema = step[0]
                    if len(schema) < 5: continue
                    arguments = list(step[1:])
                    # arguments = list(map(lambda x: x.strip(), arguments.strip()[:-1].split(",")))
                    eval = re.evaluate(schema, arguments)
                    print( ",".join(map (str, [schema] + eval )) )

                    # Now run result with the model
                    if model.model[schema].is_classifier:
                        est = model.model[schema].model.predict_proba([eval])[0]
                        # if len(est) > 1: est = est[1]
                        # else: est = est[0]
                    else:
                        est = model.model[schema].model.predict([eval])[0]
                    print(" --- ", est)



                if False:
                    with bz2.BZ2File(all_operators_filename, "r") as actions:
                    # relaxed_reachable, atoms, actions, axioms, _ = instantiate.explore(task)
                        for action in actions:
                            action = action.decode("utf-8")
                            saction = action.strip()
                            if saction[-1] != ")":
                                print("TRUNC", saction)
                                continue
                            schema, arguments = action.split("(")

                            
                            
                            arguments = list(map(lambda x: x.strip(), arguments.strip()[:-1].split(",")))
                        
                            is_in_plan = 1 if  tuple([schema] + arguments) in plan else 0
                        
                            eval = re.evaluate(schema, arguments)
                            print( ",".join(map (str, [schema] + eval + [is_in_plan])) )

                            # Now run result with the model
                            if model.model[schema].is_classifier:
                                est = model.model[schema].model.predict_proba([eval])
                            else:
                                est = model.model[schema].model.predict([eval])
                            print(" --- ", est)



        except OSError:
            pass
        except KeyboardInterrupt:
            break

                           
    #print ("Only 0/1 rules: ", len(re.get_only_0_rules()), len(re.get_only_1_rules()), len(re.get_all_rules()))
