#! /usr/bin/env python

from __future__ import print_function

import os
import io
import numpy as np
from pddl_parser import parsing_functions

from collections import defaultdict
from rule_training_evaluator import *
import lisp_parser
import shutil
import bz2

from sys import version_info


is_python_3 = version_info[0] > 2 # test python version

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
    
    argparser = argparse.ArgumentParser()
    argparser.add_argument("runs_folder", help="path to task pddl file")
    argparser.add_argument("store_training_data", help="Directory to store the training data by gen-subdominization-training")    
    argparser.add_argument("--op-file", default="sas_plan", help="File to store the training data by gen-subdominization-training")
    argparser.add_argument("--domain-name", default="domain", help="name of the domain")    

    options = argparser.parse_args()

    if os.path.exists(options.store_training_data):
        if (is_python_3):
            result = input('Output path "{}" already exists. Overwrite (Y/n)?'.format(options.store_training_data))
        else:
            result = raw_input('Output path "{}" already exists. Overwrite (Y/n)?'.format(options.store_training_data))
        if result.lower() not in ['y', 'yes', '']:
            sys.exit()
        shutil.rmtree(options.store_training_data)

    operators_filename = options.op_file

    if not os.path.exists(options.store_training_data):
        os.makedirs(options.store_training_data)
        
    aleph_base_file_content = io.StringIO()
    
    aleph_base_file_content.write("%%%%%%%%%%%%%%%%%%%%%%%%%%%%\n"
                          "% specify tree type:\n"
                          ":- set(tree_type,class_probability).\n"
                          ":- set(evalfn,gini). % only alternative when using class_probability is entropy\n"
                          ":- set(classes,[ground,dont_ground]).\n\n")

    all_instances = sorted([d for d in os.listdir(options.runs_folder) if os.path.isfile('{}/{}/{}'.format(options.runs_folder, d, operators_filename))])

    domain_filename = '{}/{}/{}'.format(options.runs_folder, all_instances[0], "domain.pddl")
    domain_pddl = parse_pddl_file("domain", domain_filename)
    domain_name, domain_requirements, types, type_dict, constants, predicates, predicate_dict, functions, action_schemas, axioms = parsing_functions.parse_domain_pddl(domain_pddl)
    predicates = [p for p in predicates if p.name != "="]
    
    aleph_base_file_content.write("%%%%%%%%%%%%%%%%%%%%%%%%%%%%\n"
                          "% modes:\n")
    
    determination_backgrounds = []
    for predicate in predicates:
        params = "("
        if (len(predicate.arguments) > 0):
            params += "-'type:"
            params += predicate.arguments[0].type_name
            params += "'"
            for arg in predicate.arguments[1:]:
                params += ", -'type:"
                params += arg.type_name
                params += "'"
            params += ", "
        params += "+task_id)"
        
        aleph_base_file_content.write(":- modeb(*, 'ini:" + predicate.name + "'" + params + ").\n")
        determination_backgrounds.append("'ini:" + predicate.name + "'/" + str(len(predicate.arguments)))
        aleph_base_file_content.write(":- modeb(*, 'goal:" + predicate.name + "'" + params + ").\n")
        determination_backgrounds.append("'goal:" + predicate.name + "'/" + str(len(predicate.arguments)))
        
    determination_backgrounds.append("equals/2")
        
    aleph_base_file_content.write("\n")
    
    for type in types:
        aleph_base_file_content.write(":- modeb(*, equals(+'type:" + str(type) + "', +'type:" + str(type) + "')).\n")
        
    aleph_base_file_content.write("\n")
    
    # handle the training instances
    good_operators = defaultdict(lambda : defaultdict(list))
    bad_operators = defaultdict(lambda : defaultdict(list))
    
    aleph_fact_file_content = io.StringIO()
    for task_run in all_instances:
        print ("Processing ", task_run)
        domain_filename = '{}/{}/{}'.format(options.runs_folder, task_run, "domain.pddl")
        task_filename = '{}/{}/{}'.format(options.runs_folder, task_run, "problem.pddl")
        plan_filename = '{}/{}/{}'.format(options.runs_folder, task_run, operators_filename)
 
        domain_pddl = parse_pddl_file("domain", domain_filename)
        task_pddl = parse_pddl_file("task", task_filename)
 
        all_operators_filename = '{}/{}/{}'.format(options.runs_folder, task_run, "all_operators.bz2")
            
        task = parsing_functions.parse_task(domain_pddl, task_pddl)
        
        objects = set()

        aleph_fact_file_content.write("%%%%%%%%%%%%%%%%%%%%%%%%%%%%\n")
        aleph_fact_file_content.write("% init " + task_run + "\n")
        for goal_fact in task.init:
            if (goal_fact.predicate == "="): # we have our own equality
                continue
            aleph_fact_file_content.write("'ini:" + goal_fact.predicate + "'(")
            if (len(goal_fact.args) > 0):
                aleph_fact_file_content.write("'obj:" + goal_fact.args[0] + "'")
                for arg in goal_fact.args[1:]:
                    objects.add(arg)
                    aleph_fact_file_content.write(", 'obj:")
                    aleph_fact_file_content.write(arg)
                    aleph_fact_file_content.write("'")
                aleph_fact_file_content.write(", ")
            aleph_fact_file_content.write("'" + task_run + "').\n")
            
        aleph_fact_file_content.write("\n")
        
        aleph_fact_file_content.write("%%%%%%%%%%%%%%%%%%%%%%%%%%%%\n")
        aleph_fact_file_content.write("% goal " + task_run + "\n")
        for goal_fact in task.goal.parts:
            aleph_fact_file_content.write("'goal:" + goal_fact.predicate + "'(")
            if (len(goal_fact.args) > 0):
                aleph_fact_file_content.write("'obj:" + goal_fact.args[0] + "'")
                for arg in goal_fact.args[1:]:
                    objects.add(arg)
                    aleph_fact_file_content.write(", 'obj:")
                    aleph_fact_file_content.write(arg)
                    aleph_fact_file_content.write("'")
                aleph_fact_file_content.write(", ")
            aleph_fact_file_content.write("'" + task_run + "').\n")
            
        aleph_fact_file_content.write("\n")
 
        with open(plan_filename, "r") as plan_file:
            plan = set(map(lambda x : tuple(x.replace("\n", "").replace(")", "").replace("(", "").split(" ")), plan_file.readlines()))
 
            # Write good and bad operators 
            with bz2.BZ2File(all_operators_filename, "r") as actions:
                for a in actions:
                    action = a.decode("utf-8")
                    schema, arguments = action.split("(")
                    arguments = [x.strip() for x in arguments.strip()[:-1].split(",")]
                    if (tuple([schema] + arguments) in plan): # is in plan
                        good_operators[task_run][schema].append(arguments)
                    else:
                        bad_operators[task_run][schema].append(arguments)
            
            
    # write the actual files
    for schema in action_schemas:
        with open(os.path.join(options.store_training_data, options.domain_name + "_" + schema.name + ".b"), "w") as b_file:
            b_file.write(aleph_base_file_content.getvalue())
            params = "(+'type:" + schema.parameters[0].type_name + "'"
            for param in schema.parameters[1:]:
                params += ", +'type:"
                params += param.type_name
                params += "'"
            params += ", +task_id)"
            b_file.write(":- modeh(1, class('" + schema.name + "'" + params + ", -class)).\n\n")
            
            b_file.write("%%%%%%%%%%%%%%%%%%%%%%%%%%%%\n")
            b_file.write("% determinations:\n")
            for bg in determination_backgrounds:
                b_file.write(":- determination(class/2, " + bg + ").\n")
                
                
        with open(os.path.join(options.store_training_data, options.domain_name + "_" + schema.name + ".f"), "w") as f_file:
            f_file.write(aleph_fact_file_content.getvalue())
            f_file.write("%%%%%%%%%%%%%%%%%%%%%%%%%%%%\n")
            f_file.write("% training data {s}:\n".format(s=schema.name))
            
            for task in set(good_operators.keys()).union(set(bad_operators.keys())):
                for arguments in good_operators[task][schema.name]:
                    f_file.write("class('" + schema.name + "'('obj:" + arguments[0] + "'")
                    for arg in arguments[1:]:
                        f_file.write(", 'obj:" + arg + "'")
                    f_file.write(", " + task + "), ground).\n")
                    
                for arguments in bad_operators[task][schema.name]:
                    f_file.write("class('" + schema.name + "'('obj:" + arguments[0] + "'")
                    for arg in arguments[1:]:
                        f_file.write(", 'obj:" + arg + "'")
                    f_file.write(", " + task + "), dont_ground).\n")
            
    aleph_base_file_content.close()
    aleph_fact_file_content.close()
    
          
                
                
                
        
                
                
                
                
                
                
                
                
                
                
                
                
                
                
                
                
                
                
                
                
                
                
                
                
                
                
                


