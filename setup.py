
# -*- coding: utf-8 -*-

# The setuptools script to build, test and install a PyRDNAP distribution.

from os import getenv
from setuptools import setup

__all__ = ()
__version__ = '26.06.18'

_PACKAGE = 'pyrdnap'  # 'PyRDNAP'


def _assert_version(name, streq):
    if streq not in _read_file(name):
        _exit_version(name, streq)


def _c(*names):
    return ' :: '.join(names)


def _exit_version(name, attr):
    import sys
    t = '*** %r not in %s ***' % (attr, name)
    sys.exit(t)


def _long_description():
    return _read_file('README.rst')


def _parse_version(name, attr):
    with open(name) as f:
        for t in f.readlines():
            if t.startswith(attr):
                v = t.split('=')[-1]
                v = v.split('#')[0]
                return v.strip().strip('\'"')
        _exit_version(name, attr)


def _read_file(name):
    with open(name, 'rb') as f:
        t = f.read()
        if isinstance(t, bytes):
            t = t.decode('utf-8')
        return t


def _version():
    v = _parse_version('pyrdnap/__init__.py', '__version__')
    c =  getenv('PYRDNAP_DIST_RC', '')
    return v.replace('.0', '.') + c


_KeyWords = ('NAP', 'Normaal-Amsterdams-Peil',
             'RD', 'RijksDriehoeksmeting',
#            'RDNAPTRANS(tm)', 'RDNAPTRANS(tm)2018',
             'RDNAPTRANS', 'RDNAPTRANS2018',)

_requires = _parse_version('pyrdnap/__pygeodesy.py', '_requires')
_pygeodesy_requires = 'pygeodesy>=' + _requires

_assert_version('requirements.txt', _pygeodesy_requires)
_assert_version('README.rst', 'version %s or newer' % (_requires,))

setup(name=_PACKAGE,
      packages=['pyrdnap', 'pyrdnap.v1grid', 'pyrdnap.v2grid'],
      description='Pure Python RDNAPTRANS(tm)2018 conversions',
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
      classifiers=[_c('Development Status', '5 - Production/Stable'),
                   _c('Environment', 'Console'),
                   _c('Intended Audience', 'Developers'),
                   _c('License', 'OSI Approved', 'MIT License'),
                   _c('Operating System', 'OS Independent'),
                   _c('Programming Language', 'Python'),
                   _c('Programming Language', 'Python', '2.7'),
                   _c('Programming Language', 'Python', '3.13'),
                   _c('Programming Language', 'Python', '3.14'),
                   _c('Programming Language', 'Python', '3.15'),
                   _c('Topic', 'Software Development'),
                   _c('Topic', 'Scientific/Engineering', 'GIS'),
      ],  # PYCHOK indent

#     download_url='https://GitHub.com/mrJean1/PyRDNAP',
#     entry_points={},
#     include_package_data=False,
      install_requires=[_pygeodesy_requires],
#     namespace_packages=[],
#     py_modules=[],
)  # PYCHOK indent
