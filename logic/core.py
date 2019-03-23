#!/usr/bin/env python

import os
import json
import collections as c
import sys
from collections import defaultdict
from taskw import TaskWarrior
import logging

logger = logging.getLogger(__name__)

class Projector():

    folded_projects = defaultdict(int)

    def __init__(self, cnfg):
        self.tasks = self.__accrue_tw_data()
        # self._cnfg = cnfg['root']
        # self.effort_uda = self._cnfg['uda_name']
        # self.accrue_per_project(tasks)
        # self.perform()

    def __accrue_tw_data(self):
        tw = TaskWarrior()
        tasks = tw.load_tasks()['pending']
        for t in tasks:
            logger.debug(":%s:", str(t))
        return tasks

#     def accrue_per_project(self, tasks):
        # for task in tasks:
            # project = task['project']
            # self.folded_projects[project] = sum((self.folded_projects[project],
                                                # task[self.effort_uda]))
    def _stage_tw_data(self):
        # atomic_unit
        #  

        for t in self.tasks:
            duration = t["estimate"]
            t["chunks"] = duration / atomic_unit

    def perform(self):
        scenario = {}

        tasks = 
        
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
