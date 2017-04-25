#! /usr/bin/env python
# -*- coding: utf-8 -*-

#! /usr/bin/env python
# -*- coding: utf-8 -*-

import os

from lab.environments import LocalEnvironment, MaiaEnvironment
from lab.reports import Attribute, arithmetic_mean, geometric_mean

import common_setup
from common_setup import IssueConfig, IssueExperiment
from relativescatter import RelativeScatterPlotReport
from csv_report import CSVReport

DIR = os.path.dirname(os.path.abspath(__file__))
BENCHMARKS_DIR = os.environ["DOWNWARD_BENCHMARKS"]
REVISIONS = ["issue705-base", "issue705-v1"]
CONFIGS = [
    IssueConfig(
        'bounded-blind',
        ['--search', 'astar(blind(), bound=0)'],
    )
]
SUITE = list(sorted(set(common_setup.DEFAULT_OPTIMAL_SUITE) |
                    set(common_setup.DEFAULT_SATISFICING_SUITE)))
ENVIRONMENT = MaiaEnvironment(
    priority=0, email="florian.pommerening@unibas.ch")

if common_setup.is_test_run():
    SUITE = IssueExperiment.DEFAULT_TEST_SUITE
    ENVIRONMENT = LocalEnvironment(processes=1)

exp = IssueExperiment(
    revisions=REVISIONS,
    configs=CONFIGS,
    environment=ENVIRONMENT,
)

exp.add_suite(BENCHMARKS_DIR, SUITE)
exp.add_resource('sg_parser', 'sg-parser.py', dest='sg-parser.py')
exp.add_command('sg-parser', ['{sg_parser}'])

exp.add_absolute_report_step(attributes=[
    Attribute("sg_construction_time", functions=[arithmetic_mean], min_wins=True),
    Attribute("sg_peak_mem_diff", functions=[arithmetic_mean], min_wins=True),

    Attribute("sg_counts_empty", functions=[arithmetic_mean], min_wins=True),
    Attribute("sg_counts_leaf_empty", functions=[arithmetic_mean], min_wins=True),
    Attribute("sg_counts_leaf_more", functions=[arithmetic_mean], min_wins=True),
    Attribute("sg_counts_leaf_single", functions=[arithmetic_mean], min_wins=True),
    Attribute("sg_counts_leaves", functions=[arithmetic_mean], min_wins=True),
    Attribute("sg_counts_switch_empty", functions=[arithmetic_mean], min_wins=True),
    Attribute("sg_counts_switch_more", functions=[arithmetic_mean], min_wins=True),
    Attribute("sg_counts_switch_single", functions=[arithmetic_mean], min_wins=True),
    Attribute("sg_counts_switches", functions=[arithmetic_mean], min_wins=True),
    Attribute("sg_counts_immediates", functions=[arithmetic_mean], min_wins=True),

    Attribute("sg_size_estimate_default_generator", functions=[arithmetic_mean], min_wins=True),
    Attribute("sg_size_estimate_operators", functions=[arithmetic_mean], min_wins=True),
    Attribute("sg_size_estimate_overhead", functions=[arithmetic_mean], min_wins=True),
    Attribute("sg_size_estimate_switch_var", functions=[arithmetic_mean], min_wins=True),
    Attribute("sg_size_estimate_total", functions=[arithmetic_mean], min_wins=True),
    Attribute("sg_size_estimate_value_generator", functions=[arithmetic_mean], min_wins=True),
    Attribute("sg_size_estimate_next_generator", functions=[arithmetic_mean], min_wins=True),

    Attribute("sg_counts_empty_rel", functions=[geometric_mean], min_wins=True),
    Attribute("sg_counts_leaf_empty_rel", functions=[geometric_mean], min_wins=True),
    Attribute("sg_counts_leaf_more_rel", functions=[geometric_mean], min_wins=True),
    Attribute("sg_counts_leaf_single_rel", functions=[geometric_mean], min_wins=True),
    Attribute("sg_counts_leaves_rel", functions=[geometric_mean], min_wins=True),
    Attribute("sg_counts_switch_empty_rel", functions=[geometric_mean], min_wins=True),
    Attribute("sg_counts_switch_more_rel", functions=[geometric_mean], min_wins=True),
    Attribute("sg_counts_switch_single_rel", functions=[geometric_mean], min_wins=True),
    Attribute("sg_counts_switches_rel", functions=[geometric_mean], min_wins=True),
    Attribute("sg_counts_immediates_rel", functions=[geometric_mean], min_wins=True),

    Attribute("sg_size_estimate_default_generator_rel", functions=[geometric_mean], min_wins=True),
    Attribute("sg_size_estimate_operators_rel", functions=[geometric_mean], min_wins=True),
    Attribute("sg_size_estimate_overhead_rel", functions=[geometric_mean], min_wins=True),
    Attribute("sg_size_estimate_switch_var_rel", functions=[geometric_mean], min_wins=True),
    Attribute("sg_size_estimate_value_generator_rel", functions=[geometric_mean], min_wins=True),
    Attribute("sg_size_estimate_next_generator_rel", functions=[geometric_mean], min_wins=True),

    "error",
    "run_dir",
])

exp.add_report(CSVReport(attributes=["algorithm", "domain", "sg_*", "translator_task_size"]), outfile="csvreport.csv")


exp.run_steps()
