
# -*- coding: utf-8 -*-

u'''Main classes L{RDNAP2018v1} and L{RDNAP2018v2} follow C{variant 1} respectively C{variant
2} of the U{RDNAPTRANS(tm)2018_v220627<https://formulieren.kadaster.nl/aanvragen_rdnaptrans>}
specification.  Each provide a C{forward} method to convert geodetic lat-/longitudes and height
to local C{RD} coodinates and C{NAP} heights and a C{reverse} method for converting vice-versa.

The L{RDNAP2018v1.forward} and L{.reverse<RDNAP2018v1.reverse>} results have been formally
validated to meet the C{RDNAPTRANS(tm)2018_v220627} requirements.

Likewise for the L{RDNAP2018v2.forward} and L{.reverse<RDNAP2018v2.reverse>} results.
'''
# make sure int/int division yields float quotient, see .basics
from __future__ import division as _; del _  # noqa: E702 ;

from pyrdnap.rd0 import _RD, _RD0 as A0, RDNAP7Tuple
from pyrdnap.v_grids import _v_grid  # _V_grid
from pyrdnap.__pygeodesy import (_0_0, _0_5, _1_0, _2_0,
                                 _isNAN, _isNAN0, _earth_datum, _xkwds_pop2,
                                 _name_, _ALL_DOCS, _all_OTHER, _FOR_DOCS,
                                 _NamedBase, RDNAPError)
from pygeodesy import (map1, EPS0, EPS1, NAN, PI_2, PI, PI2,  # basics, "consterns"
                       typename, LatLonDatum3Tuple, RD4Tuple,  # namedTuples
                       deprecated_property_RO, property_RO, property_ROnce,  # props
                       Degrees, Lamd, Lat, Lon, Meter, Phid,  # units
                       sincos2, sincos2d)  # utily

from math import asin, atan, copysign, degrees, exp, \
                 fabs, floor, hypot, radians, sin, sqrt

__all__ = ()
__version__ = '26.07.09'

_forward_  = 'forward'
_outside__ = 'outside '
_region4   = _RD._region4
_reverse_  = 'reverse'
_TOL_D     = 1e-9  # degrees 2.3.3f+
_TOL_M     = 1e-6  # meter
_TOL_R     = radians(_TOL_D)  # 2e-11
_TRIPS     = 16    # 5..6 sufficient


class _RDNAPbase(_NamedBase):
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
            raise RDNAPError(repr(E), txt='not oblate')
        if raiser:  # PYCHOK no cover
            T = self._datum.transform
            if not T.isunity:
                raise RDNAPError(repr(T), txt='not unity')
            self.raiser = True
        if name:
            self.name = name

    def _forward(self, lat, lon, height=0, raiser=None, name=_forward_):
        '''(INTERNAL) Convert geodetic C{(B{lat}, B{lon})} and B{C{height}}
           to local C{(RDx, RDy)} coordinates and C{NAPh} quasi-geoid-height.
        '''
        lat, lon, _NAN = _LatLon3(lat, lon)
        if _NAN:
            RDx = RDy = NAPh = NAN
        else:
            RDx, RDy, NAPh = self._forward3(raiser, lat, lon, height)
        return RDNAP7Tuple(RDx, RDy, NAPh,
                           lat, lon, height, self.forwardDatum, name=name)

    def _forward2(self, lat, lon):
        # datum-transform C{(lat, lon)} from ETRS to RD-Bessel
        x, y, z = _geodetic2cartesian(lat, lon, A0.H0_ETRS, self._EETRS)
        x, y, z = _RD._xETRS2RD.transform(x, y, z)  # pseudo
        return _cartesian2geodetic(x, y, z, A0.E0)  # pseudo

    def _forward2x(self, *args):  # PYCHOK no cover
        return self._notOverloaded(*args)

    def _forward3(self, raiser, lat, lon, height):  # in .__main__
        # C{_forward} core, returning C{(RDx, RDy, NAPh)}
        lat0, lon0 = \
        lat_, lon_ = self._forward2x(raiser, lat, lon)
        for _ in range(_TRIPS):  # 2.3.3a-f, 1..2
            latc, lonc = self._rdlatlon2(lat_, lon_, lat0, lon0)
            if fabs(latc - lat_) < _TOL_D and \
               fabs(lonc - lon_) < _TOL_D:
                break
            lat_, lon_ = latc, lonc

        phiClamC = _ellipsoidal2spherical(latc, lonc)
        RDx, RDy = _spherical2oblique(*phiClamC)
        NAPh     =  NAN if height is None or _isNAN(height) else (
                    height - self._rdNAPh_v(lat, lon, latc, lonc))
        return RDx, RDy, NAPh

    def forward3(self, lat, lon, **name):
        '''Datum-transform C{(B{lat}, B{lon})} from GRS80 (ETRS98) to Bessel1841
           (RD-Bessel) as specified by C{RDNAPTRANS(tm)2018_v220627} both in-
           and outside the C{RD} region.

           @return: A L{LatLonDatum3Tuple}C{(lat, lon, datum)} with C{lat},
                    C{lon} and C{datum} all Bessel1841 (RD-Bessel).
        '''
        lat, lon, _NAN = _LatLon3(lat, lon)
        if _NAN:
            lat = lon = NAN
        else:
            lat, lon = self._forward2(lat, lon)
        n = name.get(_name_, typename(_RDNAPbase.forward3))
        return LatLonDatum3Tuple(lat, lon, A0.D0, name=n)

    @property_RO
    def forwardDatum(self):
        '''Get the C{forward} datum (L{Datum}, default GRS80).
        '''
        return self._datum

    def _inside2(self, raiser, lat, lon):
        # if RD-Bessel or ETRS C{(lat, lon)} is outside the C{RD}
        # region raise an error if C{raiser} or self.raiser is True
        if (raiser or (raiser is None and self.raiser)) and \
                      not _isinside(lat, lon):  # _region4
            raise self._outsidError(lat, lon)   # _region4
        return lat, lon

    def isinside(self, lat, lon, eps=0):
        '''Is geodetic C{(B{lat}, B{lon})} inside the C{RD region4}?

           @arg lat: Latitude (C{degrees}, geodetic).
           @arg lon: Longitude (C{degrees}, geodetic).
           @kwarg eps: Over-/undersize the C{RD} region (C{degrees}).

           @return: C{None} if B{C{lat}} or B{C{lon}} is NAN, C{False}
                    if outside the C{RD} region, C{True} otherwise.
        '''
        lat, lon, _NAN = _LatLon3(lat, lon)
        return None if _NAN else _isinside(lat, lon, Degrees(eps=eps))

    def isinsideRD(self, RDx, RDy, eps=0):
        '''Is local C{(B{RDx}, B{RDy})} inside the C{RD region4RD}?

           @arg RDx: X coordinate (C{meter}, local).
           @arg RDy: Y coordinate (C{meter}, local).
           @kwarg eps: Over-/undersize the C{RD} region (C{meter}).

           @return: C{None} if B{C{RDx}} or B{C{RDy}} is NAN, C{False}
                    if outside the C{RD} region, C{True} otherwise.
        '''
        x, y, _NAN = _RDxRDy3(RDx, RDy)
        return None if _NAN else _isinside(x, y, Meter(eps=eps), self.region4(True))

    def _outsidError(self, *lat_lon):
        # format an RDNAPError for C{lat_lon} outside the RD region
        E = RDNAPError(lat_lon, txt=_outside__ + _region4.toRepr())
        return E

    @property
    def raiser(self):
        '''Do points outside the C{RD} region cause an C{RDNAPError}?
        '''
        return self._raiser

    @raiser.setter  # PYCHOK setter!
    def raiser(self, raiser):
        '''Use C{True} to throw an C{RDNAPError} for points outside the C{RD} region.
        '''
        self._raiser = bool(raiser)

    @property_RO
    def _rdgrid(self):  # PYCHOK no cover
        return self._notOverloaded()

    def _rdlatlon2(self, lat, lon, lat0=None, lon0=None):  # 2.3.2
        # return the RD-corrected C{(lat, lon)} if inside
        if _isinside(lat, lon):
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

    def rdNAPh(self, lat, lon, height=0):  # 2.5.1 and 3.5
        '''Interpolate the C{NAPh} quasi-geoid-height for a point
           C{(lat, lon)} I{within} the C{RD} region.

           @arg lat: Latitude (C{degrees}, geodetic).
           @arg lon: Longitude (C{degrees}, geodetic).
           @kwarg height: Optional geoid height (C{meter}, conventionally).

           @return: C{NAPh} quasi-geoid-height (C{meter}) or C{NAN} if
                    B{C{lat}} or B{C{lon}} is outside the C{RD} region.
        '''
        lat, lon, _NAN = _LatLon3(lat, lon)
        if _NAN:
            h = NAN
        else:
            h = self._rdNAPh(lat, lon)
            if not _isNAN(h):
                h = Meter(height=height) - h
        return Meter(NAPh=h)

    def _rdNAPh(self, lat, lon):
        # return C{NAPh} at C{(lat, lon)} or C{NAN} if
        # outside or ... if _isNAN(lat) or _isNAN(lon)
        if _isinside(lat, lon):
            c_f_N_f6 = _RD._c_f_N_f6(lat, lon)
            return _bilinear(self._rdgrid._NAP_h, *c_f_N_f6)
        return NAN  # c0 2.5.1e+

    def _rdNAPh_v(self, lat1, lon1, lat2, lon2):
        # interpolate C{NAPh} at ETRS C{lat1, lon1} for variant 1 or at
        # RD-corrected or inverse-projected C{lat2, lon2} for variant 2
        return self._rdNAPh(lat2, lon2) if self.variant == 2 else \
               self._rdNAPh(lat1, lon1)

    @deprecated_property_RO
    def region(self):  # PYCHOK no cover
        '''DEPRECATED on 2026.06.12, use method L{region4()<_RDNAPbase.region4>}.'''
        return self._region4()

    def region4(self, asRD=False):
        '''Get the South, West, North and East bounds of the C{RD} region.

           @kwarg asRd: Use C{B{asRD}=True} for the bounds in C{RD meter},
                        otherwise C{degrees} (C{bool}).

           @return: A L{Bounds4Tuple}C{(latS, lonW, latN, lonE)} with
                    geodetic lat- and longitudes in C{degrees} or an
                    L{RD4Tuple}C{(minRDx, minRDy, maxRDx, maxRDy)} with
                    the bounds in C{meter}, truncated to C{millimeter}.
        '''
        return self._region4RD[self.variant] if asRD else _region4

    @property_ROnce
    def _region4RD(self):
        # C{RD} regions in C{meter}, see .__main__._RD4Tuple
        n = _region4.name
        d = {1: RD4Tuple(-87853.981, 228817.837, 318159.693, 894090.744, name=n),
             2: RD4Tuple(-87776.807, 228895.002, 317993.007, 893924.047, name=n)}
        return d

    def _reverse(self, RDx, RDy, NAPh, raiser=None, name=_reverse_):
        '''(INTERNAL) Convert local C{(B{RDx}, B{RDy})} and B{C{NAPh}}
           quasi-geoid-height to geodetic C{lat}, C{lon} and C{height}.
        '''
        RDx, RDy, _NAN = _RDxRDy3(RDx, RDy)
        if _NAN:
            h = lat = lon = NAN
        else:
            lat, lon, h = self._reverse3(raiser, RDx, RDy, NAPh)
        return RDNAP7Tuple(RDx, RDy, NAPh,
                           lat, lon,    h, self.reverseDatum, name=name)

    def _reverse2(self, lat, lon):
        # datum-transform C{(lat, lon)} from RD-Bessel to ETRS
        x, y, z = _geodetic2cartesian(lat, lon, A0.H0, A0.E0)
        x, y, z = _RD._xRD2ETRS.transform(x, y, z)
        return _cartesian2geodetic(x, y, z, self._EETRS)

    def _reverse3(self, raiser, RDx, RDy, NAPh):  # in .__main__
        # C{_reverse} core, returning C{(lat, lon, height)}
        phiClamC = _oblique2spherical(RDx, RDy)
        latlon   = _spherical2ellipsoidal(*phiClamC)  # RD-Bessel

        latlon   = self._inside2(raiser, *latlon)
        latclonc = self._rdlatlon2(*latlon)  # RD-corrected
        lat, lon = self._reverse2(*latclonc)
        h        = NAN if NAPh is None or _isNAN(NAPh) else (
                   NAPh + self._rdNAPh_v(lat, lon, *latclonc))
        return lat, lon, h

    def reverse3(self, lat, lon, **name):
        '''Datum-transform C{(B{lat}, B{lon})} from Bessel1841 (RD-Bessel) to
           GRS80 (ETRS98) as specified by C{RDNAPTRANS(tm)2018_v220627}, both
           in- and outside the C{RD} region.

           @return: A L{LatLonDatum3Tuple}C{(lat, lon, datum)} with C{lat},
                    C{lon} and C{datum} all GRS80 (ETRS89).
        '''
        lat, lon, _NAN = _LatLon3(lat, lon)
        if _NAN:
            lat = lon = NAN
        else:
            lat, lon = self._reverse2(lat, lon)
        n = name.get(_name_, typename(_RDNAPbase.reverse3))
        return LatLonDatum3Tuple(lat, lon, self.reverseDatum, name=n)

    @property_RO
    def reverseDatum(self):
        '''Get the C{reverse} datum (L{Datum}, default GRS80).
        '''
        return self._datum  # sae as .forwardDatum

    def similarity(self, inverse=None):  # PYCHOK no cover
        return self._notOverloaded(inverse=inverse)

    def toStr(self, prec=9, **unused):  # PYCHOK signature
        '''Return this C{RDNAP20181v1} or C{-v2} instance as a string.

           @kwarg prec: Precision, number of decimal digits (C{int}, 0..9).

           @return: This C{RDNAP2018v1} or C{-v2} (C{str}).
        '''
        return self.attrs(_name_, 'variant', 'forwardDatum', prec=prec)  # _ellipsoid_, _name__

    @property_RO
    def variant(self):  # PYCHOK no cover
        return self._notOverloaded()


class RDNAP2018v1(_RDNAPbase):
    '''Transformer implementing C{variant 1} of the U{RDNAPTRANS(tm)2018_v220627
       <https://formulieren.kadaster.nl/aanvragen_rdnaptrans>} specification.
    '''
    if _FOR_DOCS:
        __init__ = _RDNAPbase.__init__

    def forward(self, lat, lon, height=0, **raiser_name):
        '''Convert GRS80 (ETRS98) geodetic C{(B{lat}, B{lon})} and B{C{height}}
           to local C{RDx}, C{RDy} coordinates and C{NAPh} quasi-geoid-height.

           @arg lat: Latitude (C{degrees} geodetic).
           @arg lon: Longitude (C{degrees} geodetic).
           @kwarg height: Height, optional (C{meter} above geoid) or C{NAN}
                          to ignore C{NAPh} interpolation.
           @kwarg raiser_name: Use C{B{raiser}=True} to raise an L{RDNAPError}
                         if B{C{lat}} or B{C{lon}} is outside the C{RD} region,
                         overriding property C{raiser} (C{bool}) and optional
                         C{B{name}='forward'} (C{str}).

           @return: An L{RDNAP7Tuple}C{(RDx, RDy, NAPh, lat, lon, height, datum)}
                    with local C{RDx}, C{RDy} coordinates and C{NAPh} height, all
                    in C{meter} or with C{height} is C{NAN} if C{lat} or C{lon} is
                    outside the C{RD} region.

           @raise RDNAPError: If the point is outside the C{RD} region and property
                              C{raiser is True} or keyword argument C{B{raiser}=True}.
        '''
        return self._forward(lat, lon, height, **raiser_name)

    def _forward2x(self, raiser, *lat_lon):  # PYCHOK signature
        # datum-transform C{(lat, lon)} from ETRS89 to RD-Bessel
        # and raise an C{RDNAPError} if outside the C{RD} region
        lat_lon = self._forward2(*lat_lon)
        return self._inside2(raiser, *lat_lon)

    if _FOR_DOCS:
        forward3   = _RDNAPbase.forward3
        isinside   = _RDNAPbase.isinside
        isinsideRD = _RDNAPbase.isinsideRD

    @property_ROnce
    def _rdgrid(self):
        try:
            from pyrdnap import v1grid
        except Exception as x:
            raise RDNAPError(_v_grid(1), cause=x)
        return v1grid

    if _FOR_DOCS:
        rdNAPh  = _RDNAPbase.rdNAPh
        region4 = _RDNAPbase.region4

    def reverse(self, RDx, RDy, NAPh=0, **raiser_name):
        '''Convert a local C{(B{RDx}, B{RDy})} point and B{C{NAPh}} height to
           GRS80 (ETRS89) geodetic lat-, longitude and height, B{by default}.

           @arg RDx: Local C{RD} X (C{meter}, conventionally).
           @arg RDy: Local C{RD} Y (C{meter}, conventionally).
           @kwarg NAPh: C{NAP} quasi-geoid-height (C{meter}, conventionally) or
                        C{NAN} to ignore C{NAPh} interpolation.
           @kwarg raiser_name: Use C{B{raiser}=True} to raise an L{RDNAPError}
                         for points outside the C{RD} region, overriding property
                         C{raiser} (C{bool}) and an optional C{B{name}='reverse'}
                         (C{str}).

           @return: An L{RDNAP7Tuple}C{(RDx, RDy, NAPh, lat, lon, height, datum)}
                    with geodetic C{lat}, C{lon} and C{datum} GRS80 (ETRS89) and
                    C{height} in C{meter} or C{NAN} if C{lat} or C{lon} is outside
                    the C{RD} region.

           @raise RDNAPError: If the point is outside the C{RD} region and property
                              C{raiser is True} or keyword argument C{B{raiser}=True}.
        '''
        return self._reverse(RDx, RDy, NAPh, **raiser_name)

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
    '''
    if _FOR_DOCS:
        __init__ = _RDNAPbase.__init__

    def forward(self, lat, lon, height=0, **raiser_name):
        '''Convert GRS80 (ETRS98) geodetic C{(B{lat}, B{lon})} and B{C{height}}
           to local C{RDx, RDy} coordinates and C{NAPh} quasi-geoid-height,
           provided the point is not outside the C{RD} region.

           @arg lat: Latitude (C{degrees} geodetic).
           @arg lon: Longitude (C{degrees} geodetic).
           @kwarg height: Height, optional (C{meter} above geoid) or C{NAN}
                          to ignore C{NAPh} interpolation.
           @kwarg raiser_name: Use C{B{raiser}=True} to raise an L{RDNAPError}
                         if B{C{lat}} or B{C{lon}} is outside the C{RD} region,
                         overriding property C{raiser} (C{bool}) and an optional
                         C{B{name}='forward'} (C{str}).

           @return: An L{RDNAP7Tuple}C{(RDx, RDy, NAPh, lat, lon, height, datum)}
                    with local C{RDx}, C{RDy} coordinates and C{NAPh} height, all
                    in C{meter} or all C{NAN} if C{lat} or C{lon} is outside the
                    C{RD} region.

           @raise RDNAPError: If the point is outside the C{RD} region and property
                              C{raiser is True} or keyword argument C{B{raiser}=True}.
        '''
        raiser, name = _xkwds_pop2(raiser_name, raiser=self.raiser)
        try:  # force outside exception
            r = self._forward(lat, lon, height, raiser=True, **name)
        except RDNAPError as x:
            if raiser or _outside__ not in str(x):
                raise  # reraise
            d = self.forwardDatum
            n = name.get(_name_, _forward_)
            r = RDNAP7Tuple(NAN, NAN, NAN, lat, lon, height, d, name=n)
        return r

    def _forward2x(self, *raiser_lat_lon):  # 2.3.4
        # NO datum-transform C{(lat, lon)} to RD-Bessel, but
        # raise an C{RDNAPError} if outside the C{RD} region
        # (using the ETRS as RD-Bessel lat- and longitudes)
        return self._inside2(*raiser_lat_lon)

    if _FOR_DOCS:
        forward3   = _RDNAPbase.forward3
        isinside   = _RDNAPbase.isinside
        isinsideRD = _RDNAPbase.isinsideRD

    @property_ROnce
    def _rdgrid(self):
        try:
            from pyrdnap import v2grid
        except Exception as x:
            raise RDNAPError(_v_grid(2), cause=x)
        return v2grid

    if _FOR_DOCS:
        rdNAPh  = _RDNAPbase.rdNAPh
        region4 = _RDNAPbase.region4

    def reverse(self, RDx, RDy, NAPh=0, **raiser_name):
        '''Convert a local C{(B{RDx}, B{RDy})} point and B{C{NAPh}} height to
           GRS80 (ETRS89) geodetic lat-, longitude and height, provided the
           point is not outside the C{RD} region.

           @arg RDx: Local C{RD} X (C{meter}, conventionally).
           @arg RDy: Local C{RD} Y (C{meter}, conventionally).
           @kwarg NAPh: C{NAP} quasi-geoid-height (C{meter}, conventionally) or
                        C{NAN} to ignore C{NAPh} interpolation.
           @kwarg raiser_name: Use C{B{raiser}=True} to raise an L{RDNAPError}
                         for points outside the C{RD} region, overriding property
                         C{raiser} (C{bool}) and an optional C{B{name}='reverse'}
                         (C{str}).

           @return: An L{RDNAP7Tuple}C{(RDx, RDy, NAPh, lat, lon, height, datum)}
                    with geodetic C{lat}, C{lon} and C{datum} GRS80 (ETRS89) and
                    C{height} in C{meter} or with C{lat}, C{lon} and C{height}
                    all C{NAN} if outside the C{RD} region.

           @raise RDNAPError: If the point is outside the C{RD} region and property
                              C{raiser is True} or keyword argument C{B{raiser}=True}.
        '''
        raiser, name = _xkwds_pop2(raiser_name, raiser=self.raiser)
        try:  # force outside exception
            r = self._reverse(RDx, RDy, NAPh, raiser=True, **name)
        except RDNAPError as x:
            if raiser or _outside__ not in str(x):
                raise  # reraise
            d = self.reverseDatum
            n = name.get(_name_, _reverse_)
            r = RDNAP7Tuple(RDx, RDy, NAPh, NAN, NAN, NAN, d, name=n)
        return r

    if _FOR_DOCS:
        reverse3 = _RDNAPbase.reverse3

    def similarity(self, inverse=False):
        '''Get the similarity transform (C{None}, always).
        '''
        return None if inverse else None

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
#   elif _isNAN(x) or _isNAN(y) or _isNAN(x0):
#       r = NAN
    else:
        r = copysign(PI_2, x0) if x0 else _0_0
    return r


def _atan_exp(w):  # 2.4.1c
    return atan(exp(w)) * _2_0 - PI_2


def _bilinear(v_grid, c_latI, f_latI, latN_f,  # 2.3.1f and g
                      c_lonI, f_lonI, lonN_f):
    # interpolate a lat_corr_, lon_corr_ or NAP_h...
    # assert isinstance(v_grid, _V_grid), v_grid
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
#   if _isNAN(r) or _isNAN(z):
#       return NAN, NAN
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
    phiC = phi = Phid(lat)  # clip=90
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


def _isinside(lat, lon, eps=0, region4=_region4):
    # is C{(lat, lon)} inside C{region4}, optionally over-
    # or undersized by positive respectively negative C{eps}?
    S, W, N, E = region4
    return ((S - lat) <= eps and (lat - N) <= eps and
            (W - lon) <= eps and (lon - E) <= eps) if eps else \
            (S <= lat <= N   and  W <= lon <= E)


def _LatLon3(lat, lon):
    lat, lon = Lat(lat), Lon(lon)
    return lat, lon, (_isNAN(lon) or _isNAN(lat))


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
#   elif _isNAN(r):
#       return NAN, NAN
    else:
        _, xN =  A0.sincos2PHI0C
        yN    = _0_0
        phiC  =  A0.PHI0C  # asin(sin(PHI0C))
    lamC = _atan3(yN, xN, x) + A0.LAM0C
    return phiC, lamC  # -Capital 𝛷, 𝛬


def _RDxRDy3(RDx, RDy):
    x, y = map1(Meter, RDx, RDy)
    return x, y, (_isNAN(x) or _isNAN(y))


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
#       raise RDNAPError((phiC, lamC))
    return x, y


__all__ += _ALL_DOCS(_RDNAPbase)
__all__ += _all_OTHER(RDNAP2018v1, RDNAP2018v2, RD4Tuple)
del _ALL_DOCS, _all_OTHER

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
