
import os
import json
import collections as c
import sys
from collections import defaultdict
from collections import Mapping
from taskw import TaskWarrior
import logging
import datetime

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
        _tasks = list()
        tasks = tw.load_tasks()['pending']
        for t in tasks:
            logger.debug("Task>> %s:", str(t))
            if "estimate" not in t.keys():
                    # e.g. recurring meta tasks etc.
                    continue
            _tasks.append(t)
        return _tasks


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
        logger.debug('trigger GEA optimization run')
        algorithm.run(runs)
        logger.debug('GEA done')

        return unique(nondominated(algorithm.result))


class TimeRevisor():

    def __init__(self, atomic_slot, deadline):
        self.today = datetime.datetime.today()
        self.atomic_unit = 'week'

        if deadline['date'] != "YYYY-MM-DD":  # untouched cnfg
            self.deadline = (datetime.datetime.
                             strptime(deadline['date'],
                                      '%Y-%m-%d'))
        else:
            self.deadline = (self.today +
                             datetime.timedelta(days=deadline['stretch']))

    def project_termination(self, task):
        _weeks = task['chunks']
        termination_point = (self.today +
                             datetime.timedelta(weeks=_weeks))
        return termination_point

    def assess_trespass(self, termination):
        by = self.deadline - termination
        trespassing = True if by.total_seconds() < 0 else False
        return (trespassing, by)

    def inspect_trespassing(self, candidates):
        trespassers = list()

        for task in candidates:
            end = self.project_termination(task)
            task['termination'] = end
            trespassed, by = self.assess_trespass(end)
            if trespassed:
                task['exceeding_by'] = by  # for depiction?
                trespassers.append(task)

        return trespassers


class Projector():

    folded_projects = defaultdict(int)

    def __init__(self, run_cnfg):
        self.atomic_slot = run_cnfg['run_meta']['atomic_slot']
        self.chunking = ChunkingMap(run_cnfg['chunking'],
                                    self.atomic_slot)

        if run_cnfg['run_meta']['strategy'] == "LushHighPrio":
            self.slotter = LushHighPrio

        self.time_r = TimeRevisor(self.atomic_slot,
                                  run_cnfg['run_meta']['deadline'])

    def _do_chunking(self, tasks):
        for t in tasks:
            chunk = self.chunking[t]
            duration = t["estimate"]
            t['chunk'] = chunk
            t['chunks'] = duration // chunk

    def perform(self, tasks):
        scenario = defaultdict(lambda: dict(tasks=[],
                                            accumulative_priority=0))
        scenarios = list()

        tasks = self._do_chunking(tasks)
        logger.debug('tasks staged for slotter')

        solutions = self.slotter(tasks, self.atomic_slot).determine()

        logger.debug('solutions accrued --> \n {}'.format(str(solutions)))

        for solution in solutions:
            # idx: only one objective and items collection
            scenario['accumulative_priority'] = solution.objectives[0]
            scenario['tasks'] = [tasks[i]
                                 for i in range(len(tasks))
                                 if solution.variables[0][i]]
            scenario['trespassers'] = (self.time_r.
                                       inspect_trespassing(scenario['tasks']))
            scenarios.append(scenario)

        return scenarios
