#include "successor_generator.h"

#include "global_state.h"
#include "task_tools.h"

#include "utils/collections.h"

#include <algorithm>
#include <cassert>

using namespace std;

/* NOTE on possible optimizations:

   * Sharing "GeneratorEmpty" instances might help quite a bit with
     reducing memory usage and possibly even speed, because there are
     bound to be many instance of those. However, it complicates
     deleting the successor generator, and memory doesn't seem to be
     an issue. Speed appears to be fine now, too. So this is probably
     an unnecessary complication.

   * Using slist instead of list led to a further 10% speedup on the
     largest Logistics instance, logistics-98/prob28.pddl. It would of
     course also reduce memory usage. However, it would make the code
     g++-specific, so it's probably not worth it.

*/

bool smaller_variable_id(const FactProxy &f1, const FactProxy &f2) {
    return f1.get_variable().get_id() < f2.get_variable().get_id();
}

class GeneratorBase {
public:
    virtual ~GeneratorBase() = default;
    virtual void generate_applicable_ops(
        const State &state, vector<OperatorID> &applicable_ops) const = 0;
    // Transitional method, used until the search is switched to the new task interface.
    virtual void generate_applicable_ops(
        const GlobalState &state, vector<OperatorID> &applicable_ops) const = 0;
};

class GeneratorSwitch : public GeneratorBase {
    VariableProxy switch_var;
    list<OperatorID> immediate_operators;
    vector<GeneratorBase *> generator_for_value;
    GeneratorBase *default_generator;
public:
    ~GeneratorSwitch();
    GeneratorSwitch(const VariableProxy &switch_var,
                    list<OperatorID> &&immediate_operators,
                    const vector<GeneratorBase *> &&generator_for_value,
                    GeneratorBase *default_generator);
    virtual void generate_applicable_ops(
        const State &state, vector<OperatorID> &applicable_ops) const;
    // Transitional method, used until the search is switched to the new task interface.
    virtual void generate_applicable_ops(
        const GlobalState &state, vector<OperatorID> &applicable_ops) const;
};

class GeneratorLeaf : public GeneratorBase {
    list<OperatorID> applicable_operators;
public:
    GeneratorLeaf(list<OperatorID> &&applicable_operators);
    virtual void generate_applicable_ops(
        const State &state, vector<OperatorID> &applicable_ops) const;
    // Transitional method, used until the search is switched to the new task interface.
    virtual void generate_applicable_ops(
        const GlobalState &state, vector<OperatorID> &applicable_ops) const;
};

class GeneratorEmpty : public GeneratorBase {
public:
    virtual void generate_applicable_ops(
        const State &state, vector<OperatorID> &applicable_ops) const;
    // Transitional method, used until the search is switched to the new task interface.
    virtual void generate_applicable_ops(
        const GlobalState &state, vector<OperatorID> &applicable_ops) const;
};

GeneratorSwitch::GeneratorSwitch(
    const VariableProxy &switch_var, list<OperatorID> &&immediate_operators,
    const vector<GeneratorBase *> &&generator_for_value,
    GeneratorBase *default_generator)
    : switch_var(switch_var),
      immediate_operators(move(immediate_operators)),
      generator_for_value(move(generator_for_value)),
      default_generator(default_generator) {
}

GeneratorSwitch::~GeneratorSwitch() {
    for (GeneratorBase *generator : generator_for_value)
        delete generator;
    delete default_generator;
}

void GeneratorSwitch::generate_applicable_ops(
    const State &state, vector<OperatorID> &applicable_ops) const {
    /* A loop over push_back is faster than using insert in this situation
       because the lists are typically very small. We measured this in issue688. */
    for (OperatorID id : immediate_operators) {
        applicable_ops.push_back(id);
    }
    int val = state[switch_var].get_value();
    generator_for_value[val]->generate_applicable_ops(state, applicable_ops);
    default_generator->generate_applicable_ops(state, applicable_ops);
}

void GeneratorSwitch::generate_applicable_ops(
    const GlobalState &state, vector<OperatorID> &applicable_ops) const {
    // See above for the reason for using push_back instead of insert.
    for (OperatorID id : immediate_operators) {
        applicable_ops.push_back(id);
    }
    int val = state[switch_var.get_id()];
    generator_for_value[val]->generate_applicable_ops(state, applicable_ops);
    default_generator->generate_applicable_ops(state, applicable_ops);
}

GeneratorLeaf::GeneratorLeaf(list<OperatorID> &&applicable_operators)
    : applicable_operators(move(applicable_operators)) {
}

void GeneratorLeaf::generate_applicable_ops(
    const State &, vector<OperatorID> &applicable_ops) const {
    // See above for the reason for using push_back instead of insert.
    for (OperatorID id : applicable_operators) {
        applicable_ops.push_back(id);
    }
}

void GeneratorLeaf::generate_applicable_ops(
    const GlobalState &, vector<OperatorID> &applicable_ops) const {
    // See above for the reason for using push_back instead of insert.
    for (OperatorID id : applicable_operators) {
        applicable_ops.push_back(id);
    }
}

void GeneratorEmpty::generate_applicable_ops(
    const State &, vector<OperatorID> &) const {
}

void GeneratorEmpty::generate_applicable_ops(
    const GlobalState &, vector<OperatorID> &) const {
}

SuccessorGenerator::SuccessorGenerator(const TaskProxy &task_proxy)
    : task_proxy(task_proxy) {
    OperatorsProxy operators = task_proxy.get_operators();
    // We need the iterators to conditions to be stable:
    conditions.reserve(operators.size());
    list<OperatorID> all_operators;
    for (OperatorProxy op : operators) {
        Condition cond;
        cond.reserve(op.get_preconditions().size());
        for (FactProxy pre : op.get_preconditions()) {
            cond.push_back(pre);
        }
        // Conditions must be ordered by variable id.
        sort(cond.begin(), cond.end(), smaller_variable_id);
        all_operators.push_back(OperatorID(op.get_id()));
        conditions.push_back(cond);
        next_condition_by_op.push_back(conditions.back().begin());
    }

    root = unique_ptr<GeneratorBase>(construct_recursive(0, move(all_operators)));
    utils::release_vector_memory(conditions);
    utils::release_vector_memory(next_condition_by_op);
}

SuccessorGenerator::~SuccessorGenerator() {
}

GeneratorBase *SuccessorGenerator::construct_recursive(
    int switch_var_id, list<OperatorID> &&operator_queue) {
    if (operator_queue.empty())
        return new GeneratorEmpty;

    VariablesProxy variables = task_proxy.get_variables();
    int num_variables = variables.size();

    while (true) {
        // Test if no further switch is necessary (or possible).
        if (switch_var_id == num_variables)
            return new GeneratorLeaf(move(operator_queue));

        VariableProxy switch_var = variables[switch_var_id];
        int number_of_children = switch_var.get_domain_size();

        vector<list<OperatorID>> operators_for_val(number_of_children);
        list<OperatorID> default_operators;
        list<OperatorID> applicable_operators;

        bool all_ops_are_immediate = true;
        bool var_is_interesting = false;

        while (!operator_queue.empty()) {
            OperatorID op_id = operator_queue.front();
            int op_index = op_id.get_index();
            operator_queue.pop_front();
            assert(utils::in_bounds(op_index, next_condition_by_op));
            Condition::const_iterator &cond_iter = next_condition_by_op[op_index];
            if (cond_iter == conditions[op_index].end()) {
                var_is_interesting = true;
                applicable_operators.push_back(op_id);
            } else {
                assert(utils::in_bounds(
                    cond_iter - conditions[op_index].begin(), conditions[op_index]));
                all_ops_are_immediate = false;
                FactProxy fact = *cond_iter;
                if (fact.get_variable() == switch_var) {
                    var_is_interesting = true;
                    while (cond_iter != conditions[op_index].end() &&
                           cond_iter->get_variable() == switch_var) {
                        ++cond_iter;
                    }
                    operators_for_val[fact.get_value()].push_back(op_id);
                } else {
                    default_operators.push_back(op_id);
                }
            }
        }

        if (all_ops_are_immediate) {
            return new GeneratorLeaf(move(applicable_operators));
        } else if (var_is_interesting) {
            vector<GeneratorBase *> generator_for_val;
            for (list<OperatorID> &ops : operators_for_val) {
                generator_for_val.push_back(
                    construct_recursive(switch_var_id + 1, move(ops)));
            }
            GeneratorBase *default_generator = construct_recursive(
                switch_var_id + 1, move(default_operators));
            return new GeneratorSwitch(switch_var,
                                       move(applicable_operators),
                                       move(generator_for_val),
                                       default_generator);
        } else {
            // this switch var can be left out because no operator depends on it
            ++switch_var_id;
            default_operators.swap(operator_queue);
        }
    }
}

void SuccessorGenerator::generate_applicable_ops(
    const State &state, vector<OperatorID> &applicable_ops) const {
    root->generate_applicable_ops(state, applicable_ops);
}


void SuccessorGenerator::generate_applicable_ops(
    const GlobalState &state, vector<OperatorID> &applicable_ops) const {
    root->generate_applicable_ops(state, applicable_ops);
}
