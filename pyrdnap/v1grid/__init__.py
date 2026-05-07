
# -*- coding: utf-8 -*-

u'''I{Variant 1} C{_NAP_h}, C{_lat_corr} and C{_lon_corr} grid columns.

Of 144,781 floats (481 x 301) in the C{_lat_corr} and C{_lon_corr} columns
of original grid file C{rdcorr2018.txt} only 55,139 respectively 55,348 are
non-zero between indices [8598:93827] respectively [8598:93830].

As a result, the first 28 and the last 169 rows (in total 197 rows or 41% of
481) can all be represented by the same C{f-array} of 301 zeros.  There are
other stretches of zeros, but none amount to 301 or more.

The non-zeros in C{_lat_corr} and C{_lon_corr} colums are initialled stored
as 349 resp. 317 runs of non-zeros plus a start and end index.  At import,
the runs are formatted into a row-order matrix (481 x 301).
'''
from pyrdnap.v1grid.nlgeo2018_txt_NAP_h import _NAP_h  # noqa: F401
from pyrdnap.v1grid.rdcorr2018_txt_lat_corr import _lat_corr  # noqa: F401
from pyrdnap.v1grid.rdcorr2018_txt_lon_corr import _lon_corr  # noqa: F401

__all__ = ()
__version__ = '26.05.06'
