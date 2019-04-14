
import json


class Depictor:

    def __init__(self, run_cnfg):
        pass

    def conjure(self, scenarios):
        print json.dump(scenarios, indent=4)
