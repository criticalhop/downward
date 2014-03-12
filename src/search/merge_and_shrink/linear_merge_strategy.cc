#include "linear_merge_strategy.h"

#include "../option_parser.h"
#include "../plugin.h"
#include "../utilities.h"

#include <cassert>
#include <cstdlib>

using namespace std;

LinearMergeStrategy::LinearMergeStrategy(const Options &opts)
    : MergeStrategy(),
      order(VariableOrderType(opts.get_enum("type"))),
      first_index(-1) {
}

bool LinearMergeStrategy::done() const {
    return order.done();
}

pair<int, int> LinearMergeStrategy::get_next(const std::vector<Abstraction *> &all_abstractions) {
    if (first_index == -1) {
        first_index = order.next();
        cout << "First variable: " << first_index << endl;
    }
    int first = first_index;
    int second = order.next();
    cout << "Next variable: " << second << endl;
    assert(all_abstractions[first]);
    if (!all_abstractions[second]) {
        exit_with(EXIT_CRITICAL_ERROR);
    }
    assert(all_abstractions[second]);
    return make_pair(first, second);
}

void LinearMergeStrategy::dump_strategy_specific_options() const {
    cout << "Linear merge strategy: ";
    order.dump();
}

string LinearMergeStrategy::name() const {
    return "linear";
}

static MergeStrategy *_parse(OptionParser &parser) {
    vector<string> merge_strategies;
    //TODO: it's a bit dangerous that the merge strategies here
    // have to be specified exactly in the same order
    // as in the enum definition. Try to find a way around this,
    // or at least raise an error when the order is wrong.
    merge_strategies.push_back("CG_GOAL_LEVEL");
    merge_strategies.push_back("CG_GOAL_RANDOM");
    merge_strategies.push_back("GOAL_CG_LEVEL");
    merge_strategies.push_back("RANDOM");
    merge_strategies.push_back("LEVEL");
    merge_strategies.push_back("REVERSE_LEVEL");
    parser.add_enum_option("type", merge_strategies,
                           "linear merge strategy",
                           "CG_GOAL_LEVEL");

    Options opts = parser.parse();
    if (parser.help_mode())
        return 0;
    if (!parser.dry_run())
        return new LinearMergeStrategy(opts);
    else
        return 0;
}

static Plugin<MergeStrategy> _plugin("merge_linear", _parse);

