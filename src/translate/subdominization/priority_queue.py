#! /usr/bin/env python
# -*- coding: utf-8 -*-

import options

from _collections import deque, defaultdict
import heapq

from operator import itemgetter

from random import randint

import timers
import sys



class PriorityQueue():
    def __init__(self):
        fail
    def get_final_queue(self):
        pass
    def print_stats(self):
        print("no statistics available")
    
class FIFOQueue(PriorityQueue):
    def __init__(self):
        self.queue = []
        self.queue_pos = 0
    def __bool__(self):
        return self.queue_pos < len(self.queue)
    __nonzero__ = __bool__
    def get_final_queue(self):
        return self.queue[:self.queue_pos]
    def print_info(self):
        print("Using FIFO priority queue for actions.")
    def push(self, action):
        self.queue.append(action)
    def pop(self):
        result = self.queue[self.queue_pos]
        self.queue_pos += 1
        return result
    
class LIFOQueue(PriorityQueue):
    def __init__(self):
        self.queue = []
        self.closed = []
    def __bool__(self):
        return len(self.queue) > 0
    __nonzero__ = __bool__
    def get_final_queue(self):
        return self.closed
    def print_info(self):
        print("Using LIFO priority queue for actions.")
    def push(self, action):
        self.queue.append(action)
    def pop(self):
        result = self.queue.pop()
        self.closed.append(result) 
        return result
    
class RandomHeapQueue(PriorityQueue):
    def __init__(self):
        self.queue = []
        self.closed = []
    def __bool__(self):
        return len(self.queue) > 0
    __nonzero__ = __bool__
    def get_final_queue(self):
        return self.closed
    def print_info(self):
        print("Using randomheap priority queue for actions.")
    def push(self, action):
        heapq.heappush(self.queue, (randint(0, 10), action))
    def pop(self):
        result = heapq.heappop(self.queue)[1]
        self.closed.append(result)
        return result

class HikingTestQueue(PriorityQueue):
    def __init__(self):
        self.queue = []
        self.closed = []
        self.num_grounded = 0
    def __bool__(self):
        return len(self.queue) > 0
    __nonzero__ = __bool__
    def get_final_queue(self):
        return self.closed
    def print_info(self):
        print("Using Hiking test priority queue for actions.")
    def push(self, action):
        prio = 0.5
        if ("drive_tent_passenger" in str(action)):
            self.num_grounded = self.num_grounded + 1
            if (self.num_grounded > 5000):
                prio = 1
        heapq.heappush(self.queue, (prio, action))
    def pop(self):
        result = heapq.heappop(self.queue)[1]
        self.closed.append(result)
        return result
    
class TrainedQueue(PriorityQueue):
    def __init__(self, task):
        from subdominization.model import TrainedModel
        if (not options.trained_model_folder):
            sys.exit("Error: need trained model to use this queue. Please specify using --trained-mode-folder")
        if (not task):
            sys.exit("Error: no task given")
        self.queue = []
        self.closed = []
#         self.sorted_closed = []
#         self.pop_count = 0
        timer = timers.Timer()
        self.model = TrainedModel(options.trained_model_folder, task)
        self.loading_time = str(timer)
    def __bool__(self):
        return len(self.queue) > 0
    __nonzero__ = __bool__
    def get_final_queue(self):
        return self.closed
    def print_info(self):
        print("Using heap priority queue with a trained model for actions.")
        print("Loaded trained model from", options.trained_model_folder, self.loading_time)
    def print_stats(self):
        self.model.print_stats()
#         while(len(self.sorted_closed) > 0):
#             item = heapq.heappop(self.sorted_closed)
#             print(round(1 - item[0], 2), item[1], "(" + str(item[2].predicate.name), end=" ")
#             print(item[2].args[0], end="")
#             for arg in item[2].args[1:]:
#                 print(" " + arg, end="")
#             print(")")
    def push(self, action):
        heapq.heappush(self.queue, (1 - self.model.get_estimate(action), action))
    def pop(self):
        result = heapq.heappop(self.queue)
        self.closed.append(result[1])
#         heapq.heappush(self.sorted_closed, (result[0], self.pop_count, result[1]))
#         self.pop_count += 1
        return result[1]
    
class SchemaRoundRobinQueue(PriorityQueue):
    def __init__(self):
        self.schemas = []
        self.current = 0
        self.queues = []
        self.num_grounded_actions = []
    def __bool__(self):
        for queue in self.queues:
            if (queue):
                return True
        return False
    __nonzero__ = __bool__
    def get_final_queue(self):
        result = []
        for queue in self.queues:
            result += queue.get_final_queue()
        return result
    def print_info(self):
        print("Using SchemaRoundRobin priority queue for actions.")
    def print_stats(self):
        for i in range(len(self.num_grounded_actions)):
            print("%d actions grounded for schema %s" % (self.num_grounded_actions[i], self.schemas[i]))
    def push(self, action):
        if (not action.predicate.name in self.schemas):
            self.schemas.append(action.predicate.name)
            self.queues.append(FIFOQueue())
            self.num_grounded_actions.append(0)
        self.queues[self.schemas.index(action.predicate.name)].push(action)
    def pop(self):
        while True:
            self.current = (self.current + 1) % len(self.schemas)
            if (self.queues[self.current]):
                self.num_grounded_actions[self.current] += 1
                return self.queues[self.current].pop()
            
class NoveltyEvaluator():
    def __init__(self):
        self.novelty = {}
    def calculate_novelty(self, action):
        if (not action.predicate.name in self.novelty):
            return 0
        else:
            novelty = sys.maxsize
            for i in range(len(action.args)):
                if (action.args[i] in self.novelty[action.predicate.name][i]):
                    novelty = min(novelty, self.novelty[action.predicate.name][i][action.args[i]])
                else:
                    return 0
            return novelty
    def update_novelty(self, action):
        if (not action.predicate.name in self.novelty):
            self.novelty[action.predicate.name] = [{} for i in range(len(action.args))]
            for i in range(len(action.args)):
                self.novelty[action.predicate.name][i][action.args[i]] = 1
        else:
            for i in range(len(action.args)):
                if (action.args[i] in self.novelty[action.predicate.name][i]):
                    self.novelty[action.predicate.name][i][action.args[i]] += 1
                else:
                    self.novelty[action.predicate.name][i][action.args[i]] = 1
            
class NoveltyFIFOQueue(PriorityQueue):
    def __init__(self):
        self.novel_action_queue = []
        self.novel_queue_pos = 0
        self.closed_novel_actions = []
        self.non_novel_action_queue = FIFOQueue()
        self.num_novel_actions_grounded = 0
        self.num_non_novel_actions_grounded = 0
        self.novelty = NoveltyEvaluator()
    def __bool__(self):
        if (self.novel_queue_pos < len(self.novel_action_queue)):
            return True
        if (self.non_novel_action_queue):
            return True
        return False
    __nonzero__ = __bool__
    def get_final_queue(self):
        return self.non_novel_action_queue.get_final_queue() + self.closed_novel_actions
    def print_info(self):
        print("Using novelty FIFO priority queue for actions.")
    def print_stats(self):
        print("Grounded %d novel actions" % self.num_novel_actions_grounded)
        print("Grounded %d non-novel actions" % self.num_non_novel_actions_grounded)
    def push(self, action):
        if (self.novelty.calculate_novelty(action) == 0):
            self.novel_action_queue.append(action)
        else:
            self.non_novel_action_queue.push(action)
    def pop(self):
        while (self.novel_queue_pos < len(self.novel_action_queue)):
            result = self.novel_action_queue[self.novel_queue_pos]
            self.novel_queue_pos += 1
            if (self.novelty.calculate_novelty(result) == 0):
                self.novelty.update_novelty(result)
                self.num_novel_actions_grounded += 1
                self.closed_novel_actions.append(result)
                return result
            else:
                self.non_novel_action_queue.push(result)
        # removed all actions from novel queue
        assert(self.novel_queue_pos >= len(self.novel_action_queue))
        result = self.non_novel_action_queue.pop()
        self.num_non_novel_actions_grounded += 1
        return result
    
class RoundRobinNoveltyQueue(PriorityQueue):
    def __init__(self):
        self.novelty = NoveltyEvaluator()
        self.schemas = []
        self.current = 0
        self.queues = []
        self.num_grounded_actions = []
        self.closed = []
    def __bool__(self):
        for queue in self.queues:
            if (queue):
                return True
        return False
    __nonzero__ = __bool__
    def get_final_queue(self):
        return self.closed
    def print_info(self):
        print("Using round-robin novelty priority queue for actions.")
    def print_stats(self):
        for i in range(len(self.num_grounded_actions)):
            print("%d actions grounded for schema %s" % (self.num_grounded_actions[i], self.schemas[i]))
    def push(self, action):
        novelty = self.novelty.calculate_novelty(action)
        if (not action.predicate.name in self.schemas):
            self.schemas.append(action.predicate.name)
            self.queues.append([])
            self.num_grounded_actions.append(0)
        heapq.heappush(self.queues[self.schemas.index(action.predicate.name)], (novelty, action))
    def pop(self):
        while True:
            self.current = (self.current + 1) % len(self.schemas)
            if (self.queues[self.current]):
                self.num_grounded_actions[self.current] += 1
                while True:
                    result = heapq.heappop(self.queues[self.current])
                    novelty_old = result[0] 
                    action = result[1]
                    novelty_new = self.novelty.calculate_novelty(action)
                    if (novelty_old == 0 and novelty_new != novelty_old):
                        heapq.heappush(self.queues[self.current], (novelty_new, action))
                    else:
                        self.novelty.update_novelty(action)
                        self.closed.append(action)
                        return action
    
def get_action_queue_from_options(task = None):
    name = options.grounding_action_queue_ordering.lower()
    if (name == "fifo"):
        return FIFOQueue()
    elif (name == "lifo"):
        return LIFOQueue()
    elif (name == "random"):
        return RandomHeapQueue()
    elif (name == "hiking"):
        return HikingTestQueue()
    elif (name == "trained"):
        return TrainedQueue(task)
    elif (name == "roundrobin"):
        return SchemaRoundRobinQueue()
    elif (name == "noveltyfifo"):
        return NoveltyFIFOQueue()
    elif (name == "roundrobinnovelty"):
        return RoundRobinNoveltyQueue()
    else:
        sys.exit("Error: unknown queue type: " + name)
        
        
