
import os
import json
import collections as c
import sys
from collections import defaultdict
from collections.abc import Mapping
from taskw import TaskWarrior
import logging

from platypus import (GeneticAlgorithm,
                      Problem,
                      Constraint,
                      Binary,
                      nondominated,
                      unique,
                      ProcessPoolEvaluator)

logger = logging.getLogger(__name__)


class TW():

    @staticmethod
    def attain_data(cnfg_file=None):
        tw = TaskWarrior(config_filename=cnfg_file)
        tasks = tw.load_tasks()['pending']
        for t in tasks:
            logger.debug("Task>> %s:", str(t))
        return tasks


class ChunkingMap(Mapping):

    def __init__(self, run_cnfg, slot_size):
        self.auto_chunking = run_cnfg['meta']['auto_chunking']
        self.slot_size = slot_size
        self.tw_items = run_cnfg["items"]
        self.task_idx = {task['id']: task for prj, task in self.tw_items}

    def __getitem__(self, key):
        task = key
        _id = task['id']
        _project = task['project']

        if _project in self.tw_items.keys():
            if _id in self.task_idx.keys():
                return self.task_idx[_id]['meta']['chunk_size']
            else:
                return _project['meta']['chunk_size']

        auto_chunk = self.slot_size * (self.auto_chunking["fraction"] / 100)
        return auto_chunk

    def __iter__(self):
        raise NotImplementedError()

    def __len__(self):
        raise NotImplementedError()


class LushHighPrio(Problem):
    """ Perceivable as Knapsack spin """

    def __init__(self, tasks, atomic_slot_size):
        super(LushHighPrio, self).__init__(1, 1, 1)

        self.tasks = tasks
        self.items_count = len(tasks)

        self.types[0] = Binary(self.items_count)
        self.directions[0] = Problem.MAXIMIZE
        self.constraints[0] = Constraint("<=", atomic_slot_size)
        self.function = self.fitness

    def _accumulate_selection(self, selection, field):
        return sum([self.tasks[i][field]
                   if selection[i] else 0
                   for i in range(self.items_count)])

    def fitness(self, instance):
        selection = instance[0]

        slot_allocation = self._accumulate_selection(selection, 'chunk')
        priority_gain = self._accumulate_selection(selection, 'priority')

        return priority_gain, slot_allocation

    def determine(self, runs=10000):

        with ProcessPoolEvaluator() as evaluator:
            algorithm = GeneticAlgorithm(self, evaluator=evaluator)
            algorithm.run(runs)

        return unique(nondominated(algorithm.result))


class Projector():

    folded_projects = defaultdict(int)

    def __init__(self, run_cnfg, engine_cnfg):
        self.atomic_slot = engine_cnfg['projector']['atomic_slot']

        self.chunking = ChunkingMap(run_cnfg,
                                    self.atomic_slot)

        if run_cnfg['meta']['strategy'] == "LushHighPrio":
            self.slotter = LushHighPrio

    def perform(self, tasks):
        scenario = {}

        for t in tasks:
            chunk = self.chunking[t]
            duration = t["estimate"]
            t['chunk'] = chunk
            t['chunks'] = duration // chunk

        solutions = self.slotter(tasks, self.atomic_slot).determine()

        return scenario
