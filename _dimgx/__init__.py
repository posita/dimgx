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

from datetime import datetime
from logging import ERROR
from os import linesep
from traceback import (
    format_exception,
    format_stack,
)
from dateutil.tz import tzutc
from humanize import naturaltime as _naturaltime
from requests import RequestException

#---- Constants ----------------------------------------------------------

__all__ = ()

TZ_UTC = tzutc()

#---- Exceptions ---------------------------------------------------------

#=========================================================================
class UnsafeTarPath(Exception):
    """
    Raised before an entry is extracted from a Docker tar archive if it
    has an unsafe path (usually either an absolute path, or one that
    contains "``..``" or equivalent).
    """

#---- Functions ----------------------------------------------------------

#=========================================================================
logexception = lambda *args, **kw: _logexception(*args, **kw) # pylint: disable=unnecessary-lambda

#=========================================================================
def naturaltime(value, future=False, months=True):
    if isinstance(value, datetime):
        if value.tzinfo is None:
            now = datetime.now()
        else:
            now = datetime.utcnow().replace(tzinfo=TZ_UTC)

        value = now - value

    return _naturaltime(value, future, months)

#=========================================================================
def _debugtrace(logger, lvl, msg, last_type, last_value, last_tb):
    logger.log(lvl, msg)
    stack = format_stack()[:-2] + format_exception(last_type, last_value, last_tb)[1:-1]
    val = 'Complete traceback (most recent call last):' + linesep \
        + ''.join(( str(l) for l in stack ))
    logger.debug(val.rstrip())

#=========================================================================
def _logexception(logger, lvl, msg_fmt, f, *args, **kw):
    try:
        if isinstance(f, Exception):
            raise f

        return f(*args, **kw)
    except EnvironmentError as e:
        if e.strerror:
            msg_e = e.strerror
        else:
            msg_e = e

        last_type, last_value, last_tb = sys.exc_info()

        try:
            _debugtrace(logger, lvl, msg_fmt.format(e=msg_e), last_type, last_value, last_tb)
        finally:
            del last_type, last_value, last_tb # break circular references

        if lvl >= ERROR:
            raise
    except Exception as e: # pylint: disable=broad-except
        last_type, last_value, last_tb = sys.exc_info()

        try:
            _debugtrace(logger, lvl, msg_fmt.format(e=e), last_type, last_value, last_tb)
        finally:
            del last_type, last_value, last_tb # break circular references

        if lvl >= ERROR:
            raise
