
# -*- coding: utf-8 -*-

# Module to run all PyRDNAP tests as  python setup.py test

from bases import test_dir
from run import run2

from glob import glob
from os.path import abspath, dirname, join
import unittest

__all__ = ('TestSuite',)
__version__ = '26.04.26'

_test_dir = dirname(abspath(__file__))


class TestSuite(unittest.TestCase):
    '''Combine all test modules into a test suite/case
       and run each test module as a separate test.
    '''
    _runs = 0  # pseudo global, 0 for testGeoids

    def _run(self, test, *argv):
        TestSuite._runs += 1  # pseudo global
        x, _ = run2(join(test_dir, test + '.py'), *argv)
        self.assertEqual(x, 0)

    def test_Validation(self):
        self._run('testValidation')

    def test_RndTrips(self):
        self._run('testRndTrips')

    def test_Ztotal(self):
        # final test to make sure all tests were run
        t = len(glob(join(_test_dir, 'test[A-Z]*.py')))
        self.assertEqual(TestSuite._runs, t)


if __name__ == '__main__':

    import sys
    unittest.main(argv=sys.argv)  # catchbreak=None, failfast=None, verbosity=2
