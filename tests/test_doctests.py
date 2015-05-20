#-*-mode: python; encoding: utf-8-*-

#=========================================================================
"""
  Copyright |(c)| 2014-2015 `Matt Bogosian`_ (|@posita|_).

  .. |(c)| unicode:: u+a9
  .. _`Matt Bogosian`: mailto:mtb19@columbia.edu
  .. |@posita| replace:: **@posita**
  .. _`@posita`: https://github.com/posita

  Please see the accompanying ``LICENSE`` (or ``LICENSE.txt``) file for
  rights and restrictions governing use of this software. All rights not
  expressly waived or licensed are reserved. If such a file did not
  accompany this software, then please contact the author before viewing
  or using this software in any capacity.
"""
#=========================================================================

from __future__ import (
    absolute_import, division, print_function, unicode_literals,
)

from builtins import * # pylint: disable=redefined-builtin,unused-wildcard-import,wildcard-import
from future.builtins.disabled import * # pylint: disable=redefined-builtin,unused-wildcard-import,wildcard-import

#---- Imports ------------------------------------------------------------

from tests.doctestdiscovery import mkloadtests
import dimgx
import tests

#---- Constants ----------------------------------------------------------

__all__ = (
    'load_tests',
)

_DOCTEST_ROOTS = (
    dimgx,
    tests,
)

#---- Functions ----------------------------------------------------------

#=========================================================================
_load_tests = mkloadtests(_DOCTEST_ROOTS)

#=========================================================================
def load_tests(_, tests, __): # pylint: disable=redefined-outer-name
    """
    >>> True is not False
    True
    """
    in_len = tests.countTestCases()
    tests = _load_tests(_, tests, __)
    out_len = tests.countTestCases()
    # Test whether at least one doctest is found (which could be the
    # doctest for this function)
    assert in_len < out_len

    return tests

#---- Initialization -----------------------------------------------------

if __name__ == '__main__':
    from unittest import main
    main()
