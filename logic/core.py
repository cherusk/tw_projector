
import os
import json
import collections as c
import sys
from collections import defaultdict
from collections import Mapping
from taskw import TaskWarrior
import logging

from concurrent.futures import ProcessPoolExecutor  # platypus parallelization
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
        self.auto_chunking = run_cnfg['auto']
        self.slot_size = slot_size
        self.tw_projects = run_cnfg['projects']
        self.task_idx = {}
        for prj in self.tw_projects.values():
            for task in prj['tasks']:
                _id = task['id']
                self.task_idx[_id] = task

    def __getitem__(self, key):
        task = key
        _id = task['id']
        _project = task['project']

        if _project in self.tw_projects.keys():
            if _id in self.task_idx.keys():
                return self.task_idx[_id]['chunk_size']
            else:
                return self.tw_projects[_project]['chunk_size']

        auto_chunk = self.slot_size * (self.auto_chunking["fraction"] / 100)

        return (auto_chunk
                if auto_chunk > self.auto_chunking["minimum"]
                else self.auto_chunking["minimum"])

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

        # Open clarification -
        # caused PicklingError: Can't pickle <type 'instancemethod'>: attribute lookup
        # with ProcessPoolEvaluator() as evaluator:
            # algorithm = GeneticAlgorithm(self, evaluator=evaluator)
            # algorithm.run(runs)

        algorithm = GeneticAlgorithm(self)
        algorithm.run(runs)

        return unique(nondominated(algorithm.result))


class Projector():

    folded_projects = defaultdict(int)

    def __init__(self, run_cnfg):
        self.atomic_slot = run_cnfg['run_meta']['atomic_slot']
        self.chunking = ChunkingMap(run_cnfg['chunking'],
                                    self.atomic_slot)

        if run_cnfg['run_meta']['strategy'] == "LushHighPrio":
            self.slotter = LushHighPrio

    def perform(self, tasks):
        scenario = defaultdict(lambda: dict(tasks=[],
                                            accumulative_priority=0))
        scenarios = list()

        for t in tasks:
            chunk = self.chunking[t]
            duration = t["estimate"]
            t['chunk'] = chunk
            t['chunks'] = duration // chunk

        solutions = self.slotter(tasks, self.atomic_slot).determine()

        for solution in solutions:
            # idx: only one objective and items collection
            scenario['accumulative_priority'] = solution.objectives[0]
            scenario['tasks'] = [tasks[i]
                                 for i in range(len(tasks))
                                 if solution.variables[0][i]]
            scenarios.append(scenario)

        return scenarios
