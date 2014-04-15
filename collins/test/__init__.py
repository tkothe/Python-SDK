#-*- encoding: utf-8 -*-
"""
:Author:    Arne Simon [arne.simon@slice-dice.de]
"""
# import sys
from os.path import abspath, dirname, join
ROOT = dirname(dirname(dirname(abspath(__file__))))
# sys.path.append(ROOT)

TEST_CONFIG = join(ROOT, "110slicedice-config.json")
TEST_SESSION = "fa8e2e2210n"
