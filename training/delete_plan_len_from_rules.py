from collections import defaultdict

action_name_planlen_par = defaultdict(set)

for s_act in open("./domain.pddl").read().split(":action")[1:]:
    action_name = s_act.strip().split()[0]
    print(action_name)
    plan_len_par = None
    for s_pred in s_act.split("\n"):
        if "plan_len" in s_pred:
            plan_len_par = s_pred.split()[-1][:-1]
            if not plan_len_par.startswith("?"): continue
            print("Plan_len par", plan_len_par)
            break
    if plan_len_par is None: continue
    action_name_planlen_par[action_name].add(plan_len_par)
    # now detect if there is any sumResult triplet
    sum_result_par = None
    for s_pred in s_act.split(":precondition")[1].split("\n"):
        if plan_len_par in s_pred and "SumResult" in s_pred:
            sum_result_par = s_pred.strip().split()[1]
            print("SumResult par", sum_result_par)
            assert "SumResult" in sum_result_par
            break
    if sum_result_par is None: continue
    for s_pred in s_act.split("\n"):
        if sum_result_par in s_pred and "SumResult" in s_pred:
            plan_len_result_par = s_pred.split()[-1][:-1]
            if plan_len_result_par.startswith("?"):
                print("Sum plan result pars:", plan_len_result_par)
                action_name_planlen_par[action_name].add(plan_len_result_par)

filtered_rules = []

# CHANGE BELOW >>>>>>
for l in open("./rules_file3").readlines():
    relevant = True
    for act_name, values in action_name_planlen_par.items():
        if act_name in l:
            pars = l.split(":-")[1]
            for par in values:
                if par in pars:
                    relevant = False
                    break
            if relevant == False:
                break
    if relevant == True:
        filtered_rules.append(l)

open("./rules_file_noplan_r3", "w+").write("".join(filtered_rules))
