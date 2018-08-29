# -*- coding: utf-8 -*-
from __future__ import print_function

import logging
import sys

from . import aliases
from . import arguments
from . import cleanup
from . import run_components
from . import returncodes as rc
from . import util


def main():
    args = arguments.parse_args()
    logging.basicConfig(level=getattr(logging, args.log_level.upper()),
                        format="%(levelname)-8s %(message)s",
                        stream=sys.stdout)
    logging.debug("processed args: %s" % args)

    if args.show_aliases:
        aliases.show_aliases()
        sys.exit()

    if args.cleanup:
        cleanup.cleanup_temporary_files(args)
        sys.exit()
        
    if (args.incremental_grounding):
        if (not "translate" in args.components or not "search" in args.components):
            sys.exit("ERROR: need to execute translator and search to do incremental grounding.")
        if ("--termination-condition" in args.translate_options):
            sys.exit("ERROR: must not specify a termination condition when using incremental grounding.")

        num_grounded_actions = -1
        args.search_time_limit = args.incremental_grounding_search_time_limit if args.incremental_grounding_search_time_limit else 10 * 60
        increment = args.incremental_grounding_increment if args.incremental_grounding_increment else 10000
        old_translate_options = list(args.translate_options)
        old_search_options = list(args.search_options)
        if (args.incremental_grounding_increment_percentage):
            args.incremental_grounding_increment_percentage = args.incremental_grounding_increment_percentage / 100 + 1
        while (True):
            if (args.overall_time_limit and args.overall_time_limit - util.get_elapsed_time() <= 0):
                print("incremental grounding ran out of time")
                sys.exit(rc.TRANSLATE_OUT_OF_TIME)
            termination_condition = ["--termination-condition", "goal-relaxed-reachable"]
            if (num_grounded_actions != -1):
                if (not args.incremental_grounding_increment and args.incremental_grounding_increment_percentage):
                    new_limit = int(num_grounded_actions * args.incremental_grounding_increment_percentage)
                else:
                    new_limit = int(num_grounded_actions / increment) * increment
                    if (args.incremental_grounding_increment_percentage):
                        inc = max(increment, int(num_grounded_actions * (args.incremental_grounding_increment_percentage - 1)))
                        if (inc == increment):
                            new_limit = int(num_grounded_actions / increment) * increment + increment
                        else:
                            new_limit = num_grounded_actions + inc
                    else:
                        new_limit = int(num_grounded_actions / increment) * increment + increment
                termination_condition += ["min-number", str(new_limit)]
            args.translate_options = old_translate_options + termination_condition
            
            (exitcode, continue_execution, num_grounded_actions) = run_components.run_translate(args, True)
            
            print()
            print("translate exit code: {exitcode}".format(**locals()))
            if (exitcode in [rc.TRANSLATE_OUT_OF_MEMORY, rc.TRANSLATE_OUT_OF_TIME, rc.TRANSLATE_CRITICAL_ERROR, rc.TRANSLATE_INPUT_ERROR]):
                print("Driver aborting after translator")
                sys.exit(exitcode)
            elif (exitcode == rc.TRANSLATE_UNSOLVABLE):
                num_grounded_actions = new_limit
                print("Task proved unsolvable in translator, increasing minimum number of grounded actions.")
                continue
            
            args.search_options = list(old_search_options)
            
            (exitcode, continue_execution) = run_components.run_search(args)
            
            print()
            print("search exit code: {exitcode}".format(**locals()))
            if (exitcode in [rc.SUCCESS, rc.SEARCH_PLAN_FOUND_AND_OUT_OF_MEMORY, rc.SEARCH_PLAN_FOUND_AND_OUT_OF_TIME, rc.SEARCH_PLAN_FOUND_AND_OUT_OF_MEMORY_AND_TIME]):
                break
            elif (exitcode in [rc.SEARCH_INPUT_ERROR, rc.SEARCH_UNSUPPORTED]):
                print("Driver aborting after search")
                sys.exit(exitcode)
        if ("validate" in args.components):
            (exitcode, continue_execution) = run_components.run_validate(args)
            print()
            print("validate exit code: {exitcode}".format(**locals()))
        print("incremental grounding successfull after {time}s".format(time=util.get_elapsed_time()))
        sys.exit(exitcode)
    elif (args.incremental_grounding_search_time_limit or args.incremental_grounding_increment):
        sys.exit("ERROR: need to specify --incremental-grounding to use its special options.")
        
    
    exitcode = None
    for component in args.components:
        if component == "translate":
            (exitcode, continue_execution) = run_components.run_translate(args)
        elif component == "search":
            (exitcode, continue_execution) = run_components.run_search(args)
        elif component == "validate":
            (exitcode, continue_execution) = run_components.run_validate(args)
        else:
            assert False
        print()
        print("{component} exit code: {exitcode}".format(**locals()))
        if not continue_execution:
            print("Driver aborting after {}".format(component))
            break
    # Exit with the exit code of the last component that ran successfully.
    # This means for example that if no plan was found, validate is not run,
    # and therefore the return code is that of the search.
    sys.exit(exitcode)


if __name__ == "__main__":
    main()
