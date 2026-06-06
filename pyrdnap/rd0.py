
# -*- coding: utf-8 -*-

u'''(INTERNAL) RijksDriehoeksmeting C{_RD} and reference C{_RD0}
constants and classes C{RDNAP7Tuple} and C{LqRD}.
'''
# make sure int/int division yields float quotient, see .basics
from __future__ import division as _; del _  # noqa: E702 ;

from pyrdnap.v_grids import _v_assert
from pyrdnap.__pygeodesy import (_0_0, _0_5, _1_0, _2_0,  # PYCHOK used!
                                 _isNAN, _isNAN0, _xinstanceof, _xsubclassof,
                                 _LLEB, _xkwds,
                                 _COMMASPACE_, _datum_, _lat_, _lon_, _height_,
                                 _ALL_OTHER, _FOR_DOCS, _Pass, _NamedTuple)
from pygeodesy import (NAN, NN, map1, map2,  # basics, "consterns"
                       Datum, Datums, Similarity,  # datums
                       Bounds4Tuple, LatLon2Tuple, PhiLam2Tuple,  # namedTuples
                       Vector2Tuple, Vector3Tuple, LqRD as _LqRD,  # ltp
                       Property_RO, property_ROnce,  # props
                       pairs,  # streprs
                       Height, Lamd, Lat, Lon, Meter, Phi, Phid,  # units
                       sincos2, tanPI_2_2)  # utily

from math import atan2, ceil, fabs, floor, log, sin, sqrt

__all__ = ()
__version__ = '26.06.06'

_LQRD = _LqRD()  # get Amersfoort, bounds, etc. (deleted below)


def _c_f_N_f3(*deg_SW_D):
    # return int(ceil) and int(floor) of Normalized
    # and (Normalized less floor) of C{deg} degrees
    N = _degN(*deg_SW_D)
    # assert N >= 0, N
    f =  floor(N)
    return int(ceil(N)), int(f), (N - f)


def _degN(deg, degSW, deg_D):
    # return C{deg} Normalized
    return (deg - degSW) * deg_D


class _RDbase(object):
    '''(INTERNAL) Base.
    '''
    def _preDict(self, _pred, **d):
        # return updated dict C{d}
        for n in self.__class__.__dict__.keys():
            if _pred(n):
                d[n] = getattr(self, n)
        return d

    def toStr(self, prec=9, **fmt_ints):
        # return this C{_RDx} as string
        d = self._toDict()  # PYCHOK OK
        t = pairs(d, prec=prec, **fmt_ints)
        return _COMMASPACE_(*t)


class _RD(_RDbase):
    '''(INTERNAL) Bounds, constants for RDNAP2018 (ASCII.txt).
    '''
    lat_D = Lat(lat_D=80.0)  # == 1 / 0.0125  # degrees, all
    lon_D = Lon(lon_D=50.0)  # == 1 / 0.02

    def __init__(self):
        S, W, N, E = self.region
        nlat = _degN(N, S, self.lat_D) + _1_0  # 2.3.2g n-phi
        nlon = _degN(E, W, self.lon_D) + _1_0  # 2.3.2g n-lambda
        _v_assert(map1(int, nlat, nlon))

    def _c_f_N_f6(self, lat, lon):
        # return (int(ceil), int(floor), Normalized less floor) of C{lat}) + \
        #        (int(ceil), int(floor), Normalized less floor) of C{lon})
        return _c_f_N_f3(lat, self.region.latS, self.lat_D) + \
               _c_f_N_f3(lon, self.region.lonW, self.lon_D)

    def isinside(self, lat, lon, eps=0, B=False):  # eps=_TOL_D, 0 or -_TOLD_D
        # is C{(lat, lon)} inside the this C{RD} region[B], optionally
        # over-/undersized by positive respectively negative C{eps}?
        S, W, N, E = self.regionB if B else self.region
        # XXX use "< N" and "< E" instead of "<="?
        return ((S - lat) <= eps and (lat - N) <= eps and
                (W - lon) <= eps and (lon - E) <= eps) if eps else \
                (S <= lat <= N   and  W <= lon <= E)

    region = _LQRD.region  # as GRS80 L{Bounds4Tuple}

    @property_ROnce
    def regionB(self):  # as Bessel1841 L{Bounds4Tuple}
        from pyrdnap.rdnap2018 import _RDNAPbase as _R
        return _R().regionB

    def _toDict(self):
        def _p(n):  # lambda
            return n.endswith('D') or n.endswith('S')

        return self._preDict(_p, region=self.region, regionB=self.regionB)

    @property_ROnce
    def _xETRS2RD(self):  # transform ETRS (GRS80) to RD-Bessel
        return Similarity(tx=-565.7346, ty=-50.4058, tz=-465.2895, s=-4.07242,
                          rx=-1.91513,  ry=1.60365,  rz=-9.09546, name='_xETRS2RD')

    @property_ROnce
    def _xRD2ETRS(self):  # transform RD-Bessel to ETRS (GRS80)
        return Similarity(tx=565.7381, ty=50.4018,  tz=465.2904, s=4.07244,
                          rx=1.91514,  ry=-1.60363, rz=9.09546, name='_xRD2ETRS')

    # % python -c "import pyrdnap; print(pyrdnap.rd0._RD.toStr())"
    # _xETRS2RD=Similarity(name='_xETRS2RD', tx=-565.73, ty=-50.406, tz=-465.29, s=-4.0724,
    #                                        rx=-1.9151, ry=1.6037, rz=-9.0955),
    # _xRD2ETRS=Similarity(name='_xRD2ETRS', tx=565.74, ty=50.402, tz=465.29, s=4.0724,
    #                                        rx=1.9151, ry=-1.6036, rz=9.0955),
    # lat_D=80.0, lon_D=50.0,
    # region=RD region (latS=50.0, lonW=2.0, latN=56.0, lonE=8.0),
    # regionB=RD regionB (latS=50.000724, lonW=1.999968, latN=56.001439, lonE=8.000842)

_RD = _RD()  # PYCHOK singleton, in .test/testRndTrips


class _RD0(_RDbase):
    '''(INTERNAL) C{RD} Amersfoort, NL / C{RD New} constants for RDNAP2018 (ASCII.txt).

       @see: U{EPSG:9809<https://EPSG.io/9809-method>}, U{"Oblique Stereographic"
             <https://PROJ.org/en/stable/operations/projections/sterea.html>} and
             <http://geotiff.maptools.org/proj_list/oblique_stereographic.html>
    '''
    H0      = Meter(H0     =_LQRD.height0)  # Amersfoort.height0 0.0 m
    H0_ETRS = Meter(H0_ETRS=_LQRD.height0_ETRS)  # 43.0 m
    K0      = 0.9999079  # 2.4.1 scale factor
    LAT0    = Lat(LAT0=_LQRD.Amersfoort.lat)  # '52  9 22.178N' == 52.156160555555+°
    LON0    = Lon(LON0=_LQRD.Amersfoort.lon)  # ' 5 23 15.5E'   ==  5.387638888888+°
    LAM0C   = \
    LAM0    = Lamd(LAM0=LON0)  # 𝜆0, 𝛬0 = 𝜆0 on sphere 0.094032038
    PHI0    = Phid(PHI0=LAT0)  # 𝜑0 0.910296727, PHI0C 𝛷0 set below
    X0      = Meter(X0=155000.0)  # false Easting  155029.784?
    Y0      = Meter(Y0=463000.0)  # false Norting  463109.889?

#   @property_ROnce
#   def C0(self):  # c, sphere
#       s, _ = self.sincos2PHI0
#       w = self._w1(s)
#       c = (w - _1_0) / (w + _1_0)
#       return (((self.N0 + s) * (_1_0 - c)) /
#               ((self.N0 - s) * (_1_0 + c)))

#   def chilam(self, lat, lon):  # EPSG:9809
#       # return 2-tuple (chi, lam), conformal in radians
#       s, _ = sincos2d(lat)
#       w2 = self._w1(s) * self.C0
#       s  = (w2 - _1_0) / (w2 + _1_0)
#       r  = radians(lon - self.LON0) * self.N0
#       return asin(s), r

    @property_ROnce
    def D0(self):  # lazily
        return Datums.Bessel1841

    @property_ROnce
    def D80(self):  # lazily
        return Datums.GRS80

    @property_ROnce
    def E0(self):  # lazily
        return self.D0.ellipsoid

    def log_e_2(self, phi):
        e = self.E0.e
        p = e * sin(phi)
        return log((_1_0 + p) / (_1_0 - p)) * (e * _0_5)

    def log_tan(self, phi):
        return log(tanPI_2_2(phi))  # tan((phi + PI/2) / 2)

    @property_ROnce
    def M0(self):  # 2.4.1 p 15 m
        return self.W0 - self.N0 * self.Q0

    @property_ROnce
    def N0(self):  # 2.4.1 p 15 n, sphere
        E = self.E0
        _, c = self.sincos2PHI0
        return sqrt(c**4 * E.e2 / E.e21 + _1_0)

    @property_ROnce
    def PHI0C(self):  # 2.4.1 p 15 𝛷0
        # get 𝛷0, Amersfoort latitude on sphere
        m, n = self.Rmn2
        s, c = self.sincos2PHI0
        return Phi(PHI0C=atan2(m * s, n * c))  # atan((m / n) * tan(PHI0))

    @property_ROnce
    def Q0(self):  # 2.4.1 p 15 q0
        return self.log_tan(self.PHI0) - self.log_e_2(self.PHI0)

    @property_ROnce
    def R(self):  # 2.4.1 p 15 R, radius conformal sphere
        m, n = self.Rmn2
        return m * n

    @property_ROnce
    def RK2(self):  # 2.4.2
        return self.R * self.K0 * _2_0

    @property_ROnce
    def Rmn2(self):  # 2.4.1 p 15 sqrt(RsubM), sqrt(RsubN)
        # get 2-tuple (RHO0, NU0) EPSG:9809
        E =  self.E0
        s, _ = self.sincos2PHI0
        s = _1_0 - s**2 * E.e2
        # assert s > 0
        N =  E.a / sqrt(s)
        # assert N > 0
        M =  E.e21 * N / s
        # assert M > 0
        return map1(sqrt, M, N)  # sqrt!

    @property_ROnce
    def sincos2PHI0(self):  # 𝜑0
        return sincos2(self.PHI0)

    @property_ROnce
    def sincos2PHI0C(self):  # 𝛷0
        return sincos2(self.PHI0C)

    def _toDict(self):
        def _p(n):  # lambda
            return n.endswith('0') or n.startswith('R') or \
                   n.endswith('0C')  # _0_

        return self._preDict(_p, H0_ETRS=self.H0_ETRS)

    @property_ROnce
    def W0(self):  # 2.4.1 p 15 w0
        return self.log_tan(self.PHI0C)  # 𝛷0

#   def _w1(self, sphi):  # EPSG:9809
#       w1 = NAN
#       if _1_0 > sphi > _N_1_0:
#           e  = self.E0.e
#           S  = (_1_0 + sphi)     / (_1_0 - sphi)
#           T  = (_1_0 - sphi * e) / (_1_0 + sphi * e)
#           w1 = pow(pow(T, e) * S, self.N0)
#       return w1

    # % python -c "import pyrdnap; print(pyrdnap.rd0._RD0.toStr())"
    # D0=Datum(name='Bessel1841', ellipsoid=Ellipsoids.Bessel1841, transform=Transforms.Bessel1841),
    # D80=Datum(name='GRS80', ellipsoid=Ellipsoids.GRS80, transform=Transforms.WGS84),
    # E0=Ellipsoid(name='Bessel1841', a=6377397.155, f=0.00334277, f_=299.1528128, b=6356078.962818),
    # H0=0.0, H0_ETRS=43.0, K0=0.9999079, LAM0=0.094032038, LAM0C=0.094032038,
    # LAT0=52.156160556, LON0=5.387638889, M0=0.003773954, N0=1.000475857,
    # PHI0=0.910296727, PHI0C=0.909684757, Q0=1.06531844,
    # R=6382644.571035411, RK2=12764113.458940838, Rmn2=(2524.794785679199, 2527.9854850929623),
    # sincos2PHI0=(0.7896858198001045, 0.6135114554811807),
    # sincos2PHI0C=(0.7893102212553742, 0.6139946047171686),
    # W0=1.069599332, X0=155000.0, Y0=463000.0

_RD0 = _RD0()  # PYCHOK singleton, in .test/testRndTrips


class RDNAP7Tuple(_NamedTuple):  # in .v_self
    '''7-Tuple C{(RDx, RDy, NAPh, lat, lon, height, datum)} with I{local} C{RDx},
       C{RDy} and C{NAPh} quasi-geoid_height, geodetic C{lat}, C{lon}, C{height}
       and C{datum} with C{lat} and C{lon} in C{degrees} and with C{RDx}, C{RDy},
       C{NAPh} and C{height} in C{meter}, conventionally.

       @note: The C{lat} and {lon} are I{by default}  B{GRS80 (ETRS89)} geodetic
              coordinates L{RDNAP2018v1.reverse} but B{Bessel1841 (RD-Bessel)}
              when returned from L{RDNAP2018v2.reverse}.
    '''
    _Names_ = ('RDx', 'RDy', 'NAPh', _lat_, _lon_, _height_, _datum_)
    _Units_ = ( Meter, Meter, Meter,  Lat,   Lon,   Height,  _Pass)

    @property_ROnce
    def _datum_index(self):
        return self._Names_.index(_datum_)

    def diff(self, other, datum=None, **name):
        '''Return the difference between this and an C{other} C{RDNAP7Tuple}.

           @kwarg datum: Optional difference C{B{datum}=None} (C{Latum}).
           @kwarg name: Optional name (C{str}).

           @return: An L{RDNAP7Tuple} with the C{_diff} for each item, but
                    C{datum=B{datum}}.
        '''
        def _diff(a, b):
            return fabs(a - b)

        _xinstanceof(RDNAP7Tuple, other=other)
        d = self._datum_index
        t = map2(_diff, self[:d], other[:d])
        return RDNAP7Tuple(t + (datum,), **name)

    @Property_RO
    def lam(self):
        '''Get the longitude (B{C{radians}}).
        '''
        return Lamd(self.lon)  # PYCHOK lon

    @Property_RO
    def latlon(self):
        '''Get the lat-, longitude in C{degrees} (L{LatLon2Tuple}C{(lat, lon)}).
        '''
        return LatLon2Tuple(self.lat, self.lon, name=self.name)

    @Property_RO
    def latlonheight(self):
        '''Get the lat-, longitude in C{degrees} and height (L{LatLon3Tuple}C{(lat, lon, height)}).
        '''
        return self.latlon.to3Tuple(self.height)

    @Property_RO
    def latlonheightdatum(self):
        '''Get the lat-, longitude in C{degrees} with height and datum (L{LatLon4Tuple}C{(lat, lon, height, datum)}).
        '''
        return self.latlonheight.to4Tuple(self.datum)

    @Property_RO
    def phi(self):
        '''Get the latitude (B{C{radians}}).
        '''
        return Phid(self.lat)  # PYCHOK lat

    @Property_RO
    def philam(self):
        '''Get the lat- and longitude in C{radians} (L{PhiLam2Tuple}C{(phi, lam)}).
        '''
        return PhiLam2Tuple(self.phi, self.lam, name=self.name)  # PYCHOK lam, phi

    @Property_RO
    def philamheight(self):
        '''Get the lat-, longitude in C{radians} and height (L{PhiLam3Tuple}C{(phi, lam, height)}).
        '''
        return self.philam.to3Tuple(self.height)  # PYCHOK height

    @Property_RO
    def philamheightdatum(self):
        '''Get the lat-, longitude in C{radians} with height and datum (L{PhiLamn4Tuple}C{(phi, lam, height, datum)}).
        '''
        return self.philamheight.to4Tuple(self.datum)

    def toDatum(self, datum2, **name):
        '''Convert this C{lat}, C{lon} and C{height} to B{C{datum2}}.

           @arg datum2: Datum to convert I{to} (L{Datum}).

           @return: An L{RDNAP7Tuple} with converted C{lat}, C{lon} and C{height}
                    or this L{RDNAP7Tuple} if this.datum is B{C{datum2}}.
        '''
        _xinstanceof(Datum, datum2=datum2)
        if self.datum is datum2:  # PYCHOK or self.datum == datum2
            return self
        g = self.toLatLon(_LLEB).toDatum(datum2)
        h = NAN if _isNAN(self.height) else g.height  # PYCHOK preserve height NAN
        return self.dup(lat=g.lat, lon=g.lon, datum=g.datum, height=h,
                                              **_xkwds(name, name=self.name))

    def toLatLon(self, LatLon, **LatLon_kwds):
        '''Return this C{lat}, C{lon}, C{datum} and C{height} as B{C{LatLon}}.

           @arg LatLon: An ellipsodial C{LatLon} class (C{pygeodesy.ellipsoidal*}).
           @kwarg LatLon_kwds: Optional, additional B{C{LatLon}} keyword arguments.

           @return: An B{C{LatLon}} instance.

           @raise TypeError: B{C{LatLon}} not ellipsoidal or an other issue.
        '''
        _xsubclassof(_LLEB, LatLon=LatLon)
        h    = _isNAN0(self.height)  # PYCHOK height
        kwds = _xkwds(LatLon_kwds, name=self.name, height=h)
        return LatLon(self.lat, self.lon, datum=self.datum, **kwds)  # PYCHOK datum

    @Property_RO
    def xy(self):
        '''Get the I{local} C{(RDx, RDy)} coordinates (L{Vector2Tuple}C{(x, y)}).
        '''
        return Vector2Tuple(self.RDx, self.RDy, name=self.name)

    @Property_RO
    def xyz(self):
        '''Get the I{local} C{(RDx, RDy, NAPh)} coordinates and height (L{Vector3Tuple}C{(x, y, z)}).
        '''
        return Vector3Tuple(self.RDx, self.RDy, self.NAPh, name=self.name)


class LqRD(_LqRD):
    '''Like U{pygeodesy.LqRD<https://mrJean1.GitHub.io/PyGeodesy/docs/pygeodesy.ltp.LqRD-class.html>}
       but with methods C{forward} and C{reverse} returning an L{RDNAP7Tuple} with C{NAPh} replaced
       by I{local} C{z}, the perpendicular distance to the local tangent plane (LTP).

       This C{quasi-RD} transformer B{does not} implement any U{RD NAP<https://www.NSGI.NL/
       coordinatenstelsels-en-transformaties/coordinatentransformaties/rdnap-etrs89-rdnaptrans>}
       specification and B{does not} provide I{Netherlands}' C{B{N}ormaal B{A}msterdams B{P}eil
       (NAP)} quasi-geodetic-height.
    '''
    if _FOR_DOCS:
        __init__ = _LqRD.__init__

    def forward(self, lat_latlonh, lon=None, height=0, **name):  # PYCHOK signature
        '''Convert I{geodetic} C{(lat, lon, height)} to I{local} C{quasi-RD (x, y, z)}.

           @arg lat_latlonh: C{Scalar} (geodetic) latitude (C{degrees}) or a I{local}
                             C{quasi-RD} L{RDNAP7Tuple}.
           @kwarg lon: C{Scalar} (geodetic) longitude (C{degrees}) iff B{C{lat_latlonh}}
                       is C{scalar}, ignored otherwise.
           @kwarg height: Optional height (C{meter}, conventionally) perpendicular to and
                          above (or below) the ellipsoid's surface, iff B{C{lat_latlonh}}
                          is C{scalar}, ignored otherwise.
           @kwarg name: Optional C{B{name}=NN} (C{str}).

           @return: An L{RDNAP7Tuple}C{(RDx, RDy, NAPh, lat, lon, height, datum)} with
                    C{NAPh} set to I{local} C{z}.

           @see: B{pygeodesy.LqRD.forward} for more information.
        '''
        t = _LqRD.forward(self, lat_latlonh, lon=lon, height=height)
        return LqRD._l9t2r7t(t, **name)

    def reverse(self, x_xyz, y=None, z=None, **name):  # PYCHOK signature
        '''Convert I{local} C{quasi-RD (x, y, z)} to I{geodetic} C{(lat, lon, height)}.

           @arg x_xyz: Local C{quasi-RD x} coordinate (C{scalar}) or a I{local}
                       C{quasi-RD} L{RDNAP7Tuple}.
           @kwarg y: Local C{quasi-RD y} coordinate (C{meter}) iff B{C{x_xyz}} is
                     C{scalar}, ignored otherwise.
           @kwarg z: Local C{z} coordinate (C{meter}) iff B{C{x_xyz}} is C{scalar},
                     ignored otherwise.
           @kwarg name: Optional C{B{name}=NN} (C{str}).

           @return: An L{RDNAP7Tuple}C{(RDx, RDy, NAPh, lat, lon, height, datum)}
                    with C{NAPh} set to I{local} B{C{z}}.

           @see: B{pygeodesy.LqRD.reverse} for more information.
        '''
        t = _LqRD.reverse(self, x_xyz, y=y, z=z)
        return LqRD._l9t2r7t(t, **name)

    @staticmethod
    def _l9t2r7t(t, name=NN, **unused):  # M=False
        return RDNAP7Tuple(t.x,   t.y,   t.z,  # NAPh = t.z
                           t.lat, t.lon, t.height, t.ecef.datum, name=name or t.name)


__all__ += _ALL_OTHER(LqRD, RDNAP7Tuple, Bounds4Tuple,  # passed along from PyGeodesy
                      Datums, LatLon2Tuple, PhiLam2Tuple, Similarity, Vector2Tuple, Vector3Tuple)
del _LQRD

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
