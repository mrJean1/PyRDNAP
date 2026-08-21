
# -*- coding: utf-8 -*-

u'''A pure Python implementation of the 2018 v220627 version of Netherlands' U{RD NAP<https://
www.NSGI.NL/coordinatenstelsels-en-transformaties/coordinatentransformaties/rdnap-etrs89-rdnaptrans>}
specification to convert between GRS80 (ETRS89) geodetic lat-, longitudes and ellipsoidal height
C{h} and local I{B{R}ijksB{D}riehoeksmeeting (B{RD})} coordinates and orthometric height C{H} using
bilinear interpolation of I{B{N}ormaal B{A}msterdams B{P}eil quasi-geoid heights (B{NAPh})}.

The results of both B{C{pyrdnap}} transformer classes L{RDNAP2018v1} and L{RDNAP2018v2} have been
formally validated and B{C{PyRDNAP}} has been certified to carry the trademark B{C{RDNAPTRANS(tm)}}.

See module L{pyrdnap.rdnap2018} for further information, usage and implementation details.

See modules L{pyrdnap.v1grid} and L{pyrdnap.v2grid} for the C{RDNAPTRANS(tm)2018_v220627} grid
files, each the original, unmodified ASCII C{.txt} but compressed as C{.txt.zip}.

See function L{pyrdnap.validation3} for C{.../Z001_ETRSandRDNAP.txt} test set details.

See files C{testresults/v1_..._round_trips.txt} for "round-trip" (forward plus reverse) test
results of the L{RDNAP2018v1} transformer, especially the final, summary lines in each file.
'''
import os.path as os_path
import sys

# _isfrozen     = getattr(_sys, 'frozen', False)
pyrdnap_abspath = os_path.dirname(os_path.abspath(__file__))  # _sys._MEIPASS + '/pyrdnap'
_pyrdnap_       = __package__ or  os_path.basename(pyrdnap_abspath)

# setting __path__ should ...
__path__ = [pyrdnap_abspath]
try:  # ... make this import work, ...
    import pyrdnap.__pygeodesy as __pygeodesy  # noqa: F401
except ImportError:  # ... if not, extend sys.path
    if pyrdnap_abspath not in sys.path:
        sys.path.insert(0, pyrdnap_abspath)
    import pyrdnap.__pygeodesy as __pygeodesy  # noqa: F401

import pyrdnap.rd0  as _rd0  # noqa: F401
import pyrdnap.rdnap2018 as _rdnap2018  # noqa: F401
import pyrdnap.v_self as _v_self  # noqa: F401

__all__ = __pygeodesy._ALL_STAR(_pyrdnap_, _rd0, _rdnap2018, _v_self, __pygeodesy)
__version__ = '26.08.18'

del _rd0, _rdnap2018, _v_self, os_path, sys


def _versions(**sep):  # in .__main__, .v_self, .test/bases
    # Get the pyrdnap, pygeodesy, Python ... versions (C{str}).
    return __pygeodesy._versions(pyrdnap=__version__, **sep)

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
