#! /usr/bin/env python

from __future__ import print_function

import os
import subprocess
import sys
sys.path.insert(1, '../../')
from driver import returncodes

DIR = os.path.dirname(os.path.abspath(__file__))
REPO_BASE = os.path.dirname(os.path.dirname(DIR))
BENCHMARKS_DIR = os.path.join(REPO_BASE, "misc", "tests", "benchmarks")
DRIVER = os.path.join(REPO_BASE, "fast-downward.py")

TRANSLATE_TASKS = {
    "small": "gripper/prob01.pddl",
    "time-intense": "trucks-strips/p10.pddl",
    "memory-intense": "satellite/p33-HC-pfile13.pddl",
}

TRANSLATE_TESTS = [
    ("small", ["--translate"], returncodes.EXIT_SUCCESS),
    ("time-intense", ["--translate-time-limit", "2s", "--translate"], returncodes.EXIT_TRANSLATE_SIGXCPU),
    ("memory-intense", ["--translate-memory-limit", "100M", "--translate"], returncodes.EXIT_TRANSLATE_OUT_OF_MEMORY),
]

SEARCH_TASKS = {
    "strips": "miconic/s1-0.pddl",
    "axioms": "philosophers/p01-phil2.pddl",
    "cond-eff": "miconic-simpleadl/s1-0.pddl",
}

MERGE_AND_SHRINK = ('astar(merge_and_shrink('
    'merge_strategy=merge_stateless(merge_selector='
        'score_based_filtering(scoring_functions=[goal_relevance,'
        'dfp,total_order(atomic_ts_order=reverse_level,'
        'product_ts_order=new_to_old,atomic_before_product=false)])),'
    'shrink_strategy=shrink_bisimulation(greedy=false),'
    'label_reduction=exact('
        'before_shrinking=true,'
        'before_merging=false),'
    'max_states=50000,threshold_before_merge=1'
'))')

SEARCH_TESTS = [
    ("strips", "astar(add())", returncodes.EXIT_SUCCESS),
    ("strips", "astar(hm())", returncodes.EXIT_SUCCESS),
    ("strips", "ehc(hm())", returncodes.EXIT_SUCCESS),
    ("strips", "astar(ipdb())", returncodes.EXIT_SUCCESS),
    ("strips", "astar(lmcut())", returncodes.EXIT_SUCCESS),
    ("strips", "astar(lmcount(lm_rhw(), admissible=false))", returncodes.EXIT_SUCCESS),
    ("strips", "astar(lmcount(lm_rhw(), admissible=true))", returncodes.EXIT_SUCCESS),
    ("strips", "astar(lmcount(lm_hm(), admissible=false))", returncodes.EXIT_SUCCESS),
    ("strips", "astar(lmcount(lm_hm(), admissible=true))", returncodes.EXIT_SUCCESS),
    ("strips", MERGE_AND_SHRINK, returncodes.EXIT_SUCCESS),
    ("axioms", "astar(add())", returncodes.EXIT_SUCCESS),
    ("axioms", "astar(hm())", returncodes.EXIT_SEARCH_UNSOLVED_INCOMPLETE),
    ("axioms", "ehc(hm())", returncodes.EXIT_SEARCH_UNSOLVED_INCOMPLETE),
    ("axioms", "astar(ipdb())", returncodes.EXIT_SEARCH_UNSUPPORTED),
    ("axioms", "astar(lmcut())", returncodes.EXIT_SEARCH_UNSUPPORTED),
    ("axioms", "astar(lmcount(lm_rhw(), admissible=false))", returncodes.EXIT_SUCCESS),
    ("axioms", "astar(lmcount(lm_rhw(), admissible=true))", returncodes.EXIT_SEARCH_UNSUPPORTED),
    ("axioms", "astar(lmcount(lm_zg(), admissible=false))", returncodes.EXIT_SUCCESS),
    ("axioms", "astar(lmcount(lm_zg(), admissible=true))", returncodes.EXIT_SEARCH_UNSUPPORTED),
    # h^m landmark factory explicitly forbids axioms.
    ("axioms", "astar(lmcount(lm_hm(), admissible=false))", returncodes.EXIT_SEARCH_UNSUPPORTED),
    ("axioms", "astar(lmcount(lm_hm(), admissible=true))", returncodes.EXIT_SEARCH_UNSUPPORTED),
    ("axioms", "astar(lmcount(lm_exhaust(), admissible=false))", returncodes.EXIT_SUCCESS),
    ("axioms", "astar(lmcount(lm_exhaust(), admissible=true))", returncodes.EXIT_SEARCH_UNSUPPORTED),
    ("axioms", MERGE_AND_SHRINK, returncodes.EXIT_SEARCH_UNSUPPORTED),
    ("cond-eff", "astar(add())", returncodes.EXIT_SUCCESS),
    ("cond-eff", "astar(hm())", returncodes.EXIT_SUCCESS),
    ("cond-eff", "astar(ipdb())", returncodes.EXIT_SEARCH_UNSUPPORTED),
    ("cond-eff", "astar(lmcut())", returncodes.EXIT_SEARCH_UNSUPPORTED),
    ("cond-eff", "astar(lmcount(lm_rhw(), admissible=false))", returncodes.EXIT_SUCCESS),
    ("cond-eff", "astar(lmcount(lm_rhw(), admissible=true))", returncodes.EXIT_SUCCESS),
    ("cond-eff", "astar(lmcount(lm_zg(), admissible=false))", returncodes.EXIT_SUCCESS),
    ("cond-eff", "astar(lmcount(lm_zg(), admissible=true))", returncodes.EXIT_SUCCESS),
    ("cond-eff", "astar(lmcount(lm_hm(), admissible=false))", returncodes.EXIT_SUCCESS),
    ("cond-eff", "astar(lmcount(lm_hm(), admissible=true))", returncodes.EXIT_SEARCH_UNSUPPORTED),
    ("cond-eff", "astar(lmcount(lm_exhaust(), admissible=false))", returncodes.EXIT_SUCCESS),
    ("cond-eff", "astar(lmcount(lm_exhaust(), admissible=true))", returncodes.EXIT_SEARCH_UNSUPPORTED),
    ("cond-eff", MERGE_AND_SHRINK, returncodes.EXIT_SUCCESS),
]


def cleanup():
    subprocess.check_call([sys.executable, DRIVER, "--cleanup"])


def run_translator(task_type, relpath, command):
    problem = os.path.join(BENCHMARKS_DIR, relpath)
    print("\nRun %(command)s on %(task_type)s task:" % locals())
    sys.stdout.flush()
    cmd = [sys.executable, DRIVER]
    cmd.extend(command)
    cmd.append(problem)
    return subprocess.call(cmd)


def run_translator_tests(failures):
    for task_type, command, expected in TRANSLATE_TESTS:
        relpath = TRANSLATE_TASKS[task_type]
        exitcode = run_translator(task_type, relpath, command)
        if not exitcode == expected:
            failures.append((task_type, command, expected, exitcode))
        cleanup()


def run_search(task_type, relpath, search):
    problem = os.path.join(BENCHMARKS_DIR, relpath)
    print("\nRun %(search)s on %(task_type)s task:" % locals())
    sys.stdout.flush()
    return subprocess.call(
        [sys.executable, DRIVER, problem, "--search", search])


def run_search_tests(failures):
    for task_type, search, expected in SEARCH_TESTS:
        relpath = SEARCH_TASKS[task_type]
        exitcode = run_search(task_type, relpath, search)
        if not exitcode == expected:
            failures.append((task_type, search, expected, exitcode))
        cleanup()


def main():
    # On Windows, ./build.py has to be called from the correct environment.
    # Since we want this script to work even when we are in a regular
    # shell, we do not build on Windows. If the planner is not yet built,
    # the driver script will complain about this.
    if os.name == "posix":
        subprocess.check_call(["./build.py"], cwd=REPO_BASE)

    failures = []
    run_translator_tests(failures)
    run_search_tests(failures)
    if failures:
        print("\nFailures:")
        for task_type, command, expected, exitcode in failures:
            print("%(command)s on %(task_type)s task: expected %(expected)d, "
                   "got %(exitcode)d" % locals())
        sys.exit(1)

    print("\nNo errors detected.")


main()
