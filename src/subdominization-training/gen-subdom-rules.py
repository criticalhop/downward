#! /usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import print_function

import sys
import itertools
from itertools import chain, combinations
import pddl
import string
import options

from build_model import *
from instantiate import *




#move(X, _, A) :- goal:at(X, B), grounded:move(X, A, B).

#move(X, _, A) :- goal:at(X, C), grounded:move(X, A, B).


class Rule:
     def __init__ (self, action_schema, rule):
         self.action_schema = action_schema
         parameters = [x.name for x in action_schema.parameters]
         self.head = "{} ({})".format(action_schema.name, ", ".join(parameters))
         self.body = [rule]


     def __repr__(self):
         return "{} :- {}.".format(self.head, ", ".join(self.body))

def partition(collection):
    if len(collection) == 1:
        yield [ collection ]
        return

    first = collection[0]
    for smaller in partition(collection[1:]):
        # insert `first` in each of the subpartition's subsets
        for n, subset in enumerate(smaller):
            yield smaller[:n] + [[ first ] + subset]  + smaller[n+1:]
        # put `first` in its own subset 
        yield [ [ first ] ] + smaller

def get_equality_rules(action_schema):
    parameters = action_schema.parameters
    parameters_by_type = defaultdict(list)
    for p in parameters:
        parameters_by_type[p.type_name].append(p.name)

    rules = []
    for ptype in parameters_by_type:
        params = parameters_by_type[ptype]
        if len(params) > 1:
            for argpair in combinations (params, 2):
                rules.append(Rule(action_schema, "equal:(%s, %s)" % argpair))

    return rules
        

if __name__ == "__main__":
    import pddl_parser
    import normalize
    import pddl_to_prolog

    print("Parsing...")
    task = pddl_parser.open()
    print("Normalizing...")
    normalize.normalize(task)


    if options.store_rules:
         frules = options.store_rules
         
    for a in task.actions:
          print ("Generate candidate rules for action %s" % a.name)

          rules = get_equality_rules (a)

          for p in task.predicates:
               valid_arguments_parameters = [["_"] + [x.name for x in a.parameters if x.type_name == arg.type_name] for arg in p.arguments]
               valid_arguments_constants = [["_"] + [x.name for x in task.constants if x.type_name == arg.type_name] for arg in p.arguments]
               for combination in itertools.product(*valid_arguments_parameters):
                    if set(combination) == set("_"):
                         continue


                    valid_arguments = [[x] if x != "_" else valid_arguments_constants[i] for (i, x) in enumerate (combination)]
                    for combination in itertools.product(*valid_arguments):
                         rules.append(Rule(a, "ini:{}({})".format(p.name, ", ".join(combination))))
                         rules.append(Rule(a, "goal:{}({})".format(p.name, ", ".join(combination))))

                    
          if options.store_rules:
               options.store_rules.write("\n".join(map(str, rules)) + "\n")
          else:
               print("\n".join(map(str, rules)))


          print (len(rules))
          print()


        


    # relaxed_reachable, atoms, actions, axioms, _ = explore(task)
    # for action in actions:
    #     rule_result = [1, 0, 1, 0]
    #     print(", ".join([action.name] + list(map(str, rule_result))))

