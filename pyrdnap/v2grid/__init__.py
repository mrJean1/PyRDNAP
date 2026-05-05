
# -*- coding: utf-8 -*-

__all__ = ()
__version__ = '26.04.20'

try:  # XXX if not _isPyChOK():
    from .naptrans2018_txt_NAP_h import _NAP_h  # noqa: F401
    from .rdtrans2018_txt_lat_corr import _lat_corr  # noqa: F401
    from .rdtrans2018_txt_lon_corr import _lon_corr  # noqa: F401
except ValueError:
    pass
