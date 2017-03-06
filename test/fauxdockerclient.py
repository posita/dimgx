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
from future.utils import iteritems

# ---- Imports -----------------------------------------------------------

from binascii import unhexlify
from datetime import datetime
from functools import wraps
from hashlib import sha256
from inspect import (
    currentframe,
    getframeinfo,
)
from io import BytesIO
from os import stat
from os.path import (
    dirname,
    join as ospath_join,
)
from tarfile import (
    DIRTYPE,
    TarInfo,
    open as tarfile_open,
)
from time import time
from dateutil.parser import parse as dateutil_parse
from docker.errors import APIError
from requests.exceptions import HTTPError
from _dimgx import TZ_UTC
from dimgx import (
    imagekey,
    normalizeimage,
)

# ---- Constants ---------------------------------------------------------

__all__ = (
    'FauxDockerClient',
)

_EPOCH = datetime(1970, 1, 1, 0, 0, 0).replace(tzinfo=TZ_UTC)

# ---- Classes -----------------------------------------------------------

# ========================================================================
class FauxDockerClient(object):
    """
    Minimal faux client for testing Docker interactions without Docker.
    """

    # ---- Public constants ----------------------------------------------

    SHORT_IDS_BY_PATH = [
        [
            '52d7263f000f', '5a48f220000e', '2e7523f2000d', 'd21db9c2000c',
            '7c3c1af8000b', '0c2ccea2000a', '424b1d5a0009', 'e79d00850008',
            '483619750007', '3807f4cc0006', 'dd1d42190005', '9e42fa970004',
            '149dccab0003', 'f62dd7680002', 'ff304d2a0001', '2b32db6c0000',
        ], [
            '05883322010f', '0ab95943010e', 'e0771bbb010d', '2a6fd83c010c',
            '477a2fc6010b', 'e97a31f3010a', 'ef8adbef0109', '37c550ef0108',
            '433d6bca0107', '20767f420106', '91d168b90105', '4fd6a0870104',
            '9c4784350103', 'c6566e3d0102', 'a0d4a0b80101', '800c14150100',
        ]
    ]

    # ---- Protected static methods --------------------------------------

    @staticmethod
    def _checkandraise(f):
        @wraps(f)
        def _wrapped(self, *_args, **_kw):
            # pylint: disable=protected-access
            if self._always_raise is not None:
                raise self._always_raise

            return f(self, *_args, **_kw)

        return _wrapped

    # ---- Constructor ---------------------------------------------------

    def __init__(self, always_raise=None):
        super().__init__()
        self._always_raise = always_raise
        self._my_dir = dirname(getframeinfo(currentframe()).filename)
        self.layers = []
        self.layers_by_id = {}
        self.layers_by_tag = {}
        num_paths = len(FauxDockerClient.SHORT_IDS_BY_PATH)  # should not exceed 0x100
        path_depth = len(FauxDockerClient.SHORT_IDS_BY_PATH[0])  # should not exceed 0x100
        max_path_idx = path_depth - 1

        for j in range(num_paths):
            for i in range(path_depth):
                layer_sig = '{:02x}{:02x}'.format(j, i)
                layer_id = sha256(sha256(unhexlify(layer_sig * 16)).digest()).hexdigest()
                short_id = layer_id[:8] + layer_sig
                layer_id = short_id + layer_id[12:60] + layer_sig
                last_layer_id = '' if i == 0 else self.layers[-1]['Id']
                layer_tar_src_path = ospath_join(self._my_dir, 'data', layer_id[:12], 'layer.tar')

                try:
                    # This isn't quite right, but it doesn't matter for
                    # our purposes
                    layer_tar_src_stat = stat(layer_tar_src_path)
                    layer_size = layer_tar_src_stat.st_size
                except OSError:
                    layer_size = 0

                self.layers.append({
                    'Created': '2015-04-{:02d}T{:02d}:00:{:02d}.000000000Z'.format(i + 10, i, j),
                    'Id': layer_id,
                    'Parent': last_layer_id,
                    'Size': layer_size,
                    'RepoTags': [ '<none>:<none>' ],
                    'VirtualSize': layer_size if i == 0 else layer_size + self.layers[-1]['Size'],
                })

                assert short_id == FauxDockerClient.SHORT_IDS_BY_PATH[j][max_path_idx - i]

        self.layers[max_path_idx]['RepoTags'] = [ 'getto:dachoppa' ]
        self.layers[-1]['RepoTags'] = [ 'greatest:hits', 'greatest:latest' ]

        for layer in self.layers:
            normalizeimage(layer)
            self.layers_by_id[layer[':id']] = layer
            self.layers_by_id[layer[':short_id']] = layer

            for repo_tag in layer[':repo_tags']:
                self.layers_by_tag[repo_tag] = layer

        for k, v in iteritems(self.layers_by_id):
            assert k == v['Id'][:len(k)].lower()

        assert self.layers_by_tag['getto:dachoppa'] == self.layers[max_path_idx]
        assert self.layers_by_tag['getto:dachoppa']['Id'][:12] == FauxDockerClient.SHORT_IDS_BY_PATH[0][0]
        assert self.layers_by_tag['greatest'] == self.layers[-1]
        assert self.layers_by_tag['greatest:latest'] == self.layers[-1]
        assert self.layers_by_tag['greatest:hits'] == self.layers[-1]
        assert self.layers_by_tag['greatest:hits']['Id'][:12] == FauxDockerClient.SHORT_IDS_BY_PATH[1][0]

        self.layers.sort(key=imagekey, reverse=True)

    # ---- Public hooks --------------------------------------------------

    @_checkandraise.__func__
    def get_image(self, image):
        if not image:
            raise APIError(HTTPError('500 Server Error'), None, explanation='Usage: image_export IMAGE [IMAGE...]')

        layers = []
        next_layer_id = image

        while next_layer_id:
            layer = normalizeimage(self._findlayer(next_layer_id), copy=True)
            layers.append(layer)
            next_layer_id = layers[-1][':parent_id']

        image_file = BytesIO()
        mtime = time()

        with tarfile_open(mode='w', fileobj=image_file) as image_tar_file:
            for layer in layers:
                ti_dir = TarInfo(layer[':id'])
                ti_dir.mtime = mtime
                ti_dir.mode = 0o755
                ti_dir.type = DIRTYPE
                image_tar_file.addfile(ti_dir)

                layer_tar_src_path = ospath_join(self._my_dir, 'data', layer[':short_id'], 'layer.tar')

                with open(layer_tar_src_path, 'rb') as layer_tar_src_file:
                    layer_tar_dst_path = '{}/layer.tar'.format(layer[':id'])
                    ti_layer = image_tar_file.gettarinfo(layer_tar_src_path, layer_tar_dst_path)
                    ti_layer.mtime = mtime
                    ti_layer.mode = 0o644
                    ti_layer.uid = ti_layer.gid = 0
                    ti_layer.uname = ti_layer.gname = ''
                    image_tar_file.addfile(ti_layer, fileobj=layer_tar_src_file)

        image_file.seek(0)

        return image_file

    @_checkandraise.__func__  # pylint: disable=redefined-outer-name,useless-suppression
    def images(self, name=None, quiet=False, all=False, viz=False, filters=None):  # pylint: disable=redefined-outer-name
        checks = (
            ( not quiet, '"quiet" must be False' ),
            ( all or False, '"all" must be True' ),
            ( not viz, '"viz" must be False' ),
            ( filters is None, '"filters" must be None' ),
        )

        for passed, err in checks:
            if not passed:
                raise NotImplementedError(err)

        if name:
            try:
                candidates = [ self._findlayer(name) ]
            except APIError:
                candidates = []
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
                'VirtualSize': candidate['VirtualSize'],
            })

        return images

    @_checkandraise.__func__
    def inspect_image(self, image_id):
        raise NotImplementedError()

    # ---- Protected methods ---------------------------------------------

    @_checkandraise.__func__
    def _findlayer(self, image_id):
        if image_id.lower() in self.layers_by_id:
            return self.layers_by_id[image_id]

        if image_id in self.layers_by_tag:
            return self.layers_by_tag[image_id]

        raise APIError(HTTPError('404 Client Error: Not Found'), None, explanation='No such image: {}'.format(image_id))
