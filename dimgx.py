#!/usr/bin/env python
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

  The ``dimgx`` Python Module
  ===========================

  Utilities for programmatically inspecting `Docker
  <https://www.docker.com/whatisdocker/>`_ `images
  <https://docs.docker.com/terms/image/>`__ and extracting their `layers
  <https://docs.docker.com/terms/layer/>`__.

  Examples
  --------

  Extract all but the first layer of image ``0fe1d2c3b4a5`` to a file
  called ``output.tar`` in the current working directory (without proper
  error checking)::

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
          extractlayers(dc, layers_dict[':layers'][1:], tar_file)

  Extract all but the first and last layers *in reverse order* (note the
  ``0`` provided for the :obj:`top_most_layer` parameter to
  :func:`extractlayers`)::

      with tarfile.open('output.tar', 'w') as tar_file:
          layers_to_extract = layers_dict[':layers'][1:-1]
          layers_to_extract.reverse()
          extractlayers(dc, layers_to_extract, tar_file, top_most_layer=0)

  Module Contents
  ---------------

  .. |docker.Client| replace:: :class:`docker.Client`
  .. _`docker.Client`: https://docker-py.readthedocs.org/en/latest/api/
  .. |docker.Client.images| replace:: :func:`docker.Client.images`
  .. _`docker.Client.images`: https://docker-py.readthedocs.org/en/latest/api/#images
  .. |docker.Client.inspect_image| replace:: :py:func:`docker.Client.inspect_image`
  .. _`docker.Client.inspect_image`: https://docker-py.readthedocs.org/en/latest/api/#inspect_image
  """
#=========================================================================

from __future__ import (
    absolute_import, division, print_function, unicode_literals,
)

from builtins import * # pylint: disable=redefined-builtin,unused-wildcard-import,wildcard-import
from future.builtins.disabled import * # pylint: disable=redefined-builtin,unused-wildcard-import,wildcard-import

#---- Imports ------------------------------------------------------------

from copy import deepcopy
from datetime import datetime
from io import open
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
from _dimgx.version import __version__

#---- Constants ----------------------------------------------------------

__all__ = (
    'UnsafeTarPath',
    'denormalizeimage',
    'extractlayers',
    'inspectlayers',
    'normalizeimage',
)

_LOGGER = getLogger(__name__)
_WHITEOUT_PFX = '.wh.'
_WHITEOUT_PFX_LEN = len(_WHITEOUT_PFX)

#---- Functions ----------------------------------------------------------

#=========================================================================
def denormalizeimage(image_desc, copy=False):
    """
    :param image_desc: a normalized image description as returned from
                       |docker.Client.images|_,
                       |docker.Client.inspect_image|_, etc., and passed to
                       :func:normalizeimage

    :param copy: if :const:`True`, make a copy of :obj:`image_desc` before
                 performing any denormalizations

    Removes any entries created by :func:normalizeimage.
    """
    if copy:
        image = deepcopy(image_desc)
    else:
        image = image_desc

    remove = [ k for k in image if k.startswith(':') ]

    for k in remove:
        del image[k]

    return image

#=========================================================================
def extractlayers(dc, layers, tar_file, top_most_layer=-1):
    """
    :param dc: a |docker.Client|_

    :param layers: a sequence of inspection objects (likely retrieved with
                   :func:`inspectlayers`) corresponding to the layers to
                   extract and flatten

    :param tar_file: a :class:`~tarfile.TarFile` open for writing to which
                     to write the flattened layer archive

    :param top_most_layer: an image ID or an index into :obj:`layers`
                           indicating the most recent layer to retrieve
                           (the default of ``-1`` references the last item
                           in :obj:`layers`; see below)

    :raises: :class:`docker.errors.APIError` or
             :class:`docker.errors.DockerException` - on failure
             interacting with Docker (e.g., bad image ID, failed
             connection, Docker not running, etc.); or

             :class:`UnsafeTarPath` - probably indicative of a bug in
             Docker

    Retrieves the layers corresponding to the :obj:`layers` parameter and
    extracts them into :obj:`tar_file`. Changes from layers corresponding
    to larger indexes in :obj:`layers` will overwrite or block those from
    smaller ones.

    Callers will need to set the :obj:`top_most_layer` parameter if
    :obj:`layers` is not in ascending order. It is always safe to provide
    the same value as the :obj:`image_spec` parameter to
    :func:`inspectlayers`, but this may be ineffecient if that layer does
    not appear in :obj:`layers`.
    """
    if not layers:
        _LOGGER.warning('nothing to extract')

        return

    image_spec = top_most_layer if not isinstance(top_most_layer, int) else layers[top_most_layer][':id']
    tmp_dir = path_realpath(mkdtemp())

    try:
        image = logexception(_LOGGER, ERROR, 'unable to retrieve image layers from "{}": {{e}}'.format(image_spec), dc.get_image, image_spec)

        with tarfile_open(mode='r|*', fileobj=image) as image_tar_file:
            next_info = image_tar_file.next()

            while next_info:
                next_path = path_realpath(path_join(tmp_dir, next_info.name))

                if not next_path.startswith(tmp_dir):
                    exc = UnsafeTarPath('unsafe path: "{}"'.format(next_info.name))
                    logexception(_LOGGER, ERROR, 'unable to retrieve entry from export of "{}": {{e}}'.format(image_spec), exc)

                image_tar_file.extract(next_info, tmp_dir)
                next_info = image_tar_file.next()

        seen = set()
        hides_subtrees = set()

        # Look through each layer's archive (oldest to newest)
        for layer in layers[::-1]:
            layer_id = layer[':id']
            layer_tar_path = path_join(tmp_dir, layer_id, 'layer.tar')

            with tarfile_open(layer_tar_path) as layer_tar_file:
                next_info = layer_tar_file.next()

                while next_info:
                    next_dirname = posixpath_dirname(next_info.name)
                    next_basename = posixpath_basename(next_info.name)

                    if next_basename.startswith(_WHITEOUT_PFX):
                        removed_path = posixpath_join(next_dirname, next_basename[_WHITEOUT_PFX_LEN:])
                        hides_subtrees.add(( removed_path, 'removal' ))

                        if removed_path in seen:
                            _LOGGER.debug('skipping removal "%s"', removed_path)
                        else:
                            _LOGGER.debug('hiding "%s" as removed', removed_path)
                    elif next_info.name in seen:
                        _LOGGER.debug('skipping "%s" as overwritten', next_info.name)
                    else:
                        next_name_len = len(next_info.name)
                        hidden = None

                        for h, deverbal in hides_subtrees: # https://en.wikipedia.org/wiki/deverbal
                            if len(h) > next_name_len:
                                continue

                            common_pfx = posixpath_commonprefix(( h, next_info.name ))
                            common_pfx_len = len(common_pfx)

                            if next_name_len == common_pfx_len \
                                    or next_info.name[common_pfx_len:].startswith(posixpath_sep):
                                hidden = deverbal, h
                                break

                        if hidden:
                            _LOGGER.debug('skipping "%s" hidden by %s of %s', next_info.name, *hidden)
                        else:
                            mtime = naturaltime(datetime.utcfromtimestamp(next_info.mtime).replace(tzinfo=TZ_UTC))
                            _LOGGER.info('writing "%s" from "%s" to archive (size: %s; mode: %o; mtime: %s)', next_info.name, layer_id, naturalsize(next_info.size), next_info.mode, mtime)

                            if next_info.linkname:
                                # TarFile.extractfile() tries to do
                                # something weird when its parameter
                                # represents a link (see the docs)
                                fileobj = None
                            else:
                                fileobj = layer_tar_file.extractfile(next_info)

                            tar_file.addfile(next_info, fileobj)
                            seen.add(next_info.name)

                            if not next_info.isdir():
                                hides_subtrees.add(( next_info.name, 'presence' ))

                    next_info = layer_tar_file.next()
    finally:
        rmtree(tmp_dir, ignore_errors=True)

#=========================================================================
def inspectlayers(dc, image_spec):
    """
    :param dc: a |docker.Client|_

    :param image_spec: the name or ID of the image to inspect

    :returns: a :class:`dict` containing the descriptions (see below)

    :raises: :class:`docker.errors.APIError` or
             :class:`docker.errors.DockerException` on failure
             interacting with Docker

    Retrieves and normalizes descriptions for the :obj:`image_spec` image
    and each of its ancestors by calling |docker.Client.images|_.

    The returned :class:`dict` is as follows::

        {
            ':layers': ( image_desc_0, ... image_desc_n ),
            image_id_0: 0,
            ...
            image_id_n: n,
            ...
        }

    The :attr:`':layers'` :class:`tuple` is in ascending order (i.e., from
    the root to :obj:`image_spec`). The other entries map the layers'
    various IDs, to their respective indexes in the :attr:`':layers'`
    :class:`tuple`.
    """
    images = logexception(_LOGGER, ERROR, 'unable to retrieve image summaries: {{e}}'.format(), dc.images, all=True)
    images_dict = {}

    for image in images:
        normalizeimage(image)
        image_id = image[':id']
        image_short_id = image[':short_id']
        images_dict[image_id] = image
        images_dict[image_short_id] = image

        for repo_tag in image[':repo_tags']:
            images_dict[repo_tag] = image

    if image_spec not in images_dict:
        raise RuntimeError('{} not found among the layers retreieved for that image'.format(image_spec))

    layers = []
    layer = images_dict[image_spec]
    layer_id = layer[':id']

    if image_spec not in ( layer_id, layer[':short_id'] ):
        _LOGGER.debug('image "%s" has ID "%s"', image_spec, layer[':short_id'])

    while True:
        layers.append(layer)
        parent_layer_short_id = layer[':parent_id'][:12]

        if not parent_layer_short_id:
            _LOGGER.debug('found root layer "%s"', layer[':short_id'])
            break

        layer_id = parent_layer_short_id
        layer = images_dict[layer_id]

    layers.reverse()
    layers_by_id = {
        ':all_images': images_dict,
        ':layers': tuple(layers),
    }

    for i, layer in enumerate(layers):
        layers_by_id[layer[':id']] = i
        layers_by_id[layer[':short_id']] = i

        for repo_tag in layer[':repo_tags']:
            layers_by_id[repo_tag] = i

    return layers_by_id

#=========================================================================
def normalizeimage(image_desc, copy=False):
    """
    :param image_desc: an image description as returned from
                       |docker.Client.images|_,
                       |docker.Client.inspect_image|_, etc.

    :param copy: if :const:`True`, make a copy of :obj:`image_desc` before
                 performing any normalizations

    :returns: the normalized image description (:obj:`image_desc` if
              :obj:`copy` is :const:`False`)

    This method is attempts to address certain `Docker API inconsistencies
    <https://github.com/docker/docker/issues/5893#issuecomment-102398746>`__.
    The following keys are added to :obj:`image_desc`:

    * :attr:`':id'` - a normalized :attr:`'Id'`
    * :attr:`':short_id'` - the first 12 hexidecimal characters from
      :attr:`':id'`
    * :attr:`':parent_id'` - a normalized :attr:`'ParentId'` or
      :attr:`'Parent'`
    * :attr:`':created_dt'` - a timezone-aware :class:`datetime` object
      representing :attr:`'Created'`
    * :attr:`':repo_tags'` - a normalized :attr:`'RepoTags'`, including
      any short names (i.e., those implying ``:latest``)
    """
    if copy:
        image = deepcopy(image_desc)
    else:
        image = image_desc

    image_id = image.get('Id', image.get('id')).lower()
    image[':id'] = image_id
    image[':parent_id'] = image.get('ParentId', image.get('Parent', image.get('parent', ''))).lower()
    image_short_id = image_id[:12]
    image[':short_id'] = image_short_id
    image_created = image.get('Created', image.get('created'))

    if isinstance(image_created, int):
        # Work-around for
        # <https://github.com/PythonCharmers/python-future/issues/144> and
        # <https://bitbucket.org/pypy/pypy/issue/2048/datetimeutcfromtimestamp-barfs-when>
        if hasattr(image_created, '__native__'):
            image_created = image_created.__native__()

        image[':created_dt'] = datetime.utcfromtimestamp(image_created).replace(tzinfo=TZ_UTC)
    else:
        image[':created_dt'] = dateutil_parse(image_created)

    image[':repo_tags'] = []

    for repo_tag in image.get('RepoTags', ()):
        if repo_tag == '<none>:<none>':
            continue

        repo, tag = repo_tag.split(':')

        if tag == 'latest':
            image[':repo_tags'].append(repo)

        image[':repo_tags'].append(repo_tag)

    return image

#---- Initialization -----------------------------------------------------

if __name__ == '__main__':
    from _dimgx.cmd import main as _main
    _main()
