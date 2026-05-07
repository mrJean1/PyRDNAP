
# -*- coding: utf-8 -*-

u'''(INTERNAL) C{pyrdnap} access to some private C{pygeodesy} attributes.
'''


def _PyGeodesy_dir():
    # Adjust sys.path to enable import pygeodesy
    d = None
    try:
        from pygeodesy import version as _v
    except ImportError:
        import os.path as os_path
        import sys  # PYCHOK used!
        # PYTHONPATH=.../PyRDNAP for development ONLY
        p = os_path.abspath(__file__)
        p = os_path.dirname(p)  # pyrdnap_abspath
        p = os_path.dirname(p)  # PyRDNAP
        g = p.replace('PyRDNAP', 'PyGeodesy')
        if g != p and g not in sys.path:
            sys.path.insert(0, g)
            try:
                from pygeodesy import version as _v  # PYCHOK redef
                d = g
            except ImportError:
                _v = 'missing'
#           finally:
#               try:
#                   sys.path.remove(g)
#               except ValueError:
#                   pass

    def _t(v):
        return tuple(map(int, v.split('.')))  # _DOT_

    _r = '26.5.7'
    if _v == 'missing' or _t(_v) < _t(_r):
        _v = ' %s, need %s or newer' % (_v, _r)
        raise ValueError('pygeodesy' + _v)

    return d  # or None

_PyGeodesy_dir = _PyGeodesy_dir()  # PYCHOK path or None

from pygeodesy.basics import _xinstanceof, _xsubclassof  # noqa: F401
from pygeodesy.constants import _0_0, _0_0s, _0_5, _1_0, _N_1_0, _2_0, _isNAN  # noqa: F401
from pygeodesy.datums import _earth_datum  # noqa: F401
from pygeodesy.ellipsoidalBase import LatLonEllipsoidalBase as _LLEB  # noqa: F401
from pygeodesy.errors import _xkwds  # noqa: F401
from pygeodesy.internals import _secs2str, _versions  # noqa: F401
from pygeodesy.interns import _COMMASPACE_, _DASH_, _datum_, _E_, _height_, _lat_, _lon_, \
                              _N_, _NL_, _S_, _SPACE_, _UNDER_, _W_  # noqa: F401
from pygeodesy.lazily import _ALL_DOCS, _ALL_OTHER, _FOR_DOCS, import_module  # noqa: F401
from pygeodesy.named import _NamedBase, _NamedTuple, notOverloaded, _Pass  # noqa: F401

__all__ = ()
__version__ = '26.05.07'

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
