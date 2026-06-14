
# -*- coding: utf-8 -*-

u'''Main classes L{RDNAP2018v1} and L{RDNAP2018v2} follow C{variant 1} respectively C{variant
2} of the U{RDNAPTRANS(tm)2018_v220627<https://formulieren.kadaster.nl/aanvragen_rdnaptrans>}
specification.  Each provide a C{forward} method to convert geodetic lat-/longitudes and height
to local C{RD} coodinates and C{NAP} heights and a C{reverse} method for converting vice-versa.

The L{RDNAP2018v1.forward} and C{.reverse} results have been formally validated to meet the
C{RDNAPTRANS(tm)2018_v220627} requirements, transforming from and to ETRS89 (GRS80) points.

The L{RDNAP2018v2.forward} and C{.reverse} results have been formally validated to meet the
C{RDNAPTRANS(tm)2018_v220627} requirements, transforming from ETRS89 (GRS80) and to RD-Bessel
(Bessel1841) points.
'''
# make sure int/int division yields float quotient, see .basics
from __future__ import division as _; del _  # noqa: E702 ;

from pyrdnap.rd0 import _RD, _RD0 as A0, RDNAP7Tuple
from pyrdnap.v_grids import RDNAPError, _V_grid, _v_gridz_import
from pyrdnap.__pygeodesy import (_0_0, _0_5, _1_0, _2_0,
                                 _isNAN, _isNAN0, _earth_datum,
                                 _ALL_DOCS, _ALL_OTHER, _FOR_DOCS,
                                 _NamedBase)
from pygeodesy import (map1, EPS0, EPS1, NAN, PI_2, PI, PI2,  # "consterns"
                       Datum, Ellipsoid, LatLonDatum3Tuple,  # datums, ellipsoids
                       deprecated_property_RO, property_RO, property_ROnce,  # props
                       Lamd, Lat, Lon, Phid,  # units
                       sincos2, sincos2d)  # utily

from math import asin, atan, copysign, degrees, exp, \
                 fabs, floor, hypot, radians, sin, sqrt

__all__ = ()
__version__ = '26.06.14'

_TOL_D = 1e-9  # degrees 2.3.3f+
_TOL_M = 1e-6  # meter
_TOL_R = radians(_TOL_D)  # 2e-11
_TRIPS = 16    # 5..6 sufficient


class _RDNAPbase(_NamedBase):  # in .rd0._RD.regionB
    '''(INTERNAL) L{RDNAP2018v1}C{/-v2} base class.
    '''
    _datum  = None  # forward, v1 reverse Datum, lazily (GRS80)
    _EETRS  = None  # forward, v1 reverse Ellipsoid, lazily
    _raiser = False

    def __init__(self, a_ellipsoid=None, f=None, raiser=False, **name):
        '''New C{RDNAP2018v1} or C{-v2} instance.

           @kwarg a_ellipsoid: An ellipsoid (L{Ellipsoid}) or the ellipsoid's equatorial
                               radius (C{scalar}, conventionally in C{meter}), see B{C{f}}
                               or a datum (L{Datum}).  Default C{Datums.GRS80} for ETRS89.
           @kwarg f: The flattening of the ellipsoid (C{scalar}) if B{C{a_ellipsoid}} is
                     specified as C{scalar}, ignored otherwise.
           @kwarg raiser: If C{True} raise an L{RDNAPError} for lat-/longitudes outside
                          the C{RD} region (C{bool}).
           @kwarg name: Optional name (C{str}).

           @raise RDNAPError: Ellipsoid (or datum) is not oblate (i.e. is spherical or
                              prolate) or the datum's C{transform} is not C{unity}.
        '''
        if a_ellipsoid is f is None:
            self._datum = A0.D80  # GRS80 (ETRS89)
        else:
            _earth_datum(self, a_ellipsoid, f, **name)  # sets self._datum
        self._EETRS = E = self._datum.ellipsoid
        if not E.isOblate:
            raise RDNAPError('not oblate: %r' % (E,))
        if raiser:  # PYCHOK no cover
            T = self._datum.transform
            if not T.isunity:
                raise RDNAPError('not unity: %r' % (T,))
            self._raiser = True
        if name:
            self.name = name

    def forward(self, lat, lon, height=0, raiser=None, name='forward'):
        '''Convert GRS80 (ETRS98) geodetic C{(B{lat}, B{lon})} and B{C{height}}
           to local C{(RDx, RDy)} coordinates and C{NAPh} quasi-geoid-height.

           @arg lat: Latitude (C{degrees} geodetic).
           @arg lon: Longitude (C{degrees} geodetic).
           @kwarg height: Height, optional (C{meter} above geoid) or C{NAN}
                          to ignore C{NAPh} interpolation.
           @kwarg raiser: If C{True} raise an L{RDNAPError} if B{C{lat}} or
                          B{C{lon}} is outside the C{RD} region (C{bool}),
                          if C{False} don't, overriding property C{raiser}.
           @kwarg name: Optional name (C{str}).

           @return: An L{RDNAP7Tuple}C{(RDx, RDy, NAPh, lat, lon, height, datum)}
                    with local C{RDx}, C{RDy} coordinates and C{NAPh} height.
        '''
        lat,  lon  = Lat(lat), Lon(lon)
        lat0, lon0 = \
        lat_, lon_ = self._forwardXform2(raiser, lat, lon)
        for _ in range(_TRIPS):  # 2.3.3a-f, 1..2
            latc, lonc = self._rdlatlon2(lat_, lon_, lat0, lon0)
            if fabs(latc - lat_) < _TOL_D and \
               fabs(lonc - lon_) < _TOL_D:
                break
            lat_, lon_ = latc, lonc

        phiClamC = _ellipsoidal2spherical(latc, lonc)
        RDx, RDy = _spherical2oblique(*phiClamC)
        NAPh     =  NAN if _isNAN(height) else (height -  # NOT lat0, lon0
                    self._rdNAPh_v(lat, lon, latc, lonc))  # 2.5.2
        return RDNAP7Tuple(RDx, RDy, NAPh,
                           lat, lon, height, self.forwardDatum, name=name)

    def forward3(self, lat, lon, name='forward3'):
        '''Datum transform C{(B{lat}, B{lon})} from GRS80 (ETRS98) to Bessel1841
           (RD-Bessel) as specified by C{RDNAPTRANS(tm)2018_v220627}.

           @return: A L{LatLonDatum3Tuple}C{(lat, lon, datum)} with C{datum} and
                    C{lat} and C{lon} all Bessel1841 (RD-Bessel).
        '''
        x, y, z  = _geodetic2cartesian(lat, lon, A0.H0_ETRS, self._EETRS)
        x, y, z  = _RD._xETRS2RD.transform(x, y, z)  # pseudo
        lat, lon = _cartesian2geodetic(x, y, z, A0.E0)  # pseudo
        return LatLonDatum3Tuple(lat, lon, A0.D0, name=name)

    @property_RO
    def forwardDatum(self):
        '''Get the C{forward} datum (L{Datum}, default GRS80).
        '''
        return self._datum

    def _forwardXform2(self, *args):  # PYCHOK no cover
        return self._notOverloaded(*args)

    def _inside2(self, raiser, lat, lon, **asRD):
        # if RD-Bessel C{(lat, lon)} is not inside C{RD} region
        # raise an error if C{raiser} or self.raiser is True
        if (raiser or (raiser is None and self._raiser)) and \
                   not _RD.isinside(lat, lon, **asRD):
            raise self._outsidError(lat, lon)
        return lat, lon

    def isinside(self, lat, lon, asRD=True, eps=0):
        '''Is geodetic C{(B{lat}, B{lon})} inside the C{RD} or C{ETRS} region (C{bool})?

           @kwarg asRD: Use C{B{asRD}=False} for the C{ETRS} region and in case
                        C{(B{lat}, B{lon})} are ETRS89 (GRS80), not Bessel1841
                        (RD_Bessel) (C{bool}).
           @kwarg eps: Over-/undersize the C{ETRS} or C{RD} region (C{degrees}).
        '''
        return _RD.isinside(Lat(lat), Lon(lon), asRD, eps)

    def _outsidError(self, *lat_lon):
        # format an RDNAPError for C{lat_lon} outside C{RD} region
        return RDNAPError('%r outside %r' % (lat_lon, self.region4()))

    @property_RO
    def _rdgrid(self):  # PYCHOK no cover
        return self._notOverloaded()

    def _rdlatlon2(self, lat, lon, lat0=None, lon0=None):  # 2.3.2
        # return the RD-corrected C{(lat, lon)}
        if _RD.isinside(lat, lon):
            c_f_N_f6 = _RD._c_f_N_f6(lat, lon)
            lat_corr = _bilinear(self._rdgrid._lat_corr, *c_f_N_f6)
            lon_corr = _bilinear(self._rdgrid._lon_corr, *c_f_N_f6)

            if lat0 is lon0 is None:  # reverse
                lat += lat_corr
                lon += lon_corr
            else:  # forward
                lat  = lat0 - lat_corr
                lon  = lon0 - lon_corr
        return lat, lon  # NAN, NAN?

    def rdNAPh(self, lat, lon, raiser=False):  # 2.5.1 and 3.5
        '''Interpolate the C{NAPh} quasi-geoid-height I{within} the C{RD} region.

           @arg lat: Latitude (C{degrees} geodetic).
           @arg lon: Longitude (C{degrees} geodetic).
           @kwarg raiser: If C{True} raise an L{RDNAPError} if B{C{lat}} or
                          B{C{lon}} is outside the C{RD} region (C{bool}),
                          otherwise don't and return C{NAN}.

           @return: C{NAPh} (C{meter}) or C{NAN} if C{B{raiser} is False} and
                    B{C{lat}} or B{C{lon}} is outside the C{RD} region.
        '''
        return self._rdNAPh(Lat(lat), Lon(lon), raiser)

    def _rdNAPh(self, lat, lon, raiser):
        # return C{NAPh} at C{(lat, lon)} or C{NAN} if outside
        if _RD.isinside(lat, lon):  # eps=0
            c_f_N_f6 = _RD._c_f_N_f6(lat, lon)
            return _bilinear(self._rdgrid._NAP_h, *c_f_N_f6)
        elif raiser:
            raise self._outsidError(lat, lon)
        return NAN  # c0 2.5.1e+

    def _rdNAPh_v(self, lat1, lon1, lat2, lon2):
        '''(INTERNAL) Interpolate C{NAPh} at ETRS C{lat1, lon1} for variant 1 or
           at RD-corrected or inverse-projected C{lat2, lon2} for variant 2.
        '''
        return self._rdNAPh(lat2, lon2, False) if self.variant == 2 else \
               self._rdNAPh(lat1, lon1, False)

    @deprecated_property_RO
    def region(self):  # PYCHOK no cover
        '''DEPRECATED on 2026.06.12, use method L{region4()<_RDNAPbase.region4>}.'''
        return self._region4RD

    def region4(self, asRD=True):  # in .rd0._RD
        '''Get the South, West, North and East bounds of the C{RD} or C{ETRS} region.

           @kwarg asRD: Use C{B{asRD}=False} to get the C{ETRS} (ETRS89) instead of the
                        C{RD} (RD-Bessel) region (C{bool}).

           @return: A L{Bounds4Tuple}C{(latS, lonW, latN, lonE)} with C{RD-Bessel}
                    (Bessel1841) or C{ETRS} (ETRS89) geodetic lat- and longtudes.
        '''
        return self._region4RD if asRD else self._region4ETRS

    @property_ROnce
    def _region4ETRS(self):  # as ETRS (ETRS89) L{Bounds4Tuple}
        S, W, N, E = r = self._region4RD
        s, w, _ = self.reverse3(S, W)
        n, e, _ = self.reverse3(N, E)
        _ETRS_  = r.name.replace('RD', 'ETRS')
        return r.classof(s, w, n, e, name=_ETRS_)  # r.dup(latS=s, ...)

    @property_ROnce
    def _region4RD(self):  # as RD-Bessel L{Bounds4Tuple}
        return _RD._region4RD

    def _reverse(self, RDx, RDy, NAPh, asRD=False, raiser=None, name='reverse', asETRS=None):
        '''(INTERNAL) Convert local C{(B{RDx}, B{RDy})} and B{C{NAPh}}
           quasi-geoid-height to geodetic C{lat}, C{lon} and C{height}
           as RD-Bessel C{B{asRD}=True} or ETRS C{B{asRB}=False} or use
           C{B{asETRS}=True} respectively C{False} overriding C{B{asRD}}.
        '''
        phiClamC = _oblique2spherical(RDx, RDy)
        latlon   = _spherical2ellipsoidal(*phiClamC)

        latc, lonc   = self._rdlatlon2(*latlon)
        lat,  lon, d = self._reverseXform3(raiser, latc, lonc)
        h            = NAN if _isNAN(NAPh) else (NAPh +
                       self._rdNAPh_v(lat, lon, *latlon))

        if (asRD if asETRS is None else (not asETRS)):
            lat, lon, d = latc, lonc, A0.D0
        return RDNAP7Tuple(RDx, RDy, NAPh,
                           lat, lon,    h, d, name=name)

    def reverse3(self, lat, lon, name='reverse3'):
        '''Datum transform C{(B{lat}, B{lon})} from Bessel1841 (RD-Bessel) to
           GRS80 (ETRS98) as specified by C{RDNAPTRANS(tm)2018_v220627}.

           @return: A L{LatLon3Tuple}C{(lat, lon, datum)} with C{datum} and
                    C{lat} and C{lon} all GRS80 (ETRS89).
        '''
        x, y, z  = _geodetic2cartesian(lat, lon, A0.H0, A0.E0)
        x, y, z  = _RD._xRD2ETRS.transform(x, y, z)
        lat, lon = _cartesian2geodetic(x, y, z, self._EETRS)
        return LatLonDatum3Tuple(lat, lon, self.forwardDatum, name=name)

    @property_RO
    def reverseDatum(self):
        '''Get the I{default} C{reverse} datum (L{Datum}), GRS80 or Bessel1841.
        '''
        return {1: self._datum,  # self.forwardDatum
                2: A0.D0}.get(self.variant)

    def _reverseXform3(self, *raiser_lat_lon):
        # datum transform C{(lat, lon)} from RD-Bessel to ETRS
        # and raise an C{RDNAPError} if outside the C{RD} region
        lat, lon = self._inside2(*raiser_lat_lon)
        return self.reverse3(lat, lon)

    def similarity(self, inverse=None):  # PYCHOK no cover
        return self._notOverloaded(inverse=inverse)

    def toStr(self, prec=9, **unused):  # PYCHOK signature
        '''Return this C{RDNAP20181v1} or C{-v2} instance as a string.

           @kwarg prec: Precision, number of decimal digits (C{int}, 0..9).

           @return: This C{RDNAP2018v1} or C{-v2} (C{str}).
        '''
        return self.attrs('name', 'variant', 'forwardDatum', prec=prec)  # _ellipsoid_, _name__

    @property_RO
    def variant(self):  # PYCHOK no cover
        return self._notOverloaded()


class RDNAP2018v1(_RDNAPbase):
    '''Transformer implementing C{variant 1} of the U{RDNAPTRANS(tm)2018_v220627
       <https://formulieren.kadaster.nl/aanvragen_rdnaptrans>} specification.

       @note: Method L{RDNAP2018v2.reverse} returns B{by default GRS80 (ETRS89)}
              validated, geodetic lat- and longitudes and datum.
    '''
    if _FOR_DOCS:
        __init__ = _RDNAPbase.__init__
        forward  = _RDNAPbase.forward
        forward3 = _RDNAPbase.forward3

    def _forwardXform2(self, raiser, *lat_lon):  # PYCHOK signature
        # datum transform C{(lat, lon)} from ETRS89 to RD-Bessel
        # and raise an C{RDNAPError} if outside the C{RD} region
        lat, lon, _ = self.forward3(*lat_lon)
        return self._inside2(raiser, lat, lon)

    if _FOR_DOCS:
        isinside = _RDNAPbase.isinside
        rdNAPh   = _RDNAPbase.rdNAPh
        region4  = _RDNAPbase.region4

    @property_ROnce
    def _rdgrid(self):
        try:
            from pyrdnap import v1grid
        except (AttributeError, ImportError, RDNAPError):
            v1grid = _v_gridz_import(self.variant)
        return v1grid

    def reverse(self, RDx, RDy, NAPh=0, asRD=False, **raiser_name):
        '''Convert a local C{(B{RDx}, B{RDy})} point and B{C{NAPh}} height to
           B{GRS80 (ETRS89)} geodetic C{(lat, lon, height)} B{by default}.

           @arg RDx: Local C{RD} X (C{meter}, conventionally).
           @arg RDy: Local C{RD} Y (C{meter}, conventionally).
           @kwarg NAPh: C{NAP} quasi-geoid-height (C{meter}, conventionally)
                        or C{NAN} to ignore C{NAPh} interpolation.
           @kwarg asRD: Use C{B{asRD}=True} to return (non-validated) Bessel1841
                        (RD-Bessel) instead of (validated) GRS80 (ETRS89) geodetic
                        lat- and longitudes (C{bool}).
           @kwarg raiser_name: Like the C{forward} method, C{B{raiser}=None}
                         (C{bool}) and optional C{B{name}='reverse'} (C{str}).

           @return: An L{RDNAP7Tuple}C{(RDx, RDy, NAPh, lat, lon, height, datum)}
                    with geodetic C{lat} and C{lon}, C{height} and C{datum}
                    B{GRS80 (ETRS89)} or C{Bessel1841 (RD-Bessel)}.

           @note: L{RDNAP2018v1.reverse} has been validated only for default
                  C{B{asRD}=False} per C{RDNAPTRANS(tm)2018_v220627}.
        '''
        return self._reverse(RDx, RDy, NAPh, asRD, **raiser_name)

    if _FOR_DOCS:
        reverse3 = _RDNAPbase.reverse3

    def similarity(self, inverse=False):
        '''Get the similarity transform (C{Similarity}).

           @kwarg inverse: Use C{True} for the C{reverse} or C{False}
                           for the C{forward} transform (C{bool}).
        '''
        return _RD._xRD2ETRS if inverse else _RD._xETRS2RD

    @property_ROnce
    def variant(self):
        '''Get this C{RDNAP2018}'s variant (C{int}).
        '''
        return 1


class RDNAP2018v2(_RDNAPbase):
    '''Transformer implementing C{variant 2} of the U{RDNAPTRANS(tm)2018_v220627
       <https://formulieren.kadaster.nl/aanvragen_rdnaptrans>} specification.

       @note: Method L{RDNAP2018v2.reverse} returns B{by default Bessel1841
              (RD-Bessel)} validated, geodetic lat- and longitudes and datum.
    '''
    if _FOR_DOCS:
        __init__ = _RDNAPbase.__init__
        forward  = _RDNAPbase.forward
        forward3 = _RDNAPbase.forward3

    def _forwardXform2(self, *raiser_lat_lon):
        # no datum transform C{(lat, lon)} to RD-Bessel, but
        # raise an C{RDNAPError} if outside the C{RD} region
        return self._inside2(*raiser_lat_lon)  # asRD=False?

    @property_ROnce
    def _rdgrid(self):
        try:
            from pyrdnap import v2grid
        except (AttributeError, ImportError, RDNAPError):
            v2grid = _v_gridz_import(self.variant)
        return v2grid

    if _FOR_DOCS:
        isinside = _RDNAPbase.isinside
        rdNAPh   = _RDNAPbase.rdNAPh
        region4  = _RDNAPbase.region4

    def reverse(self, RDx, RDy, NAPh=0, asRD=True, **raiser_name):
        '''Convert a local C{(B{RDx}, B{RDy})} point and B{C{NAPh}} height to
           B{Bessel1841 (RD-Bessel)} geodetic C{(lat, lon, height)} B{by default}.

           @arg RDx: Local C{RD} X (C{meter}, conventionally).
           @arg RDy: Local C{RD} Y (C{meter}, conventionally).
           @kwarg NAPh: C{NAP} quasi-geoid-height (C{meter}, conventionally) or
                        C{NAN} to ignore C{NAPh} interpolation.
           @kwarg asRD: Use C{B{asRD}=False} to return (non-validated) GRS80
                        (ETRS89) instead of (validated) Bessel1841 (RD-Bessel)
                        geodetic lat- and longitudes (C{bool}).
           @kwarg raiser_name: Like the C{forward} method, C{B{raiser}=None}
                         (C{bool}) and optional C{B{name}='reverse'} (C{str}).

           @return: An L{RDNAP7Tuple}C{(RDx, RDy, NAPh, lat, lon, height, datum)}
                    with geodetic C{lat} and C{lon}, C{height} and C{datum}
                    B{Bessel1841 (RD-Bessel)} or C{GRS80 (ETRS89)}.

           @note: L{RDNAP2018v2.reverse} has been validated only for default
                  C{B{asRD}=True} per C{RDNAPTRANS(tm)2018_v220627}.
        '''
        return self._reverse(RDx, RDy, NAPh, asRD, **raiser_name)

    if _FOR_DOCS:
        reverse3 = _RDNAPbase.reverse3

    def similarity(self, *unused):  # PYCHOK signature
        '''Get the similarity transform, always C{None}.
        '''
        return None

    @property_ROnce
    def variant(self):
        '''Get this C{RDNAP2018}'s variant (C{int}).
        '''
        return 2


def _atan3(y, x, x0):  # 2.2.3e and 3.1.1i
    # equiv to math.atan2 iff x0 is y
    if x > 0:
        r = atan(y / x)
    elif x < 0:
        r = atan(y / x) + copysign(PI, x0)
    else:
        r = copysign(PI_2, x0) if x0 else _0_0
    return r


def _atan_exp(w):  # 2.4.1c
    return atan(exp(w)) * _2_0 - PI_2


def _bilinear(v_grid, c_latI, f_latI, latN_f,  # 2.3.1f and g
                      c_lonI, f_lonI, lonN_f):
    # interpolate a lat_corr_, lon_corr_ or NAP_h...
    assert isinstance(v_grid, _V_grid), v_grid
    ne = v_grid(c_latI, c_lonI)
    nw = v_grid(c_latI, f_lonI)
    se = v_grid(f_latI, c_lonI)
    sw = v_grid(f_latI, f_lonI)
    lonN_f1 = _1_0 - lonN_f  # == 1 - (lonN - f_lonN)
    return (ne * lonN_f + nw * lonN_f1) * latN_f + \
           (se * lonN_f + sw * lonN_f1) * (_1_0 - latN_f)


def _cartesian2geodetic(x, y, z, E):  # 2.2.3 == EcefUPC.reverse?
    # convert cartesian C{(x, y, z)} to C{E}-geodetic C{(lat, lon)}
    r = hypot(x, y)
    if r > _TOL_M:
        a    = E.a * E.e2
        phi_ = atan(z / r)  # atan2(z, r)
        for _ in range(_TRIPS):  # 4..6
            s   = sin(phi_)
            s  *= a / sqrt(_1_0 - s**2 * E.e2)
            phi = atan((z + s) / r)  # atan2(z + s, r)
            if fabs(phi - phi_) < _TOL_R:
                break
            phi_ = phi
    else:
        phi = copysign(PI_2, z)
    lam = _atan3(y, x, y)
    return map1(degrees, phi, lam)  # lat, lon


def _ellipsoidal2spherical(lat, lon):  # 2.4.1
    # convert RD-Bessel C{(lat, lon)} to spherical C{(𝛷, 𝛬)}
    phiC = phi = Phid(lat)
    if PI_2 > phi > -PI_2:  # 2.4.1c
        q = A0.log_tan(phi) - A0.log_e_2(phi)
        w = A0.N0 * q + A0.M0  # 2.4.1b
        phiC = _atan_exp(w)
    lamC = (Lamd(lon) - A0.LAM0) * A0.N0 + A0.LAM0C  # 2.4.1d
    return phiC, lamC  # -Capital 𝛷, 𝛬


def _eq0(r, r0=_0_0):
    return fabs(r - r0) < _TOL_R


# def _eq0d(d, d0=_0_0):
#     return fabs(d - d0) < _TOL_D


def _geodetic2cartesian(lat, lon, h, E):  # 2.2.1
    # convert C{E}-geodetic C{(lat, lon)} to cartesian C{(x, y, z)}
    y, x = sincos2d(lon)
    z, c = sincos2d(lat)
    n  =  E.a / sqrt(_1_0 - z**2 * E.e2)
    H  = _isNAN0(h)
    c *= n + H
    x *= c
    y *= c
    z *= n * (_1_0 - E.e2) + H
    return x, y, z


def _ne0(r, r0=_0_0):
    return fabs(r - r0) > _TOL_R


# def _ne0d(d, d0=_0_0):
#     return fabs(d - d0) > _TOL_D


def _oblique2spherical(x, y):  # 3.1.1
    # inverse oblique stereographic conformal projection from
    # C{RD (x, y)} to spherical C{(𝛷, 𝛬)}, see C++ function
    # sterea_e_inverse in U{Proj/src/projections/sterea.cpp
    # <https://Proj.org/en/stable/operations/projections/sterea.html>}
    x -= A0.X0
    y -= A0.Y0
    r  = hypot(x, y)
    if r > _TOL_M:  # x and y
        s0, c0 = A0.sincos2PHI0C
        sp, cp = sincos2(atan(r / A0.RK2) * _2_0)  # psi  atan2(r, A0.RK2)
        ca = sp * y / r
        xN = cp * c0 - ca * s0
        yN = sp * x / r
        zN = cp * s0 + ca * c0
        phiC = asin(zN)
    else:
        _, xN =  A0.sincos2PHI0C
        yN    = _0_0
        phiC  =  A0.PHI0C  # asin(sin(PHI0C))
    lamC = _atan3(yN, xN, x) + A0.LAM0C
    return phiC, lamC  # -Capital 𝛷, 𝛬


def _spherical2ellipsoidal(phiC, lamC):  # 3.1.2
    # inverse Gauss conformal projection from
    # spherical C{(𝛷, 𝛬)} to RD-Bessel C{(lat, lon)}
    phi = phiC
    if PI_2 > phi > -PI_2:
        q = (A0.log_tan(phi) - A0.M0) / A0.N0
#       w =  A0.log_tan(phi)
        for _ in range(_TRIPS):  # 3..6
            phi_ =  phi
            phi  = _atan_exp(A0.log_e_2(phi) + q)
            if fabs(phi - phi_) < _TOL_R:
                break
    lam  = (lamC - A0.LAM0C) / A0.N0 + A0.LAM0
    lam += floor((PI - lam) / PI2) * PI2
    return map1(degrees, phi, lam)  # lat, lon


def _spherical2oblique(phiC, lamC):  # 2.4.2
    # oblique stereographic conformal projection
    # from spherical C{(𝛷, 𝛬)} to C{RD (x, y)}
    x = A0.X0  # 2.4.2g
    y = A0.Y0  # 2.4.2h
    a = phiC - A0.PHI0C  # 𝛷 - 𝛷0
    b = lamC - A0.LAM0C  # 𝛬 - 𝛬0
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
            t  = sp_22 * _2_0  # 0 < t < 2
            q  = A0.RK2 / (_2_0 - t)
            x += q * (c * sin(b))
            y += q * (s - s0 + s0 * t) / c0
    elif _eq0(a) and _eq0(b):
        pass
    else:  # if _eq0(phiC, -A0.PHI0C) and _eq0(lamC, A0.LAM0C - PI):
        x = y = NAN
#   else:
#       raise RDNAPError(str((phiC, lamC)))
    return x, y


__all__ += _ALL_DOCS(_RDNAPbase)
__all__ += _ALL_OTHER(RDNAP2018v1, RDNAP2018v2, RDNAPError,
                      Datum, Ellipsoid, LatLonDatum3Tuple)  # passed along from PyGeodesy

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
