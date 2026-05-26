
# -*- coding: utf-8 -*-

# Test L{PyRDNAP} with round-trips of random lat-/longitudes inside.

from bases import TestsBase, Datums, NAN, startswith

from pyrdnap import LqRD, RDNAP2018v1, RDNAP2018v2
from pyrdnap.rd0 import _RD, _RD0 as A0

from random import random, seed
from time import localtime

__all__ = ()
__version__ = '26.05.24'

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
        S, W, N, E = r = R.region
        self.test('region', r, r)
        for llh in ((A0.LAT0, A0.LON0, A0.H0),
                    (r.latC, r.lonC, 0),
                    (N, E, 0), (N, W, 0), (S, E, 0), (S, W, 0)):
            t = R.forward(*llh)
            self.test('rdnap', t, t, nl=1)
            r = LqRD().forward(*t.latlonheight)
            self.test(' lqrd', r, r)
            z = r.diff(t)
            self.test(' diff', z, z)

    def testRandom(self, R, **nl):
        S, W, N, E = R.region
        E_W = E - W
        N_S = N - S
        r   = random.__name__
        self.test(R.name, r, r, **nl)
        for _ in range(_nrandom):
            self.testRndTrip(R, _rnd(random() * N_S + S),
                                _rnd(random() * E_W + W))

    def testRDs(self):
        self.test('_RD', _RD.toStr(), '_xETRS2RD=Similarity(name=', known=startswith, nl=1)
        self.test('_RD0', A0.toStr(), "D0=Datum(name='Bessel1841', ", known=startswith, nl=1)

        R = RDNAP2018v1(name='Cover')
        self.test('v1', R, "name='Cover'", known=startswith,nl=1)
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
        self.test('philamheightdatum', t.philamheightdatum, '(0.910297, 0.094032, 0, Datum', known=startswith)

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

        t = _rnd(r.lat), _rnd(r.lon), (_rnd(r.height) or 0.0)
        if h is NAN:
            llh, t = llh[:2], t[:2]
        k = _str(t, 2) == _str(llh, 2)
        self.test(R.name, t, llh, known=k, nt=1)

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

    t.testRDs()  # coverage
    t.test('ndigits', _ndigits, _ndigits)
    t.results()
    t.exit()
