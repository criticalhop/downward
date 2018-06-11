#!/usr/bin/python
# -*- coding: utf-8 -*-

import sys
import pickle
import os.path
from _collections import defaultdict

from subdominization.rule_evaluator import RulesEvaluator
from subdominization.learn import LearnRules

from random import randint

from numpy import std



class TrainedModel():
    def __init__(self, modelFolder, task):
        if (not os.path.isdir(modelFolder)):
            sys.exit("Error: given --trained-model-folder is not a folder: " + modelFolder)
        self.model = defaultdict()
        for file in os.listdir(modelFolder):
            if (os.path.isfile(os.path.join(modelFolder, file))):
                if (file.endswith(".model")):
                    with open(os.path.join(modelFolder, file), "rb") as modelFile:
                        self.model[file[:-6]] = pickle.load(modelFile)
                elif (file == "relevant_rules"):
                    rules = []
                    with open(os.path.join(modelFolder, file), "r") as rulesFile:
                        self.ruleEvaluator = RulesEvaluator(rulesFile.readlines(), task)
        if (not self.ruleEvaluator):
            sys.exit("Error: no relevant_rules file inthen " + modelFolder)
        if (not self.model):
            sys.exit("Error: no *.model files in " + modelFolder)
        self.no_rule_schemas = set()
        self.estimates_per_schema = defaultdict()
        
    def get_estimate(self, action):
#         print(action.predicate.name)
        
        if (not action.predicate.name in self.model):
            if (not action.predicate.name in self.no_rule_schemas):
                self.no_rule_schemas.add(action.predicate.name)
#             print(action.predicate.name, randint(0, 100) / 100)
            return randint(0, 100) / 100 # TODO use the ratio of occurrence of this schema in plans?
        
        # the returned list has only one entry, of which the second entry is the probability that the action is in the plan
        estimate = self.model[action.predicate.name].model.predict_proba([self.ruleEvaluator.evaluate(action)])[0][1] 
#         print(action.predicate.name, estimate)
        
        if (not action.predicate.name in self.estimates_per_schema):
            self.estimates_per_schema[action.predicate.name] = []
        self.estimates_per_schema[action.predicate.name].append(estimate)
               
        return estimate
    
    def print_stats(self):
        print("schema \t AVG \t STDDEV")
        for key, estimates in self.estimates_per_schema.items():
            print(key, sum(estimates) / len(estimates), std(estimates))
        for schema in self.no_rule_schemas:
            print("no relevant rule for action schema", schema)

        


