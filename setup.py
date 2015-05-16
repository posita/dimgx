#!/usr/bin/env python
#-*-mode: python; encoding: utf-8-*-

#=========================================================================
"""
  Copyright |(c)| 2015 `Matt Bogosian`_ (|@posita|_).

  .. |(c)| unicode:: u+a9
  .. _`Matt Bogosian`: mailto:mtb19@columbia.edu
  .. |@posita| replace:: **@posita**
  .. _`@posita`: https://github.com/posita

  Please see the ``LICENSE`` (or ``LICENSE.txt``) file which accompanied
  this software for rights and restrictions governing its use. All rights
  not expressly waived or licensed are reserved. If such a file did not
  accompany this software, then please contact the author before viewing
  or using this software in any capacity.
"""
#=========================================================================

from __future__ import (
    absolute_import, division, print_function,
    # See <http://bugs.python.org/setuptools/issue152>
    # unicode_literals,
)

#---- Imports ------------------------------------------------------------

from setuptools import (
    find_packages,
    setup,
)

# See this e-mail thread:
# <http://www.eby-sarna.com/pipermail/peak/2010-May/003348.html>
import logging # pylint: disable=unused-import
import multiprocessing # pylint: disable=unused-import

from inspect import (
    currentframe,
    getframeinfo,
)
from os.path import (
    dirname,
    isfile,
    join as ospath_join,
)

#---- Constants ----------------------------------------------------------

__all__ = ()

INSTALL_REQUIRES = (
    'docker-py',
    'future',
    'humanize',
    'python-dateutil',
)

_MY_DIR = dirname(getframeinfo(currentframe()).filename)

#---- Initialization -----------------------------------------------------

_namespace = {
    '__version__': '<none>',
    '_version_path': ospath_join(_MY_DIR, '_dimgx', 'version.py'),
}

if isfile(_namespace['_version_path']):
    exec(compile(open(_namespace['_version_path']).read(), _namespace['_version_path'], 'exec'), _namespace, _namespace) # pylint: disable=exec-used

_SETUP_ARGS = {
    'name'                : 'dimgx',
    'version'             : _namespace['__version__'],
    'author'              : 'Matt Bogosian',
    'author_email'        : 'mtb19@columbia.edu',
    'url'                 : 'https://github.com/posita/py-dimgx',
    'license'             : 'MIT License',
    'description'         : 'extract and flatten Docker image layers',
    'long_description'    : open(ospath_join(_MY_DIR, 'README.rst')).read(),

    # From <http://pypi.python.org/pypi?%3Aaction=list_classifiers>
    'classifiers': (
        'Topic :: Software Development :: Build Tools',
        'Development Status :: 3 - Alpha',
        'Environment :: Console',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: Implementation :: CPython',
        'Programming Language :: Python :: Implementation :: PyPy',
        'Topic :: System :: Archiving :: Packaging',
    ),

    'packages'            : find_packages(exclude = ( 'tests', )),
    'py_modules'          : ( 'dimgx', ),
    'include_package_data': True,
    'install_requires'    : INSTALL_REQUIRES,
    'test_suite'          : 'tests',

    'entry_points'        : {
        'console_scripts' : [
            'dimgx = _dimgx.cmd:main',
        ],
    },
}

if __name__ == '__main__':
    setup(**_SETUP_ARGS)
