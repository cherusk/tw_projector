
import unittest
import os
import glob
from taskw import TaskWarrior
from logic.core import Projector
from logic.cnfg import CnfgMediator
import datetime as dt


class projectorTesting(unittest.TestCase):

    def load_tw_cnfg(self):
        return os.path.join(self.local_dir, "./cnfg/.taskrc")

    def stage_tw(self, cnfg_file):
        overrides = {'data': {'location':  os.path.join(self.local_dir, 'task')}}
        tw = TaskWarrior(config_filename=cnfg_file,
                         config_overrides=overrides)
        self.tw = tw

    def stage_run_cnfg(self):
        dflts_file = os.path.join(self.local_dir,
                                  "../dflts_cnfg.yml")
        run_cnfg_deposit = os.path.join(self.local_dir,
                                        "./tst_run_cnfg.yml")
        (CnfgMediator(dflt_file=dflts_file).
         generate(self.tasks,
         deposit=run_cnfg_deposit))
        self.cnfg = (CnfgMediator().
                     gather(param_file=run_cnfg_deposit))

    def setUp(self):
        ''' setup strategy '''
        self.local_dir = os.path.dirname(__file__)
        cnfg_file = self.load_tw_cnfg()
        self.stage_tw(cnfg_file)
        self.form_test_items()
        self.tasks = self.tw.load_tasks()['pending']
        self.stage_run_cnfg()

    def tearDown(self):
        data_reside = os.path.join(self.local_dir, "task", "*.data")
        for tw_data_f in glob.glob(data_reside):
            os.remove(tw_data_f)

    def form_test_items():
        raise NotImplementedError("part of setUp strategy")


class slotterTesting(projectorTesting):

    def setUp(self):
        super(slotterTesting, self).setUp()

    def tearDown(self):
        super(slotterTesting, self).tearDown()

    def form_test_items(self):
        self.tw.task_add("TaskA",   project="ProjA",
                         priority="1", estimate=100)
        self.tw.task_add("TaskAA",  project="ProjA",
                         priority="2", estimate=200)
        self.tw.task_add("TaskB",   project="ProjB",
                         priority="3", estimate=200)
        self.tw.task_add("TaskC",   project="ProjC",
                         priority="4", estimate=300)
        self.tw.task_add("TaskCC",  project="ProjC",
                         priority="4", estimate=300)

    def override_run_cnfg(self):
        self.cnfg["chunking"]["projects"]["ProjB"]["chunk_size"] = 4
        (self.cnfg["chunking"]["projects"]["ProjC"]
                  ["tasks"][0]["chunk_size"]) = 4
        self.cnfg["run_meta"]["atomic_slot"] = 10

    def test_engine(self):

        self.override_run_cnfg()

        scenarios = Projector(self.cnfg).perform(self.tasks)
        scenario = scenarios[0]

        expected_outcome_set = set(["TaskAA",
                                    "TaskB",
                                    "TaskC",
                                    "TaskCC"])

        self.assertEqual(len(scenario['tasks']), 4)
        self.assertSetEqual(expected_outcome_set,
                            set([task['description']
                                 for task in scenario['tasks']]))
        self.assertEqual(scenario['accumulative_priority'], 13)
        self.assertIsNotNone(scenario)


class timeAspectTesting(projectorTesting):

    def setUp(self):
        super(timeAspectTesting, self).setUp()
        self.today = dt.datetime.today()

    def tearDown(self):
        super(timeAspectTesting, self).tearDown()

    def form_test_items(self):
        self.tw.task_add("TaskA",  project="ProjA",
                         priority="2", estimate=4)
        self.tw.task_add("TaskB",   project="ProjB",
                         priority="3", estimate=4)
        self.tw.task_add("TaskC_trespasser",   project="ProjC",
                         priority="4", estimate=1000)

    def test_revisor_deadline(self):

        conformant_thresh = (self.today +
                             dt.timedelta(days=20)).strftime('%Y-%m-%d')
        self.cnfg["run_meta"]["deadline"]["date"] = conformant_thresh
        self.cnfg["run_meta"]["atomic_slot"] = 10

        scenarios = Projector(self.cnfg).perform(self.tasks)
        scenario = scenarios[0]

        self.assertIsNotNone(scenario)
        self.assertTrue(len(scenario['trespassers']) > 0)
        self.assertIn('TaskC_trespasser', [task['description']
                                           for task in
                                           scenario['trespassers']])

    def test_revisor_stretch(self):
        self.cnfg["run_meta"]["deadline"]["date"] = "YYYY-MM-DD"
        self.cnfg["run_meta"]["deadline"]["stretch"] = 100

        scenarios = Projector(self.cnfg).perform(self.tasks)
        scenario = scenarios[0]

        self.assertIsNotNone(scenario)
        self.assertTrue(len(scenario['trespassers']) > 0)
        normalized_trespassers = [task['description']
                                  for task in
                                  scenario['trespassers']]
        self.assertIn('TaskC_trespasser',
                      normalized_trespassers)
        self.assertNotIn("TaskA",
                         normalized_trespassers)
        self.assertNotIn("TaskB",
                         normalized_trespassers)
