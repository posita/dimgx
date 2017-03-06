#!/usr/bin/env python
# -*- encoding: utf-8; mode: python; grammar-ext: py -*-

# ========================================================================
"""
Copyright and other protections apply. Please see the accompanying
:doc:`LICENSE <LICENSE>` and :doc:`CREDITS <CREDITS>` file(s) for rights
and restrictions governing use of this software. All rights not expressly
waived or licensed are reserved. If those files are missing or appear to
be modified from their originals, then please contact the author before
viewing or using this software in any capacity.
"""
# ========================================================================

from __future__ import (
    absolute_import, division, print_function,
    # See <https://bugs.python.org/setuptools/issue152>
    # unicode_literals,
)

# ---- Imports -----------------------------------------------------------

from setuptools import (
    find_packages,
    setup,
)

from codecs import open as codecs_open
from inspect import (
    currentframe,
    getframeinfo,
)
from os import environ
from os.path import (
    dirname,
    isfile,
    join as ospath_join,
)

# ---- Constants ---------------------------------------------------------

__all__ = ()

_MY_DIR = dirname(getframeinfo(currentframe()).filename)

INSTALL_REQUIRES = (
    'docker-py',
    'future',
    'humanize',
    'python-dateutil',
)

# WARNING: This imposes limitations on test/requirements.txt such that the
# full Pip syntax is not supported. See also
# <http://stackoverflow.com/questions/14399534/>.
with open(ospath_join(_MY_DIR, 'test', 'requirements.txt')) as f:
    TESTS_REQUIRE = f.read().splitlines()

# ---- Initialization ----------------------------------------------------

_namespace = {
    '_version_path': ospath_join(_MY_DIR, '_dimgx', 'version.py'),
}

if isfile(_namespace['_version_path']):
    with open(_namespace['_version_path']) as _version_file:
        exec(compile(_version_file.read(), _namespace['_version_path'], 'exec'), _namespace, _namespace)  # pylint: disable=exec-used

with codecs_open(ospath_join(_MY_DIR, 'README.rst'), encoding='utf-8') as _readme_file:
    README = _readme_file.read()

__vers_str__ = _namespace.get('__vers_str__')
__release__ = _namespace.get('__release__', __vers_str__)

_SETUP_ARGS = {
    'name': 'dimgx',
    'version': __vers_str__,
    'author': 'Matt Bogosian',
    'author_email': 'matt@bogosian.net',
    'url': 'https://dimgx.readthedocs.org/en/{}/'.format(__release__),
    'license': 'MIT License',
    'description': 'Docker IMaGe layer eXtractor (and flattener)',
    'long_description': README,

    # From <https://pypi.python.org/pypi?%3Aaction=list_classifiers>
    'classifiers': (
        'Topic :: Software Development :: Build Tools',
        'Development Status :: 4 - Beta',
        'Environment :: Console',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: Implementation :: CPython',
        'Programming Language :: Python :: Implementation :: PyPy',
        'Topic :: System :: Archiving :: Packaging',
    ),

    'packages': find_packages(),
    'py_modules': ( 'dimgx', ),
    'include_package_data': True,

    'entry_points': {
        'console_scripts': (
            'dimgx = _dimgx.cmd:main',
        ),
    },

    'install_requires': INSTALL_REQUIRES,
    'setup_requires': ( 'pytest-runner', ),
    'tests_require': TESTS_REQUIRE,
}

if __name__ == '__main__':
    environ['COVERAGE_PROCESS_START'] = environ.get('COVERAGE_PROCESS_START', ospath_join(_MY_DIR, '.coveragerc'))
    setup(**_SETUP_ARGS)
