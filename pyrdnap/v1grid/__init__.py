
# -*- coding: utf-8 -*-

u'''Extract from the compressed C{RDNAPTRANS(tm)2018_v229627}
variant 1 C{nlgeo2018.txt.zip} and C{rdcorr2018.txt.zip} grid
files B{only} the C{NAP_...}, C{lat_corr_} and C{lon_corr_}
columns and encode each in Python as a row-order matrix, a
481-tuple of 301-arrays of single- or double precision floats.

Of the 144,781 floats (481 x 301) in the C{lat_corr_} and
C{lon_corr_} columns of the C{rdcorr2018.txt} grid file
only 55,139 respectively 55,348 are non-zero between indices
[8598:93827] respectively [8598:93830] (and 89,642 respectively
89,433 are zero).

As a result, the first 28 and the last 169 matrix rows (in total
197 rows or 41% of 481) are representable by the same 301-array
of single-precision zeros.  There are other stretches of zeros,
but none amount to 301 or more.
'''
from pyrdnap.v_grids import _d_array, _f_array, _RxC, _v_grid_txt

__all__ = ()
__version__ = '26.06.14'

_NAP_h    = _v_grid_txt(1, 'nlgeo',  2, _f_array)
_lat_corr = _v_grid_txt(1, 'rdcorr', 2, _d_array, _0s=89642)
_lon_corr = _v_grid_txt(1, 'rdcorr', 3, _d_array, _0s=89433)

assert _NAP_h._RxC == _lat_corr._RxC == _lon_corr._RxC == _RxC
