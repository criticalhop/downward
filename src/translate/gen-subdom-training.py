#! /usr/bin/env python

from __future__ import print_function

from collections import defaultdict


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
        self.evaluation_result_count_0 = 0
        self.evaluation_result_count_1 = 0
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
                self.evaluation_result_count_0 += 1
                return 0
        #print (action.name, "valid according to", self.text)
        self.evaluation_result_count_1 += 1
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

    def get_only_0_rules(self):

        return [rule.text for (schema, rules)  in self.rules.items() for rule in rules if rule.evaluation_result_count_1 == 0]

    def get_only_1_rules(self):
        return [rule.text for (schema, rules)  in self.rules.items() for rule in rules if rule.evaluation_result_count_0 == 0]

    def get_all_rules (self):
        return [rule.text for (schema, rules)  in self.rules.items() for rule in rules]





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
    argparser.add_argument("store_training_data", help="File to store the rules used to generate training data by gen-subdominization-training")    

    options = argparser.parse_args()

    for task_run in os.listdir(options.runs_folder):
        if os.path.isfile('{}/{}/{}'.format(options.runs_folder, task_run, "sas_plan")):
            domain_file = '{}/{}/{}'.format(options.runs_folder, task_run, "domain.pddl")
            problem_file = '{}/{}/{}'.format(options.runs_folder, task_run, "problem.pddl")

            domain_pddl = parse_pddl_file("domain", domain_filename)
            task_pddl = parse_pddl_file("task", task_filename)

            task = parsing_functions.parse_task(domain_pddl, task_pddl)
    exit()
    
    # task = pddl_parser.open(domain_file, problem_file)    
    # relaxed_reachable, atoms, actions, axioms, _ = instantiate.explore(task)

    
    # plan = [x.replace('\n', '') for x in options.training_plan]
    # re = RulesEvaluator(options.training_rules, task)

    # training_lines = defaultdict(list)
    
    # for action in actions:
    #     is_in_plan = 1 if action.name in plan else 0
    #     eval = re.evaluate(action)
    #     #print( ", ".join(map (str, [action.name] + eval + [is_in_plan])) )
        
    #     schema = action.name.split(' ')[0][1:]
    #     training_lines [schema].append(", ".join(map (str, eval + [is_in_plan])))

    # if options.store_training_data:
    #     for schema in training_lines:
    #         output_file = open('{}/training_data_{}.csv'.format(options.store_training_data, schema), 'a')
    #         output_file.write("\n".join(training_lines[schema]))
    #         output_file.close()

    # print ("Only 0/1 rules: ", len(re.get_only_0_rules()), len(re.get_only_1_rules()), len(re.get_all_rules()))
