#! /usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import print_function

import sys
import itertools
from itertools import chain, combinations
import pddl
import string

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
        
def all_combinations(param_list1, param_list2):
    def valid_match(subset):
        return len(set(map(lambda x : x[1], subset))) == len(subset) and len(subset) > 0
    matches = [(i, j) for (i, p1) in enumerate(param_list1) for (j, p2) in enumerate(param_list2) if p1.type_name == p2.type_name]
    all_matches_subsets = chain.from_iterable(combinations(matches,n) for n in range(len(matches)+1))

    return [x for x in all_matches_subsets if valid_match(x)]

if __name__ == "__main__":
    import pddl_parser
    import normalize
    import pddl_to_prolog

    print("Parsing...")
    task = pddl_parser.open()
    print("Normalizing...")
    normalize.normalize(task)

    for a in task.actions:
        print ("Generate candidate rules for action %s" % a.name)

        rules = get_equality_rules (a)
    
        for p in task.predicates:
            for binding in all_combinations(a.parameters, p.arguments):
                arguments = ["_" for x in p.arguments]
                for x in binding:
                    arguments[x[1]] = a.parameters[x[0]].name

                rules.append(Rule(a, "ini:{}({})".format(p.name, ", ".join(arguments))))
                rules.append(Rule(a, "goal:{}({})".format(p.name, ", ".join(arguments))))

        frules = open('rules_{}.txt'.format(a.name), 'w')
        frules.write("\n".join(map(str, rules)))
        frules.close()
        print (len(rules))
        print()

        

        


    # relaxed_reachable, atoms, actions, axioms, _ = explore(task)
    # for action in actions:
    #     rule_result = [1, 0, 1, 0]
    #     print(", ".join([action.name] + list(map(str, rule_result))))

