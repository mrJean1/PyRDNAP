
# -*- coding: utf-8 -*-

# Base classes and functions for PyRDNAP tests, partial
# copy of PyGeodesy module pygeodesy/test/bases.py

# from glob import glob
# from inspect import isclass, isfunction, ismethod, ismodule
from os.path import abspath, basename, dirname
import sys
from time import time

test_dir    = dirname(abspath(__file__))
PyRDNAP_dir = dirname(test_dir)
# extend sys.path to include the ../.. directory,
# required for module .run.py to work
if PyRDNAP_dir not in sys.path:  # Python 3+ ModuleNotFoundError
    sys.path.insert(0, PyRDNAP_dir)

from pyrdnap import _versions  # pyrdnap 1st
from pygeodesy import DeprecationWarnings, internals, interns, NAN, \
                      NN, normDMS, pairs, printf, property_RO, typename
from pygeodesy import clips, Datums, str2ub, ub2str  # noqa: F401 shared

_DOT_      = interns._DOT_
_ELLIPSIS_ = interns._ELLIPSIS_  # PYCHOK shared
_getenv    = internals._getenv
_skipped_  = 'skipped'  # in .run
_SPACE_    = interns._SPACE_
_TILDE_    = interns._TILDE_
_HOME_dir  = dirname(PyRDNAP_dir or _TILDE_) or _TILDE_  # _PYGeodesy_dir
secs2str   = internals._secs2str
# _xcopy     = basics._xcopy

__all__ = ('coverage', 'Datums', 'NAN', 'NN',
           'isAppleSi', 'isiOS', 'ismacOS', 'isNix',  # 'isIntelPython'
           'isPyPy', 'isPython2', 'isPython3', 'isWindows',
           'property_RO', 'PythonX', 'test_dir',
           'TestsBase',  # classes
           'clips', 'normDMS', 'pairs', 'printf', 'secs2str',  # functions
           'str2ub', 'tilde', 'typename', 'ub2str', 'versions')
__version__ = '26.05.09'

try:  # from pygeodesy.basics ...
    # _Ints = int, long
    _Strs = basestring, str
except NameError:  # Python 3+
    # _Ints = int,
    _Strs = str,

# endswith   = str.endswith
# startswith = str.startswith
try:
    if float(_getenv('PYRDNAP_COVERAGE', '0')) > 0:
        import coverage
    else:
        coverage = None  # ignore coverage
except (ImportError, TypeError, ValueError):
    coverage = None

_W_opts = sys.warnoptions or NN
if _W_opts:
    _W_opts = _SPACE_(*(_SPACE_('-W', _) for _ in _W_opts))

v2         = sys.version_info[:2]  # (.major, .minor)
# bits_mach2 = internals._MODS.bits_machine2  # property_RO
isAppleSi  = internals._isAppleSi()
# isiOS is used by some tests known to fail on iOS only
isiOS      = internals._isiOS()  # public
ismacOS    = internals._ismacOS()  # public
isNix      = internals._isNix()
isPyPy     = internals._isPyPy()
isPython2  = v2[0] == 2
isPython3  = v2[0] == 3
# isPython35 = v2 >= (3, 5)
isPython37 = v2 >= (3, 7)  # in .run
# isPython39 = v2 >= (3, 9)  # arm64 Apple Si
isWindows  = internals._isWindows()
PythonX    = sys.executable  # python or Pythonista path
# isIntelPython = 'intelpython' in PythonX
del v2


class TestsBase(object):
    '''Tests based on @examples from the original JavaScript code
       and examples in <https://www.EdWilliams.org/avform.htm> or
       elsewhere as indicated.
    '''
    _file     =  NN
    _name     =  NN
    _iterisk  =  NN
    _prefix   = _SPACE_ * 4
    _raiser   =  False
    _time     =  None  # -prefix
    _time0    =  0
    _verbose  =  True  # print all tests, otherwise failures only
    _versions =  NN  # cached versions() string, set below

    failed  = 0
    known   = 0
    skipped = 0
    total   = 0

    def __init__(self, testfile, version, module=None, verbose=True,
                                          raiser=False):  # testX=False
        self._file    = testfile
        self._name    = basename(testfile)
        self.title(self._name, version, module=module)
        self._verbose = verbose
        self._raiser  = raiser if raiser else '-raiser'.startswith(sys.argv[-1])
        self._time0   = time()
        try:
            sys.argv.remove('-prefix')
            self._time = self._time0
        except (IndexError, ValueError):
            pass

    def errors(self):
        '''Return the number of tests failures,
           excluding the KNOWN failures.
        '''
        return self.failed - self.known  # new failures

    def exit(self, errors=0):
        '''Exit with the number of test failures as exit status.
        '''
        sys.exit(min(errors + self.errors(), 99))

    @property_RO
    def name(self):
        return self._name

    def printf(self, fmt, *args, **kwds):  # nl=0, nt=0
        '''Print a formatted line to sys.stdout.
        '''
        printf((fmt % args), prefix=self._prefix, **kwds)

    def results(self, passed='passed', nl=1):
        '''Summarize the test results.
        '''
        n = 'all'
        r = passed  # or _skipped_
        s = time() - self._time0
        t = self.total
        w = DeprecationWarnings()
        f = self.failed + (w or 0)
        if f:
            a = ', incl. '
            k = self.known or NN
            if k:
                if k == f:
                    k = ', ALL KNOWN'
                else:
                    k = '%s%s KNOWN' % (a, k)
                    a = ' plus '
            if w:
                w = '%s%s %s%s' % (a, w, typename(DeprecationWarning),
                                         ('s' if w > 1 else ''))
            p = f * 100.0 / t
            r = '(%.1f%%) FAILED%s%s' % (p, k, w or '')
            n = '%s of %d' % (f, t)
        elif t:
            n = '%s %d' % (n, t)
        k = self.skipped or NN
        if k:
            k = ', %d %s' % (k, _skipped_)
        r = '%s%s (%s) %s' % (r, k, self.versions, secs2str(s))
        self.printf('%s %s tests %s', n, self._name, r, nl=nl)

    def skip(self, text=NN, n=1):
        '''Skip this test, leave a message.
        '''
        self.skipped += n
        if text and self._verbose:
            t = 'test' if n < 2 else '%s tests' % (n,)
            self.printf('%s %s (%d): %s', t, _skipped_, self.skipped, text, nl=1)

    def subtitle(self, module, testing='ing', **kwds):
        '''Print the subtitle of a test suite.
        '''
        t = (basename(module.__name__), module.__version__) + pairs(kwds.items())
        self.printf('test%s(%s)', testing, ', '.join(t), nl=1)

    def test(self, name, value, expect, error=0, **kwds):
        '''Compare a test value with the expected result.
        '''
        if self._time:
            self._prefix, self._time = prefix2(self._time)

        if self._iterisk:
            name += self._iterisk

        fmt, known, kwds = _get_kwds(**kwds)

        if not isinstance(expect, _Strs):
            expect = fmt % (expect,)  # expect as str

        f, r, v = NN, False, fmt % (value,)  # value as str
        if v != expect and v != normDMS(expect) and not (
           callable(known) and known(v, expect)):
            self.failed += 1  # failures
            if not known or callable(known):
                r = True
            else:  # failed before
                self.known += 1
                f = ', KNOWN'
            if error:
                f = '%s (%g)' % (f, error)
            f = '  FAILED%s, expected %s' % (f, expect)

        self.total += 1  # tests, in .testEllipses
        if f or self._verbose:
            self.printf('test %d %s: %s%s', self.total, name, v, f, **kwds)
        if r and self._raiser:
            raise TestError('test %d %s', self.total, name)

        if self._time:  # undo _prefix change
            self.__dict__.pop('_prefix')  # _xkwds_pop(self.__dict__, _prefix=None)

        return bool(f)  # True: fail, False: pass in .testKarneySigns

    def test_tol(self, name, value, expect, tol=1e-12, **kwds):
        e = 0 if value is None or expect is None else abs(value - expect)  # None iteration
        if e:
            m = max(abs(value), abs(expect))
            if m:
                e = min(e, m, e / m)
            return self.test(name, value, expect, error=e, known=e < tol, **kwds)
        else:
            return self.test(name, value, expect,          known=True, **kwds)

    def test__(self, fmt, *args, **kwds):
        '''Print subtotal test line.
        '''
        t = '-' * len(str(self.total))
        self.printf('test %s %s', t, (fmt % args), **kwds)

#   def testCopy(self, inst, *attrs, **kwds):  # Clas=None
#       C = kwds.get('Clas', type(inst))
#
#       c = _xcopy(inst, **kwds)
#       t =  type(c), id(c) != id(inst)
#       self.test('copy(%s)' % type(C), t, (C, True))
#       for a in attrs:
#           self.test('.' + a, getattr(c, a), getattr(inst, a))
#
#       c = inst.copy(**kwds)
#       t = type(c), id(c) != id(inst)
#       self.test(typename(C) + '.copy()', t, (C, True))
#       for a in attrs:
#           self.test('.' + a, getattr(c, a), getattr(inst, a))

    def title(self, test, version, module=None):
        '''Print the title of the test suite.
        '''
        m = NN
        if module:
            m = ' (module %s %s)' % (basename(module.__name__),
                                     module.__version__)  # _DVERSION_
        self.printf('testing %s %s%s', test, version, m, nl=1)

    @property
    def verbose(self):
        '''Get verbosity (C{bool}).
        '''
        return self._verbose

    @verbose.setter  # PYCHOK setter!
    def verbose(self, v):
        '''Set verbosity (C{bool}).
        '''
        self._verbose = bool(v)

    @property_RO
    def versions(self):
        '''Get versions (C{str}).
        '''
        return self._versions or versions()


class TestError(RuntimeError):  # ValueError's are often caught
    '''Error to show the line number of a test failure.
    '''
    def __init__(self, fmt, *args):
        RuntimeError.__init__(self, fmt % args)


def _env_c2(c, dev_null='>/dev/null', NUL_='>NUL:'):  # .testFrozen, .testLazily
    cmd = _SPACE_(PythonX, c)

    if ismacOS or isNix:
        env_cmd = _SPACE_('env %s', cmd, dev_null)
    elif isWindows:
        env_cmd = _SPACE_('set %s;', cmd, NUL_)
    else:
        env_cmd =  NN

    H = _getenv('HOME', NN)
    if H and cmd.startswith(H):
        cmd = NN(_TILDE_, cmd[len(H):])

    return env_cmd, cmd


def _get_kwds(fmt='%s', prec=0, known=False, **kwds):
    '''(INTERNAL) Get C{fmt}, C{known} and other C{kwds}.
    '''
    if prec > 0:
        fmt = '%%.%df' % (prec,)
    elif prec < 0:
        fmt = '%%.%de' % (-prec,)
    return fmt, known, kwds


def prefix2(prev):  # in .run
    '''Get time prefix and time stamp.
    '''
    t = time()
    p = '%8.3f ' % ((t - prev),)
    p = p.replace('  0.', '   .')
    return p, t


def tilde(path):
    '''Return a shortened path, especially Pythonista.
    '''
    return path.replace(_HOME_dir, _TILDE_)


def versions():
    '''Get pyrdnap, pygeodesy, Python versions, bits,
       machine, OS, env variables and packages.
    '''
    vs = TestsBase._versions
    if not vs:

        vs = tuple(_versions().split())
        for t in (coverage,):  # numpy, scipy):
            if t:
                vs += internals._name_version(t),

        if _getenv('PYTHONDONTWRITEBYTECODE', None):
            vs += '-B',

        if _W_opts:
            vs += _W_opts,

        TestsBase._versions = vs = _SPACE_.join(vs)
    return vs

# versions()  # get versions once


if __name__ == '__main__':
    try:
        import coverage  # PYCHOK re-imported
    except ImportError:
        pass
    print(versions())

# **) MIT License
#
# Copyright (C) 2026-2026 -- mrJean1 at Gmail -- All Rights Reserved.
#
# Permission is hereby granted, free of charge, to any person obtaining a
# copy of this software and associated documentation files (the "Software"),
# to deal in the Software without restriction, including without limitation
# the rights to use, copy, modify, merge, publish, distribute, sublicense,
# and/or sell copies of the Software, and to permit persons to whom the
# Software is furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included
# in all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS
# OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.  IN NO EVENT SHALL
# THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR
# OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE,
# ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR
# OTHER DEALINGS IN THE SOFTWARE.
