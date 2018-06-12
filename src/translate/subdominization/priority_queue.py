#! /usr/bin/env python
# -*- coding: utf-8 -*-

import options
from subdominization.model import TrainedModel

from _collections import deque, defaultdict
import heapq

from operator import itemgetter

from random import randint

import timers



class PriorityQueue():
    def __init__(self):
        fail
    def print_stats(self):
        print("no statistics available")
    
class FIFOQueue(PriorityQueue):
    def __init__(self):
        self.queue = []
        self.queue_pos = 0
    def __bool__(self):
        return self.queue_pos < len(self.queue)
    __nonzero__ = __bool__
    def print_info(self):
        print("Using FIFO priority queue for actions.")
    def push(self, atom):
        self.queue.append(atom)
    def pop(self):
        result = self.queue[self.queue_pos]
        self.queue_pos += 1
        return result
    
class LIFOQueue(PriorityQueue):
    def __init__(self):
        self.queue = []
    def __bool__(self):
        return len(self.queue) > 0
    __nonzero__ = __bool__
    def print_info(self):
        print("Using LIFO priority queue for actions.")
    def push(self, atom):
        self.queue.append(atom)
    def pop(self):
        return self.queue.pop()
    
class RandomQueue(PriorityQueue):
    def __init__(self):
        self.queue = []
    def __bool__(self):
        return len(self.queue) > 0
    __nonzero__ = __bool__
    def print_info(self):
        print("Using random priority queue for actions.")
    def push(self, atom):
        self.queue.append((atom, randint(0, 10)))
        self.queue = sorted(self.queue, key=itemgetter(1))
    def pop(self):
        return self.queue.pop()[0]
    
class RandomHeapQueue(PriorityQueue):
    def __init__(self):
        self.queue = []
    def __bool__(self):
        return len(self.queue) > 0
    __nonzero__ = __bool__
    def print_info(self):
        print("Using randomheap priority queue for actions.")
    def push(self, atom):
        heapq.heappush(self.queue, (randint(0, 10), atom))
    def pop(self):
        return heapq.heappop(self.queue)[1]

class HikingTestQueue(PriorityQueue):
    def __init__(self):
        self.queue = []
        self.num_grounded = 0
    def __bool__(self):
        return len(self.queue) > 0
    __nonzero__ = __bool__
    def print_info(self):
        print("Using Hiking test priority queue for actions.")
    def push(self, atom):
        prio = 0.5
        if ("drive_tent_passenger" in str(atom)):
            self.num_grounded = self.num_grounded + 1
            if (self.num_grounded > 5000):
                prio = 1
        heapq.heappush(self.queue, (prio, atom))
    def pop(self):
        return heapq.heappop(self.queue)[1]
    
class TrainedQueue(PriorityQueue):
    def __init__(self, task):
        if (not options.trained_model_folder):
            sys.exit("Error: need trained model to use this queue. Please specify using --trained-mode-folder")
        if (not task):
            sys.exit("Error: no task given")
        self.queue = []
        timer = timers.Timer()
        self.model = TrainedModel(options.trained_model_folder, task)
        self.loading_time = str(timer)
    def __bool__(self):
        return len(self.queue) > 0
    __nonzero__ = __bool__
    def print_info(self):
        print("Using heap priority queue with a trained model for actions.")
        print("Loaded trained model from", options.trained_model_folder, self.loading_time)
    def print_stats(self):
        self.model.print_stats()
    def push(self, atom):
        heapq.heappush(self.queue, (self.model.get_estimate(atom), atom))
    def pop(self):
        return heapq.heappop(self.queue)[1]
    
class SchemaRoundRobinQueue(PriorityQueue):
    def __init__(self):
        self.schemas = []
        self.current = 0
        self.queues = []
    def __bool__(self):
        for queue in self.queues:
            if (queue):
                return True
        return False
    __nonzero__ = __bool__
    def print_info(self):
        print("Using SchemaRoundRobin priority queue for actions.")
    def push(self, atom):
        if (not atom.predicate.name in self.schemas):
            self.schemas.append(atom.predicate.name)
            self.queues.append(FIFOQueue())        
        self.queues[self.schemas.index(atom.predicate.name)].push(atom)
    def pop(self):
        while True:
            self.current = (self.current + 1) % len(self.schemas)
            if (self.queues[self.current]):
                return self.queues[self.current].pop()
    
def get_action_queue_from_options(task = None):
    name = options.grounding_action_queue_ordering.lower()
    if (name == "fifo"):
        return FIFOQueue()
    elif (name == "lifo"):
        return LIFOQueue()
    elif (name == "random"):
        return RandomQueue()
    elif (name == "randomheap"):
        return RandomHeapQueue()
    elif (name == "hiking"):
        return HikingTestQueue()
    elif (name == "trained"):
        return TrainedQueue(task)
    elif (name == "roundrobin"):
        return SchemaRoundRobinQueue()
    else:
        sys.exit("Error: unknown queue type: " + name)
        
        
