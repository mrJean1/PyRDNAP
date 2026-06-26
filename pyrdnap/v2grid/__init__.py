
# -*- coding: utf-8 -*-

u'''Variant 2 grids.  Extract from the compressed C{RDNAPTRANS(tm)2018_v229627}
C{naptrans2018.txt.zip} and C{rdtrans2018.txt.zip} grid files B{only} columns
C{NAP_...}, C{lat_corr_} and C{lon_corr_} and encode each as a row-order matrix
in Python, a 481-tuple of 301-arrays of single- or double precision floats.
'''
from pyrdnap.v_grids import _d_array, _f_array, _RxC, _v_grid_txt

__all__ = ()
__version__ = '26.06.18'

_NAP_h    = _v_grid_txt(2, 'naptrans', 2, _f_array)
_lat_corr = _v_grid_txt(2, 'rdtrans',  2, _d_array)
_lon_corr = _v_grid_txt(2, 'rdtrans',  3, _d_array)

assert _NAP_h._RxC == _lat_corr._RxC == _lon_corr._RxC == _RxC
