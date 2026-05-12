
# -*- coding: utf-8 -*-

u'''Extract from the original, compressed, variant 2 grid files
C{naptrans2018.txt.zip} and C{rdtrans2018.txt.zip} the C{NAP_...},
C{lat_corr_} and C{lon_corr_} columns B{only} and encode each
in Python as a row-order matrix, a 481-tuple of 301-arrays of
single- or double precision floats.
'''
from pyrdnap.v_grids import _d_array, _f_array, _v_grid_txt

__all__ = ()
__version__ = '26.05.11'

_NAP_h    = _v_grid_txt(2, 'naptrans', 2, _f_array)  # PYCHOK shared
_lat_corr = _v_grid_txt(2, 'rdtrans',  2, _d_array)  # PYCHOK shared
_lon_corr = _v_grid_txt(2, 'rdtrans',  3, _d_array)  # PYCHOK shared
