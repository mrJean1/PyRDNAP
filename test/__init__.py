
# -*- coding: utf-8 -*-

# Module to run all PyRDNAP tests as  python setup.py test

from os.path import abspath, dirname
import sys

test_dir = dirname(abspath(__file__))
# setting __path__ is sufficient for importing
# modules internal to this test package
__path__ = [test_dir, dirname(test_dir)]
# extend sys.path to include the .. directory,
# required for module ..setup.py to work
if test_dir not in sys.path:
    sys.path.insert(0, test_dir)

from unitTestSuite import TestSuite  # PYCHOK for setup.py

__all__ = ('TestSuite',)
__version__ = '26.04.28'

del abspath, dirname, sys, test_dir
