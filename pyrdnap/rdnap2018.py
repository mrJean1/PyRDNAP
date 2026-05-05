
# -*- coding: utf-8 -*-

u'''A pure Python implementation of the Netherlands' U{RD NAP<https://www.NSGI.NL/
coordinatenstelsels-en-transformaties/coordinatentransformaties/rdnap-etrs89-rdnaptrans>}
specifications to convert between geodetic GRS80 (ETRS89) lat-/longitudes in degrees
and local C{RijksDriehoeksmeeting (RD)} coordinates and C{Normaal Amsterdam Peil (NAP)
quasi-geoid-height} in C{meter}.

Classes L{RDNAP2018v1} and L{RDNAP2018v2} follow C{variant 1} respectively C{variant 2}
of the specification U{RDNAPTRANS(tm)2018<https://formulieren.kadaster.nl/aanvragen_rdnaptrans>}.
Each provide a C{forward} method to convert geodetic lat-/longitudes and heights to C{RD}
coodinates and C{NAP} heights and a C{reverse} method for converting the other way.

The C{forward} and C{reverse} results of L{RDNAP2018v1} meet the C{RDNAPTRANS(tm)2018_v220627}
self-validation requirements of C{0.000000010 degrees} and C{0.0010 meter} for tests inside
the C{RD} region, see B{C{Note below}}.  Class L{RDNAP2018v2} does not and is not required to.

Also, the original C{RDNAPTRANS(tm)2018_v220627} grid files for both variants are I{not included}
in C{PyPRDNAP} and C{pyrdnap} due to the total size of those files.  Instead, the grid files for
each C{variant} I{include only} the C{lat_corr}, C{lon_corr} and C{NAP_quasi_geoid_height_...}
columns, extracted from the original grid files with leading and trailing zeros removed and
re-formatted as row-order matrices.

@note: C{PyRDNAP}, C{pyrdnap} and L{RDNAP2018v1} have B{not been formally validated} and are
       B{not certified} to carry the trademark name C{RDNAPTRANS(tm)}.
'''
# make sure int/int division yields float quotient, see .basics
from __future__ import division as _; del _  # noqa: E702 ;

from pyrdnap.v_grids import _v_assert, _V_grid, _v_gridz_import
from pyrdnap.__pygeodesy import (_0_0 as _ZERO, _0_5, _1_0, _2_0,
                                 _earth_datum,
                                 _COMMASPACE_, _datum_, _E_, _lat_, _lon_,
                                 _height_, _N_, _S_, _UNDER_, _W_,
                                 _ALL_DOCS, _ALL_OTHER, _FOR_DOCS, _Pass,
                                 _NamedBase, _NamedTuple, notOverloaded)
from pygeodesy import (EPS0, EPS1, NAN, NN, PI_2, PI, PI2,  # "consterns"
                       Datum, Datums, Ellipsoid, Similarity,  # datums, ellipsoids
                       LatLon2Tuple, Vector2Tuple, Vector3Tuple,  # namedTuples
                       Property_RO, property_RO, property_ROnce,  # props
                       pairs,  # streprs
                       Height, Lamd, Lat, Lon, Meter, Phi, Phid,  # units
                       sincos2, sincos2d)  # utily

from math import asin, atan, ceil, copysign, degrees, exp, fabs, \
                 floor, hypot, isnan, log, radians, sin, sqrt, tan

__all__ = ()
__version__ = '26.05.05'

_H0_ETRS89 =  43.0

_TOL_D = 1e-9  # degrees 2.3.3f+
_TOL_M = 1e-6  # meter
_TOL_R = radians(_TOL_D)  # 2e-11
_TRIPS = 16    # 5..6 sufficient


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

    # % python -c "import pyrdnap; print(pyrdnap.rdnap2018._RD.toStr())"
    # _xETRS2RD=Similarity(name='_xETRS2RD', tx=-565.73, ty=-50.406, tz=-465.29, s1=1.0,
    #                                        rx=-1.9151, ry=1.6037, rz=-9.0955, s=-4.0724),
    # _xRD2ETRS=Similarity(name='_xRD2ETRS', tx=565.74, ty=50.402, tz=465.29, s1=1.0,
    #                                        rx=1.9151, ry=-1.6036, rz=9.0955, s=4.0724),
    # LAT_INC=0.0125, LAT_MAX=56, LAT_MIN=50, LON_INC=0.02, LON_MAX=8, LON_MIN=2,
    # N_LAT_LON=(481.0, 301.0)

_RD = _RD()  # PYCHOK singleton


class _RD0(_RDbase):
    '''(INTERNAL) C{RD} Amersfoort, NL references.

       @see: U{EPSG:9809<https://EPSG.io/9809-method>}, U{"Oblique Stereographic"
             <https://PROJ.org/en/stable/operations/projections/sterea.html>} and
             <http://geotiff.maptools.org/proj_list/oblique_stereographic.html>
    '''
    H0    = _ZERO  # E0 height in meter
    K0    =  0.9999079  # scale factor
    LAT0  =  Lat(LAT0='52  9 22.178N')  # 52.15616055+°
    LON0  =  Lon(LON0=' 5 23 15.5E')    # 5.387638888+°
    LAM0C = \
    LAM0  =  Lamd(LAM0=LON0)  # 𝜆0, 𝛬0 = 𝜆0 on sphere 0.094032038
    PHI0  =  Phid(PHI0=LAT0)  # 𝜑0 0.910296727, 𝛷0 below
    X0    =  Meter(X0=155000.0)  # false Easting  155029.784?
    Y0    =  Meter(Y0=463000.0)  # false Norting  463109.889?

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

        return self._preDict(_p, R=self.R, RK2=self.RK2,
                                         _rMN2=self._rMN2)

#   def _w1(self, sphi):  # EPSG:9809
#       w1 = NAN
#       if _1_0 > sphi > _N_1_0:
#           e  = self.E0.e
#           S  = (_1_0 + sphi)     / (_1_0 - sphi)
#           T  = (_1_0 - sphi * e) / (_1_0 + sphi * e)
#           w1 = pow(pow(T, e) * S, self.N0)
#       return w1

    # % python -c "import pyrdnap; print(pyrdnap.rdnap2018._RD0.toStr())"
    # D0=Datum(name='Bessel1841', ellipsoid=Ellipsoids.Bessel1841, transform=Transforms.Bessel1841),
    # E0=Ellipsoid(name='Bessel1841', a=6377397.155, f=0.00334277, f_=299.1528128, b=6356078.962818),
    # H0=0.0, K0=0.9999079, LAM0=0.094032038, LAM0C=0.094032038, LAT0=52.156160556, LON0=5.387638889,
    # M0=0.003773954, N0=1.000475857, PHI0=0.910296727, PHI0C=0.909684757, R=6382644.571035412, RK2=12764113.458940839,
    # sincos2PHI0=(0.7896858198001045, 0.6135114554811807), sincos2PHI0C=(0.7893102212553742, 0.6139946047171687),
    # X0=155000.0, Y0=463000.0, _rMN2=(6374588.709792872, 6390710.612840701)

_RD0 = _RD0()  # PYCHOK singleton, in .test


class _RDNAPbase(_NamedBase):
    '''C{RDNAP} base class for L{RDNAP2018v1} and {-v2}.
    '''
    _datum  = None  # forward Datum, lazily
    _EETRS  = None  # Ellipsoid, lazily
    _raiser = False

    def __init__(self, a_ellipsoid=None, f=None, raiser=False, **name):
        '''New C{RDNAP2018v1} or C{-v2} instance.

           @kwarg a_ellipsoid: An ellipsoid (L{Ellipsoid}), a datum (L{Datum}) or the
                               ellipsoid's equatorial radius (C{scalar}, conventionally
                               in C{meter}), see B{C{f}}.  Default C{Datums.GRS80}.
           @kwarg f: The flattening of the ellipsoid (C{scalar}) if B{C{a_ellipsoid}}
                     is specified as C{scalar}, ignored otherwise.
           @kwarg raiser: If C{True} raise an L{RDNAPError} for lat-/longitudes outside
                          the C{RD} region (C{bool}).
           @kwarg name: Optional name (C{str}).

           @raise RDNAPError: Ellipsoid (or datum) is spherical or prolate, i.e. not
                              oblate or the datum's transform is not C{unity}.
        '''
        if a_ellipsoid is f is None:
            self._datum = Datums.GRS80
        else:
            _earth_datum(a_ellipsoid, f, **name)
        E = self._datum.ellipsoid
        if not E.isOblate:
            raise RDNAPError('not oblate %r' % (E,))
        self._EETRS = E
        if raiser:
            T = self._datum.transform
            if not T.isunity:
                raise RDNAPError('not unity %r' % (T,))
            self._raiser = True
        if name:
            self.name = name

    def forward(self, lat, lon, height=0, raiser=False):  # ETRS89 to RDNAP
        '''Convert geodetic ETRS98 C{(B{lat}, B{lon})} and B{C{height}} to
           local C{(RDx, RDy)} coordinates and C{NAPh} quasi-geoid-height.

           @arg lat: Latitude (C{degrees} ETRS89, geodetic).
           @arg lon: Longitude (C{degrees} ETRS89, geodetic).
           @kwarg height: Height, optional (C{meter} above geoid) or C{NAN}
                          to ignore C{NAPh} interpolation.
           @kwarg raiser: If C{True} raise an L{RDNAPError} if B{C{lat89}}
                          or B{C{lon89}} is outside the C{RD} region (C{bool}).

           @return: An L{RDNAP7Tuple}C{(RDx, RDy, NAPh, lat, lon, height, datum)}
                    with local C{RDx}, C{RDy} coordinates and C{NAPh} height.
        '''
        lat8, lon8 = lat, lon
        lat0, lon0 = \
        lat_, lon_ = self._forwardXform(lat, lon, raiser)
        for _ in range(_TRIPS):  # 2.3.3a-f, 1..2
            lat, lon = self._rdlatlon2(lat_, lon_, lat0, lon0)
            if fabs(lat - lat_) < _TOL_D and \
               fabs(lon - lon_) < _TOL_D:
                break
            lat_, lon_ = lat, lon

        phiC, lamC = _ellipsoidal2spherical(lat, lon)
        RDx,  RDy  = _spherical2oblique(phiC, lamC)
        NAPh       =  NAN if _isNAN(height) else (height -
                      self.rdNAPh(lat8, lon8))  # 2.5.2
        return RDNAP7Tuple(RDx, RDy, NAPh, lat8, lon8, height, self.forwardDatum,
                                           name=self.name or 'forward')

    @property_RO
    def forwardDatum(self):
        '''Get the geodetic C{forward} datum (L{Datum}).
        '''
        return self._datum

    def _forwardXform(self, lat, lon, raiser):
        # default and variant 2: no datum transform
        if (raiser or self._raiser) and not _RD.isinside(lat, lon):
            raise self._outsidError(lat, lon)
        return lat, lon

    def isinside(self, lat, lon, eps=0):
        '''Is C{(B{lat}, B{lon})} inside the C{RD} region (C{bool})?

           @kwarg eps: Over-/undersize the C{RD} region (C{degrees}).
        '''
        return _RD.isinside(lat, lon, eps)

    def _outsidError(self, *lat_lon):
        # format an "outside C{RD} region Error"
        return RDNAPError('%r outside %s' % (lat_lon, self.region))

    @property_RO
    def _rdgrid(self):
        raise notOverloaded(self)

    def _rdlatlon2(self, lat, lon, lat0=None, lon0=None):  # 2.3.2
        # return the RD-corrected C{(lat, lon)}
        if _RD.isinside(lat, lon):
            c_f_N_f6 = _RD.c_f_N_f6(lat, lon)
            lat_corr = _bilinear(self._rdgrid._lat_corr, *c_f_N_f6)
            lon_corr = _bilinear(self._rdgrid._lon_corr, *c_f_N_f6)

            if lat0 is lon0 is None:  # reverse
                lat += lat_corr
                lon += lon_corr
            else:  # forward
                lat  = lat0 - lat_corr
                lon  = lon0 - lon_corr
#       elif raiser or self._raiser:
#           raise self._outsidError(lat, lon)
        return lat, lon  # NAN, NAN?

    def rdNAPh(self, lat, lon):  # 2.5.1 and 3.5
        '''Interpolate the C{NAP_h} quasi-geoid-height
           I{within} the C{RD} region.

           @arg lat: Latitude (C{degrees} ETRS89, geodetic).
           @arg lon: Longitude (C{degrees} ETRS89, geodetic).

           @return: C{NAPh} (C{meter}) or C{NAN} if B{C{lat}}
                    or B{C{lon}} is outside the C{RD} region.
        '''
        if _RD.isinside(lat, lon):
            c_f_N_f6 = _RD.c_f_N_f6(lat, lon)
            NAP_h    = _bilinear(self._rdgrid._NAP_h, *c_f_N_f6)
            return NAP_h
#       elif raiser or self._raiser:
#           raise self._outsidError(lat, lon)
        return NAN  # c0 2.5.1e+

    @property_RO
    def region(self):
        '''Get the C{RD} region as L{RDregion4Tuple}C{(S, W, N, E)}, all C{degrees}.
        '''
        return _RD.region

    def _reverse(self, RDx, RDy, NAPh, raiser=False):
        '''(INTERNAL) Convert local C{(B{RDx}, B{RDy})} coordinates and
           B{C{NAPh}} quasi-geoid-height to geodetic ETRS89 or RD-Bessel
           C{lat}, C{lon} and C{height}.
        '''
        phiC, lamC = _oblique2spherical(RDx, RDy)
        lat,  lon  = _spherical2ellipsoidal(phiC, lamC)

        lat, lon = self._rdlatlon2(lat, lon)
        lat, lon = self._reverseXform(lat, lon, raiser)
        h        = NAN if _isNAN(NAPh) else (NAPh +
                   self.rdNAPh(lat, lon))
        return RDNAP7Tuple(RDx, RDy, NAPh, lat, lon, h, self.reverseDatum,
                                           name=self.name or 'reverse')

    @property_RO
    def reverseDatum(self):
        '''Get the geodetic C{reverse} datum (L{Datum}), GRS80 or Bessel1841.
        '''
        return {1:  self._datum,
                2: _RD0.D0}.get(self.variant)

    _reverseXform = _forwardXform

    def toStr(self, prec=9, **unused):  # PYCHOK signature
        '''Return this C{RDNAP2018*} instance as a string.

           @kwarg prec: Precision, number of decimal digits (0..9).

           @return: This C{RDNAP2018*} (C{str}).
        '''
        return self.attrs('name', 'variant', 'forwardDatum', prec=prec)  # _ellipsoid_, _name__

    @property_RO
    def variant(self):
        raise None


class RDNAP2018v1(_RDNAPbase):
    '''Transformer implementing RDNAP 2018 C{variant 1}.
    '''
    if _FOR_DOCS:
        __init__ = _RDNAPbase.__init__
        forward  = _RDNAPbase.forward

    def _forwardXform(self, lat, lon, raiser):
        # transform C{(lat, lon)} from ETRS (GRS80) to RD-Bessel datum
        x, y, z  = _geodetic2cartesian(lat, lon, self._EETRS, _H0_ETRS89)
        x, y, z  = _RD._xETRS2RD.transform(x, y, z)
        lat, lon = _cartesian2geodetic(x, y, z, _RD0.E0)
        if (raiser or self._raiser) and not _RD.isinside(lat, lon):
            raise self._outsidError(lat, lon)
        return lat, lon

    @property_ROnce
    def _rdgrid(self):
        try:
            from pyrdnap import v1grid
        except ImportError:
            v1grid = _v_gridz_import(self.variant)
        return v1grid

    def reverse(self, RDx, RDy, NAPh=0, raiser=False):  # RDNAP to ETRS89
        '''Convert a local C{(B{RDx}, B{RDy})} point and B{C{NAPh}}
           height to I{geodetic} B{ETRS89} C{(lat, lon, height)}.

           @arg RDx: Local C{RD} X (C{meter}, conventionally).
           @arg RDy: Local C{RD} Y (C{meter}, conventionally).
           @kwarg NAPh: C{NAP} quasi-geoid-height (C{meter}, conventionally)
                        or C{NAN} to ignore C{NAPh} interpolation.
           @kwarg raiser: If C{True} raise an L{RDNAPError} if C{lat} or
                          C{RDy} is outside the C{RD} region (C{bool}).

           @return: An L{RDNAP7Tuple}C{(RDx, RDy, NAPh, lat, lon, height,
                    datum)} with C{lat} and C{lon} coordinates, C{height}
                    and C{datum} I{GRS80 (ETRS89)}.
        '''
        return self._reverse(RDx, RDy, NAPh, raiser)

    def _reverseXform(self, lat, lon, raiser):
        # transform C{(lat, lon)} from RD-Bessel to ETRS (GRS80) datum
        x, y, z  = _geodetic2cartesian(lat, lon, _RD0.E0, _RD0.H0)
        x, y, z  = _RD._xRD2ETRS.transform(x, y, z)
        lat, lon = _cartesian2geodetic(x, y, z, self._EETRS)
        if (raiser or self._raiser) and not _RD.isinside(lat, lon):
            raise self._outsidError(lat, lon)
        return lat, lon

    def similarity(self, inverse=False):
        '''Get the forward or reverse datum transform (C{Similarity}).
        '''
        return _RD._xRD2ETRS if inverse else _RD._xETRS2RD

    @property_ROnce
    def variant(self):
        '''Get this C{RDNAP2018}'s variant (C{int}).
        '''
        return 1


class RDNAP2018v2(_RDNAPbase):
    '''Transformer implementing RDNAP 2018 C{variant 2}.

       @note: Method L{RDNAP2018v2.reverse} returns geodetic B{RD-Bessel}
              and I{not ETRS89} lat-/longitudes.
    '''
    if _FOR_DOCS:
        __init__ = _RDNAPbase.__init__
        forward  = _RDNAPbase.forward

    @property_ROnce
    def _rdgrid(self):
        try:
            from pyrdnap import v2grid
        except ImportError:
            v2grid = _v_gridz_import(self.variant)
        return v2grid

    def reverse(self, RDx, RDy, NAPh=0, raiser=False):  # RDNAP to RD-Bessel
        '''Convert a local C{(B{RDx}, B{RDy})} point and B{C{NAPh}}
           height to I{geodetic} B{RD-Bessel} C{(lat, lon, height)}.

           @arg RDx: Local C{RD} X (C{meter}, conventionally).
           @arg RDy: Local C{RD} Y (C{meter}, conventionally).
           @kwarg NAPh: C{NAP} quasi-geoid-height (C{meter}, conventionally)
                        or C{NAN} to ignore C{NAPh} interpolation.
           @kwarg raiser: If C{True} raise an L{RDNAPError} if C{lat} or
                          C{lon} is outside the C{RD} region (C{bool}).

           @return: An L{RDNAP7Tuple}C{(RDx, RDy, NAPh, lat, lon, height,
                    datum)} with C{lat} and C{lon} coordinates, C{height}
                    and C{datum} I{Bessel1841 (RD-Bessel)}.
        '''
        return self._reverse(RDx, RDy, NAPh, raiser)

    def similarity(self, **unused):  # PYCHOK signature
        '''Get the forward or reverse datum transform, always C{None}.
        '''
        return None

    @property_ROnce
    def variant(self):
        '''Get this C{RDNAP2018}'s variant (C{int}).
        '''
        return 2


class RDNAPError(ValueError):
    '''Error raised for C{RD} and C{NAP} issues.
    '''
    pass


class RDNAP7Tuple(_NamedTuple):
    '''7-Tuple C{(RDx, RDy, NAPh, lat, lon, height, datum)} with I{local} C{RDx},
       C{RDy} and C{NAPh} quasi-geoid_height, I{geodetic} C{lat}, C{lon}, C{height}
       and C{datum} with C{lat} and C{lon} in C{degrees} and C{RDx}, C{RDy}, C{NAPh}
       and C{height} in C{meter}, conventionally.

       @note: The C{lat} and {lon} are I{GRS80 (ETRS89)} coordinates from
              L{RDNAP2018v1.reverse} but I{Bessel1841 (RD-Bessel)} from
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
    '''4-Tuple C{(S, W, N, E)} with C{RD} region in C{ETRS89 degrees}.
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


def _atan3(y, x, x0):  # 2.2.3e and 3.1.1i
    # equiv to math.atan2 iff x0 is y
    if x > 0:
        r = atan(y / x)
    elif x < 0:
        r = atan(y / x) + copysign(PI, x0)
    else:
        r = copysign(PI_2, x0) if x0 else _ZERO
    return r


def _atan_exp(w):  # 2.4.1c
    return atan(exp(w)) * _2_0 - PI_2


def _bilinear(v_grid, c_latI, f_latI, latN_f,  # 2.3.1f and g
                      c_lonI, f_lonI, lonN_f):
    # interpolate a _lat_corr, _lon_corr or _NAP_h
    assert isinstance(v_grid, _V_grid)
    nw = v_grid(c_latI, f_lonI)
    ne = v_grid(c_latI, c_lonI)
    sw = v_grid(f_latI, f_lonI)
    se = v_grid(f_latI, c_lonI)
    lonN_f1 = _1_0 - lonN_f  # == 1 - (lonN - f_lonN)
    return (nw * lonN_f1 + ne * lonN_f) * latN_f + \
           (sw * lonN_f1 + se * lonN_f) * (_1_0 - latN_f)


def _cartesian2geodetic(x, y, z, E):  # 2.2.3 == EcefUPC.reverse?
    # convert cartesian C{(x, y, z)} to C{E}-geodetic C{(lat, lon)}
    r = hypot(x, y)
    if r > _TOL_M:
        a    = E.a * E.e2
        phi_ = atan(z / r)
        for _ in range(_TRIPS):  # 4..6
            s   = sin(phi_)
            s  *= a / sqrt(_1_0 - s**2 * E.e2)
            phi = atan((z + s) / r)
            if fabs(phi - phi_) < _TOL_R:
                break
            phi_ = phi
    else:
        phi = copysign(PI_2, z)
    lam = _atan3(y, x, y)
    return degrees(phi), degrees(lam)


def _c_f_N_f3(d, d_MIN, d_INC):
    # return int(ceil), int(floor) and (Normalized less floor) of C{d} degrees
    N = (d - d_MIN) / d_INC
    f = floor(N)
    return int(ceil(N)), int(f), (N - f)


def _ellipsoidal2spherical(lat, lon):  # 2.4.1
    # convert geodetic C{(lat, lon)} to spherical C{(𝛷, 𝛬)}
    A0   = _RD0
    phiC =  phi = Phid(lat)
    if PI_2 > phi > -PI_2:  # 2.4.1c
        q = A0.ln_tan(phi) - A0.ln_e_2(phi)
        w = A0.N0 * q + A0.M0  # 2.4.1b
        phiC = _atan_exp(w)
    lamC = (Lamd(lon) - A0.LAM0) * A0.N0 + A0.LAM0C  # 2.4.1d
    return phiC, lamC  # -Capital


def _eq0(r, r0=_ZERO):
    return fabs(r - r0) < _TOL_R


# def _eq0d(d, d0=_ZERO):
#     return fabs(d - d0) < _TOL_D


def _geodetic2cartesian(lat, lon, E, h0=0):  # 2.2.1
    # convert C{E}-geodetic C{(lat, lon)} to cartesian C{(x, y, z)}
    y, x = sincos2d(lon)
    z, c = sincos2d(lat)
    n  = E.a / sqrt(_1_0 - z**2 * E.e2)
    c *= n + h0
    x *= c
    y *= c
    z *= n * (_1_0 - E.e2) + h0
    return x, y, z


def _isNAN(f):
    return (f is NAN) or isnan(f)


def _ne0(r, r0=_ZERO):
    return fabs(r - r0) > _TOL_R


# def _ne0d(d, d0=_ZERO):
#     return fabs(d - d0) > _TOL_D


def _oblique2spherical(x, y):  # 3.1.1
    # inverse oblique stereographic conformal projection
    # from 2-D C{(x, y)} to spherical C{(𝛷, 𝛬)}
    A0 = _RD0
    x -=  A0.X0
    y -=  A0.Y0
    r  =  hypot(x, y)
    if r > _TOL_M:  # x and y
        s0, c0 = A0.sincos2PHI0C
        sp, cp = sincos2(atan(r / A0.RK2) * _2_0)  # psi
        ca = sp * y / r
        xN = cp * c0 - ca * s0
        yN = sp * x / r
        zN = ca * c0 + cp * s0
        phiC = asin(zN)
    else:
        _, xN =  A0.sincos2PHI0C
        yN    = _ZERO
        phiC  =  A0.PHI0C  # asin(sin(PHI0C))
    lamC = _atan3(yN, xN, x) + A0.LAM0C
    return phiC, lamC  # -Capital


def _spherical2ellipsoidal(phiC, lamC):  # 3.1.2
    # inverse Gauss conformal projection from
    # spherical C{(𝛷, 𝛬)} to geodetic C{(phi, lam)}
    A0  = _RD0
    phi =  phiC
    if PI_2 > phi > -PI_2:
        q = (A0.ln_tan(phi) - A0.M0) / A0.N0
#       w =  A0.ln_tan(phi)
        for _ in range(_TRIPS):  # 3..6
            phi_ =  phi
            phi  = _atan_exp(A0.ln_e_2(phi) + q)
            if fabs(phi - phi_) < _TOL_R:
                break
    lam = (lamC - A0.LAM0C) / A0.N0 + A0.LAM0
    lam = floor((PI - lam) / PI2) * PI2 + lam
    return degrees(phi), degrees(lam)


def _spherical2oblique(phiC, lamC):  # 2.4.2
    # oblique stereographic conformal projection
    # from spherical C{(𝛷, 𝛬)} to 2-D C{(x, y)}
    A0 = _RD0
    a  =  phiC - A0.PHI0C  # 𝛷 - 𝛷0
    b  =  lamC - A0.LAM0C  # 𝛬 - 𝛬0
    if (_ne0(a) or _ne0(b)) and (_ne0(phiC, -A0.PHI0C) or
                                 _ne0(lamC, -A0.LAM0C + PI)):
        s0, c0 = A0.sincos2PHI0C  # sin(𝛷0), cos(𝛷0)
        s,  c  = sincos2(phiC)  # sin(𝛷), cos(𝛷)
        sp_22  = sin(a * _0_5)**2 + \
                 sin(b * _0_5)**2 * c * c0  # sin(𝜓/2)**2
        if EPS0 < sp_22 < EPS1:
            # r = 2kR * tan(𝜓/2)
            # q = r / (sin(𝜓/2) * cos(𝜓/2) * 2)
            #   = 2kR * sin(𝜓/2) / (sin(𝜓/2) * cos(𝜓/2)**2 * 2)
            #   = 2kR / (cos(𝜓/2)**2 * 2)
            #   = 2kR / ((1 - sin(𝜓/2)**2) * 2)
            #   = 2kR / (2 - sin(𝜓/2)**2 * 2)
            t = sp_22 * _2_0  # 0 < t < 2
            q = A0.RK2 / (_2_0 - t)
            x = q * (c * sin(b))
            y = q * (s - s0 + s0 * t) / c0
        else:
            x = y = _ZERO  # NAN?
        x += A0.X0
        y += A0.Y0
    elif _eq0(phiC, A0.PHI0C) and _eq0(lamC, A0.LAM0C):
        x  = A0.X0  # x0 2.4.2g
        y  = A0.Y0  # y0 2.4.2h
    else:  # if _eq0(phiC, -A0.PHI0C) and _eq0(lamC, A0.LAM0C - PI):
        x = y = NAN
#   else:
#       raise RDNAPError(str((phiC, lamC)))
    return x, y


__all__ += _ALL_DOCS(_RDNAPbase)
__all__ += _ALL_OTHER(RDNAP2018v1, RDNAP2018v2, RDNAPError, RDNAP7Tuple, RDregion4Tuple,
                      # passed along from PyGeodesy
                      Datum, Ellipsoid, LatLon2Tuple, Similarity, Vector2Tuple, Vector3Tuple)

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
