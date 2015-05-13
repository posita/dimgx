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

  The ``dimgx`` Python Module
  ===========================

  Utilities for programmatically inspecting `Docker
  <https://www.docker.com/whatisdocker/>`_ `images
  <https://docs.docker.com/terms/image/>`__ and extracting their `layers
  <https://docs.docker.com/terms/layer/>`__.

  Example
  -------

  Extract all but the first and last layers of image ``0fe1d2c3b4a5`` to a
  file called ``output.tar`` in the current working directory (without
  proper error checking)::

      import docker
      import os
      import tarfile
      from dimgx import *

      DEFAULT_DOCKER_HOST = docker.utils.utils.DEFAULT_UNIX_SOCKET
      DOCKER_HOST = os.environ.get('DOCKER_HOST', DEFAULT_DOCKER_HOST)
      dc = docker.Client(DOCKER_HOST)

      IMAGE_ID = '0fe1d2c3b4a5' # short version
      layers_dict = inspectlayers(dc, IMAGE_ID)
      with tarfile.open('output.tar', 'w') as tar_file:
          extractlayers(dc, layers_dict['layers_list'][1:-1], tar_file)

  Module Contents
  ---------------
  """
#=========================================================================

from __future__ import (
    absolute_import, division, print_function, unicode_literals,
)

from builtins import * # pylint: disable=redefined-builtin,unused-wildcard-import,wildcard-import
from future.builtins.disabled import * # pylint: disable=redefined-builtin,unused-wildcard-import,wildcard-import

#---- Imports ------------------------------------------------------------

from datetime import datetime
from io import (
    BytesIO,
    open,
)
from logging import (
    ERROR,
    getLogger,
)
from posixpath import (
    basename as posixpath_basename,
    commonprefix as posixpath_commonprefix,
    dirname as posixpath_dirname,
    join as posixpath_join,
    sep as posixpath_sep,
)
from os.path import (
    join as path_join,
    realpath as path_realpath,
)
from shutil import rmtree
from tarfile import open as tarfile_open
from tempfile import mkdtemp
from dateutil.parser import parse as dateutil_parse
from humanize import naturalsize
from _dimgx import (
    TZ_UTC,
    UnsafeTarPath,
    logexception,
    naturaltime,
)

#---- Constants ----------------------------------------------------------

__all__ = (
    'UnsafeTarPath',
    'extractlayers',
    'inspectlayers',
)

_LOGGER = getLogger(__name__)
_WHITEOUT_PFX = '.wh.'
_WHITEOUT_PFX_LEN = len(_WHITEOUT_PFX)

#---- Functions ----------------------------------------------------------

#=========================================================================
def extractlayers(dc, layers, tar_file):
    """
    :param dc: a |docker.Client|_

    :param layers: a sequence of inspection objects (likely retrieved with
                   :py:func:`inspectlayers`) corresponding to the layers
                   to extract and flatten

    :param tar_file: a :py:class:`~tarfile.TarFile` open for writing to
                     which to write the flattened layer archive

    :raises: :py:class:`docker.errors.APIError` or
             :py:class:`docker.errors.DockerException` - on failure
             interacting with Docker (e.g., bad image ID, failed
             connection, Docker not running, etc.); or

             :py:class:`UnsafeTarPath` - probably indicative of a bug in
             Docker

    Retrieves the layers corresponding to the ``layers`` argument and
    extracts them into ``tar_file``. Changes from layers corresponding to
    larger indexes in ``layers`` will overwrite or block those from
    smaller ones.

    .. |docker.Client| replace:: :py:class:`docker.Client`
    .. _`docker.Client`: https://docker-py.readthedocs.org/en/latest/api/
    """
    image_spec = max(layers, key=lambda l: dateutil_parse(l['Created']))['Id']
    tmp_dir = path_realpath(mkdtemp())

    try:
        image = logexception(_LOGGER, ERROR, 'unable to retrieve image layers from "{}": {{e}}'.format(image_spec), dc.get_image, image_spec)

        with BytesIO(image.data) as image_source_file:
            with tarfile_open(fileobj=image_source_file) as image_tar_file:
                next_info = image_tar_file.next()

                while next_info:
                    next_path = path_realpath(path_join(tmp_dir, next_info.name))

                    if not next_path.startswith(tmp_dir):
                        exc = UnsafeTarPath('unsafe path: "{}"'.format(next_info.name))
                        logexception(_LOGGER, ERROR, 'unable to retrieve entry from export of "{}": {{e}}'.format(image_spec), exc)

                    image_tar_file.extract(next_info, tmp_dir)
                    next_info = image_tar_file.next()

        del image # this could be fairly large
        seen = set()
        deleted = set()

        # Look through each layer's archive (oldest to newest)
        for layer in layers[::-1]:
            layer_id = layer['Id']
            layer_tar_path = path_join(tmp_dir, layer_id, 'layer.tar')

            with tarfile_open(layer_tar_path) as layer_tar_file:
                next_info = layer_tar_file.next()

                while next_info:
                    next_dirname = posixpath_dirname(next_info.name)
                    next_basename = posixpath_basename(next_info.name)

                    if next_basename.startswith(_WHITEOUT_PFX):
                        deleted_path = posixpath_join(next_dirname, next_basename[_WHITEOUT_PFX_LEN:])
                        deleted.add(deleted_path)

                        if deleted_path in seen:
                            _LOGGER.debug('skipping deleted "%s"', deleted_path)
                        else:
                            _LOGGER.debug('hiding "%s" as deleted', deleted_path)
                    else:
                        next_name_len = len(next_info.name)
                        hidden_by_deleted = False

                        for d in deleted:
                            if len(d) > next_name_len:
                                continue

                            common_pfx = posixpath_commonprefix(( d, next_info.name ))
                            common_pfx_len = len(common_pfx)

                            if next_name_len == common_pfx_len \
                                    or next_info.name[common_pfx_len:].startswith(posixpath_sep):
                                hidden_by_deleted = True
                                break

                        if hidden_by_deleted:
                            _LOGGER.debug('skipping "%s" as hidden by deletion', next_info.name)
                        elif next_info.name in seen:
                            _LOGGER.debug('skipping "%s" as overwritten', next_info.name)
                        else:
                            mtime = naturaltime(datetime.utcfromtimestamp(next_info.mtime).replace(tzinfo=TZ_UTC))
                            _LOGGER.info('writing "%s" from "%s" to archive (size: %s; mode: %o; mtime: %s)', next_info.name, layer_id, naturalsize(next_info.size), next_info.mode, mtime)

                            if next_info.linkname:
                                # TarFile.extractfile() tries to do
                                # something weird when its argument
                                # represents a link (see the docs)
                                fileobj = None
                            else:
                                fileobj = layer_tar_file.extractfile(next_info)

                            tar_file.addfile(next_info, fileobj)
                            seen.add(next_info.name)

                    next_info = layer_tar_file.next()
    finally:
        rmtree(tmp_dir, ignore_errors=True)

#=========================================================================
def inspectlayers(dc, image_spec):
    """
    :param dc: a |docker.Client|_

    :param image_spec: the name or ID of the image to inspect

    :returns: a :py:class:`dict` containing the inspection objects (see
              below)

    :raises: :py:class:`docker.errors.APIError` or
             :py:class:`docker.errors.DockerException` on failure
             interacting with Docker

    Retrieves inspection objects by calling |docker.Client.inspect_image|_
    on ``image_spec`` and each of that image's ancestors until it reaches
    the primogenitor.

    The returned :py:class:`dict` contains a :py:class:`tuple` of
    inspection objects under its ``'layers_list'`` key. The
    ``'layers_list'`` :py:class:`tuple` is in ascending order (i.e., from
    oldest to newest). Other keys map the layers' IDs, in both short and
    long format, to their respective indexes into the ``'layers_list'``
    :py:class:`tuple`.

    .. |docker.Client| replace:: :py:class:`docker.Client`
    .. _`docker.Client`: https://docker-py.readthedocs.org/en/latest/api/
    .. |docker.Client.inspect_image| replace:: :py:func:`docker.Client.inspect_image`
    .. _`docker.Client.inspect_image`: https://docker-py.readthedocs.org/en/latest/api/#inspect_image
    """
    layers = []
    layer_ref = image_spec

    while True:
        img_details = logexception(_LOGGER, ERROR, 'unable to retrieve image details "{}": {{e}}'.format(image_spec), dc.inspect_image, layer_ref)
        layer_id = img_details['Id'][:12]

        if layer_id != layer_ref:
            _LOGGER.debug('image "%s" has ID "%s"', layer_ref, layer_id)

        layers.append(img_details)
        parent_layer_id = img_details.get('Parent')[:12]

        if not parent_layer_id:
            _LOGGER.debug('image "%s" has no parent', layer_ref)
            break

        layer_ref = parent_layer_id

    layers.reverse()
    layers_by_id = { 'layers_list': tuple(layers) }
    layers_by_id.update(( ( l['Id'][:12].lower(), i) for i, l in enumerate(layers) ))
    layers_by_id.update(( ( l['Id'].lower(), i) for i, l in enumerate(layers) ))

    return layers_by_id

#---- Initialization -----------------------------------------------------

if __name__ == '__main__':
    from _dimgx.cmd import main as _main
    _main()
