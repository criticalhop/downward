#! /usr/bin/env python
# -*- coding: utf-8 -*-

import options
import pddl

import sys


class TerminationCondition():
    def print_info(self):
        pass
    def terminate(self):
        pass
    def notify_atom(self, atom):
        pass
    
class DefaultCondition(TerminationCondition):
    def print_info(self):
        print("Using default termination condition, i.e. grounding all actions.")
    def terminate(self):
        return False
    def notify_atom(self, atom):
        pass
    
class GoalRelaxedReachableCondition(TerminationCondition):
    def __init__(self):
        self.goal_reached = False
    def print_info(self):
        print("Grounding stopped if goal is relaxed reachable.")
    def terminate(self):
        return self.goal_reached
    def notify_atom(self, atom):
        if (not self.goal_reached and isinstance(atom.predicate, str) and atom.predicate == "@goal-reachable"):
            self.goal_reached = True
    
class GoalRelaxedReachablePlusNumberCondition(TerminationCondition):
    def __init__(self, num_additional_actions):
        self.goal_reached = False
        self.num_additional_actions = int(num_additional_actions)
    def print_info(self):
        print("Grounding stopped if goal is relaxed reachable + %d additional actions." % self.num_additional_actions)
    def terminate(self):
        return self.goal_reached and self.num_additional_actions <= 0
    def notify_atom(self, atom):
        if (self.goal_reached):
            if (isinstance(atom.predicate, pddl.Action)):
                self.num_additional_actions -= 1
        elif (isinstance(atom.predicate, str) and atom.predicate == "@goal-reachable"):
            self.goal_reached = True
            
class GoalRelaxedReachableMinNumberCondition(TerminationCondition):
    def __init__(self, min_num_actions):
        self.goal_reached = False
        self.min_num_actions = int(min_num_actions)
    def print_info(self):
        print("Grounding stopped if goal is relaxed reachable and at least %d actions have been grounded." % self.min_num_actions)
    def terminate(self):
        return self.goal_reached and self.min_num_actions <= 0
    def notify_atom(self, atom):
        if (isinstance(atom.predicate, pddl.Action)):
            self.min_num_actions -= 1
        elif (isinstance(atom.predicate, str) and atom.predicate == "@goal-reachable"):
            self.goal_reached = True

class GoalRelaxedReachablePlusPercentageCondition(TerminationCondition):
    def __init__(self, percentage_additional_actions):
        self.goal_reached = False
        self.percentage_additional_actions = int(percentage_additional_actions)
        if (self.percentage_additional_actions < 0):
           sys.exit("ERROR: percentage of additional actions must be >=0") 
        self.number_grounded_actions = 0
    def print_info(self):
        print("Grounding stopped if goal is relaxed reachable + {percentage}% additional actions.".format(percentage = self.percentage_additional_actions))
    def terminate(self):
        return self.goal_reached and self.num_additional_actions <= 0
    def notify_atom(self, atom):
        if (self.goal_reached):
            if (isinstance(atom.predicate, pddl.Action)):
                self.num_additional_actions -= 1
        elif (isinstance(atom.predicate, str) and atom.predicate == "@goal-reachable"):
            self.goal_reached = True
            self.num_additional_actions = self.number_grounded_actions * self.percentage_additional_actions / 100
        elif (isinstance(atom.predicate, pddl.Action)):
            self.number_grounded_actions += 1 
    
def get_termination_condition_from_options():
    args = options.termination_condition
    if (len(args) == 1):
        if (args[0] == "default"):
            return DefaultCondition()
        elif (args[0] == "goal-relaxed-reachable"):
            return GoalRelaxedReachableCondition()
        else:
            sys.exit("Error: unknown termination condition: " + args[0])
    elif (len(args) == 3):
        if (args[0] == "goal-relaxed-reachable"):
            if (args[1] == "number"):
                return GoalRelaxedReachablePlusNumberCondition(args[2])
            if (args[1] == "min-number"):
                return GoalRelaxedReachableMinNumberCondition(args[2])
            elif (args[1] == "percentage"):
                return GoalRelaxedReachablePlusPercentageCondition(args[2])
            else:
                sys.exit("ERROR: unknown option for goal-relaxed-reachable termination condition " + args[1])
        else:
            sys.exit("ERROR: unknown termination condition " + args[0])
    else:
        sys.exit("ERROR: unrecognized termination condition " + str(args))
        
        
