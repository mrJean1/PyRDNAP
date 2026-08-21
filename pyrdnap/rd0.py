
# -*- coding: utf-8 -*-

u'''(INTERNAL) RijksDriehoeksmeting C{_RD} and reference C{_RD0}
constants and classes C{RDNAP7Tuple} and C{LqRD}.
'''
# make sure int/int division yields float quotient in Py2
from __future__ import division as _; del _  # noqa: E702 ;

from pyrdnap.v_grids import _v_assert
from pyrdnap.__pygeodesy import (_0_5, _1_0,  _2_0,  # PYCHOK used!
                                 _isNAN, _isNAN0, _xinstanceof, _xsubclassof,
                                 _LLEB, _xkwds,
                                 _COMMASPACE_, _datum_, _h_, _N_,
                                 _ALL_OTHER, _FOR_DOCS,
                                 _H_lat_lon_height4Tuple, _NamedTuple, _Pass)
from pygeodesy import (map1, map2, NAN, NN,  # basics, "consterns"
                       Datum, Datums, Similarity,  # datums
                       Ellipsoid, Ellipsoids, LqRD as _LqRD,  # ellipsoids, ltp
                       deprecated_property_RO, Property_RO,  # props
                       property_RO, property_ROver, pairs,  # props, streprs
                       Lam, Lamd, Lat, Lon, Meter, Phi, Phid,  # units
                       sincos2, tanPI_2_2)  # utily

from math import atan2, ceil, fabs, floor, log, sin, sqrt

__all__ = ()
__version__ = '26.08.18'

_LQRD0 = _LqRD()  # get Amersfoort, region4, etc. (deleted below)


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
    lat_D = Lat(lat_D=80.0)  # degrees, all
    lon_D = Lon(lon_D=50.0)

#   latD  = Lat(latD=1 / lat_D)  # degrees, all
#   lonD  = Lon(lonD=1 / lon_D)

    def __init__(self):
        S, W, N, E = self._region4
        nlat = _degN(N, S, self.lat_D) + _1_0  # 2.3.2g n-phi
        nlon = _degN(E, W, self.lon_D) + _1_0  # 2.3.2g n-lambda
        _v_assert(map1(int, nlat, nlon))

    _bounds4 = _LQRD0.bounds4()  # in .rdnap2018 Bounds4Tuple

    def _c_f_N_f6(self, lat, lon):
        # return (int(ceil), int(floor), Normalized less floor) of C{lat}) + \
        #        (int(ceil), int(floor), Normalized less floor) of C{lon})
        S, W, _, _ = self._region4
        return _c_f_N_f3(lat, S, self.lat_D) + \
               _c_f_N_f3(lon, W, self.lon_D)

    @property_ROver
    def _RDNAPv0(self):
        from pyrdnap.rdnap2018 import _RDNAPbase
        return _RDNAPbase()  # singleton, instance!

    _region4 = _LQRD0.region4()  # in .rdnap2018 Bounds4Tuple

    def _toDict(self):
        def _p(n):  # lambda
            return any(map(n.endswith, '4DS'))

        return self._preDict(_p)

    @property_ROver
    def _xETRS2RD(self):  # transform ETRS to RD-Bessel
        return Similarity(tx=-565.7346, ty=-50.4058, tz=-465.2895, s=-4.07242,
                          rx=-1.91513,  ry=1.60365,  rz=-9.09546, name='_xETRS2RD')

    @property_ROver
    def _xRD2ETRS(self):  # transform RD-Bessel to ETRS
        return Similarity(tx=565.7381, ty=50.4018,  tz=465.2904, s=4.07244,
                          rx=1.91514,  ry=-1.60363, rz=9.09546, name='_xRD2ETRS')

    # % python -c "import pyrdnap; print(pyrdnap.rd0._RD.toStr())"
    #  _bounds4=RD bounds (latS=50.75, lonW=2.539333, latN=55.765, lonE=7.22),
    # _region4=RD region (latS=50.0, lonW=2.0, latN=56.0, lonE=8.0),
    # _xETRS2RD=Similarity(name='_xETRS2RD', tx=-565.73, ty=-50.406, tz=-465.29, s=-4.0724,
    #                                        rx=-1.9151, ry=1.6037, rz=-9.0955),
    # _xRD2ETRS=Similarity(name='_xRD2ETRS', tx=565.74, ty=50.402, tz=465.29, s=4.0724,
    #                                        rx=1.9151, ry=-1.6036, rz=9.0955),
    # lat_D=80.0, lon_D=50.0  # latD=0.0125, lonD=0.02

_RD = _RD()  # PYCHOK singleton, in .test/testRndTrips


class _RD0(_RDbase):
    '''(INTERNAL) C{RD} Amersfoort, NL / C{RD New} constants for RDNAP2018 (ASCII.txt).

       @see: U{EPSG:9809<https://EPSG.io/9809-method>}, U{"Oblique Stereographic"
             <https://PROJ.org/en/stable/operations/projections/sterea.html>} and
             <http://geotiff.maptools.org/proj_list/oblique_stereographic.html>
    '''
    H0      = Meter(H0     =_LQRD0.height0)  # Amersfoort.height0 0.0 m
    H0_ETRS = Meter(H0_ETRS=_LQRD0.height0_ETRS)  # 43.0 m
    K0      = 0.9999079  # 2.4.1 scale factor
    LAT0    = Lat(LAT0=_LQRD0.Amersfoort.lat)  # '52  9 22.178N' == 52.156160555555+°
    LON0    = Lon(LON0=_LQRD0.Amersfoort.lon)  # ' 5 23 15.5E'   ==  5.387638888888+°
    LAM0    = Lamd(LAM0=LON0)  # 𝜆0, 0.094032038
    LAM0C   = Lam(LAM0C=LAM0)  # 𝛬0 on sphere == 𝜆0
    PHI0    = Phid(PHI0=LAT0)  # 𝜑0 0.910296727, PHI0C 𝛷0 set below
    X0      = Meter(X0=155000.0)  # false Easting  155029.784?
    Y0      = Meter(Y0=463000.0)  # false Norting  463109.889?

#   @property_ROver
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

    @property_ROver
    def D0(self):  # lazily
        return Datums.Bessel1841

    @property_ROver
    def D80(self):  # lazily
        return Datums.GRS80

    @property_ROver
    def E0(self):  # lazily
        return self.D0.ellipsoid

    def log_e_2(self, phi):
        e = self.E0.e
        p = e * sin(phi)
        return log((_1_0 + p) / (_1_0 - p)) * (e * _0_5)

    def log_tan(self, phi):
        return log(tanPI_2_2(phi))  # tan((phi + PI/2) / 2)

    @property_ROver
    def M0(self):  # 2.4.1 p 15 m
        return self.W0 - self.N0 * self.Q0

    @property_ROver
    def N0(self):  # 2.4.1 p 15 n, sphere
        E = self.E0
        _, c = self.sincos2PHI0
        return sqrt(c**4 * E.e2 / E.e21 + _1_0)

    @property_ROver
    def PHI0C(self):  # 2.4.1 p 15 𝛷0 on sphere
        m, n = self.Rmn2
        s, c = self.sincos2PHI0
        return Phi(PHI0C=atan2(m * s, n * c))  # atan((m / n) * tan(PHI0))

    @property_ROver
    def Q0(self):  # 2.4.1 p 15 q0
        return self.log_tan(self.PHI0) - self.log_e_2(self.PHI0)

    @property_ROver
    def R(self):  # 2.4.1 p 15 R, radius conformal sphere
        m, n = self.Rmn2
        return m * n

    @property_ROver
    def RK2(self):  # 2.4.2
        return self.R * self.K0 * _2_0

    @property_ROver
    def Rmn2(self):  # 2.4.1 p 15 (sqrt(RsubM), sqrt(RsubN))
        # RsubM, RsubN == RHO0, NU0 EPSG:9809
        E =  self.E0
        s, _ = self.sincos2PHI0
        s = _1_0 - s**2 * E.e2
        # assert s > 0
        N =  E.a / sqrt(s)
        # assert N > 0
        M =  E.e21 * N / s
        # assert M > 0
        return map1(sqrt, M, N)  # sqrt!

    @property_ROver
    def sincos2PHI0(self):  # 𝜑0
        return sincos2(self.PHI0)

    @property_ROver
    def sincos2PHI0C(self):  # 𝛷0
        return sincos2(self.PHI0C)

    def _toDict(self):
        def _p(n):  # lambda
            return n.endswith('0') or n.startswith('R') or \
                   n.endswith('0C')  # _0_

        return self._preDict(_p, H0_ETRS=self.H0_ETRS)

    @property_ROver
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


class RDNAP7Tuple(_H_lat_lon_height4Tuple):  # in .v_self
    '''7-Tuple C{(RDx, RDy, H, lat, lon, height, datum)} with I{local} C{RDx}, C{RDy}
       and (orthometric) height C{H}, geodetic C{lat}, C{lon}, (ellipsoidal) C{height}
       and C{datum} with C{lat} and C{lon} in C{degrees} and with C{RDx}, C{RDy}, C{H}
       and C{height} in C{meter}, conventionally.

       @note: I{By default} C{lat}, C{lon} and C{datum} are B{GRS80 (ETRS89)} when
              returned from L{RDNAP2018v1.reverse} but B{Bessel1841 (RD-Bessel)}
              from L{RDNAP2018v2.reverse}.
    '''
    _Names_ = ('RDx', 'RDy')  + _H_lat_lon_height4Tuple._Names_ + (_datum_,)
    _Units_ = ( Meter, Meter) + _H_lat_lon_height4Tuple._Units_ + (_Pass,)

    def diff(self, other, datum=None, **name):
        '''Return the difference between this and an C{other} C{RDNAP7Tuple}.

           @kwarg datum: Datum C{diff} (C{Datum}, None or NAN).
           @kwarg name: Optional name (C{str}).

           @return: An L{RDNAP7Tuple} with the C{fabs(diff)} for each item,
                    except C{datum} as B{C{datum}}.
        '''
        def _diff(a, b):
            try:
                return fabs(a - b)
            except TypeError:
                return datum

        _xinstanceof(RDNAP7Tuple, other=other)
        t = map2(_diff, self, other)
        return RDNAP7Tuple(t, **name)

    @Property_RO
    def latlonheightdatum(self):
        '''Get the lat-, longitude in C{degrees} with height and datum (L{LatLon4Tuple}C{(lat, lon, height, datum)}).
        '''
        return self.latlonheight.to4Tuple(self.datum)

    @deprecated_property_RO
    def NAPh(self):
        '''DEPRECATED on 2026.07.21, use attribute C{H}.'''
        return self.H  # PYCHOK H

    @Property_RO
    def philamheightdatum(self):
        '''Get the lat-, longitude in C{radians} with height and datum (L{PhiLamn4Tuple}C{(phi, lam, height, datum)}).
        '''
        return self.philamheight.to4Tuple(self.datum)

    def toDatum(self, datum2, name=NN):
        '''Convert this C{lat}, C{lon} and C{height} to B{C{datum2}}.

           @arg datum2: Datum to convert I{to} (L{Datum}).
           @kwarg name: Optional name (C{str}), overriding this name.

           @return: An L{RDNAP7Tuple} with transformed C{lat}, C{lon} and C{height}
                    or this L{RDNAP7Tuple} if this.datum is B{C{datum2}}.

           @note: This datum conversion is based on C{pygeodesy} which differs from
                  C{RDNAPTRANS(tm)2018_v220627}.

           @see: Methods L{RDNAP7Tuple.toETRS} and L{RDNAP7Tuple.toRD}.
        '''
        _xinstanceof(Datum, datum2=datum2)
        if self.datum is datum2 or self.datum == datum2:  # PYCHOK datum
            return self
        g = self.toLatLon(_LLEB).toDatum(datum2)
        h = NAN if _isNAN(self.height) else g.height  # PYCHOK preserve height NAN
        return self.dup(lat=g.lat, lon=g.lon, datum=g.datum, height=h,
                                              name=name or self.name)

    def toETRS(self, **name):
        '''Copy this L{RDNAP7Tuple} with C{lat} and C{lon} C{reverse3} transformed
           to ETRS89 (GRS80), provided this C{datum} is RD-Bessel (Bessel1841).

           @kwarg name: Optional name (C{str}), overriding this name.

           @see: Methods L{RDNAP7Tuple.toRD} and L{RDNAP7Tuple.toDatum}.
        '''
        return self._toX(_RD0.D0, _RD._RDNAPv0.reverse3, **name)

    def toLatLon(self, LatLon, **LatLon_kwds):
        '''Return this C{lat}, C{lon}, C{datum} and C{height} as B{C{LatLon}}.

           @arg LatLon: An ellipsoidal C{LatLon} class (C{pygeodesy.ellipsoidal*}).
           @kwarg LatLon_kwds: Optional, additional B{C{LatLon}} keyword arguments.

           @return: An B{C{LatLon}} instance.

           @raise TypeError: B{C{LatLon}} not ellipsoidal or an other issue.
        '''
        _xsubclassof(_LLEB, LatLon=LatLon)
        h    = _isNAN0(self.height)  # PYCHOK height
        kwds = _xkwds(LatLon_kwds, name=self.name, height=h)
        return LatLon(self.lat, self.lon, datum=self.datum, **kwds)  # PYCHOK datum

    def toRD(self, **name):
        '''Copy this L{RDNAP7Tuple} with C{lat} and C{lon} C{forward3} transformed
           to RD-Bessel (Bessel1841), provided this C{datum} is ETRS89 (GRS80).

           @kwarg name: Optional name (C{str}), overriding this name.

           @see: Methods L{RDNAP7Tuple.toETRS} and L{RDNAP7Tuple.toDatum}.
        '''
        return self._toX(_RD0.D80, _RD._RDNAPv0.forward3, **name)

    def _toX(self, datum, _xform, name=NN):
        # helper for C{toETRS} and C{toRD}
        if self.datum is datum or self.datum == datum:  # PYCHOK datum
            lat, lon, d = _xform(*self.latlon)
            return self.dup(lat=lat, lon=lon, datum=d, name=name or self.name)
        return self

    @deprecated_property_RO
    def xy(self):
        '''DEPRECATED on 2026.08.14, use attribute C{xyh}, C{xyH} or C{xyN}.'''
        from pygeodesy import Vector2Tuple
        return Vector2Tuple(self.RDx, self.RDy, name=self.name)  # PYCHOK RDx, RDy

    @Property_RO
    def xyh(self):
        '''Get the I{local} coordinates and ellipsoidal height (L{RDxyheight3Tuple}C{(RDx, RDy, h)}).
        '''
        return RDxyheight3Tuple(self.RDx, self.RDy, self.height, name=self.name)

    @Property_RO
    def xyH(self):
        '''Get the I{local} coordinates and orthometric height (L{RDxyHeight3Tuple}C{(RDx, RDy, H)}).
        '''
        return RDxyHeight3Tuple(self.RDx, self.RDy, self.H, name=self.name)

    @Property_RO
    def xyN(self):
        '''Get the I{local} coordinates and geoid height (L{RDxyNgeoid3Tuple}C{(RDx, RDy, N)}).
        '''
        return RDxyNgeoid3Tuple(self.RDx, self.RDy, self.N, name=self.name)

    @deprecated_property_RO
    def xyz(self):
        '''DEPRECATED on 2026.08.14, use attribute C{xyH}.'''
        from pygeodesy import Vector3Tuple
        return Vector3Tuple(self.RDx, self.RDy, self.H, name=self.name)  # PYCHOK RDx, RDy


class LqRD(_LqRD):
    '''Like U{pygeodesy.LqRD<https://mrJean1.GitHub.io/PyGeodesy/docs/pygeodesy.ltp.LqRD-class.html>}
       but with methods C{forward} and C{reverse} returning an L{RDNAP7Tuple} with C{H} replaced
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

           @return: An L{RDNAP7Tuple}C{(RDx, RDy, H, lat, lon, height, datum)} with C{H}
                    set to I{local} C{z}.

           @see: C{pygeodesy.LqRD.forward} for more information.
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

           @return: An L{RDNAP7Tuple}C{(RDx, RDy, H, lat, lon, height, datum)} with C{H}
                    set to I{local} B{C{z}}.

           @see: C{pygeodesy.LqRD.reverse} for more information.
        '''
        t = _LqRD.reverse(self, x_xyz, y=y, z=z)
        return LqRD._l9t2r7t(t, **name)

    @staticmethod
    def _l9t2r7t(t, name=NN, **unused):  # M=False
        return RDNAP7Tuple(t.x,   t.y,   t.z,  # H = t.z
                           t.lat, t.lon, t.height, t.ecef.datum, name=name or t.name)


class _RDxy3Tuple(_NamedTuple):  # provides .x, .y and .z

    @property_RO
    def x(self):
        '''Get I{local} C{RDx} (C{Meter}).
        '''
        return self[0]  # PYCHOK RDx

    @property_RO
    def y(self):
        '''Get I{local} C{RDy} (C{Meter}).
        '''
        return self[1]  # PYCHOK RDy

    @property_RO
    def z(self):
        '''Get the ellipsoidal, geoid I{or} orthometric height (C{Meter}).
        '''
        return self[2]  # PYCHOK height, H or N


class RDxyHeight3Tuple(_RDxy3Tuple):
    '''3-tuple C{(RDx, RDy, H)} with orthometric height C{H}, all in C{meter}.
    '''
    _Names_ = RDNAP7Tuple._Names_[:3]
    _Units_ = RDNAP7Tuple._Units_[:3]


class RDxyheight3Tuple(_RDxy3Tuple):
    '''3-tuple C{(RDx, RDy, h)} with ellipsoidal height C{h}, all in C{meter}.
    '''
    _Names_ = RDxyHeight3Tuple._Names_[:2] + (_h_,)
    _Units_ = RDxyHeight3Tuple._Units_


class RDxyNgeoid3Tuple(_RDxy3Tuple):
    '''3-tuple C{(RDx, RDy, N)} with geoid height C{N}, all in C{meter}.
    '''
    _Names_ = RDxyHeight3Tuple._Names_[:2] + (_N_,)
    _Units_ = RDxyHeight3Tuple._Units_


__all__ += _ALL_OTHER(RDNAP7Tuple, RDxyheight3Tuple, RDxyHeight3Tuple,
                      RDxyNgeoid3Tuple, LqRD,  # passed along from PyGeodesy
                      Datum, Datums, Ellipsoid, Ellipsoids, Similarity)
del _ALL_OTHER, _LQRD0

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
