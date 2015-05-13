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

#---- Constants ----------------------------------------------------------

__all__ = ()

INSTALL_REQUIRES = (
    'docker-py',
    'future',
    'humanize',
    'python-dateutil',
)

#---- Initialization -----------------------------------------------------

_SETUP_ARGS = {
    'name'                : 'dimgx',
    'version'             : '0.1.0',
    'author'              : 'Matt Bogosian',
    'author_email'        : 'mtb19@columbia.edu',
    'url'                 : 'https://github.com/posita/py-dimgx',
    'license'             : 'MIT License',
    'description'         : 'extract and flatten Docker image layers',

    # From <http://pypi.python.org/pypi?%3Aaction=list_classifiers>
    'classifiers': (
        'Topic :: Software Development :: Build Tools',
        'Environment :: Console',
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: System :: Archiving :: Packaging',
    ),

    'packages'            : find_packages(exclude = ( 'tests', )),
    'py_modules'          : ( 'dimgx', ),
    'include_package_data': True,
    'install_requires'    : INSTALL_REQUIRES,
    'test_suite'          : 'tests',
}

if __name__ == '__main__':
    setup(**_SETUP_ARGS)
