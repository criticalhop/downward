#! /usr/bin/env python

from __future__ import print_function

import os
import numpy as np
from pddl_parser import parsing_functions

from collections import defaultdict
from rule_training_evaluator import *
import lisp_parser
import shutil
import bz2

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
    argparser.add_argument("store_training_data", help="Directory to store the training data by gen-subdominization-training")    
    argparser.add_argument("--op-file", default="sas_plan", help="File to store the training data by gen-subdominization-training")    

    options = argparser.parse_args()

    if os.path.exists(options.store_training_data):
        result = raw_input('Output path "{}" already exists. Overwrite (y/n)?'.format(options.store_training_data))
        if result.lower() not in ['y', 'yes']:
            exit()
        shutil.rmtree(options.store_training_data)

        

        
    operators_filename = options.op_file

    if not os.path.exists(options.store_training_data):
        os.makedirs(options.store_training_data)

    training_lines = defaultdict(list)

    all_instances = sorted([d for d in os.listdir(options.runs_folder) if os.path.isfile('{}/{}/{}'.format(options.runs_folder, d, operators_filename))])

    domain_filename = '{}/{}/{}'.format(options.runs_folder, all_instances[0], "domain.pddl")
    domain_pddl = parse_pddl_file("domain", domain_filename)
    domain_name, domain_requirements, types, type_dict, constants, predicates, predicate_dict, functions, actions, axioms = parsing_functions.parse_domain_pddl(domain_pddl)
    predicates = [p for p in predicates if p.name != "="]
    print(predicates)
    
    for task_run in all_instances:        
        print ("Processing ", task_run)
        domain_filename = '{}/{}/{}'.format(options.runs_folder, task_run, "domain.pddl")
        task_filename = '{}/{}/{}'.format(options.runs_folder, task_run, "problem.pddl")
        plan_filename = '{}/{}/{}'.format(options.runs_folder, task_run, operators_filename)

        domain_pddl = parse_pddl_file("domain", domain_filename)
        task_pddl = parse_pddl_file("task", task_filename)

        all_operators_filename = '{}/{}/{}'.format(options.runs_folder, task_run, "all_operators.bz2")
           
        task = parsing_functions.parse_task(domain_pddl, task_pddl)



        with open(plan_filename) as plan_file:
            task_background_data.add(task_id, task.init, task.goal.parts)
           
            plan = set(map (lambda x : tuple(x.replace("\n", "").replace(")", "").replace("(", "").split(" ")), plan_file.readlines()))

            # Write good and bad operators 
            with bz2.BZ2File(all_operators_filename, "r") as actions:
                for action in actions:
                    schema, arguments = action.split("(")
                    arguments = map(lambda x: x.strip(), arguments.strip()[:-1].split(","))
                   
                    is_in_plan = 1 if  tuple([schema] + arguments) in plan else 0

                    if is_in_plan:
                        good_operators[schema].add (task_id, action)
                    else:
                        bad_operators[schema].add (task_id, action)

        #Write output to file 
        for schema in sorted(training_lines, key=lambda x : (x.count(";"), x)):
            output_file = open('{}/{}.csv'.format(options.store_training_data, schema), 'w')
            for line in training_lines[schema]:
                output_file.write(line + "\n")
            output_file.close()


                           
    #print ("Only 0/1 rules: ", len(re.get_only_0_rules()), len(re.get_only_1_rules()), len(re.get_all_rules()))
