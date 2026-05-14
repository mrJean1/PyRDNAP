
# -*- coding: utf-8 -*-

u'''(INTERNAL) C{RD NAP 2018} v#grid utilities.
'''
from pyrdnap import pyrdnap_abspath  # pyrdnap 1st
from pyrdnap.__pygeodesy import _0_0s, import_module, _ValueError
from pygeodesy import print_

from array import array
import os.path as os_path
import sys
from zipfile import ZipFile

__all__ = ()
__version__ = '26.05.13'

_R_C = 481, 301  # shape: rows, cols
_RxC = 144781    # total


class RDNAPError(_ValueError):  # exported by rdnap2018
    '''Error raised for C{RD}, C{NAP} and unzip issues.
    '''
    pass


class _V_grid(tuple):
    '''(INTERNAL) V_grid, an R-tuple of C-arrays of C{floats}.
    '''

    def __call__(self, i, j):
        # R, C = _R_C
        # assert isinstance(i, int) and 0 <= i < R
        # assert isinstance(j, int) and 0 <= j < C
        return self[i][j]

    def _assert(self, _0s=0):
        z, Z = self._assert2(*_R_C)
        _v_assert(z, _0s)
        _v_assert(Z,  197 if _0s else 0)
        _v_assert(sum(map(len, self)), _RxC)
        return self

    def _assert2(self, R, C):
        _v_assert(len(self), R)
        _v_assert(len(_ZEROW), C)
        z = Z = 0  # count zeros and _ZEROSWs
        try:
            for i, r in enumerate(self):
                _v_assert(type(r), array)
                _v_assert(len(r), C)
                if r is _ZEROW:
                    Z += 1
                    z += C
                else:
                    z += sum((0 if f else 1) for f in r)
        except AssertionError as x:
            raise AssertionError('row %s: %s' % (i, x))
        return z, Z

    def _round(self, _op, ndigits):
        # round(_op(f for a in self
        #             for f in a), ndigits)
        return round(_op(map(_op, self)), ndigits)


def _d_array(floats):  # lat_/lon_corr_
    return array('d', floats)


def _f_array(floats):  # _NAP_h, _ZEROW
    return array('f', floats)

_ZEROW = _f_array(_0_0s(301))  # PYCHOK singleton


def _v_grid(v):
    return 'v%sgrid' % (v,)


def _v_assert(value, valid=_R_C):  # in .rd0
    if value != valid:
        raise AssertionError('%r not %r' % (value, valid))
    return True


def _v_grid_txt(v, name, col2or3, _array, **_0s):
    '''(INTERNAL) Return a C{_V_grid} for column C{col2or3} of
       compressed, variant C{v} grid file C{<name>2018.txt.zip}.
       '''
    v = _V_grid(_v_txt_unzip(v, name, col2or3, _array))
    return v._assert(**_0s)


def _v_gridz3(v):  # PHYCOK no cover
    '''(INTERNAL) Return the fully-qualified path, directory and module.
    '''
    m = _v_grid(v)
    d =  pyrdnap_abspath
    p =  os_path.join(d, m + 'z.zip')
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
    p, d, m = _v_gridz3(v)
    t = os_path.join(d, m)
    if (not force) and os_path.exists(t):
        t = '%r exists: %r' % (m, t)
        raise RDNAPError(t)
    try:
        with ZipFile(p) as z:
            z.extractall(d)
    except Exception as x:
        raise RDNAPError(m, cause=x)
    if verbose:
        print_('unzipped', repr(p))
        print_('    into', repr(t))


def _v_txt_unzip(v, name, col2or3, _array):
    '''(INTERNAL) Open grid file C{<name>2018.txt} or unzip
       C{<name>2018.txt.zip} of variant C{v}, extract column
       C{col2or3} and yield 481 rows, each a 301-C{_array}
       of floats or _ZEROW if all zeros.
    '''
    r = []
    try:
        n = name + '2018.txt'
        p = pyrdnap_abspath
        p = os_path.join(p, _v_grid(v), n)
        with (open(p, 'rb') if os_path.exists(p) else
              ZipFile(p + '.zip').open(n)) as f:
            _, C = _R_C
            _r = r.append
            t  = f.readline()  # ignore 1st line
            while t:
                for _ in range(C * 2):
                    t = f.readline()
                    if t:
                        _r(t.strip().split()[col2or3])
                    else:
                        break
                while len(r) >= C:
                    y = _array(map(float, r[:C]))
                    yield y if any(y) else _ZEROW
                    r[:] = r[C:]
    except Exception as x:
        raise RDNAPError(n, cause=x)
    _v_assert(len(r), 0)


# __all__ += _ALL_OTHER(RDNAPError)  # in .rdnap2018

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
