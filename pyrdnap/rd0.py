
# -*- coding: utf-8 -*-

u'''(INTERNAL) C{RD} and C{RD0} constants and C{RDNAP7Tuple} and C{RDregion} classes.
'''
# make sure int/int division yields float quotient, see .basics
from __future__ import division as _; del _  # noqa: E702 ;

from pyrdnap.v_grids import _v_assert
from pyrdnap.__pygeodesy import (_0_0, _0_5, _1_0, _2_0,  # PYCHOK used!
                                 _isNAN, _xinstanceof, _xsubclassof,
                                 _LLEB, _xkwds,
                                 _COMMASPACE_, _datum_, _E_, _lat_, _lon_,
                                 _height_, _N_, _S_, _UNDER_, _W_,
                                 _ALL_OTHER, _Pass, _NamedTuple)
from pygeodesy import (NN, PI_2,  # "consterns"
                       Datum, Datums, Similarity,  # datums
                       LatLon2Tuple, Vector2Tuple, Vector3Tuple,  # namedTuples
                       Property_RO, property_ROnce,  # props
                       pairs,  # streprs
                       Height, Lamd, Lat, Lon, Meter, Phi, Phid,  # units
                       sincos2)  # utily

from math import atan, ceil, floor, log, sin, sqrt, tan

__all__ = ()
__version__ = '26.05.06'


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
    '''(INTERNAL) Limits, constants for RDNAP2018 (ASCII.txt).
    '''
    LAT_INC   = Lat(LAT_INC=0.0125)
    LAT_MAX   = Lat(LAT_MAX=56.0)  # degrees
    LAT_MIN   = Lat(LAT_MIN=50.0)
    LON_INC   = Lon(LON_INC=0.02)
    LON_MAX   = Lon(LON_MAX= 8.0)   # degrees
    LON_MIN   = Lon(LON_MIN=_2_0)
    N_LAT_LON = ((LAT_MAX - LAT_MIN) / LAT_INC + _1_0,  # 2.3.2g n-phi
                 (LON_MAX - LON_MIN) / LON_INC + _1_0)  # 2.3.2g n-lambda

    def __init__(self):
        _v_assert(tuple(map(int, self.N_LAT_LON)))

    def c_f_N_f6(self, lat, lon):
        # return (int(ceil), int(floor), C{lat}-Normalized less floor) + \
        #        (int(ceil), int(floor), C{lon}-Normalized less floor)
        return _c_f_N_f3(lat, self.LAT_MIN, self.LAT_INC) + \
               _c_f_N_f3(lon, self.LON_MIN, self.LON_INC)

    def isinside(self, lat, lon, eps=0):  # eps=_TOL_D, 0 or -_TOLD_D
        # is C{(lat, lon)} inside the this C{RD} region, optionally
        # over-/undersized by positive resp. negative C{eps}?
        S, W, N, E = self.region
        return ((S - lat) <= eps and (lat - N) <= eps and
                (W - lon) <= eps and (lon - E) <= eps) if eps else \
                (S <= lat <= N   and  W <= lon <= E)

    @property_ROnce
    def region(self):
        t = RDregion4Tuple(self.LAT_MIN, self.LON_MIN,
                           self.LAT_MAX, self.LON_MAX, name='RD region ')
        assert t.S < t.N and t.W < t.E, t.name
        return t

    def _toDict(self):
        def _p(n):  # lambda
            return n.replace(_UNDER_, NN).isupper()

        return self._preDict(_p, _xETRS2RD=self._xETRS2RD,
                                 _xRD2ETRS=self._xRD2ETRS)

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
    # LAT_INC=0.0125, LAT_MAX=56.0, LAT_MIN=50.0, LON_INC=0.02, LON_MAX=8.0, LON_MIN=2.0,
    # N_LAT_LON=(481.0, 301.0)

_RD = _RD()  # PYCHOK singleton


class _RD0(_RDbase):
    '''(INTERNAL) C{RD} Amersfoort, NL references.

       @see: U{EPSG:9809<https://EPSG.io/9809-method>}, U{"Oblique Stereographic"
             <https://PROJ.org/en/stable/operations/projections/sterea.html>} and
             <http://geotiff.maptools.org/proj_list/oblique_stereographic.html>
    '''
    H0      = Meter(H0=_0_0)  # E0 height in meter
    H0_ETRS = Meter(H0_ETRS=43.0)
    K0      = 0.9999079  # scale factor
    LAT0    = Lat(LAT0='52  9 22.178N')  # 52.15616055+°
    LON0    = Lon(LON0=' 5 23 15.5E')    # 5.387638888+°
    LAM0C   = \
    LAM0    = Lamd(LAM0=LON0)  # 𝜆0, 𝛬0 = 𝜆0 on sphere 0.094032038
    PHI0    = Phid(PHI0=LAT0)  # 𝜑0 0.910296727, 𝛷0 below
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
    def E0(self):  # lazily
        return self.D0.ellipsoid

    def ln_e_2(self, phi):
        e = self.E0.e
        p = e * sin(phi)
        return log((_1_0 + p) / (_1_0 - p)) * (e * _0_5)

    def ln_tan(self, phi):
        return log(tan((phi + PI_2) * _0_5))

    @property_ROnce
    def M0(self):  # 2.4.1+ m
        q0 = self.ln_tan(self.PHI0) - self.ln_e_2(self.PHI0)
        w0 = self.ln_tan(self.PHI0C)
        return w0 - self.N0 * q0

    @property_ROnce
    def N0(self):  # 2.4.1+ n, sphere
        E = self.E0
        _, c = self.sincos2PHI0
        return sqrt(_1_0 + c**4 * E.e2 / E.e21)

    @property_ROnce
    def PHI0C(self):  # 2.4.1+
        # get 𝛷0, Amersfoort latitude on sphere
        rM, rN = self._rMN2
        return Phi(PHI0C=atan((sqrt(rM) / sqrt(rN)) * tan(self.PHI0)))

    @property_ROnce
    def R(self):  # radius conformal sphere
        rM, rN = self._rMN2
        return sqrt(rM * rN)

    @property_ROnce
    def RK2(self):  # 2.4.1+
        return self.R * self.K0 * _2_0

    @property_ROnce
    def _rMN2(self):  # 2.4.1+
        # get 2-tuple (RHO0, NU0) EPSG:9809
        E  =  self.E0
        s, _  = self.sincos2PHI0
        s  = _1_0 - s**2 * E.e2
        rN =  E.a / sqrt(s)
        rM =  E.e21 * rN / s
        return rM, rN

    @property_ROnce
    def sincos2PHI0(self):
        return sincos2(self.PHI0)

    @property_ROnce
    def sincos2PHI0C(self):
        return sincos2(self.PHI0C)

    def _toDict(self):
        def _p(n):  # lambda
            return n.endswith('0') or n.endswith('0C')  # _0_

        return self._preDict(_p, H0_ETRS=self.H0_ETRS, R=self.R,
                                 RK2=self.RK2, _rMN2=self._rMN2)

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
    # E0=Ellipsoid(name='Bessel1841', a=6377397.155, f=0.00334277, f_=299.1528128, b=6356078.962818),
    # H0=0.0, H0_ETRS=43.0, K0=0.9999079, LAM0=0.094032038, LAM0C=0.094032038, LAT0=52.156160556, LON0=5.387638889,
    # M0=0.003773954, N0=1.000475857, PHI0=0.910296727, PHI0C=0.909684757, R=6382644.571035412, RK2=12764113.458940839,
    # sincos2PHI0=(0.7896858198001045, 0.6135114554811807), sincos2PHI0C=(0.7893102212553742, 0.6139946047171687),
    # X0=155000.0, Y0=463000.0, _rMN2=(6374588.709792872, 6390710.612840701)

_RD0 = _RD0()  # PYCHOK singleton, in .test


class RDNAP7Tuple(_NamedTuple):
    '''7-Tuple C{(RDx, RDy, NAPh, lat, lon, height, datum)} with I{local} C{RDx},
       C{RDy} and C{NAPh} quasi-geoid_height, geodetic C{lat}, C{lon}, C{height}
       and C{datum} with C{lat} and C{lon} in C{degrees} and C{RDx}, C{RDy}, C{NAPh}
       and C{height} in C{meter}, conventionally.

       @note: The C{lat} and {lon} are geodetic B{GRS80 (ETRS89)} coordinates from
              L{RDNAP2018v1.reverse} but B{Bessel1841 (RD-Bessel)} when returned from
              L{RDNAP2018v2.reverse}.
    '''
    _Names_ = ('RDx', 'RDy', 'NAPh', _lat_, _lon_, _height_, _datum_)
    _Units_ = ( Meter, Meter, Meter,  Lat,   Lon,   Height,  _Pass)

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

    def toDatum(self, datum2, **name):
        '''Convert this C{lat}, C{lon} and C{height} to B{C{datum2}}.

           @arg datum2: Datum to convert I{to} (L{Datum}).

           @return: An L{RDNAP7Tuple} with converted C{lat}, C{lon} and C{height}.
        '''
        _xinstanceof(Datum, datum2=datum2)
        h = self.height  # PYCHOK preserve height NAN, because Ecef._forward ...
        g = self.toLatLon(_LLEB).toDatum(datum2)  # ... treats height NAN as 0
        return self.dup(lat=g.lat, lon=g.lon, datum=g.datum,
                        height=h if _isNAN(h) else g.height, **name)

    def toLatLon(self, LatLon, **LatLon_kwds):
        '''Return this C{lat}, C{lon}, C{datum} and C{height} as B{C{LatLon}}.

           @arg LatLon: An ellipsodial C{LatLon} class (C{pygeodesy.ellipsoidal*}).
           @kwarg LatLon_kwds: Optional, additional B{C{LatLon}} keyword arguments.

           @return: An B{C{LatLon}} instance.

           @raise TypeError: B{C{LatLon}} not ellipsoidal or an other issue.
        '''
        _xsubclassof(_LLEB, LatLon=LatLon)
        h = self.height  # PYCHOK treat height NAN as 0, like Ecef._forward
        kwds = _xkwds(LatLon_kwds, name=self.name, height=_0_0 if _isNAN(h) else h)
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


class RDregion4Tuple(_NamedTuple):
    '''4-Tuple C{(S, W, N, E)} with C{RD} region in C{GRS80 (ETRS89) degrees}.
    '''
    _Names_ = (_S_, _W_, _N_, _E_)
    _Units_ = ( Lat, Lon, Lat, Lon)

    @Property_RO
    def SW(self):
        '''Get the C{SW} corner as (L{LatLon2Tuple}C{(lat, lon)}).
        '''
        return LatLon2Tuple(self.S, self.W, name=self.name)

    @Property_RO
    def NE(self):
        '''Get the C{NE} corner as (L{LatLon2Tuple}C{(lat, lon)}).
        '''
        return LatLon2Tuple(self.N, self.E, name=self.name)


def _c_f_N_f3(d, d_MIN, d_INC):
    # return int(ceil), int(floor) and (Normalized less floor) of C{d} degrees
    N = (d - d_MIN) / d_INC
    f = floor(N)
    return int(ceil(N)), int(f), (N - f)


__all__ += _ALL_OTHER(RDNAP7Tuple, RDregion4Tuple,
                      # passed along from PyGeodesy
                      LatLon2Tuple, Similarity, Vector2Tuple, Vector3Tuple)

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
