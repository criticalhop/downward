#! /usr/bin/env python
# -*- coding: utf-8 -*-

import options

from _collections import deque
import heapq

from operator import itemgetter

from random import randint

class PriorityQueue():
    def __init__(self):
        print("should not instantiate PriorityQueue directly")
        exit(1)
    
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
    
def get_action_queue_from_options():
    name = options.grounding_action_queue_ordering.lower()
    if (name == "fifo"):
        return FIFOQueue()
    elif (name == "lifo"):
        return LIFOQueue()
    elif (name == "random"):
        return RandomQueue()
    elif (name == "randomheap"):
        return RandomHeapQueue()
    else:
        print("INPUT ERROR: unknown queue type: " + name)
        exit(1)
        
        