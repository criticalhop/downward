from collections import defaultdict

class RuleEval:
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
                arguments = tuple(rule[1:rule.find(')')].split(", "))
                compliant_values = set()
                accepted_types = set()
                action_schema = list(filter(lambda a : a.name == self.action_schema, task.actions))[0]
                argument_types = set([p.type_name for p in action_schema.parameters if p.name in arguments])
                
                # TODO : Support super types in equality rules
                compliant_values = set([tuple ([o.name for a in arguments])
                                        for o in task.objects if o.type_name in argument_types])

                #print (self.text, arguments, compliant_values)
                                             
            else:
                 print("Error: unknown rule ", rule_type, rule)
                 exit()

            if len(arguments) == 0:
                continue

            # print (arguments)

            arguments = tuple(map(lambda x : action_arguments.index(x),  arguments))

            # print (arguments)
             
            if arguments in self.constraints:
                self.constraints [arguments] = self.constraints [arguments] & compliant_values
            else:
                self.constraints [arguments] = compliant_values

            
            # print (len(self.constraints))
            # if len(self.constraints) > 1:
            #     exit()
                
        #print (self.text, self.constraints)

    def evaluate_inigoal_rule(self, rule, fact_list):
        def eval_constants(fact, constants):
            for (i, val) in constants:
                if fact.args[i] != val:
                    return False
            return True
        compliant_values = set()
            
        predicate_name, arguments  = rule.split("(")
        arguments = arguments.replace(")", "").replace("\n", "").replace(".", "").replace(" ", "").split(",")
        valid_arguments = tuple(set([a for a in arguments if a.startswith("?")]))

        constants = [(i, val) for (i, val) in enumerate(arguments) if val != "_" and not val.startswith("?")]
        positions_argument = {}
        
        for a in valid_arguments:
            positions_argument[a] = [i for (i, v) in enumerate(arguments) if v == a]

        arguments = valid_arguments
        for fact in fact_list:
            if fact.predicate == predicate_name and eval_constants(fact, constants): 
                values = []
                for a in arguments:
                    if len(set([fact.args[p] for p in positions_argument[a]])) > 1:
                        break
                    values.append(fact.args[positions_argument[a][0]])

                if len(values) == len(arguments):
                    compliant_values.add(tuple(values))
                    
        return arguments, compliant_values

    def evaluate(self, action):
        arguments = action.name[:-1].split(" ")[1:]
        for c in self.constraints:
            values = tuple(map(lambda x : arguments[x],  c))
            if not values in self.constraints[c]:
                # print (action.name, "not valid according to", self.text)
                self.evaluation_result_count_0 += 1
                #print ("Evaluate", self.text, action, 0)
                return 0
        #print (action.name, "valid according to", self.text)
        self.evaluation_result_count_1 += 1
        #print ("Evaluate", self.text, action, 1)
        return 1
    
class RulesEvaluator:
    def __init__(self, rule_text, task):
        self.rules = defaultdict(list)
        for l in rule_text:
            re = RuleEval(l, task)
            self.rules[re.action_schema].append(re)

               
    def eliminate_rules(self, rules_text):
        for a in self.rules:
            self.rules[a] = [rule for rule in self.rules[a] if rule.text not in rules_text]
            
    def evaluate(self, action):
        name = action.name.split(" ")[0][1:]
        return [rule.evaluate(action) for rule in  self.rules[name]]

    def get_relevant_rules(self):
        return [rule.text for (schema, rules)  in self.rules.items() for rule in rules if rule.evaluation_result_count_0 > 0 and rule.evaluation_result_count_1 > 0]

    def get_all_rules (self):
        return [rule.text for (schema, rules)  in self.rules.items() for rule in rules]
