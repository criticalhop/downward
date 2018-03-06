#! /usr/bin/env python

from __future__ import print_function

from collections import defaultdict

import build_model
import instantiate
import pddl_to_prolog
import pddl
import timers
import options




class RuleEval:
    def evaluate_inigoal_rule(self, rule, fact_list):
        compliant_values = set()
            
        predicate_name, arguments  = rule.split("(")
        arguments = arguments.replace(")", "").replace("\n", "").replace(".", "").replace(" ", "").split(",")
        valid_arguments = tuple(set([a for a in arguments if a != "_"]))
        positions_argument = {}
        
        for a in valid_arguments:
            positions_argument[a] = [i for (i, v) in enumerate(arguments) if v == a]

        arguments = valid_arguments

        for fact in fact_list:
            if fact.predicate == predicate_name:
                values = []
                for a in arguments:
                    if len(set([fact.args[p] for p in positions_argument[a]])) > 1:
                        break
                    values.append(fact.args[positions_argument[a][0]])

                if len(values) == len(arguments):
                    compliant_values.add(tuple(values))

        return arguments, compliant_values

    def __init__(self, rule_text, task):
        self.text = rule_text.replace('\n','')
        head, body = rule_text.split(":-")
        self.action_schema, action_arguments = head.split(" (")
        self.constraints = {}

        action_arguments = action_arguments.replace(")", "").replace("\n", "").replace(".", "").replace(" ", "").split(",")

        for rule in body.split(";"):
            rule_type, rule = rule.split(":")
            rule_type = rule_type.strip()

            if rule_type == "ini":
                arguments, compliant_values = self.evaluate_inigoal_rule (rule, task.init)                        
            elif rule_type == "goal":
                arguments, compliant_values = self.evaluate_inigoal_rule (rule, task.goal.parts)
            elif rule_type == "equal":
                arguments = ()
            else:
                 print("Error: unknown rule ", rule_type, rule)
                 exit()

            if len(arguments) == 0:
                continue

            arguments = tuple(map(lambda x : action_arguments.index(x),  arguments))
            
            if arguments in self.constraints:
                self.constraints [arguments] = self.constraints [arguments] & compliant_values
            else:
                self.constraints [arguments] = compliant_values
                
        #print (self.text, self.constraints)

    def evaluate(self, action):
        arguments = action.name[:-1].split(" ")[1:]
        for c in self.constraints:
            values = tuple(map(lambda x : arguments[x],  c))
            if not values in self.constraints[c]:
                # print (action.name, "not valid according to", self.text)

                return 0
        #print (action.name, "valid according to", self.text) 
        return 1
    
class RulesEvaluator:
    def __init__(self, file_reader, task):
        self.rules = defaultdict(list)
        for l in file_reader.readlines():
            if "ini:" in l or "goal:" in l:
                re = RuleEval(l, task)                
                self.rules[re.action_schema].append(re)


    def evaluate(self, action):
        name = action.name.split(" ")[0][1:]
        return [rule.evaluate(action) for rule in  self.rules[name]] 

if __name__ == "__main__":
    import pddl_parser
    task = pddl_parser.open()
    relaxed_reachable, atoms, actions, axioms, _ = instantiate.explore(task)


    if options.store_training_data:
        output_files = {}
        for schema in task.actions:
            output_files[schema.name] = open('{}/training_data_{}.csv'.format(options.store_training_data, schema.name), 'a')
            
    plan = [x.replace('\n', '') for x in options.training_plan]
    re = RulesEvaluator(options.training_rules, task)
    for action in actions:
        is_in_plan = 1 if action.name in plan else 0
        eval = re.evaluate(action)
        #print( ", ".join(map (str, [action.name] + eval + [is_in_plan])) )
        
        if options.store_training_data:
            schema = action.name.split(' ')[0][1:]
            assert (schema in output_files)
            output_files[schema].write(", ".join(map (str, [action.name] + eval + [is_in_plan])) + '\n')

    for of in output_files:
        output_files[of].close()
