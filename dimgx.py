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
          extractlayers(dc, layers_dict[':layers'][:-1], tar_file)

  Extract all but the first and last layers *in reverse order* (note the
  ``-1`` provided for the :obj:`top_most_layer` parameter to
  :func:`extractlayers`)::

      with tarfile.open('output.tar', 'w') as tar_file:
          layers_to_extract = layers_dict[':layers'][1:-1]
          layers_to_extract.reverse()
          extractlayers(dc, layers_to_extract, tar_file, top_most_layer=-1)

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
from future.utils import native

#---- Imports ------------------------------------------------------------

from copy import deepcopy
from datetime import datetime
from functools import cmp_to_key
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
def extractlayers(dc, layers, tar_file, top_most_layer=0):
    """
    :param dc: a |docker.Client|_

    :param layers: a sequence of inspection objects (likely retrieved with
                   :func:`inspectlayers`) corresponding to the layers to
                   extract and flatten in order of precedence

    :param tar_file: a :class:`~tarfile.TarFile` open for writing to which
                     to write the flattened layer archive

    :param top_most_layer: an image ID or an index into :obj:`layers`
                           indicating the most recent layer to retrieve
                           (the default of ``0`` references the first item
                           in :obj:`layers`; see below)

    :raises: :class:`docker.errors.APIError` or
             :class:`docker.errors.DockerException` - on failure
             interacting with Docker (e.g., bad image ID, failed
             connection, Docker not running, etc.); or

             :class:`UnsafeTarPath` - probably indicative of a bug in
             Docker

    Retrieves the layers corresponding to the :obj:`layers` parameter and
    extracts them into :obj:`tar_file`. Changes from layers corresponding
    to smaller indexes in :obj:`layers` will overwrite or block those from
    larger ones.

    Callers will need to set the :obj:`top_most_layer` parameter if
    :obj:`layers` is not in descending order. It is always safe to provide
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

        # Look through each layer's archive (newest to oldest)
        for layer in layers:
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
def imagekey(image):
    """
    :param image: a normalized image description as returned from
                  |docker.Client.images|_, |docker.Client.inspect_image|_,
                  etc., and passed through :func:`dimgx.normalizeimage`

    :returns: an object providing the appropriate `rich comparison
              functions
              <https://docs.python.org/howto/sorting.html#odd-and-ends>`__
              for use (e.g.) as the ``key`` parameter to :func:`sorted`.

    The underlying implementation is a :func:`cmp`-like function that is
    wrapped with :func:`functools.cmp_to_key`. See `this
    <https://docs.python.org/howto/sorting.html#the-old-way-using-the-cmp-parameter>`__
    for details.

    .. |docker.Client.images| replace:: :func:`docker.Client.images`
    .. _`docker.Client.images`: https://docker-py.readthedocs.org/en/latest/api/#images
    .. |docker.Client.inspect_image| replace:: :func:`docker.Client.inspect_image`
    .. _`docker.Client.inspect_image`: https://docker-py.readthedocs.org/en/latest/api/#inspect_image
    """
    return _imagekey(image) # pylint: disable=no-value-for-parameter

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
            ':layers': ( image_desc_n, ... image_desc_0 ),
            image_id_n: n,
            ...
            image_id_0: 0,
            ...
        }

    The :attr:`':layers'` :class:`list` is in desscending order (i.e.,
    from :obj:`image_spec` to the root). The other entries map the layers'
    various IDs, to their respective indexes in the :attr:`':layers'`
    :class:`list`.
    """
    images = logexception(_LOGGER, ERROR, 'unable to retrieve image summaries: {{e}}'.format(), dc.images, all=True)
    images = sorted(( normalizeimage(i) for i in images ), key=imagekey, reverse=True)
    image_spec_len = len(image_spec)
    images_by_id = {}
    children = {}
    layer = None

    for image in images:
        image_id = image[':id']
        image_parent_id = image[':parent_id']
        images_by_id[image_id] = image

        try:
            image[':child_ids'] = children[image_id]
        except KeyError:
            image[':child_ids'] = []

        try:
            children[image_parent_id].append(image_id)
        except KeyError:
            children[image_parent_id] = [ image_id ]

        if image_spec in image[':repo_tags'] \
                or image_spec.lower() == image_id[0:image_spec_len]:
            if layer is not None:
                raise RuntimeError('{} does not resolve to a single image'.format(image_spec))

            layer = image

    if layer is None:
        raise RuntimeError('{} not found among the layers retreieved for that image'.format(image_spec))

    layers = []

    layers_by_id = {
        ':all_images': images_by_id,
        ':layers': layers,
    }

    layer_id = layer[':id']

    if image_spec.lower() not in ( layer_id, layer[':short_id'] ):
        _LOGGER.debug('image "%s" has ID "%s"', image_spec, layer[':short_id'])

    i = 0

    while True:
        layers.append(layer)

        for j in range(1, len(layer_id) + 1):
            layer_id_part = layer_id[0:j]
            layers_by_id[layer_id_part] = None if layer_id_part in layers_by_id else i

        for repo_tag in layer[':repo_tags']:
            layers_by_id[repo_tag] = i

        parent_layer_id = layer[':parent_id']

        if not parent_layer_id:
            _LOGGER.debug('found root layer "%s"', layer[':short_id'])
            break

        layer = images_by_id[parent_layer_id]
        layer_id = layer[':id']
        i += 1

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
        image_created = native(image_created)
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

#=========================================================================
@cmp_to_key
def _imagekey(i, j):
    created_diff = (i[':created_dt'] - j[':created_dt']).total_seconds()

    # The creation times in image descriptions retrieved from
    # :func:docker.Client.images do not include fractional seconds, so
    # there are likely to be clashes; the best we can do without
    # additional calls is look for a parent/child relationship among
    # adjacent descriptions with the same creation time, but this breaks
    # for (e.g.) the following:
    #
    # [ ...,
    #   { 'Created': 1234, 'Id': '5b6a...', 'ParentId', '3d4c...' }, # child
    #   { 'Created': 1234, 'Id': '0def...', 'ParentId', 'fade...' }, # interloper
    #   { 'Created': 1234, 'Id': '3d4c...', 'ParentId', '0f2e...' }, # parent
    #   ... ]
    #
    # The solution is to call func:docker.Client.inspect_image where there
    # is a creation time clash to see if can be resolved with more
    # granular creation times
    return created_diff if created_diff else -(j[':parent_id'] == i[':id']) or +(i[':parent_id'] == j[':id'])

#---- Initialization -----------------------------------------------------

if __name__ == '__main__':
    from _dimgx.cmd import main as _main
    _main()
