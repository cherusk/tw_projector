
import yaml
from collections import defaultdict


class CnfgMediator():

    def __init__(self, dflt_file=None):
        if dflt_file:
            self.dflts = self._load(dflt_file,
                                    logic=yaml.load)

    def _load(self, _file, logic=None):
        with open(_file, "r") as fp:
            return logic(fp)

    def gather(self, param_file=None):
        run_cnfg = self._load(param_file,
                              logic=yaml.load)
        return run_cnfg

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
        dflts = self.dflts['projector']
        generation = {
                "run_meta": dflts['engine'],
                "chunking": {"auto": dflts['chunking']['auto'],
                             "projects": defaultdict(lambda: dict(chunk_size=(dflts['chunking']
                                                                                   ['projects']),
                                                                  tasks=list()))}
                     }

        for t in tasks:
            project = t['project']

            if (projects and
               project not in projects):  # consider RE!
                continue
            (generation["chunking"]["projects"]
                       [project]['tasks']).append(dict(id=t['id'],
                                                  chunk_size=dflts['chunking']
                                                                  ['tasks'],
                                                  description=t['description']))

        # COSTLY! - though, no yaml human readable defaultdict support
        # yaml.representer.RepresenterError: cannot represent an object: defaultdict
        # Ignorable since of one shot nature as well.
        (generation["chunking"]
                   ["projects"]) = dict(generation["chunking"]
                                                  ["projects"])

        self._save(deposit, generation)
