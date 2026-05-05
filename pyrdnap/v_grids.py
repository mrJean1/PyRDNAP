
# -*- coding: utf-8 -*-

u'''(INTERNAL) RDNAP v#grid utilities.
'''
from pyrdnap import pyrdnap_abspath  # pyrdnap 1st
from pyrdnap.__pygeodesy import _0_0s, _1_0, import_module
from pygeodesy import print_

from array import array
import os.path as os_path
import sys

__all__ = ()
__version__ = '26.05.05'

_R_C = 481, 301  # shape: rows, cols
_RxC = 144781    # total


class _V_grid(tuple):
    '''(INTERNAL) V_grid, an R-tuple of C-arrays of C{floats}.
    '''
    _scale =  None

    def __call__(self, i, j):
        # R, C = _R_C
        # assert isinstance(i, int) and 0 <= i < R
        # assert isinstance(j, int) and 0 <= j < C
        return self[i][j] * self._scale

    def _assert(self, scale, ndigits, *len_min_0s_max):
        self._scale = scale
        z = self._assert0s(*_R_C)
        n = sum(map(len, self))  # _RxC
        t = (n, self._round(min, ndigits),
             z, self._round(max, ndigits))
        _v_assert(t, len_min_0s_max)
        return self

    def _assert0s(self, R, C):
        _v_assert(len(self), R)
        z = 0  # count zeros
        try:
            for i, r in enumerate(self):
                _v_assert(type(r), array)
                _v_assert(len(r), C)
                z += C if r is _ZEROW else \
                     sum((0 if f else 1) for f in r)
        except AssertionError as x:
            raise AssertionError('row %s: %s' % (i, x))
        return z

    def _round(self, _op, ndigits):
        # round(_op(f for a in self
        #             for f in a), ndigits)
        return round(_op(map(_op, self)), ndigits)


def _d(floats):  # _lat_/_lon_corr
    return array('d', floats)


def _f(floats):  # _NAP_h, _ZEROW
    return array('f', floats)

_ZEROW = _f(_0_0s(301))  # PYCHOK singleton


def _v_assert(value, valid=_R_C):
    if value != valid:
        raise AssertionError('%r not %r' % (value, valid))
    return True


def _v1corr_grid(s_e_tuples, ndigits, cmin, cmax, c0s=0, flen=_RxC, scale=1e-5):
    '''(INTERNAL) Build a variant 1 C{lat_/lon_corr} _V_grid from C{s_e_tuples},
       each a run of non-zero floats preceeded by a start and end index.
    '''
    v = _V_grid(_v1corr_rows(s_e_tuples, *_R_C))
    return v._assert(scale, ndigits, flen, cmin, c0s, cmax)


def _v1corr_rows(s_e_tuples, R, C):
    '''(INTERNAL) Yield R d-/f-arrays, each of C floats.
    '''
    # Of 144,781 floats, only 55,139 resp. 55,348 are non-zero between C{lat_corr}
    # indices [8598:93827] resp. C{lon_corr} [8598:93830].  As a result, the 1st
    # 28 and the last 169 rows (in total 197 rows, 41% of 481) are all the same,
    # single C{f-array} of 301 zeros, _ZEROW.  There are other stretches of zeros,
    # but none are 301 or longer.
    z = _ZEROW  # f-array of C zeros
    i =  s_e_tuples[0][0]  # index of 1st non-zero
    y, s = divmod(i, C)
    for _ in range(y):  # 28 leading ZEROWs
        yield z
    r = list(_0_0s(s))  # remainder, 170 zeros
    for t in s_e_tuples:
        s, e = t[:2]
        r.extend(_0_0s(s - i))
        r.extend(t[2:])  # len(r) < 600
        while len(r) >= C:
            d = _d(r[:C])  # d-array
            r[:] = r[C:]
            yield d if any(d) else z  # just in case
            y += 1
        i = e
    if r:  # remaining, 216/219 non-zeros
        # assert 0 < len(r) < C
        r.extend(_0_0s(C - len(r)))
        yield _d(r)  # d-array
        # r[:] = ()
        y += 1
    for _ in range(y, R):  # 169 trailing ZEROWs
        yield z


def _v2corr_grid(darrays, ndigits, cmin, cmax, c0s=0, flen=_RxC, scale=0):
    '''(INTERNAL) A variant 2 C{lat_/lon_corr} _V_grid.
    '''
    return _V_grid(darrays)._assert(scale, ndigits, flen, cmin, c0s, cmax)


def _v_h_grid(farrays, hmin, hmax, flen=_RxC, scale=_1_0):
    '''(INTERNAL) An C{NAP_h} _V_grid.
    '''
    return _V_grid(farrays)._assert(scale, 4, flen, hmin, 0, hmax)


def _v_gridz3(v):  # PHYCOK no cover
    '''(INTERNAL) Return the fully-qualified path, directory and module.
    '''
    m = 'v%sgrid' % (v,)
    z =  m + 'z.zip'
    d =  pyrdnap_abspath
    p =  os_path.join(d, z)
    return p, d, m


def _v_gridz_import(v):  # PHYCOK no cover
    '''(INTERNAL) Try "from v#gridz.zip import v#grid"
    '''
    v_grid  =  None
    p, _, m = _v_gridz3(v)
    try:  # Py 3.4+
        # <https://RealPython.com/python-zip-import/
        # #explore-pythons-zipimport-the-tool-behind-zip-imports>
        from zipimport import zipimporter as Z  # ZipImportError
        # get an importer for zip file p and load module m
        v_grid = Z(p).load_module(m)  # Py3.14-
        # XXX should use .exec_module but that fails and/or
        # XXX needs .create_module, .find_spec, etc???
    except (AttributeError, ImportError):
        try:  # trusted old-fashion way
            sys.path.insert(0, p)
            v_grid = import_module(m)
#       except ImportError:
#           v_grid = None
        finally:
            try:
                sys.path.remove(p)
            except ValueError:
                pass  # AssertionError
#   if v_grid:
#       sys.modules[m] = v_grid
    return v_grid


def _v_gridz_unzip(v, force=False, verbose=False):  # PHYCOK no cover
    '''(INTERNAL) Unzip a C{v#gridz.zip} file into the "pyrdnap" directory
    '''
    try:
        from zipfile import BadZipFile, ZipFile
    except ImportError:  # Py3.3-
        from zipfile import BadZipfile as BadZipFile, ZipFile

    p, d, m = _v_gridz3(v)
    t = os_path.join(d, m)
    if (not force) and os_path.exists(t):
        t = 'dir %r exists: %r' % (m, t)
        raise OSError(t)
    try:
        with ZipFile(p, 'r') as z:
            z.extractall(d)
    except BadZipFile as x:
        raise ValueError(str(x), cause=x)
    if verbose:
        print_('unzipped', repr(p))
        print_('    into', repr(t))

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
