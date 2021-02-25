RELEVANT_RULES_FILE = "relevant_rules_file_r2_"
ALL_RELEVANT_RULES_FILE = "relevant_rules_file_r2_all"

all_rules = set()

for i in range(2, 24):
    fn = RELEVANT_RULES_FILE+str(i)
    new_rules = set(open(fn).read().split("\n"))
    all_rules |= new_rules

open(ALL_RELEVANT_RULES_FILE, "w+").write("\n".join(sorted(list(all_rules))))


