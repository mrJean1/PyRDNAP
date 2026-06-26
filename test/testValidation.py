
# -*- coding: utf-8 -*-

# Test L{PyRDNAP} with the offical self-validation tests.  Both RDNAP2018 variants are
# tested the final RDNAP... lines show the max |diff| and the required |diff| for variant
# 1.  See function L{pyrdnap.validation3<pyrdnap.v_self.validation3>} for more details.
#
# Note, variant 1 passes, but variant 2 fails partially as validated.

from bases import _ELLIPSIS_, _getenv, NN, PyRDNAP_dir, _SPACE_, TestsBase

from pyrdnap import RDNAP2018v1, RDNAP2018v2, validation3

import os.path as os_path

__all__ = ()
__version__ = '26.06.26'

_PyRDNAP_up1 =  os_path.dirname(PyRDNAP_dir)  # or _ELLIPSIS_
_v1_max_diff = 'RDNAP2018v1 max |diff| lat 0.00000000247, lon 0.00000000187, height 0.000050, RDx 0.00008785, RDy 0.00022281, NAPh 0.00004999'
_v2_max_diff = 'RDNAP2018v2 max |diff| lat 0.00119963344, lon 0.00082945486, height 0.000637, RDx 0.00829877, RDy 0.01574313, NAPh 0.00063739'
# _v1_ETRS89 = 'forward max |diff| (RDx 0, RDy 0, NAPh 0, lat 6.99816e-09, lon 4.75236e-09, height 4.12274e-09, ...)'
# _v1_RDNAP  = 'reverse max |diff| (RDx 0.000223603, RDy 0.000799715, NAPh 5.68434e-14, lat 0, lon 0, height 0, ...)'


def _str(failed, total=47754, inside=7959):
    return '%s failed, %s total, %s inside' % (failed, total, inside)


class Tests(TestsBase):

    def testValidation(self, R, v_txt, max_diff, failed=0, **nl):

        self.last_line = None

        def _p(*args):
            p = self.last_line
            if p:
                self.test(R.name, p, p)
            # defer printing each line
            t = _SPACE_(*args)
            self.last_line = t.replace(_PyRDNAP_up1, _ELLIPSIS_)

        t = validation3.__name__
        self.test(R.name, t, t, **nl)
        # note, inside the C{RD} region only!
        t = validation3(v_txt, R, in_out=True, _print=_p, _printest=None)
        self.test(R.name, self.last_line, max_diff)
        self.test(R.name, _str(*t), _str(failed))


if __name__ == '__main__':

    t =  Tests(__file__, __version__)
    s =  47754  # total tests
    p = 'PYRDNAP_SELF_VALIDATION'  # path to .../Z001_ETRS89andRDNAP.txt
    v = _getenv(p, NN)
    if v:
        p = os_path.abspath(os_path.join(*v.split('/')))
        if os_path.exists(p):
            t.testValidation(RDNAP2018v2(name='v2'), p, _v2_max_diff, 356)
            t.testValidation(RDNAP2018v1(name='v1'), p, _v1_max_diff, nl=1)
            s = 0
        else:
            p = repr(p)
#           v = 'A0 52.15616  5.387639  0        155029.784672 463109.826226 -43.275509\n' + \
#               'B0 52.155173 5.387204 43.277164 155000        463000          0\n'
    if s:
        t.test('missing', p, p)
        t.skip(n=s)
    t.results()
    t.exit()

# % python3.14 test/testValidation.py
#
#     testing testValidation.py 26.06.26
#     test 1 v2: validation3
#     test 2 v2: testing RDNAP2018v2(name='v2', variant=2, forwardDatum=Datum(name='GRS80', ellipsoid=Ellipsoids.GRS80, transform=Transforms.WGS84))
#     test 3 v2:   using '.../RDNAPTRANStm2018_NSGI_txts/Z001_ETRS89andRDNAP.txt'
#     test 4 v2:  header 'point_id\tETRS89_lat. \tETRS89_lon.\tETRS89_h  \tRD_x       \tRD_y       \tNAP_H'  (line 1)
#
#     test 5 v2: RDNAP2018v2 356 of 47754 tests FAILED for 89 of 7959 of 10000 points -inside (pyrdnap 26.6.26 pygeodesy 26.6.24 Python 3.14.5 64bit arm64 macOS 26.5.1) 485.843 ms
#     test 6 v2: RDNAP2018v2 req |diff| lat 0.00000001000, lon 0.00000001000, height 0.001000, RDx 0.00100000, RDy 0.00100000, NAPh 0.00100000
#     test 7 v2: RDNAP2018v2 max |diff| lat 1.1996334e-03, lon 8.2945486e-04, height 6.37e-04, RDx 8.2988e-03, RDy 1.5743e-02, NAPh 6.3739e-04
#     test 8 v2: RDNAP2018v2 max |diff| lat 0.00119963344, lon 0.00082945486, height 0.000637, RDx 0.00829877, RDy 0.01574313, NAPh 0.00063739
#     test 9 v2: 356 failed, 47754 total, 7959 inside
#
#     test 10 v1: validation3
#     test 11 v1: testing RDNAP2018v1(name='v1', variant=1, forwardDatum=Datum(name='GRS80', ellipsoid=Ellipsoids.GRS80, transform=Transforms.WGS84))
#     test 12 v1:   using '.../RDNAPTRANStm2018_NSGI_txts/Z001_ETRS89andRDNAP.txt'
#     test 13 v1:  header 'point_id\tETRS89_lat. \tETRS89_lon.\tETRS89_h  \tRD_x       \tRD_y       \tNAP_H'  (line 1)
#
#     test 14 v1: RDNAP2018v1 all 47754 tests PASSED, 7959 of 10000 points -inside (pyrdnap 26.6.26 pygeodesy 26.6.24 Python 3.14.5 64bit arm64 macOS 26.5.1) 547.759 ms
#     test 15 v1: RDNAP2018v1 req |diff| lat 0.00000001000, lon 0.00000001000, height 0.001000, RDx 0.00100000, RDy 0.00100000, NAPh 0.00100000
#     test 16 v1: RDNAP2018v1 max |diff| lat 2.4685889e-09, lon 1.8726842e-09, height 5.00e-05, RDx 8.7847e-05, RDy 2.2281e-04, NAPh 4.9993e-05
#     test 17 v1: RDNAP2018v1 max |diff| lat 0.00000000247, lon 0.00000000187, height 0.000050, RDx 0.00008785, RDy 0.00022281, NAPh 0.00004999
#     test 18 v1: 0 failed, 47754 total, 7959 inside
#
#     all 18 testValidation.py tests passed (pyrdnap 26.6.26 pygeodesy 26.6.24 Python 3.14.5 64bit arm64 macOS 26.5.1) 1.034 sec
