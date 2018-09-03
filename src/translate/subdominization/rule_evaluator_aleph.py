#! /usr/bin/env python
# -*- coding: utf-8 -*-

from collections import defaultdict
import itertools
import pddl

import re
regexp_is_float = re.compile("\d.\d+")
def is_float(text):
    return regexp_is_float.match(text.strip())

class AlephRule:
    def __init__(self, rule_text, task):

        predicate = rule_text.



        
        self.action_arguments = action_arguments_rule
        self.input_free_variables = free_variables
        self.output_free_variables = free_variables
        self.rule = dict()

    def evaluate(self, action_arguments, free_variable_inputs):
        query = tuple([action_arguments[x] for x in self.action_arguments] + [free_variable_inputs[x] for x in self.input_free_variables])
        if query not in self.rule:
            return None
        else:
            return self.rule(query)
    
class AlephRuleTree:
    def __init__(self, text):
        text_rule, text_false = text.split(";")[0].split(" ")
        text_true = ";".join(text.split(";")[1:])
        
        self.rule = AlephRule (text_rule)
        self.case_true = AlephRuleConstant(text_true) if is_float(text_true) else AlephRuleTree(text_true)
        self.case_false = AlephRuleConstant(text_false) if is_float(text_false) else AlephRuleTree(text_false)
        
    def evaluate(self, action_arguments, free_variable_values):
        eval_rule = self.rule.evaluate(action_arguments, free_variable_values)
        if eval_rule:
            return self.rule.evaluate(action_arguments, eval_rule)
        else:
            return self.rule.evaluate(action_arguments, free_variable_values)
        
        return (self.value)
    
class AlephRuleConstant:
    def __init__(self, text):
        self.value = float(text)
        
    def evaluate(self, action_arguments, free_variables_inputs):
        return (self.value)

        


class RuleEvaluatorAleph:
    def __init__(self, rule_text, task):
        self.rules = {}
        for l in rule_text:
            action_schema = l.split(" ")[0]
            self.rules[action_schema].append(AlephRuleList(l))
            
    def evaluate(self, action):
        return self.rules[action.predicate.name].evaluate(action)


""""

move-b-to-b(a0,a1,a2) :- ini:on(a0,a1) 0.00774327660127322; equals(a2,a2) 0.508; goal:on(a0,a2) 0.108601216333623; ini:on(a0,a2) 0.50609756097561; 0.0294117647058824

""""
