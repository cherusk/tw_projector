
import os
import json
import collections as c
import sys
from collections import defaultdict
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


class Projector():

    folded_projects = defaultdict(int)

    def __init__(self, run_cnfg, engine_cnfg):
        pass

        # self._cnfg = cnfg['root']
        # self.effort_uda = self._cnfg['uda_name']
        # self.accrue_per_jproject(tasks)
        # self.perform()

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
