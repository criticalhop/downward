#! /usr/bin/env python
# -*- coding: utf-8 -*-

from downward import suites
from lab.reports import Attribute, gm

import common_setup


def main(revisions=None):
    SUITE = suites.suite_optimal_with_ipc11()

    B_CONFIGS = {
        'dfp-b50k': ['--search', 'astar(merge_and_shrink(merge_strategy=merge_dfp,shrink_strategy=shrink_bisimulation(max_states=50000,threshold=1,greedy=false),label_reduction=label_reduction(before_shrinking=true,before_merging=false)))'],
    }
    G_CONFIGS = {
        'dfp-ginf': ['--search', 'astar(merge_and_shrink(merge_strategy=merge_dfp,shrink_strategy=shrink_bisimulation(max_states=infinity,threshold=1,greedy=true),label_reduction=label_reduction(before_shrinking=true,before_merging=false)))'],
    }
    F_CONFIGS = {
        'dfp-f50k': ['--search', 'astar(merge_and_shrink(merge_strategy=merge_dfp,shrink_strategy=shrink_fh(max_states=50000),label_reduction=label_reduction(before_shrinking=false,before_merging=true)))'],
    }
    CONFIGS = dict(B_CONFIGS)
    CONFIGS.update(G_CONFIGS)
    CONFIGS.update(F_CONFIGS)

    exp = common_setup.IssueExperiment(
        revisions=revisions,
        configs=CONFIGS,
        suite=SUITE,
        test_suite=['depot:pfile1'],
        processes=4,
        email='silvan.sievers@unibas.ch',
    )
    exp.add_resource('ms_parser', 'ms-parser.py', dest='ms-parser.py')
    exp.add_command('ms-parser', ['ms_parser'])

    # planner outcome attributes
    perfect_heuristic = Attribute('perfect_heuristic', absolute=True, min_wins=False)
    proved_unsolvability = Attribute('proved_unsolvability', absolute=True, min_wins=False)
    actual_search_time = Attribute('actual_search_time', absolute=False, min_wins=True, functions=[gm])
    initial_h_value = Attribute('initial_h_value', absolute=False, min_wins=False)

    # m&s attributes
    ms_construction_time = Attribute('ms_construction_time', absolute=False, min_wins=True, functions=[gm])
    ms_abstraction_constructed = Attribute('ms_abstraction_constructed', absolute=True, min_wins=False)
    ms_final_size = Attribute('ms_final_size', absolute=False, min_wins=True)
    ms_out_of_memory = Attribute('ms_out_of_memory', absolute=True, min_wins=True)
    ms_out_of_time = Attribute('ms_out_of_time', absolute=True, min_wins=True)
    search_out_of_memory = Attribute('search_out_of_memory', absolute=True, min_wins=True)
    search_out_of_time = Attribute('search_out_of_time', absolute=True, min_wins=True)

    extra_attributes = [
        perfect_heuristic,
        proved_unsolvability,
        actual_search_time,
        initial_h_value,

        ms_construction_time,
        ms_abstraction_constructed,
        ms_final_size,
        ms_out_of_memory,
        ms_out_of_time,
        search_out_of_memory,
        search_out_of_time,
    ]
    attributes = exp.DEFAULT_TABLE_ATTRIBUTES
    attributes.extend(extra_attributes)

    exp.add_comparison_table_step(attributes=attributes)

    exp()

if __name__ == '__main__':
    main(revisions=['issue583-base-v2', 'issue583-v4'])
