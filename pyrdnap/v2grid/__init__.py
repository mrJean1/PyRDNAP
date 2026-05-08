
# -*- coding: utf-8 -*-

u'''Variant 2 grid files, but B{only} columns C{NAP_h_...}, C{lat_corr_} and
C{lon_corr_} of the original C{RDNAPTRANS2018_v220627/...2/naptrans2018.txt}
and C{...2/rdtrans2018.txt} grid files and encoded into Python as 3 row-order
matrices, each a 481-tuple of 301-arrays of floats.

The combined size of these 3 grid files is 4 MB vs 9.8 MB for the original 2.
'''
from pyrdnap.v2grid.naptrans2018_txt_NAP_h import _NAP_h  # noqa: F401
from pyrdnap.v2grid.rdtrans2018_txt_lat_corr import _lat_corr  # noqa: F401
from pyrdnap.v2grid.rdtrans2018_txt_lon_corr import _lon_corr  # noqa: F401

__all__ = ()
__version__ = '26.05.08'
