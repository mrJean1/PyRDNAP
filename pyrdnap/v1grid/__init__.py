
# -*- coding: utf-8 -*-

u'''I{Variant 1} C{_NAP_h}, C{_lat_corr} and C{_lon_corr} grids.

Of 144,781 floats (481 x 301) in the C{lat_corr} and C{lon_corr} columns of
I{variant 1} only 55,139 resp. 55,348 are non-zero between indices [8598:93827]
resp. C{lon_corr} [8598:93830].

As a result, the 1st 28 and the last 169 rows (in total 197 rows, or 41% of
481) can all be represented by the same, single C{f-array} of 301 zeros.
There are other stretches of zeros, but none are 301 or longer.

The non-zeros in C{_lat_corr} and C{_lon_corr} tuples are initialled stored
as 349 resp. 317 "runs of non-zeros" plus a start and end index.  At import
the runs are formatted into a row-order matrix (481 x 301).
'''
try:
    from .nlgeo2018_txt_NAP_h import _NAP_h  # noqa: F401
    from .rdcorr2018_txt_lat_corr import _lat_corr  # noqa: F401
    from .rdcorr2018_txt_lon_corr import _lon_corr  # noqa: F401
except ValueError:  # Py2.7- _isPyCHOK()
    from pyrdnap.v1grid.nlgeo2018_txt_NAP_h import _NAP_h  # noqa: F401
    from pyrdnap.v1grid.rdcorr2018_txt_lat_corr import _lat_corr  # noqa: F401
    from pyrdnap.v1grid.rdcorr2018_txt_lon_corr import _lon_corr  # noqa: F401

__all__ = ()
__version__ = '26.05.06'
