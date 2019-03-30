
import unittest
import os
from taskw import TaskWarrior
from logic.core import Projector


class projectorTesting(unittest.TestCase):

    def setUp(self):
        local_dir = os.path.dirname(__file__)
        cnfg_file = os.path.join(local_dir, "./cnfg/.taskrc")
        tw = TaskWarrior(config_filename=cnfg_file)
        tw.task_add("TaskX", project="ProjX", priority="1", estimate=100)
        tw.task_add("TaskY", project="ProjX", priority="1", estimate=200)
        tw.task_add("TaskA", project="ProjZ", priority="2", estimate=500)
        tw.task_add("TaskB", project="ProjZ", priority="3", estimate=300)
        tw.task_add("TaskC", project="ProjU", priority="4", estimate=300)
        self.tasks = tw.load_tasks()['pending']
        self.tw = tw

    def tearDown(self):
        pass
        # for t in self.tasks:
            # self.tw.task_delete(id=t['id'])

    def test_engine(self):
        cnfg = None
        scenario = Projector(cnfg).perform(self.tasks)

        self.assertIsNotNone(scenario)
