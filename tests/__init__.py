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
# pylint: disable=missing-super-argument

#---- Imports ------------------------------------------------------------

from hashlib import sha256
from io import BytesIO
from os import environ
from logging import (
    CRITICAL,
    basicConfig as logging_basicConfig,
    getLevelName as logging_getLevelName,
    getLogger,
)
from _dimgx.cmd import _DEFAULT_LOG_FMT

#---- Constants ----------------------------------------------------------

__all__ = (
    'HashedBytesIo',
)

_LOG_LEVEL = environ.get('_DIMGX_LOG_LVL')
_LOG_LEVEL = CRITICAL + 1 if not _LOG_LEVEL else logging_getLevelName(_LOG_LEVEL)

#---- Classes ------------------------------------------------------------

#=========================================================================
class HashedBytesIo(BytesIO):

    #---- Constructor ----------------------------------------------------

    #=====================================================================
    def __init__(self, initial_bytes=None, hashimpl=sha256):
        super().__init__(initial_bytes)
        self._hash_obj = hashimpl()

    #---- Public properties ----------------------------------------------

    #=====================================================================
    @property
    def hash_obj(self):
        return self._hash_obj

    #---- Public hook methods --------------------------------------------

    #=====================================================================
    def write(self, b):
        super().write(b)
        self._hash_obj.update(b)

#---- Initialization -----------------------------------------------------

# Suppress dimgx logging messages during testing
logging_basicConfig(format=_DEFAULT_LOG_FMT)
getLogger('dimgx').setLevel(_LOG_LEVEL)
getLogger('_dimgx').setLevel(_LOG_LEVEL)
