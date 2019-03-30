
import yaml
from collections import defaultdict

class CnfgMediator():

    def __init__(self):
        self.dflt = { "core" : {    "strategy" : "LushHighPrio",
                                    "auto_chunking" :
                                        {  "fraction": 10,  # in percentage of atomic slot
                                           "minimum": 1 }},  # in hours
                      "project" : { "chunk_size": 2 },  # in hours
                      "task" :    { "chunk_size": 2 }}  # in hours

    def _load(self, _file, logic=None):
        with open(_file, "r") as fp:
            return logic(fp)

    def gather(self, param_file=None, engine_cnfg_file=None):
        run_cnfg = self._load(param_file,
                                        logic=yaml.load)
        engine_cnfg = self._load(engine_cnfg_file,
                                      logic=yaml.load)
        return run_cnfg, engine_cnfg

    def _save(self, _file, content):
        hr_dumper = yaml.SafeDumper
        hr_dumper.ignore_aliases = lambda self, data: True  # unroll aliases
        with open(_file, "w") as fp:
            yaml.dump(content,
                      fp,
                      Dumper=hr_dumper,
                      explicit_start=True,
                      default_flow_style=False)

    def generate(self, tasks, deposit=None, granularity=None, projects=[]):
        generation = {
                "meta": self.dflt['core'],
                "items": defaultdict(lambda: dict(meta=self.dflt['project'],
                                     tasks=list()))
                }

        for t in tasks:
            project = t['project']
            if project not in projects:  # consider RE!
                continue
            generation["items"][project]['tasks'].append(dict(meta=self.dflt['task'],
                                                              id=t['id'],
                                                              description=t['description']))

        # COSTLY! - though, no yaml human readable defaultdict support
        # yaml.representer.RepresenterError: cannot represent an object: defaultdict
        # Ignorable since of one shot nature as well.
        generation["items"] = dict(generation["items"])

        self._save(deposit, generation)
