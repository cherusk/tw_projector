#!/usr/bin/env python

import sys
import os
from pprint import pprint

sys.path.insert(1, os.path.dirname(__file__))

import argparse
import logging
from logic.core import Projector
from logic.core import TW
from logic.cnfg import CnfgMediator


logger = logging.getLogger(__name__)


def setup_args():
    parser = argparse.ArgumentParser(prog='tw_projector',
                                     description="""Assisiting logic for bulk
                                     assessing timewise projections and overall
                                     approach scenario election.""")

    subparsers = parser.add_subparsers(dest='command')
    generator_parser = subparsers.add_parser('generate')
    generator_parser.add_argument('-c', '--generated_run_cnfg',
                                  help="""projection parameterization cnfg file
                                  deposit""",
                                  default="./generated_run_param_tmplt.yml")
    generator_parser.add_argument('-g', '--granularity',
                                  help="""hierarchy granularity, juxtaposes to
                                  manual adjustment effort required or level of
                                  immediate specification convenience""",
                                  choices=['project', 'task'],
                                  default="project")
    generator_parser.add_argument('-e', '--project_elector',
                                  metavar='projectX,projectY',
                                  help="""selecting projects to focus on""",
                                  default=[])

    projection_parser = subparsers.add_parser('project')
    projection_parser.add_argument('-p', '--run_param_file',
                                   help="""projection parameterization cnfg
                                   file""")
    projection_parser.add_argument('-c', '--logic_cnfg',
                                   help="""logic config file to load""")
    args = parser.parse_args()
    return args


def run():
    logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)

    args = setup_args()
    tasks = TW.attain_data()

    if args.command == "project":
        run_cnfg, engine_cnfg = CnfgMediator().gather(param_file=args.run_param_file,
                                                      engine_cnfg=args.logic_cnfg)
        scenario = Projector(run_cnfg, engine_cnfg).perform(tasks)
        # Depictor().conjure(scenario)
    elif args.command == "generate":
        if args.project_elector:
            args.project_elector = args.project_elector.split(",")
        CnfgMediator().generate(tasks,
                                deposit=args.generated_run_cnfg,
                                projects=args.project_elector,
                                granularity=args.granularity)
    else:
        raise RuntimeError("Unknown command %s" % args.command)


if __name__ == "__main__":
    run()
