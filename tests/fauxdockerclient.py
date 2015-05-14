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
    absolute_import, division, print_function, unicode_literals,
)

from builtins import * # pylint: disable=redefined-builtin,unused-wildcard-import,wildcard-import
from future.builtins.disabled import * # pylint: disable=redefined-builtin,unused-wildcard-import,wildcard-import
from future.utils import iteritems
# pylint: disable=missing-super-argument

#---- Imports ------------------------------------------------------------

from binascii import unhexlify
from datetime import datetime
from functools import (
    cmp_to_key,
    wraps,
)
from hashlib import sha256
from dateutil.parser import parse as dateutil_parse
from docker.errors import APIError
from requests.exceptions import HTTPError
from _dimgx import TZ_UTC
from dimgx import normalizeimage

#---- Constants ----------------------------------------------------------

__all__ = (
    'FauxDockerClient',
)

_EPOCH = datetime(1970, 1, 1, 0, 0, 0).replace(tzinfo=TZ_UTC)

#---- Classes ------------------------------------------------------------

#=========================================================================
class FauxDockerClient(object):
    """
    Minimal faux client for testing Docker interactions without Docker.
    """

    #---- Public constants -----------------------------------------------

    IDS_BY_PATH = (
      (
        '2b32db6c0000', 'ff304d2a0001', 'f62dd7680002', '149dccab0003',
        '9e42fa970004', 'dd1d42190005', '3807f4cc0006', '483619750007',
        'e79d00850008', '424b1d5a0009', '0c2ccea2000a', '7c3c1af8000b',
        'd21db9c2000c', '2e7523f2000d', '5a48f220000e', '52d7263f000f',
      ), (
        '800c14150100', 'a0d4a0b80101', 'c6566e3d0102', '9c4784350103',
        '4fd6a0870104', '91d168b90105', '20767f420106', '433d6bca0107',
        '37c550ef0108', 'ef8adbef0109', 'e97a31f3010a', '477a2fc6010b',
        '2a6fd83c010c', 'e0771bbb010d', '0ab95943010e', '05883322010f',
      )
    )

    #---- Protected static methods ---------------------------------------

    #=====================================================================
    @staticmethod
    def _checkexc(f):
        @wraps(f)
        def _wrapped(self, *_args, **_kw):
            # pylint: disable=protected-access
            if self._raise_exc is not None:
                raise self._raise_exc

            return f(self, *_args, **_kw)

        return _wrapped

    #---- Constructor ----------------------------------------------------

    #=====================================================================
    def __init__(self, raise_exc=None):
        super().__init__()
        self._raise_exc = raise_exc
        self.layers = []
        self.layers_by_id = {}
        self.layers_by_tag = {}
        self.ids_by_path = []
        num_paths = 0x2 # should not exceed 0x100
        path_depth = 0x10 # should not exceed 0x100

        for j in range(num_paths):
            ids = []
            self.ids_by_path.append(ids)

            for i in range(path_depth):
                layer_sig = '{:02x}{:02x}'.format(j, i)
                layer_id = sha256(sha256(unhexlify(layer_sig * 16)).digest()).hexdigest()
                ids.append(layer_id[:8] + layer_sig)
                layer_id = ids[-1] + layer_id[12:60] + layer_sig
                last_layer_id = '' if i == 0 else self.layers[-1]['Id']
                self.layers.append({
                    'Created': '2015-05-{:02d}T{:02d}:00:{:02d}.000000000Z'.format(i + 10, i, j),
                    'Id': layer_id,
                    'Parent': last_layer_id,
                    'Size': int(layer_id[:7], 16),
                    'RepoTags': [ '<none>:<none>' ],
                })
                assert ids[-1] == FauxDockerClient.IDS_BY_PATH[j][i]

        self.layers[-1 - path_depth]['RepoTags'] = [ 'getto:dachoppa' ]
        self.layers[-1]['RepoTags'] = [ 'greatest:hits', 'greatest:latest' ]

        for layer in self.layers:
            normalized_layer = normalizeimage(layer, copy=True)
            self.layers_by_id[normalized_layer[':id']] = layer
            self.layers_by_id[normalized_layer[':short_id']] = layer

            for repo_tag in normalized_layer[':repo_tags']:
                self.layers_by_tag[repo_tag] = layer

        for k, v in iteritems(self.layers_by_id):
            assert k == v['Id'][:len(k)].lower()

        assert self.layers_by_tag['getto:dachoppa'] == self.layers[-1 - path_depth]
        assert self.layers_by_tag['greatest'] == self.layers[-1]
        assert self.layers_by_tag['greatest:hits'] == self.layers[-1]
        assert self.layers_by_tag['greatest:latest'] == self.layers[-1]
        assert self.layers_by_tag['getto:dachoppa']['Id'][:12] == self.ids_by_path[0][-1]
        assert self.layers_by_tag['greatest:hits']['Id'][:12] == self.ids_by_path[1][-1]

        self.layers.sort(key=lambda i: imagekey(normalizeimage(i, copy=True)))

    #---- Public hook methods --------------------------------------------

    #=====================================================================
    @_checkexc.__func__
    def get_image(self, image):
        raise APIError(HTTPError('404 Client Error: Not Found'))

    #=====================================================================
    @_checkexc.__func__
    def images(self, name=None, quiet=False, all=False, viz=False, filters=None): # pylint: disable=redefined-outer-name
        if quiet \
                or not all \
                or viz \
                or filters:
            raise NotImplementedError()

        if name:
            candidates = []

            if name.lower() in self.layers_by_id:
                candidates.append(self.layers_by_id[name])
            elif name in self.layers_by_tag:
                candidates.append(self.layers_by_tag[name])
        else:
            candidates = self.layers

        images = []

        for candidate in candidates:
            images.append({
                'Created': int((dateutil_parse(candidate['Created']) - _EPOCH).total_seconds()),
                'Id': candidate['Id'],
                'ParentId': candidate['Parent'],
                'RepoTags': candidate['RepoTags'],
                'Size': candidate['Size'],
            })

        return images

    #=====================================================================
    @_checkexc.__func__
    def inspect_image(self, image_id): # pylint: disable=unused-argument
        raise NotImplementedError()

#---- Functions ----------------------------------------------------------

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