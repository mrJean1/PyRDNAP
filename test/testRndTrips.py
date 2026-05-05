
# -*- coding: utf-8 -*-

# Test L{PyRDNAP} with round-trips of random lat-/longitudes inside.

from bases import TestsBase, NAN

from pyrdnap import RDNAP2018v1, RDNAP2018v2
# from pyrdnap.rdnap2018 import _RD0 as A0

from random import random, seed
from time import localtime

__all__ = ()
__version__ = '26.05.02'

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
        lat0, lon0 = 52.15616056, 5.38763889
        self.testRndTrip(R, lat0, lon0,   0.0)     # (A0.X0, A0.Y0, 0.0)
        self.testRndTrip(R, lat0, lon0,  43.2551)  # (A0.X0, A0.Y0, 0.0)
        self.testRndTrip(R, lat0, lon0, 143.2551)  # (A0.X0, A0.Y0, 100.0)

    def testEPSG(self, R):
        # <https://EPSG.io/9809-method> Example
        self.test(R.name, 'EPSG:9809', 'EPSG:9809', nl=1)
        self.testRndTrip(R, 53.0, 6.0,
                            RDx_RDy='(196105.283, 557057.739)')

    def testRandom(self, R, **nl):
        S, W, N, E = R.region
        E_W = E - W
        N_S = N - S
        r   = random.__name__
        self.test(R.name, r, r, **nl)
        for _ in range(_nrandom):
            self.testRndTrip(R, _rnd(random() * N_S + S),
                                _rnd(random() * E_W + W))

    def testRndTrip(self, R, lat, lon, h=NAN, RDx_RDy=None):
        llh = lat, lon, h
        t =  R.forward(*llh)
        s = _str(t)  # partial
        self.test('forward', s, s)
        if RDx_RDy:
            self.test('RDx_RDy', _str(t.xy), RDx_RDy, known=True)

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
        self.test(R.name, 'SAS', 'SAS', nl=1)
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

    t.test('ndigits', _ndigits, _ndigits)
    t.results()
    t.exit()
