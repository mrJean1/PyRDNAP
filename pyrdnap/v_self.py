
# -*- coding: utf-8 -*-

u'''Function L{validation3} to run the C{RD NAP 2018} self-validation test set
C{.../RDNAPTRANS2018_v220627/.../Z001_ETRS89andRDNAP.txt} obtainable from U{NSGI.NL
<https://www.NSGI.NL/coordinatenstelsels-en-transformaties/coordinatentransformaties/rdnap-etrs89-rdnaptrans>}
after registration.

For each test point, 3 lines are produced: the 1st showing the point C{id}, the original
(ETRS89) C{lat}, C{lon} and C{height} and the expected C{RDx}, C{RDy} and C{NAPh} values.

The 2nd line shows the C{lat}, C{lon} and C{height} and C{RDx}, C{RDy} and {NAPh} results
from the L{RDNAP2018v1} or C{-v2} transformer's L{reverse<pyrdnap.RDNAP2018v1.reverse>}
respectively L{forward<pyrdnap.RDNAP2018v1.forward>} method.

The 3rd line contains the (absolute value) of the differences for each result on the 2nd
line and the corresponding, original test point value on the 1st line.

The final lines of the output are the C{maximum} of all (absolute value) differences in
2 formats and a line with the C{RD NAP 2018} requirements, C{0.000000010 degrees} or
C{0.0010 meter} for each result.

A test C{FAILED} if any C{reverse} or C{forward} result I{exceeds} the C{RD NAP 2018}
requirement for that result.

For points with C{NAPh} marked C{"*"}, C{NAPh} is set to C{NAN}.

@see: Module L{pyrdnap<pyrdnap.__main__>} for examples to invoke L{validation3}.
'''
from pyrdnap.rd0 import RDNAP7Tuple
from pyrdnap.__pygeodesy import (_ALL_OTHER, _COMMASPACE_, _NAN_, _NL_,
                                 _SPACE_, _STAR_, _secs2str, _xinstanceof)
from pygeodesy import NN, NAN, map2, typename

from math import fabs
import os.path as os_path
from time import time

__all__ = ()
__version__ = '26.06.02'

_NAMES = RDNAP7Tuple._Names_[3:6] + RDNAP7Tuple._Names_[0:3]
#        (lat   lon   height RDx   RDy   NAPh)
_REQ_D = (1e-8, 1e-8, 1e-3,  1e-3, 1e-3, 1e-3)  # 0 == ignore
_NDECS = (11,   11,   6,     8,    8,    8)  # fmt precision
_NDecs = tuple((_ - 4) for _ in _NDECS)  # fe4 precision


def _line(ln):  # in .__main__
    return ' (line %s)' % (ln,)


def _readlines(filename):  # in .__main__
    # yield each line as str, not bytes
    with open(filename, 'rb') as f:
        t = f.readline()
        while t:
            yield t.strip().decode('utf-8')
            t = f.readline()


def validation3(self_txt, R, all_=False, in_out=True, _print=None, _printest=None):  # MCCABE 18
    '''Run the C{RD NAP 2018} self-validation test set.

       @arg self_txt: Name of the file containing the C{RD NAP 2018} self-validation tests
                      (C{str}), C{.../RDNAPTRANS2018_v220627/.../Z001_ETRS89andRDNAP.txt}.
       @arg R: An RDNAP2018v# transformer (L{RDNAP2018v1} or L{RDNAP2018v2} instance).
       @kwarg all_: If C{True} print all tests and test results, otherwise only failing
                    tests (C{bool}).
       @kwarg in_out: If C{True} test only points C{inside} the C{RD} region, if C{False}
                      only points C{outside} (C{bool}).
       @kwarg _print: A Python 3+ C{print}-like callable or C{None} to not print the header
                      and the final, summary lines.
       @kwarg _printest: A Python 3+ C{print}-like callable or C{None} to not print B{C{all_}}
                         B{C{in_out}} tests or only the failing ones.

       @return: 3-Tuple C{(failed, total, in_outside)} with the number of C{FAILED} tests,
                the C{total} number of tests and the number of points B{C{in_out}} the C{RD}
                region.
    '''
    from pyrdnap import RDNAP2018v1, RDNAP2018v2, RDNAPError, _versions

    _xinstanceof(str, bytes, self_txt=self_txt)
    _xinstanceof(RDNAP2018v1, RDNAP2018v2, R=R)
    R_ = typename(R)

    nfailed = ntotal = nin_out = 0
    if _print:
        _print('testing', repr(R))
        _print('  using', repr(self_txt))
    if self_txt and os_path.exists(self_txt):
        diffs = [0] * len(_REQ_D)  # max |diff| of all
        ds = list(diffs)  # |diff| per line
        ln = t0 = 0
        for t in _readlines(self_txt):
            ln += 1
            if t0:
                ts = t.split()  # list
                if ts[6] == _STAR_:
                    ts[6] = _NAN_
                lat, lon, h, RDx, RDy, NAPh = xs = map2(float, ts[1:])
                if in_out == bool(R.isinside(lat, lon)):
                    F  = NN  # PASSED
                    rs = R.reverse(RDx, RDy, NAPh).latlonheight + \
                         R.forward(lat, lon, h).xyz
                    ntotal  += len(rs)
                    nin_out += 1
                    for i, (m, q, r, x) in enumerate(zip(diffs, _REQ_D, rs, xs)):
                        if q > 0:
                            ds[i] = d = fabs(r - x)
                            if d > m:  # new max |diff|
                                diffs[i] = d
                            if d > q:
                                nfailed += 1
                                F = 'FAILED'
                        else:  # PYCHOK no cover
                            ntotal -= 1
                            ds[i] = NAN
                    if _printest and (F or all_):
                        _printest('id', _SPACE_(*ts), _line(ln))
                        _printest(R_, _zfmt(rs), F)
                        _printest('     |diff|', _zfe4(ds), F, _NL_)
            else:  # 1st line
                if _print:
                    _print(' header', repr(t), _line(ln), _NL_)
                t0 = time()

        if _print:
            s = time() - t0
            t = '-inside' if in_out else '-outside'
            if _printest:
                t += ' -all' if all_ else ' -failed'
            t = '%s of %s points %s' % (nin_out, (ln - 1), t)
            t = '%s (%s) %s' % (t, _versions(), _secs2str(s))
            if nfailed:
                _print(R_, nfailed, 'of', ntotal, 'tests', 'FAILED,', t)
            else:
                _print(R_, 'all', ntotal, 'tests', 'PASSED,', t)
            for n, _z, fs in (('req', _zfmt, _REQ_D), ('max', _zfe4, diffs),
                                                      ('max', _zfmt, diffs)):
                _print(R_, n, '|diff|', _z(fs))
    else:  # PYCHOK no cover
        t = "doesn't exist: %r" % (self_txt,)
        if _print:
            _print(t)
        else:
            raise RDNAPError(t)
        nfailed = 1
    return nfailed, ntotal, nin_out


def _zfe4(floats):
    t = ('%s %.*e' % t for t in zip(_NAMES, _NDecs, floats))
    return _COMMASPACE_.join(t)


def _zfmt(floats):
    t = ('%s %.*f' % t for t in zip(_NAMES, _NDECS, floats))
    return _COMMASPACE_.join(t)


__all__ += _ALL_OTHER(validation3)

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
