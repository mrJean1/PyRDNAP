
# -*- coding: utf-8 -*-

# The setuptools script to build, test and install a PyRDNAP distribution.

from os import getenv
from setuptools import setup

__all__ = ()
__version__ = '26.05.13'

_PACKAGE = 'pyrdnap'  # 'PyRDNAP'


def _c(*names):
    return ' :: '.join(names)


def _long_description():
    with open('README.rst', 'rb') as f:
        t = f.read()
        if isinstance(t, bytes):
            t = t.decode('utf-8')
        return t


def _version():
    with open('pyrdnap/__init__.py') as f:
        for t in f.readlines():
            if t.startswith('__version__'):
                v = t.split('=')[-1].strip().strip('\'"')
                c = getenv('PYRDNAP_DIST_RC', '')
                return '.'.join(map(str, map(int, v.split('.')))) + c


_KeyWords = ('NAP', 'Normaal-Amsterdams-Peil',
             'RD', 'RijksDriehoeksmeting',)

setup(name=_PACKAGE,
      packages=['pyrdnap', 'pyrdnap.v1grid', 'pyrdnap.v2grid'],
      description='Pure Python RD NAP 2018 conversions',
      version=_version(),

      author='Jean M. Brouwers',
      author_email='mrJean1@Gmail.com',
      maintainer='Jean M. Brouwers',
      maintainer_email='mrJean1@Gmail.com',

      license='MIT',
      keywords=' '.join(_KeyWords),
      url='https://GitHub.com/mrJean1/PyRDNAP',

      long_description=_long_description(),

      package_data={_PACKAGE: ['v1grid/*.txt.zip', 'v2grid/*.txt.zip', 'LICENSE']},

#     test_suite='test.TestSuite',

      zip_safe=False,

      # <https://PyPI.org/pypi?%3Aaction=list_classifiers>
      classifiers=[_c('Development Status', '3 - Alpha'),
                   _c('Environment', 'Console'),
                   _c('Intended Audience', 'Developers'),
                   _c('License', 'OSI Approved', 'MIT License'),
                   _c('Operating System', 'OS Independent'),
                   _c('Programming Language', 'Python'),
#                  _c('Programming Language', 'Python', '2.6'),
                   _c('Programming Language', 'Python', '2.7'),
#                  _c('Programming Language', 'Python', '3.5'),
#                  _c('Programming Language', 'Python', '3.6'),
#                  _c('Programming Language', 'Python', '3.7'),
#                  _c('Programming Language', 'Python', '3.8'),
#                  _c('Programming Language', 'Python', '3.9'),
#                  _c('Programming Language', 'Python', '3.10'),
#                  _c('Programming Language', 'Python', '3.11'),
#                  _c('Programming Language', 'Python', '3.12'),
#                  _c('Programming Language', 'Python', '3.13'),
                   _c('Programming Language', 'Python', '3.14'),
                   _c('Programming Language', 'Python', '3.15'),
                   _c('Topic', 'Software Development'),
                   _c('Topic', 'Scientific/Engineering', 'GIS'),
      ],  # PYCHOK indent

#     download_url='https://GitHub.com/mrJean1/PyRDNAP',
#     entry_points={},
#     include_package_data=False,
      install_requires=['pygeodesy>=26.5.9'],
#     namespace_packages=[],
#     py_modules=[],
)  # PYCHOK indent
