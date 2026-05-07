
# -*- coding: utf-8 -*-

u'''A pure Python implementation of the Netherlands' U{RD NAP<https://www.NSGI.NL/
coordinatenstelsels-en-transformaties/coordinatentransformaties/rdnap-etrs89-rdnaptrans>}
specifications to convert between geodetic GRS80 (ETRS89) lat-/longitudes in degrees
and local C{RijksDriehoeksmeeting (RD)} coordinates and C{Normaal Amsterdams Peil (NAP)
quasi-geoid-height} in C{meter}.

@note: C{PyRDNAP} and C{pyrdnap} have B{not been formally validated} and are B{not certified}
       to carry the trademark name C{RDNAPTRANS(tm)}.

@see: Module L{pyrdnap.rdnap2018} for further information and implementation details.
'''
import os.path as os_path
import sys

# _isfrozen     = getattr(_sys, 'frozen', False)
pyrdnap_abspath = os_path.dirname(os_path.abspath(__file__))  # _sys._MEIPASS + '/pyrdnap'
_pyrdnap_       = __package__ or  os_path.basename(pyrdnap_abspath)

# setting __path__ should ...
__path__ = [pyrdnap_abspath]
try:  # ... make this import work, ...
    import pyrdnap.__pygeodesy as _  # PYCHOK unused
except ImportError:  # ... if it doesn't, extend sys.path to include
    # this very directory such that all public and private sub-modules
    # can be imported (by epydoc, checked by PyChecker, etc.)
    if pyrdnap_abspath not in sys.path:
        sys.path.insert(0, pyrdnap_abspath)  # XXX __path__[0]

try:  # PYCHOK once
    from pyrdnap.__pygeodesy import _SPACE_, _versions as _pygeodesy_versions  # PYCHOK ...
except (AttributeError, ImportError) as x:
    raise AssertionError(str(x))

from pyrdnap.rd0 import *  # PYCHOK *
from pyrdnap.rd0 import __all__ as _rd0  # PYCHOK ?
from pyrdnap.rdnap2018 import *  # PYCHOK *
from pyrdnap.rdnap2018 import __all__ as _rdnap  # PYCHOK ?
from pyrdnap.v_self import *  # PYCHOK *
from pyrdnap.v_self import __all__ as _v_self  # PYCHOK ?

__all__ = ('pyrdnap_abspath',) + _rd0 + _rdnap + _v_self
__version__ = '26.05.07'


def _versions():  # in .__main__, .test/bases
    # Get the pyrdnap, pygeodesy, Python ... versions (C{str}).
    v  = __version__.replace('.0', '.')
    l_ = [_pyrdnap_, v] + _pygeodesy_versions(None)
    return _SPACE_.join(l_)


del _rd0, _rdnap, _v_self  # os_path, sys

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
