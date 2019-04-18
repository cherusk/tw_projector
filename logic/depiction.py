
import json


class Depictor:

    def __init__(self, run_cnfg):
        pass

    def conjure(self, scenarios):
        print json.dumps(scenarios,
                         indent=4,
                         default=str)
