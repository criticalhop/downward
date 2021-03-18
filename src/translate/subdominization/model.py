#!/usr/bin/python
# -*- coding: utf-8 -*-

from sys import exit 
import pickle
import os.path
import random

from subdominization.rule_evaluator import RulesEvaluator
from subdominization.learn import LearnRules

from numpy import std
from compiledtrees.compiled import CompiledClassifierPredictor
from sklearn.dummy import DummyClassifier


class FastModel:
    def __init__(self, sofile):
        self.is_classifier = True
        self.model = CompiledClassifierPredictor(sofile)


class DummyModel:
    def __init__(self, value):
        self.value = value
    def predict_proba(self, X):
        return self.value

class FastDummyModel:
    def __init__(self, value):
        self.is_classifier = True
        self.model = DummyModel(value)
        self.value = value
    def predict_proba(self, X):
        return [0, self.value]

class TrainedModel():
    def __init__(self, modelFolder, task):
        if (not os.path.isdir(modelFolder)):
            exit("Error: given --trained-model-folder is not a folder: " + modelFolder)
        self.model = {}
        found_rules = False
        found_model = False
        for file in os.listdir(modelFolder):
            if (os.path.isfile(os.path.join(modelFolder, file))):
                if (file.endswith(".so")): continue
                if (file.endswith(".model")):
                    found_model = True
                    if (os.path.isfile(os.path.join(modelFolder, file+".so"))):
                        self.model[file[:-6]] = FastModel(os.path.join(modelFolder, file+".so"))
                    else:
                        with open(os.path.join(modelFolder, file), "rb") as modelFile:
                            self.model[file[:-6]] = pickle.load(modelFile)
                            self.model[file[:-6]].model.n_jobs = 1
                            if not isinstance(self.model[file[:-6]].model, DummyClassifier):
                                self.model[file[:-6]].model_orig = self.model[file[:-6]].model
                                self.model[file[:-6]].model = CompiledClassifierPredictor(self.model[file[:-6]].model)
                                self.model[file[:-6]].model.save(os.path.join(modelFolder, file+".so"))
                            else:
                                self.model[file[:-6]].model = FastDummyModel(self.model[file[:-6]].model.constant)

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
                # raw_estimate = self.model[action.predicate.name].model.predict_proba([self.ruleEvaluator.evaluate(action)])[0]
                # raw_estimate_orig = self.model[action.predicate.name].model_orig.predict_proba([self.ruleEvaluator.evaluate(action)])[0]
                if isinstance(self.model[action.predicate.name].model, FastDummyModel):
                    # estimate = self.model[action.predicate.name].model.predict_proba(None)
                    estimate = self.model[action.predicate.name].model.value
                else:
                    raw_estimate = self.model[action.predicate.name].model.predict_proba(self.ruleEvaluator.evaluate(action))
                    estimate = raw_estimate[1]
                # estimate_orig = raw_estimate_orig[1]
                # if round(estimate, 4) != round(estimate_orig, 4):
                    # print("Fast model error!", estimate, estimate_orig)
                #print(action.predicate.name, raw_estimate)
            except IndexError:
                #print(action.predicate.name)
                if "goal" in action.predicate.name:
                    estimate = 1.0
                else:
                    estimate = raw_estimate
        else:
            estimate = self.model[action.predicate.name].model.predict([self.ruleEvaluator.evaluate(action)])[0]

        if (estimate < 0 or estimate > 1): # in case the estimate is off
            self.values_off_for_schema.add(action.predicate.name)
            if (estimate < 0):
                return 0
            else:
                return 1
        
        # if (not action.predicate.name in self.estimates_per_schema):
            # self.estimates_per_schema[action.predicate.name] = []
        # self.estimates_per_schema[action.predicate.name].append(estimate)
               
        return estimate
    
    def print_stats(self):
        # print("schema \t AVG \t STDDEV")
        # for key, estimates in self.estimates_per_schema.items():
            # print(key, sum(estimates) / len(estimates), std(estimates))
        for schema in self.no_rule_schemas:
            print("no relevant rule for action schema", schema)
        for schema in self.values_off_for_schema:
            print("bad estimate(s) for action schema", schema)

        


