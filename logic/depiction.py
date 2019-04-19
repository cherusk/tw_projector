
import json


class Depictor:

    def __init__(self, run_cnfg):
        pass

    # might push sorting to origin of structures
    def sort_by_prio(self, scenarios):
        def prio_elector(elem):
            return elem["priority"]

        for scenario in scenarios:
            for t_data_k in ['tasks', 'trespassers']:
                scenario[t_data_k] = sorted(scenario[t_data_k],
                                            key=prio_elector)

        return scenarios

    def conjure(self, scenarios):
        scenarios = self.sort_by_prio(scenarios)
        print json.dumps(scenarios,
                         indent=4,
                         default=str)
