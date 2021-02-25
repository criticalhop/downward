#!/usr/bin/python
# -*- coding: utf-8 -*-

from sys import exit 
import pickle
import os.path
import random

from subdominization.rule_evaluator import RulesEvaluator
from subdominization.learn import LearnRules

from numpy import std



class TrainedModel():
    def __init__(self, modelFolder, task):
        if (not os.path.isdir(modelFolder)):
            exit("Error: given --trained-model-folder is not a folder: " + modelFolder)
        self.model = {}
        found_rules = False
        found_model = False
        for file in os.listdir(modelFolder):
            if (os.path.isfile(os.path.join(modelFolder, file))):
                if (file.endswith(".model")):
                    with open(os.path.join(modelFolder, file), "rb") as modelFile:
                        found_model = True
                        self.model[file[:-6]] = pickle.load(modelFile)
                elif (file == "relevant_rules"):
                    rules = []
                    with open(os.path.join(modelFolder, file), "r") as rulesFile:
                        found_rules = True
                        self.ruleEvaluator = RulesEvaluator(rulesFile.readlines(), task)
        if (not found_rules):
            exit("Error: no relevant_rules file in " + modelFolder)
        if (not found_model):
            exit("Error: no *.model files in " + modelFolder)
        self.no_rule_schemas = set()
        self.estimates_per_schema = {}
        self.values_off_for_schema = set()
        
    def get_estimate(self, action):
        # returns the probability that the given action is part of a plan

        if (not action.predicate.name in self.model):
            self.no_rule_schemas.add(action.predicate.name)
            return None
        
        if (self.model[action.predicate.name].is_classifier):
            # the returned list has only one entry (estimates for the input action), 
            # of which the second entry is the probability that the action is in the plan (class 1)
            try:
                raw_estimate = self.model[action.predicate.name].model.predict_proba([self.ruleEvaluator.evaluate(action)])[0]
                estimate = raw_estimate[1]
                print(action.predicate.name, raw_estimate)
            except IndexError:
                print(action.predicate.name)
                if "goal" in action.predicate.name:
                    estimate = 1.0
                else:
                    estimate = raw_estimate
            if estimate > 0.5 or estimate == 0:
                print(action.predicate.name, estimate)
            if estimate == 0.5:  # most likely is a random classifier??
                estimate = random.randint(0, 50)/100.0
        else:
            estimate = self.model[action.predicate.name].model.predict([self.ruleEvaluator.evaluate(action)])[0]

        if (estimate < 0 or estimate > 1): # in case the estimate is off
            self.values_off_for_schema.add(action.predicate.name)
            if (estimate < 0):
                return 0
            else:
                return 1
        
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
        for schema in self.values_off_for_schema:
            print("bad estimate(s) for action schema", schema)

        


