
# -*- coding: utf-8 -*-

u'''Run a C{RD NAP 2018 forward} or C{reverse} conversion round-trip examples or
run the entire C{RD NAP 2018} self-validation test suite in various ways.

Use C{"python -m pyrdnap -h | --help"} for further information.

@note: C{PyRDNAP} and C{pyrdnap} have B{not been formally validated} and are B{not
       certified} to carry the trademark name C{RDNAPTRANS(tm)}.
'''
from pyrdnap import _pyrdnap_, RDNAP2018v1, RDNAP2018v2, _versions  # pyrdnap 1st
from pyrdnap.v_self import validation3
from pygeodesy import print_

import sys

__all__ = ()
__version__ = '26.05.08'

_DASH_ = '-'
_R     =  RDNAP2018v1(name='v1Test')
_v     = '-v1'


def _run_validation(argv, R, in_out):
    a = argv[0]
    f = bool('-failed'.startswith(a) and len(a) > 1)
    a = a == '-all'
    nf, _, _ = validation3(argv[-1], R, all_=a, in_out=in_out,
                          _print=print_,
                          _printest=print_ if a or f else None)
    sys.exit(min(nf, 99))


def _usage(x):
    _t = '\t[ -v1 | -v2 ]'
    print_('usage: python3 -m', _pyrdnap_, ' [ -h | -help ]', ' [ -v | --version ]',)
    print_(_t, '-forward  <lat> <lon>  [ <height> ]')
    print_(_t, '-reverse  <x> <y> <z>')
    print_(_t, '-inside  [ -all | -failed ] ', '<.../RDNAPTRANS2018_v220627/.../Z001_ETRS89andRDNAP.txt>')
    print_(_t, '-outside [ -all | -failed ] ', '<.../RDNAPTRANS2018_v220627/.../Z001_ETRS89andRDNAP.txt>')
    print_(_t, '-unzip  [ -force ]')
    sys.exit(x)


argv = sys.argv[1:]
while argv and argv[0].startswith(_DASH_):
    arg  = argv.pop(0)
    larg = len(arg)
    narg = len(argv)
    if argv == '-h' or ('--help'.startswith(arg) and larg > 2):
        _usage(0)
    elif arg == '-v' or ('--version'.startswith(arg) and larg > 2):
        print_(_versions())
        sys.exit(0)
    elif arg in ('-v1', '-v2'):
        _R = RDNAP2018v2(name='v2Test') if arg == '-v2' else \
             RDNAP2018v1(name='v1Test')
        _v = arg
    elif '-inside'.startswith(arg) and larg >= 2 and narg > 0:
        _run_validation(argv, _R, True)
    elif '-outside'.startswith(arg) and larg >= 2 and narg > 0:
        _run_validation(argv, _R, False)
    elif '-forward'.startswith(arg) and larg > 1 and narg > 1:
        r = _R.forward(*map(float, argv[:3]))
        print_('forward:', r)
        r = _R.reverse(r.RDx, r.RDy, r.NAPh)
        print_('reverse:', r)
    elif '-reverse'.startswith(arg) and larg > 1 and narg > 1:
        r = _R.reverse(*map(float, argv[:3]))
        print_('reverse:', r)
        r = _R.forward(r.lat, r.lon, r.height)
        print_('forward:', r)
    elif '-unzip'.startswith(arg) and larg > 3:
        from pyrdnap.v_grids import _v_gridz_unzip
        _f = bool(argv and argv[0] == '-force')
        _v_gridz_unzip(_v[2], force=_f, verbose=True)
    else:
        print_('invalid option:', repr(arg))
        _usage(1)


# % python3 -m pyrdnap -v1 -forward 52.15616 5.3876389
# forward: (155029.784672, 463109.826226, -43.275509, 52.15616, 5.387639, 0, Datum(name='GRS80', ellipsoid=Ellipsoids.GRS80, transform=Transforms.WGS84))
# reverse: (155029.784672, 463109.826226, -43.275509, 52.15616, 5.387639, -0.0, Datum(name='GRS80', ellipsoid=Ellipsoids.GRS80, transform=Transforms.WGS84))


# % python3 -m pyrdnap -v1 -reverse 155000 463000
# reverse: (155000.0, 463000.0, 0, 52.155173, 5.387204, 43.277164, Datum(name='GRS80', ellipsoid=Ellipsoids.GRS80, transform=Transforms.WGS84))
# forward: (155000.0, 463000.0, 0.0, 52.155173, 5.387204, 43.277164, Datum(name='GRS80', ellipsoid=Ellipsoids.GRS80, transform=Transforms.WGS84))


# % python3 -m pyrdnap -v1 -inside .../RDNAPTRANS2018_v220627/.../Z001_ETRS89andRDNAP.txt
# testing RDNAP2018v1(name='v1Test', variant=1, forwardDatum=Datum(name='GRS80', ellipsoid=Ellipsoids.GRS80, transform=Transforms.WGS84))
#   using '.../RDNAPTRANS2018_v220627/.../Z001_ETRS89andRDNAP.txt'
#  header 'point_id\tETRS89_lat. \tETRS89_lon.\tETRS89_h  \tRD_x       \tRD_y       \tNAP_H'  (line 1)
# RDNAP2018v1 all 47754 tests PASSED, 7959 of 10000 lines -inside (pyrdnap 26.5.5 pygeodesy 26.5.2 Python 3.13.12 64bit arm64 macOS 26.4.1) 382.024 ms
# RDNAP2018v1 req |diff| lat 0.00000001000, lon 0.00000001000, height 0.001000, RDx 0.00100000, RDy 0.00100000, NAPh 0.00100000
# RDNAP2018v1 max |diff| lat 0.00000000247, lon 0.00000000187, height 0.000050, RDx 0.00008785, RDy 0.00022281, NAPh 0.00004999


# % python3 -m pyrdnap -v1 -outside .../RDNAPTRANS2018_v220627/.../Z001_ETRS89andRDNAP.txt
# testing RDNAP2018v1(name='v1Test', variant=1, forwardDatum=Datum(name='GRS80', ellipsoid=Ellipsoids.GRS80, transform=Transforms.WGS84))
#   using '.../RDNAPTRANS2018_v220627/.../Z001_ETRS89andRDNAP.txt'
#  header 'point_id\tETRS89_lat. \tETRS89_lon.\tETRS89_h  \tRD_x       \tRD_y       \tNAP_H'  (line 1)
# RDNAP2018v1 372 of 10205 tests FAILED, 2041 of 10000 lines -outside (pyrdnap 26.5.5 pygeodesy 26.4.28 Python 3.14.4 64bit arm64 macOS 26.4.1) 330.483 ms
# RDNAP2018v1 req |diff| lat 0.00000001000, lon 0.00000001000, height 0.001000, RDx 0.00100000, RDy 0.00100000, NAPh 0.00100000
# RDNAP2018v1 max |diff| lat 0.00000003546, lon 0.00000004269, height 0.000000, RDx 0.00035235, RDy 0.00077548, NAPh 0.00000000


# % python3 -m pyrdnap -v2 -forward 52.15616 5.3876389
# forward: (155029.78463, 463109.826158, -43.277178, 52.15616, 5.387639, 0, Datum(name='GRS80', ellipsoid=Ellipsoids.GRS80, transform=Transforms.WGS84))
# reverse: (155029.78463, 463109.826158, -43.277178, 52.15616, 5.387639, 0.0, Datum(name='Bessel1841', ellipsoid=Ellipsoids.Bessel1841, transform=Transforms.Bessel1841))


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
