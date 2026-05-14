
# -*- coding: utf-8 -*-

u'''Run a C{RD NAP 2018 forward} or C{reverse} conversion examples or run
the C{NSGI} or C{RD NAP 2018} validation test set in "round-trip" fashion.

Use C{"python -m pyrdnap -h | --help"} for further information.

@note: C{PyRDNAP} and C{pyrdnap} have B{not been formally validated} and
       are B{not certified} to carry the trademark name C{RDNAPTRANS(tm)}.
'''
from pyrdnap import _pyrdnap_, RDNAP2018v1, RDNAP2018v2, RDNAP7Tuple, _versions
from pyrdnap.__pygeodesy import _datum_, _EQUAL_, Fmt, _NAN_, _secs2str, _SPACE_
from pyrdnap.v_self import _line, validation3
from pygeodesy import print_, typename

import sys
from time import time

__all__ = ()
__version__ = '26.05.14'

_DASH_ = '-'
_prec  =  6
_R     =  RDNAP2018v1(name='v1Test')
_v     = '-v1'


class Run(object):
    '''(INTERNAL) C{NSGI} or C{RDNAP2018} test set runner.
    '''
    _which = None

    def __init__(self, argv, R):  # PYCHOK no cover
        '''(INTERNAL) Run a U{NSGI-validatieservice<https://www.NSGI.NL/
           coordinatenstelsels-en-transformaties/tools/validatieservice>} test set.
        '''
        a          =  argv[0]
        self._all  =  a == '-all'
        self._fail =  bool('-failed'.startswith(a) and len(a) > 1)
        self._txt  =  argv[-1]
        self._max  = [0] * 6  # withut datum[6]
        self._prec = _prec
        self._R    =  R
        self._R_   =  typename(R)
        argv[:]    = ()

    def max_diff(self, diffs=None):
        '''(INTERNAL) Print C{max |diff|} line.
        '''
        if diffs:
            self._max[:] = map(max, zip(self._max, diffs))
        else:
            n = self._which + ' max |diff| '
            t = self._max + [None]
            d = RDNAP7Tuple(t, name=n)
            print_(self.toRepr6(d))

    def forward(self):  # PYCHOK no cover
        '''(INTERNAL) Run the C{.../002_ETRS89.txt} test set, "round-trip".
        '''
        _a = self._all
        R  = self._R
        R_ = self._R_
        for lat, lon, h in self._run(self.forward):
            f = R.forward(lat, lon, h)
            if _a:
                print_(R_, self.toRepr6(f, R))
            r = R.reverse(f.RDx, f.RDy, f.NAPh)
            if _a:
                print_(R_, self.toRepr6(r, R))
            d = r.diff(f, name='|diff| ')
            if _a:
                print_(R_, self.toRepr6(d))
            self.max_diff(d)
        self.max_diff()

    def reverse(self):  # PYCHOK no cover
        '''(INTERNAL) Run the C{.../002_RDNAP.txt} test set, "round-trip".
        '''
        _a = self._all
        R  = self._R
        R_ = self._R_
        for RDx, RDy, NAPh in self._run(self.reverse):
            r = R.reverse(RDx, RDy, NAPh)
            if _a:
                print_(R_, self.toRepr6(r, R))
            f = R.forward(r.lat, r.lon, r.height)
            if _a:
                print_(R_, self.toRepr6(f, R))
            d = r.diff(f, name='|diff| ')
            if _a:
                print_(R_, self.toRepr6(d))
            self.max_diff(d)
        self.max_diff()

    def _run(self, which):
        self._which = typename(which)
        print_('testing', repr(self._R))
        print_('  using', repr(self._txt))
        with open(self._txt, 'rb') as f:
            s = time()
            n = 1
            t = f.readline()
            print_(' header', t.strip().decode('utf-8'), _line(n))
            while t:
                t = f.readline()
                if t:
                    n += 1
                    t  = t.strip().decode('utf-8')
                    if self._all:
                        print_('id', t, _line(n), nl=1)
                    yield map(float, t.split()[1:])
        s = time() - s
        n = (n - 1) * 6  # without datum[0]
        t = 'tests (%s)' % (_versions(),)
        print_(self._R_, n, t, _secs2str(s), nl=1)

    def toRepr6(self, t7, R=None):
        '''(INTERNAL) Like C{RDNAP7Tuple.toRepr} but dropping ", datum=..." item.
        '''
        s = t7.toRepr(prec=self._prec, fmt=Fmt.g)
        s = s.split(_datum_)[0] + '...)'
        if R:
            s += ' inside' if R.isinside(t7.lat, t7.lon) else ' outside'
        return s.replace(_EQUAL_, _SPACE_).replace('nan', _NAN_)

    def validation3(self, in_out):
        '''(INTERNAL) Run the C{.../Z001_ETRS89andRDNAP.txt} test set.
        '''
        nf, _, _ = validation3(self._txt, self._R, all_=self._all, in_out=in_out,
                              _print=print_,
                              _printest=print_ if self._all or self._fail else None)
        sys.exit(min(nf, 99))


def _usage(x):
    _t = '\t[ -v1 | -v2 ]'
    print_('usage: python3 -m', _pyrdnap_, ' [ -h | -help ]',
                                           ' [ -v | --version ]',
                                           ' [ -precision <ndigits> ]')
    print_(_t, '-forward [ -all ] <.../002_ETRS89.txt> |', '<lat> <lon> [ <height> ]')
    print_(_t, '-reverse [ -all ] <.../002_RDNAP.txt>  |', '<RDx> <RDy> [ <NAPh> ]')
    print_(_t, '-inside  [ -all | -failed ] ', '<.../Z001_ETRS89andRDNAP.txt>')
    print_(_t, '-outside [ -all | -failed ] ', '<.../Z001_ETRS89andRDNAP.txt>')
    print_(_t, '-unzip  [ -force ]')
    sys.exit(x)


argv = sys.argv[1:]
while argv and argv[0].startswith(_DASH_):  # MCCABE 13
    arg  = argv.pop(0)
    larg = len(arg)
    narg = len(argv)
    if argv == '-h' or ('--help'.startswith(arg) and larg > 2):
        _usage(0)
    elif arg == '-v' or ('--version'.startswith(arg) and larg > 2):
        print_(_versions())
        sys.exit(0)
    elif arg == '-v1':
        _R = RDNAP2018v1(name='v1Test')
        _v = arg
    elif arg == '-v2':
        _R = RDNAP2018v2(name='v2Test')
        _v = arg
    elif '-precision'.startswith(arg) and larg > 1 and narg > 0:
        try:
            _prec = int(argv.pop(0))
        except ValueError:
            pass

    elif '-inside'.startswith(arg) and larg >= 2 and narg > 0:
        Run(argv, _R).validation3(True)

    elif '-outside'.startswith(arg) and larg >= 2 and narg > 0:
        Run(argv, _R).validation3(False)

    elif '-forward'.startswith(arg) and larg > 1 and narg > 0:
        if narg > 1 and argv[0] != '-all':
            f = _R.forward(*map(float, argv[:3]))
            print_(f.toRepr(prec=_prec))
            r = _R.reverse(f.RDx, f.RDy, f.NAPh)
            print_(r.toRepr(prec=_prec))
        else:  # PYCHOK no cover
            Run(argv, _R).forward()

    elif '-reverse'.startswith(arg) and larg > 1 and narg > 0:
        if narg > 1 and argv[0] != '-all':
            r = _R.reverse(*map(float, argv[:3]))
            print_(r.toRepr(prec=_prec))
            f = _R.forward(r.lat, r.lon, r.height)
            print_(f.toRepr(prec=_prec))
        else:  # PYCHOK no cover
            Run(argv, _R).reverse()

    elif '-unzip'.startswith(arg) and larg > 3:
        from pyrdnap.v_grids import _v_gridz_unzip
        _f = bool(argv and argv[0] == '-force')
        _v_gridz_unzip(_v[2], force=_f, verbose=True)
    else:
        print_('invalid option:', repr(arg))
        _usage(1)


# % python3 -m pyrdnap -v
# pyrdnap 26.5.11 pygeodesy 26.5.9 Python 3.14.4 64bit arm64 macOS 26.4.1


# % python3 -m pyrdnap -v1 -forward 52.15616 5.3876389
# forward(RDx=155029.784672, RDy=463109.826226, NAPh=-43.275509, lat=52.15616, lon=5.387639, height=0, datum=Datum(name='GRS80', ellipsoid=Ellipsoids.GRS80, transform=Transforms.WGS84))
# reverse(RDx=155029.784672, RDy=463109.826226, NAPh=-43.275509, lat=52.15616, lon=5.387639, height=-0.0, datum=Datum(name='GRS80', ellipsoid=Ellipsoids.GRS80, transform=Transforms.WGS84))


# % python3 -m pyrdnap -v1 -reverse 155000 463000
# reverse(RDx=155000.0, RDy=463000.0, NAPh=0, lat=52.155173, lon=5.387204, height=43.277164, datum=Datum(name='GRS80', ellipsoid=Ellipsoids.GRS80, transform=Transforms.WGS84))
# forward(RDx=155000.0, RDy=463000.0, NAPh=0.0, lat=52.155173, lon=5.387204, height=43.277164, datum=Datum(name='GRS80', ellipsoid=Ellipsoids.GRS80, transform=Transforms.WGS84))


# % python3 -m pyrdnap -v1 -inside .../RDNAPTRANS2018_v220627/Test_set_for_self_validation/Z001_ETRS89andRDNAP.txt
# testing RDNAP2018v1(name='v1Test', variant=1, forwardDatum=Datum(name='GRS80', ellipsoid=Ellipsoids.GRS80, transform=Transforms.WGS84))
#   using '.../RDNAPTRANS2018_v220627/Test_set_for_self_validation/Z001_ETRS89andRDNAP.txt'
#  header 'point_id\tETRS89_lat. \tETRS89_lon.\tETRS89_h  \tRD_x       \tRD_y       \tNAP_H'  (line 1)
#
# RDNAP2018v1 all 47754 tests PASSED, 7959 of 10000 points -inside (pyrdnap 26.5.13 pygeodesy 26.5.9 Python 3.14.4 64bit arm64 macOS 26.4.1) 518.165 ms
# RDNAP2018v1 req |diff| lat 0.00000001000, lon 0.00000001000, height 0.001000, RDx 0.00100000, RDy 0.00100000, NAPh 0.00100000
# RDNAP2018v1 max |diff| lat 2.4685889e-09, lon 1.8726842e-09, height 5.00e-05, RDx 8.7847e-05, RDy 2.2281e-04, NAPh 4.9993e-05
# RDNAP2018v1 max |diff| lat 0.00000000247, lon 0.00000000187, height 0.000050, RDx 0.00008785, RDy 0.00022281, NAPh 0.00004999


# % python3 -m pyrdnap -v1 -outside .../RDNAPTRANS2018_v220627/Test_set_for_self_validation/Z001_ETRS89andRDNAP.txt
# testing RDNAP2018v1(name='v1Test', variant=1, forwardDatum=Datum(name='GRS80', ellipsoid=Ellipsoids.GRS80, transform=Transforms.WGS84))
#   using '.../RDNAPTRANS2018_v220627/Test_set_for_self_validation/Z001_ETRS89andRDNAP.txt'
#  header 'point_id\tETRS89_lat. \tETRS89_lon.\tETRS89_h  \tRD_x       \tRD_y       \tNAP_H'  (line 1)
#
# RDNAP2018v1 372 of 10205 tests FAILED, 2041 of 10000 points -outside (pyrdnap 26.5.13 pygeodesy 26.5.9 Python 3.14.4 64bit arm64 macOS 26.4.1) 507.861 ms
# RDNAP2018v1 req |diff| lat 0.00000001000, lon 0.00000001000, height 0.001000, RDx 0.00100000, RDy 0.00100000, NAPh 0.00100000
# RDNAP2018v1 max |diff| lat 3.5461468e-08, lon 4.2693719e-08, height 0.00e+00, RDx 3.5235e-04, RDy 7.7548e-04, NAPh 0.0000e+00
# RDNAP2018v1 max |diff| lat 0.00000003546, lon 0.00000004269, height 0.000000, RDx 0.00035235, RDy 0.00077548, NAPh 0.00000000


# % python3.14 -m pyrdnap -v1 -forward .../NSGI-validatieservice/002_ETRS89.txt
# testing RDNAP2018v1(name='v1Test', variant=1, forwardDatum=Datum(name='GRS80', ellipsoid=Ellipsoids.GRS80, transform=Transforms.WGS84))
#   using '.../NSGI-validatieservice/002_ETRS89.txt'
#  header point_id  latitude        longitude    height  (line 1)
#
# RDNAP2018v1 60000 tests (pyrdnap 26.5.13 pygeodesy 26.5.9 Python 3.14.4 64bit arm64 macOS 26.4.1) 462.933 ms
# forward max |diff| (RDx 0, RDy 0, NAPh 0, lat 6.99816e-09, lon 4.75236e-09, height 4.12274e-09, ...)


# % python3 -m pyrdnap -v1 -reverve .../NSGI-validatieservice/002_RDNAP.txt
# testing RDNAP2018v1(name='v1Test', variant=1, forwardDatum=Datum(name='GRS80', ellipsoid=Ellipsoids.GRS80, transform=Transforms.WGS84))
#   using '.../NSGI-validatieservice/002_RDNAP.txt'
#  header point_id  x_coordinate  y_coordinate height  (line 1)
#
# RDNAP2018v1 60000 tests (pyrdnap 26.5.13 pygeodesy 26.5.9 Python 3.14.4 64bit arm64 macOS 26.4.1) 473.737 ms
# reverse max |diff| (RDx 0.000223603, RDy 0.000799715, NAPh 5.68434e-14, lat 0, lon 0, height 0, ...)


# % python3 -m pyrdnap -v2 -forward 52.15616 5.3876389
# forward(RDx=155029.78463, RDy=463109.826158, NAPh=-43.277178, lat=52.15616, lon=5.387639, height=0, datum=Datum(name='GRS80', ellipsoid=Ellipsoids.GRS80, transform=Transforms.WGS84))
# reverse(RDx=155029.78463, RDy=463109.826158, NAPh=-43.277178, lat=52.15616, lon=5.387639, height=0.0, datum=Datum(name='Bessel1841', ellipsoid=Ellipsoids.Bessel1841, transform=Transforms.Bessel1841))


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
