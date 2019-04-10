
import unittest
import os
import glob
from taskw import TaskWarrior
from logic.core import Projector
from logic.cnfg import CnfgMediator


class projectorTesting(unittest.TestCase):

    def setUp(self):
        self.local_dir = os.path.dirname(__file__)
        cnfg_file = os.path.join(self.local_dir, "./cnfg/.taskrc")
        overrides = { 'data' : { 'location':  os.path.join(self.local_dir, 'task') }}
        tw = TaskWarrior(config_filename=cnfg_file,
                         config_overrides=overrides)

        tw.task_add("TaskA",   project="ProjA", priority="1", estimate=100)
        tw.task_add("TaskAA",  project="ProjA", priority="1", estimate=200)
        tw.task_add("TaskB",   project="ProjB", priority="2", estimate=200)
        tw.task_add("TaskC",   project="ProjC", priority="3", estimate=300)
        tw.task_add("TaskCC",  project="ProjC", priority="3", estimate=300)

        self.tasks = tw.load_tasks()['pending']
        self.tw = tw

    def tearDown(self):
        data_reside = os.path.join(self.local_dir, "task", "*.data")
        for tw_data_f in glob.glob(data_reside):
            os.remove(tw_data_f)

    def test_engine(self):
        local_dir = os.path.dirname(__file__)
        dflts_file = os.path.join(local_dir, "../dflts_cnfg.yml")
        run_cnfg_deposit = os.path.join(local_dir, "./tst_run_cnfg.yml")
        (CnfgMediator(dflt_file=dflts_file).
                      generate(self.tasks,
                               deposit=run_cnfg_deposit))
        cnfg = (CnfgMediator().
                gather(param_file=run_cnfg_deposit))

        cnfg["chunking"]["projects"]["ProjB"]["chunk_size"] = 4
        cnfg["chunking"]["projects"]["ProjC"]["tasks"][0]["chunk_size"] = 4
        cnfg["run_meta"]["atomic_slot"] = 10

        scenario = Projector(cnfg).perform(self.tasks)

        self.assertIsNotNone(scenario)
