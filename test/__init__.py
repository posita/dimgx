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
    absolute_import, division, print_function, unicode_literals,
)
from builtins import *  # noqa: F401,F403; pylint: disable=redefined-builtin,unused-wildcard-import,useless-suppression,wildcard-import
from future.builtins.disabled import *  # noqa: F401,F403; pylint: disable=redefined-builtin,unused-wildcard-import,useless-suppression,wildcard-import

# ---- Imports -----------------------------------------------------------

from hashlib import sha256
from io import BytesIO
from os import environ
from logging import (
    CRITICAL,
    basicConfig as logging_basicConfig,
    getLevelName as logging_getLevelName,
    getLogger,
)

from dimgx import patch_broken_tarfile_29760
from _dimgx.cmd import _DEFAULT_LOG_FMT

# ---- Constants ---------------------------------------------------------

__all__ = (
    'HashedBytesIo',
)

_LOG_LVL = environ.get('LOG_LVL')
_LOG_LVL = CRITICAL + 1 if not _LOG_LVL else logging_getLevelName(_LOG_LVL)
_LOG_FMT = environ.get('LOG_FMT', _DEFAULT_LOG_FMT)

# ---- Classes -----------------------------------------------------------

# ========================================================================
class HashedBytesIo(BytesIO):

    # ---- Constructor ---------------------------------------------------

    def __init__(self, initial_bytes=None, hashimpl=sha256):
        super().__init__(initial_bytes)
        self._hash_obj = hashimpl()

    # ---- Public properties ---------------------------------------------

    @property
    def hash_obj(self):
        return self._hash_obj

    # ---- Public hooks --------------------------------------------------

    def write(self, b):
        super().write(b)
        self._hash_obj.update(b)

# ---- Initialization ----------------------------------------------------

# Suppress dimgx logging messages during testing
logging_basicConfig(format=_LOG_FMT)
getLogger('dimgx').setLevel(_LOG_LVL)

# Make sure tarfile.TarFile.next is patched for testing
patch_broken_tarfile_29760()
