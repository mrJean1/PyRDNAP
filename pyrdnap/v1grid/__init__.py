
# -*- coding: utf-8 -*-

u'''Variant 1 grid files, but B{only} columns C{NAP_h_...}, C{lat_corr_} and
C{lon_corr_} of the original C{RDNAPTRANS2018_v220627/...1/nlgeo2018.txt} and
C{...1/rdcorr2018.txt} grid files and encoded into Python as 3 row-order
matrices, each a 481-tuple of 301-arrays of floats.

Of the 144,781 floats (481 x 301) in each of the C{lat_corr_} and C{lon_corr_}
columns of the original grid file C{...1/rdcorr2018.txt} only 55,139 respectively
55,348 are non-zero between indices [8598:93827] respectively [8598:93830].

As a result, the first 28 and the last 169 rows (in total 197 rows or 41% of
481) can all be represented by the same 301-array of single-precision zeros.
There are other stretches of zeros, but none amount to 301 or more.

The non-zeros in C{lat_corr_} and C{lon_corr_} colums are initially stored as
a 349- respectively 317-tuple of runs of non-zeros plus a start and end index.
Upon import, the runs are re-formatted into a row-order matrix, a 481-tuple of
301-arrays of floats.

The combined size of these 3 grid files is 2 MB vs 9.7 MB for the original 2.
'''
from pyrdnap.v1grid.nlgeo2018_txt_NAP_h import _NAP_h  # noqa: F401
from pyrdnap.v1grid.rdcorr2018_txt_lat_corr import _lat_corr  # noqa: F401
from pyrdnap.v1grid.rdcorr2018_txt_lon_corr import _lon_corr  # noqa: F401

__all__ = ()
__version__ = '26.05.08'
