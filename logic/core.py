
import os
import json
import collections as c
import sys
from collections import defaultdict
from collections.abc import Mapping
from taskw import TaskWarrior
import logging

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


class Projector():

    folded_projects = defaultdict(int)

    def __init__(self, run_cnfg, engine_cnfg):
        self.chunking = ChunkingMap(run_cnfg, engine_cnfg.slot_size)

#     def accrue_per_project(self, tasks):
        # for task in tasks:
            # project = task['project']
            # self.folded_projects[project] = sum((self.folded_projects[project],
                                                # task[self.effort_uda]))

    def perform(self, tasks):
        scenario = {}

        #  CNFG
        # atomic_slot

        # for t in tasks:
            # duration = t["estimate"]
            # chunks = duration / atomic_slot 


        # capacity = self._cnfg['week_capacity']

        # for project, chunking in self._cnfg['chunking_scenario']['projects'].items():
            # capacity -= chunking

            # if capacity >= 0:
                # pass
            # else:
                # cease(rc=1, msg="exceeding capacity")

            # effort = self.folded_projects[project]
            # duration = (effort / chunking) + (effort % chunking)
            # scenario[project] = duration

        return scenario
