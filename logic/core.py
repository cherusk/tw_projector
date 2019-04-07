
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
        self.chunking = ChunkingMap(run_cnfg,
                                    engine_cnfg['projector']['atomic_slot'])

    def perform(self, tasks):
        scenario = {}

        #  CNFG
        # atomic_slot

        for t in tasks:
            chunk = self.chunking[t]
            duration = t["estimate"]
            t['chunk'] = chunk
            t['chunks'] = duration // chunk

        return scenario
