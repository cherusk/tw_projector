#!/usr/bin/env python

import sys
import os

sys.path.insert(1, os.path.dirname(__file__))

# import yaml
import argparse
import logging
from logic.core import Projector


logger = logging.getLogger(__name__)

def load(_file, logic=None):
    with open(_file, "r") as fp:
        return logic(fp)


def setup_args():
    parser = argparse.ArgumentParser(description="Assisiting logic for bulk assessing timewise \
                                                  projections and overall approach scenario election.")
    parser.add_argument('-p', '--param_file', help="parameter cnfg file")
    args = parser.parse_args()
    return args


def run():
    logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)
    args = setup_args()
    # cnfg = load(os.path.join(CNFG_DIR, 'param.yml'),
                # logic=yaml.load)

    cnfg = None
    scenario = Projector(cnfg).perform()
    # Depictor().conjure(scenario)


if __name__ == "__main__":
    run()
