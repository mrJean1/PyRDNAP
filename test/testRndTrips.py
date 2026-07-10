
# -*- coding: utf-8 -*-

# Test L{PyRDNAP} with round-trips of random lat-/longitudes inside.

from bases import TestsBase, Datums, NAN, startswith

from pyrdnap import LqRD, RDNAP2018v1, RDNAP2018v2, RDNAPError, RDNAP7Tuple
from pyrdnap.rd0 import _RD, _RD0 as A0

from math import fabs
from random import random, seed
from time import localtime

__all__ = ()
__version__ = '26.07.07'

# random repeatable all day
seed(localtime().tm_yday)
del localtime, seed

_ndigits = 8  # 9 cause 95 v1 failures
_nrandom = 64


def _rnd(f):
    return round(f, _ndigits)


def _str(t, ndigits=10):
    t = tuple(round(f, ndigits) for f in t[:6])
    return str(t)


class Tests(TestsBase):

    def testAmersfoort(self, R):
        self.test(R.name, 'A0', 'A0', nl=1)
        # A0.LAT0, A0.LON0 = 52.15616056, 5.38763889
        self.testRndTrip(R, A0.LAT0, A0.LON0,   0.0)     # (A0.X0, A0.Y0, 0.0)
        self.testRndTrip(R, A0.LAT0, A0.LON0,  43.2551)  # (A0.X0, A0.Y0, 0.0)
        self.testRndTrip(R, A0.LAT0, A0.LON0, 143.2551)  # (A0.X0, A0.Y0, 100.0)

    def testEPSG(self, R):
        # <https://EPSG.io/9809-method> Example
        self.test(R.name, 'EPSG:9809', 'EPSG:9809')
        self.testRndTrip(R, 53.0, 6.0,
                            RDx_RDy='(196105.283, 557057.739)')
        # <https://geoforum.nl/t/nieuwe-epsg-codes-voor-nederland/11443>
        self.test(R.name, 'EPSGv12.054', 'EPSGv12.054')
        self.testRndTrip(R, 53.148288321,7.180899528,
                            RDx_RDy='(275000.000, 575000.000)')
        # Z001_ETRS89andRDNAP.txt first point
        self.test(R.name, 'id 30010000', 'id 30010000')
        self.testRndTrip(R, 51.728601274, 4.712120126, 301.7981,
                            RDx_RDy='(108360.8790, 415757.2745)')  # 258.0057

    def testLqRD(self):
        R = RDNAP2018v1(name='vsLqRD')
        self.test('v1', R, "name='vsLqRD'", known=startswith)
        S, W, N, E = r = R.region4()
        self.test('region', r, r)
        L = LqRD()
        for llh in ((A0.LAT0, A0.LON0, A0.H0),
                    (r.latC, r.lonC, 0),
                    (N, E, 0), (N, W, 0), (S, E, 0), (S, W, 0)):
            t = R.forward(*llh)
            self.test('rdnap', t, t, nl=1)
            r = L.forward(*t.latlonheight)
            self.test(' lqrd', r, r)
            z = r.diff(t)
            self.test(' diff', z, z)
            r = L.reverse(r.RDx, r.RDy, r.NAPh)
            self.test('-lqrd', r, r)

    def testRandom(self, R, **nl):
        S, W, N, E = R.region4()
        E_W = E - W
        N_S = N - S
        r   = random.__name__
        self.test(R.name, r, r, **nl)
        for _ in range(_nrandom):
            self.testRndTrip(R, _rnd(random() * N_S + S),
                                _rnd(random() * E_W + W))

    def testRDs(self, R):
        self.test('_RD', _RD.toStr(), '_region4=RD region (latS=50.0, ', known=startswith, nl=1)
        self.test('_RD0', A0.toStr(), "D0=Datum(name='Bessel1841', ", known=startswith, nl=1)

        # R = RDNAP2018v1(name='Cover')
        self.test('str', R, "name='v", known=startswith,nl=1)
        t = R.forward(A0.LAT0, A0.LON0)
        self.test('lat', t.lat, A0.LAT0, prec=8)
        self.test('lon', t.lon, A0.LON0, prec=8)
        self.test('latlon', t.latlon, '(52.156161, 5.387639)')
        self.test('latlonheight', t.latlonheight, '(52.156161, 5.387639, 0)')
        self.test('latlonheightdatum', t.latlonheightdatum, '(52.156161, 5.387639, 0, Datum', known=startswith)
        self.test('lam', t.lam, A0.LAM0, prec=8)
        self.test('phi', t.phi, A0.PHI0, prec=8)
        self.test('philam', t.philam, '(0.910297, 0.094032)')
        self.test('philamheight', t.philamheight, '(0.910297, 0.094032, 0)')
        self.test('philamheightdatum', t.philamheightdatum, '(0.910297, 0.094032, 0, Datum', known=startswith, nt=1)

        try:
            r = R.rdNAPh(0, 0)  # raiser=True
            self.test('rdNAPh', r, NAN)  # RDNAPError
        except RDNAPError as r:
            r = repr(r)
            self.test('rdNAPh', r, NAN)

        r = t.toETRS().toRepr()
        self.test('toETRS', r, t.toRepr(), nl=1)
        r = t.toRD()
        s = r.toRepr()
        self.test('toRD', s, s)
        r = t.toDatum(r.datum).toRepr()
        self.test('toDatum', r, r, nt=1)

        r = R.region4()
        t = r.toRepr()
        self.test('region4', t, 'RD region (latS=50.0, lonW=2.0, latN=56.0, lonE=8.0)')
        self.test('lowerleft', R.isinside(r.latS, r.lonW), True)
        self.test('upperight', R.isinside(r.latN, r.lonE), True)
        self.test('center',    R.isinside(r.latC, r.lonC), True)
        self.test('origin',    R.isinside(0, 0), False)

        r = R.region4(asRD=True)
        t = r.toRepr()
        self.test('region4RD', t, 'RD region (minRDx=-82454.183, minRDy=345614.643, ', known=startswith)
        t = R.reverse(r.minRDx, r.minRDy, None)
        self.test('lowerleft', R.isinside(t.lat, t.lon), True)
        self.test('lowerleft', R.isinsideRD(r.minRDx, r.minRDy), True)
        t = R.reverse(r.maxRDx, r.maxRDy, None)
        self.test('upperight', R.isinside(t.lat, t.lon), True)
        self.test('upperight', R.isinsideRD(r.maxRDx, r.maxRDy), True)
        self.test('origin',    R.isinside(0, 0), False)

        for t in (R.forward(NAN, NAN),
                  R.reverse(NAN, NAN)):
            self.test('lat', t.lat, NAN, prec=8, nl=1)
            self.test('lon', t.lon, NAN, prec=8)
            self.test('latlon', t.latlon, '(NAN, NAN)')
            self.test('latlonheight', t.latlonheight, '(NAN, NAN, ', known=startswith)
            self.test('latlonheightdatum', t.latlonheightdatum, '(NAN, NAN, ', known=startswith)
            self.test('lam', t.lam, NAN, prec=8)
            self.test('phi', t.phi, NAN, prec=8)
            self.test('philam', t.philam, '(NAN, NAN)')
            self.test('philamheight', t.philamheight, '(NAN, NAN, ', known=startswith)
            self.test('philamheightdatum', t.philamheightdatum, '(NAN, NAN, ', known=startswith, nt=1)

    def testRD11(self, R):  # <https://NL.WikiPedia.org/wiki/Rijksdriehoekscoördinaten>
        t = repr(R)
        self.test('RD11', t, 'RDNAP2018', known=startswith, nl=1)
        for x, y, lat, lon in (  # RDx     RDy         lat           lon        # near
                               (141000, 629000, "53 38 48.2N", "5 10 31.9E"),   # 30 km N  Terschelling
                               (100000, 600000, "53 23  0.6N", "4 33 38.4E"),   # 30 km  W Terschelling
                               ( 80000, 500000, "52 28 57.3N", "4 16 59.2E"),   # 20 km  W IJmuiden
                               ( -7000, 392000, "51 29 37.3N", "3  3 15.1E"),   # 20 km  W Westkapelle
                               ( -7000, 336000, "50 59 26.4N", "3  4 46.8E"),   # 10 km NE Roeselare
                               (101000, 336000, "51  0 39.9N", "4 37  3.9E"),   # 25 km NE Brussel
                               (161000, 289000, "50 35 28.1N", "5 28 18.9E"),   # 10 km SW Luik
                               (219000, 289000, "50 35 15.4N", "6 17 27.1E"),   # 25 km SE Aken
                               (300000, 451000, "52  1 42.1N", "7 30  0.8E"),   # 10 km NW Münster
                               (300000, 614000, "53 29 32.4N", "7 34 19.3E"),   # 05 km NE Aurich
                               (259000, 629000, "53 38 12.0N", "6 57 34.1E")):  # 05 km Z  Juist
            r = RDNAP7Tuple(x, y, NAN, lat, lon, NAN, None).toUnits()
            t = R.forward(lat, lon, NAN).dup(datum=None)  # ignore datum
            self.test('forward', t, r, known=fabs(t.RDx - r.RDx) < 1.0 and
                                             fabs(t.RDy - r.RDy) < 1.5)
            t = R.reverse(x, y, NAN).dup(datum=None)  # ignore datum
            self.test('reverse', t, r, known=fabs(t.lat - r.lat) < 0.0012 and
                                             fabs(t.lon - r.lon) < 0.0008)

    def testRndTrip(self, R, lat, lon, h=NAN, RDx_RDy=None):
        llh = lat, lon, h
        t =  R.forward(*llh)
        s = _str(t)  # partial
        self.test('forward', s, s)
        if RDx_RDy:
            self.test('RDx_RDy', _str(t.xy), RDx_RDy, known=True)
            s = t.toStr()
            self.test('b4Datum', s, s)
            s = t.toDatum(Datums.NAD83).toStr()
            self.test('toWGS84', s, s)

        r =  R.reverse(*t.xyz)
        s = _str(r)
        self.test('reverse', s, s)

        t = _rnd(r.lat), _rnd(r.lon)
        if h is not NAN:
            t += (_rnd(r.height) or 0.0),
        d = max(fabs(f - r) for f, r in zip(llh, t))
        k = d < 0.002
        self.test(R.name, t, llh, known=k, error=d)

        t = R.forward3(lat, lon)
        r = R.reverse3(t.lat, t.lon)
        t = _rnd(lat),   _rnd(lon)
        r = _rnd(r.lat), _rnd(r.lon)
        self.test('x3', t, r, nt=1)

    def testSAS(self, R):
        # <https://GitHub.com/FVellinga/gm_rdnaptrans2018/blob/main/gm_rdnaptrans2018.sas>
        self.test(R.name, 'SAS', 'SAS')
        self.testRndTrip(R, 53.19939233, 6.05939747,
                            RDx_RDy='(199920.042533, 579403.423305)')


if __name__ == '__main__':

    t = Tests(__file__, __version__)
    R1 = RDNAP2018v1(name='v1')
    R2 = RDNAP2018v2(name='v2')

    t.testRandom(R1)
    t.testRandom(R2)

    t.testAmersfoort(R1)
    t.testAmersfoort(R2)

    t.testEPSG(R1)
    t.testSAS(R1)

    t.testLqRD()

    t.testRD11(R1)
    t.testRD11(R2)

    t.testRDs(R1)
    t.testRDs(R2)

    t.test('ndigits', _ndigits, _ndigits)
    t.results()
    t.exit()
