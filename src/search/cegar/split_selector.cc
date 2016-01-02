#include "split_selector.h"

#include "abstract_state.h"

#include "../globals.h"

#include "../heuristics/additive_heuristic.h"

#include "../utils/logging.h"
#include "../utils/rng.h"

#include <cassert>
#include <iostream>
#include <limits>

using namespace std;

namespace CEGAR {
SplitSelector::SplitSelector(
    const std::shared_ptr<AbstractTask> &task,
    PickSplit pick)
    : task(task),
      task_proxy(*task),
      pick(pick) {
    if (pick == PickSplit::MIN_HADD || pick == PickSplit::MAX_HADD) {
        additive_heuristic = get_additive_heuristic(task);
        additive_heuristic->initialize_and_compute_heuristic_for_cegar(
            task_proxy.get_initial_state());
    }
}

// Define here to avoid include in header.
SplitSelector::~SplitSelector() {
}

int SplitSelector::get_num_unwanted_values(
    const AbstractState &state, const Split &split) const {
    int num_unwanted_values = state.count(split.var_id) - split.values.size();
    assert(num_unwanted_values >= 1);
    return num_unwanted_values;
}

double SplitSelector::get_refinedness(const AbstractState &state, int var_id) const {
    double all_values = task_proxy.get_variables()[var_id].get_domain_size();
    assert(all_values >= 2);
    double remaining_values = state.count(var_id);
    assert(2 <= remaining_values && remaining_values <= all_values);
    double refinedness = -(remaining_values / all_values);
    assert(-1.0 <= refinedness && refinedness < 0.0);
    return refinedness;
}

int SplitSelector::get_hadd_value(int var_id, int value) const {
    assert(additive_heuristic);
    int hadd = additive_heuristic->get_cost_for_cegar(var_id, value);
    assert(hadd != -1);
    return hadd;
}

int SplitSelector::get_min_hadd_value(int var_id, const vector<int> &values) const {
    int min_hadd = numeric_limits<int>::max();
    for (int value : values) {
        const int hadd = get_hadd_value(var_id, value);
        if (hadd < min_hadd) {
            min_hadd = hadd;
        }
    }
    return min_hadd;
}

int SplitSelector::get_max_hadd_value(int var_id, const vector<int> &values) const {
    int max_hadd = -1;
    for (int value : values) {
        const int hadd = get_hadd_value(var_id, value);
        if (hadd > max_hadd) {
            max_hadd = hadd;
        }
    }
    return max_hadd;
}

double SplitSelector::rate_split(const AbstractState &state, const Split &split) const {
    int var_id = split.var_id;
    const vector<int> &values = split.values;
    double rating;
    if (pick == PickSplit::MIN_UNWANTED || pick == PickSplit::MAX_UNWANTED) {
        rating = get_num_unwanted_values(state, split);
    } else if (pick == PickSplit::MIN_REFINED || pick == PickSplit::MAX_REFINED) {
        rating = get_refinedness(state, var_id);
    } else if (pick == PickSplit::MIN_HADD) {
        rating = get_min_hadd_value(var_id, values);
    } else if (pick == PickSplit::MAX_HADD) {
        rating = get_max_hadd_value(var_id, values);
    } else {
        cout << "Invalid pick strategy: " << static_cast<int>(pick) << endl;
        Utils::exit_with(Utils::ExitCode::INPUT_ERROR);
    }
    if (pick == PickSplit::MIN_UNWANTED ||
        pick == PickSplit::MIN_REFINED ||
        pick == PickSplit::MIN_HADD) {
        rating = -rating;
    }
    return rating;
}

const Split &SplitSelector::pick_split(const AbstractState &state,
                                       const vector<Split> &splits) const {
    assert(!splits.empty());

    if (splits.size() == 1) {
        return splits[0];
    }

    if (DEBUG) {
        cout << "Splits for state " << state << ": " << endl;
        for (const Split &split : splits)
            cout << split.var_id << "=" << split.values << " ";
        cout << endl;
    }

    if (pick == PickSplit::RANDOM) {
        return *g_rng.choose(splits);
    }

    double max_rating = numeric_limits<double>::lowest();
    const Split *selected_split = nullptr;
    for (const Split &split : splits) {
        double rating = rate_split(state, split);
        if (rating > max_rating) {
            selected_split = &split;
            max_rating = rating;
        }
    }
    assert(selected_split);
    return *selected_split;
}
}
