
# -*- coding: utf-8 -*-

u'''Main classes L{RDNAP2018v1} and L{RDNAP2018v2} follow C{variant 1} respectively C{variant 2}
of the specification U{RDNAPTRANS(tm)2018<https://formulieren.kadaster.nl/aanvragen_rdnaptrans>}.
Each provide a C{forward} method to convert geodetic lat-/longitudes and heights to C{RD}
coodinates and C{NAP} heights and a C{reverse} method for converting the other way.

The C{forward} and C{reverse} results of L{RDNAP2018v1} meet the C{RDNAPTRANS(tm)2018_v220627}
self-validation requirements of C{0.000000010 degrees} and C{0.0010 meter} for tests inside
the C{RD} region, see B{C{Note below}}.  Class L{RDNAP2018v2} does not and is not required to.

The original C{RDNAPTRANS(tm)2018_v220627} grid files for both variants are I{not included}
in C{PyPRDNAP} and C{pyrdnap} due to the size of those files.  Instead, the grid files for each
variant I{include only} the C{lat_corr_}, C{lon_corr_} and C{_NAP_quasi_geoid_height_...} columns,
extracted from the original grid files with leading and trailing zeros removed and formatted as
row-order matrices.

@note: L{RDNAP2018v1}, C{PyRDNAP} and C{pyrdnap} have B{not been formally validated} and are
       B{not certified} to carry the trademark name C{RDNAPTRANS(tm)}.
'''
# make sure int/int division yields float quotient, see .basics
from __future__ import division as _; del _  # noqa: E702 ;

from pyrdnap.rd0 import _RD, _RD0 as A0, RDNAP7Tuple
from pyrdnap.v_grids import _V_grid, _v_gridz_import
from pyrdnap.__pygeodesy import (_0_0, _0_5, _1_0, _2_0,
                                 _isNAN, _earth_datum,
                                 _ALL_DOCS, _ALL_OTHER, _FOR_DOCS,
                                 _NamedBase, notOverloaded)
from pygeodesy import (EPS0, EPS1, NAN, PI_2, PI, PI2,  # "consterns"
                       Datum, Datums, Ellipsoid,  # datums, ellipsoids
                       property_RO, property_ROnce,  # props
                       Lamd, Phid,  # units
                       sincos2, sincos2d)  # utily

from math import asin, atan, copysign, degrees, exp, \
                 fabs, floor, hypot, radians, sin, sqrt

__all__ = ()
__version__ = '26.05.08'

_TOL_D = 1e-9  # degrees 2.3.3f+
_TOL_M = 1e-6  # meter
_TOL_R = radians(_TOL_D)  # 2e-11
_TRIPS = 16    # 5..6 sufficient


class _RDNAPbase(_NamedBase):
    '''(INTERNAL) L{RDNAP2018v1}C{/-v2} base class.
    '''
    _datum  = None  # forward, v1 reverse Datum, lazily
    _EETRS  = None  # forward, v1 reverse Ellipsoid, lazily
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

           @raise RDNAPError: Ellipsoid (or datum) is not oblate (i.e. is spherical or
                              prolate) or the datum's C{transform} is not C{unity}.
        '''
        if a_ellipsoid is f is None:
            self._datum = Datums.GRS80
        else:
            _earth_datum(a_ellipsoid, f, **name)  # sets self._datum
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

    def forward(self, lat, lon, height=0, raiser=None, name='forward'):
        '''Convert geodetic GRS80 (ETRS98) C{(B{lat}, B{lon})} and B{C{height}}
           to local C{(RDx, RDy)} coordinates and C{NAPh} quasi-geoid-height.

           @arg lat: Latitude (C{degrees} geodetic).
           @arg lon: Longitude (C{degrees} geodetic).
           @kwarg height: Height, optional (C{meter} above geoid) or C{NAN}
                          to ignore C{NAPh} interpolation.
           @kwarg raiser: If C{True} raise an L{RDNAPError} if B{C{lat}} or
                          B{C{lon}} is outside the C{RD} region (C{bool}),
                          if C{False} don't, overriding property C{raiser}.
           @kwarg name: Optional C{B{name}='forward'} (C{str}).

           @return: An L{RDNAP7Tuple}C{(RDx, RDy, NAPh, lat, lon, height, datum)}
                    with local C{RDx}, C{RDy} coordinates and C{NAPh} height.
        '''
        lat0, lon0 = \
        lat_, lon_ = self._forwardXform(lat, lon, raiser)
        for _ in range(_TRIPS):  # 2.3.3a-f, 1..2
            latc, lonc = self._rdlatlon2(lat_, lon_, lat0, lon0)
            if fabs(latc - lat_) < _TOL_D and \
               fabs(lonc - lon_) < _TOL_D:
                break
            lat_, lon_ = latc, lonc

        philamC  = _ellipsoidal2spherical(latc, lonc)
        RDx, RDy = _spherical2oblique(*philamC)
        NAPh     =  NAN if _isNAN(height) else (height - self.rdNAPh(lat, lon))  # 2.5.2
        return RDNAP7Tuple(RDx, RDy, NAPh, lat, lon, height,
                                           self.forwardDatum, name=name)

    @property_RO
    def forwardDatum(self):
        '''Get the geodetic C{forward} datum (L{Datum}).
        '''
        return self._datum

    def _inside2(self, lat, lon, raiser):
        # default and variant 2: no datum Xform
        if (raiser or (raiser is None and self._raiser)) and \
                   not _RD.isinside(lat, lon):
            raise self._outsidError(lat, lon)
        return lat, lon

    _forwardXform = _inside2  # no datum Xform

    def isinside(self, lat, lon, eps=0):
        '''Is C{(B{lat}, B{lon})} inside the C{RD} region (C{bool})?

           @kwarg eps: Over-/undersize the C{RD} region (C{degrees}).
        '''
        return _RD.isinside(lat, lon, eps)

    def _outsidError(self, *lat_lon):
        # format an RDNAPError for C{lat_lon} outside C{RD} region
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
        return lat, lon  # NAN, NAN?

    def rdNAPh(self, lat, lon, raiser=False):  # 2.5.1 and 3.5
        '''Interpolate the C{NAP_h} quasi-geoid-height
           I{within} the C{RD} region.

           @arg lat: Latitude (C{degrees} GRS80 (ETRS89), geodetic).
           @arg lon: Longitude (C{degrees} GRS80 (ETRS89), geodetic).
           @kwarg raiser: If C{True} raise an L{RDNAPError} if B{C{lat}} or
                          B{C{lon}} is outside the C{RD} region (C{bool}),
                          otherwise don't abd return C{NAN}.

           @return: C{NAPh} (C{meter}) or C{NAN} if B{C{lat}}
                    or B{C{lon}} is outside the C{RD} region.
        '''
        if _RD.isinside(lat, lon):
            c_f_N_f6 = _RD.c_f_N_f6(lat, lon)
            NAP_h    = _bilinear(self._rdgrid._NAP_h, *c_f_N_f6)
            return NAP_h
        elif raiser:
            raise self._outsidError(lat, lon)
        return NAN  # c0 2.5.1e+

    @property_RO
    def region(self):
        '''Get the C{RD} region as L{RDregion4Tuple}C{(S, W, N, E)}, all C{GRS80 (ETRS89) degrees}.
        '''
        return _RD.region

    def _reverse(self, RDx, RDy, NAPh, raiser, name='reverse'):
        '''(INTERNAL) Convert local C{(B{RDx}, B{RDy})} coordinates and
           B{C{NAPh}} quasi-geoid-height to geodetic GRS80 (ETRS89) or
           Bessel1841 (RD-Bessel) C{lat}, C{lon} and C{height}.
        '''
        philamC  = _oblique2spherical(RDx, RDy)
        lat, lon = _spherical2ellipsoidal(*philamC)

        lat, lon = self._rdlatlon2(lat, lon)
        lat, lon = self._reverseXform(lat, lon, raiser)
        h        = NAN if _isNAN(NAPh) else (NAPh + self.rdNAPh(lat, lon))
        return RDNAP7Tuple(RDx, RDy, NAPh, lat, lon, h,
                                           self.reverseDatum, name=name)

    @property_RO
    def reverseDatum(self):
        '''Get the geodetic C{reverse} datum (L{Datum}), GRS80 or Bessel1841.
        '''
        return {1: self._datum,
                2: A0.D0}.get(self.variant)

    _reverseXform = _inside2  # no datum Xform

    def toStr(self, prec=9, **unused):  # PYCHOK signature
        '''Return this C{RDNAP2018#v} instance as a string.

           @kwarg prec: Precision, number of decimal digits (0..9).

           @return: This C{RDNAP2018#v} (C{str}).
        '''
        return self.attrs('name', 'variant', 'forwardDatum', prec=prec)  # _ellipsoid_, _name__

    @property_RO
    def variant(self):
        raise None


class RDNAP2018v1(_RDNAPbase):
    '''Transformer implementing RD NAP 2018 C{variant 1}.
    '''
    if _FOR_DOCS:
        __init__ = _RDNAPbase.__init__
        forward  = _RDNAPbase.forward

    def _forwardXform(self, lat, lon, raiser):
        # transform C{(lat, lon)} from ETRS (GRS80) to RD-Bessel datum
        x, y, z  = _geodetic2cartesian(lat, lon, self._EETRS, A0.H0_ETRS)
        x, y, z  = _RD._xETRS2RD.transform(x, y, z)
        lat, lon = _cartesian2geodetic(x, y, z, A0.E0)
        return self._inside2(lat, lon, raiser)

    @property_ROnce
    def _rdgrid(self):
        try:
            from pyrdnap import v1grid
        except (AttributeError, ImportError):
            v1grid = _v_gridz_import(self.variant)
        return v1grid

    def reverse(self, RDx, RDy, NAPh=0, raiser=None, **name):  # RDNAP to GRS80 (ETRS89)
        '''Convert a local C{(B{RDx}, B{RDy})} point and B{C{NAPh}} height
           to geodetic B{GRS80 (ETRS89)} C{(lat, lon, height)}.

           @arg RDx: Local C{RD} X (C{meter}, conventionally).
           @arg RDy: Local C{RD} Y (C{meter}, conventionally).
           @kwarg NAPh: C{NAP} quasi-geoid-height (C{meter}, conventionally)
                        or C{NAN} to ignore C{NAPh} interpolation.
           @kwarg raiser: If C{True} raise an L{RDNAPError} if C{lat} or
                          C{lon} is outside the C{RD} region (C{bool}), if
                          C{False} don't, overriding property C{raiser}.
           @kwarg name: Optional C{B{name}='reverse'} (C{str}).

           @return: An L{RDNAP7Tuple}C{(RDx, RDy, NAPh, lat, lon, height,
                    datum)} with geodetic C{lat} and C{lon}, C{height}
                    and C{datum} B{GRS80 (ETRS89)}.
        '''
        return self._reverse(RDx, RDy, NAPh, raiser, **name)

    def _reverseXform(self, lat, lon, raiser):
        # transform C{(lat, lon)} from RD-Bessel to ETRS (GRS80) datum
        x, y, z  = _geodetic2cartesian(lat, lon, A0.E0, A0.H0)
        x, y, z  = _RD._xRD2ETRS.transform(x, y, z)
        lat, lon = _cartesian2geodetic(x, y, z, self._EETRS)
        return self._inside2(lat, lon, raiser)

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
    '''Transformer implementing RD NAP 2018 C{variant 2}.

       @note: Method L{RDNAP2018v2.reverse} returns geodetic B{Bessel1841
              (RD-Bessel)} and B{not GRS80 (ETRS89)} lat-/longitudes.
    '''
    if _FOR_DOCS:
        __init__ = _RDNAPbase.__init__
        forward  = _RDNAPbase.forward

    @property_ROnce
    def _rdgrid(self):
        try:
            from pyrdnap import v2grid
        except (AttributeError, ImportError):
            v2grid = _v_gridz_import(self.variant)
        return v2grid

    def reverse(self, RDx, RDy, NAPh=0, raiser=None, **name):  # RDNAP to RD-Bessel
        '''Convert a local C{(B{RDx}, B{RDy})} point and B{C{NAPh}} height
           to geodetic B{Bessel1841 (RD-Bessel)} C{(lat, lon, height)}.

           @arg RDx: Local C{RD} X (C{meter}, conventionally).
           @arg RDy: Local C{RD} Y (C{meter}, conventionally).
           @kwarg NAPh: C{NAP} quasi-geoid-height (C{meter}, conventionally)
                        or C{NAN} to ignore C{NAPh} interpolation.
           @kwarg raiser: If C{True} raise an L{RDNAPError} if C{lat} or
                          C{lon} is outside the C{RD} region (C{bool}), if
                          C{False} don't, overriding property C{raiser}.
           @kwarg name: Optional C{B{name}='reverse'} (C{str}).

           @return: An L{RDNAP7Tuple}C{(RDx, RDy, NAPh, lat, lon, height,
                    datum)} with geodetic C{lat} and C{lon}, C{height}
                    and C{datum} B{Bessel1841 (RD-Bessel)}.
        '''
        return self._reverse(RDx, RDy, NAPh, raiser, **name)

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
    # interpolate a lat_corr_, lon_corr_ or NAP_h_...
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


def _ellipsoidal2spherical(lat, lon):  # 2.4.1
    # convert geodetic C{(lat, lon)} to spherical C{(𝛷, 𝛬)}
    phiC = phi = Phid(lat)
    if PI_2 > phi > -PI_2:  # 2.4.1c
        q = A0.ln_tan(phi) - A0.ln_e_2(phi)
        w = A0.N0 * q + A0.M0  # 2.4.1b
        phiC = _atan_exp(w)
    lamC = (Lamd(lon) - A0.LAM0) * A0.N0 + A0.LAM0C  # 2.4.1d
    return phiC, lamC  # -Capital


def _eq0(r, r0=_0_0):
    return fabs(r - r0) < _TOL_R


# def _eq0d(d, d0=_0_0):
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


def _ne0(r, r0=_0_0):
    return fabs(r - r0) > _TOL_R


# def _ne0d(d, d0=_0_0):
#     return fabs(d - d0) > _TOL_D


def _oblique2spherical(x, y):  # 3.1.1
    # inverse oblique stereographic conformal projection
    # from 2-D C{(x, y)} to spherical C{(𝛷, 𝛬)}
    x -= A0.X0
    y -= A0.Y0
    r  = hypot(x, y)
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
        yN    = _0_0
        phiC  =  A0.PHI0C  # asin(sin(PHI0C))
    lamC = _atan3(yN, xN, x) + A0.LAM0C
    return phiC, lamC  # -Capital


def _spherical2ellipsoidal(phiC, lamC):  # 3.1.2
    # inverse Gauss conformal projection from
    # spherical C{(𝛷, 𝛬)} to geodetic C{(phi, lam)}
    phi = phiC
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
            t = sp_22 * _2_0  # 0 < t < 2
            q = A0.RK2 / (_2_0 - t)
            x = q * (c * sin(b))
            y = q * (s - s0 + s0 * t) / c0
        else:
            x = y = _0_0  # NAN?
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
__all__ += _ALL_OTHER(RDNAP2018v1, RDNAP2018v2, RDNAPError,
                      Datum, Ellipsoid)  # passed along from PyGeodesy


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
