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

from copy import deepcopy
from datetime import datetime
from operator import itemgetter
from os import curdir
from os.path import (
    expanduser,
    expandvars,
    join as ospath_join,
)
from tarfile import TarFile
from unittest import TestCase
from docker.errors import APIError
from _dimgx import TZ_UTC
from dimgx import (
    denormalizeimage,
    extractlayers,
    inspectlayers,
    normalizeimage,
)
from test import HashedBytesIo
from test.fauxdockerclient import FauxDockerClient

# ---- Constants ---------------------------------------------------------

__all__ = ()

_EMTPY_TAR_SHA256 = '84ff92691f909a05b224e1c56abb4864f01b4f8e3c854e4bb4c7baf1d3f6d652'

# ---- Classes -----------------------------------------------------------

# ========================================================================
class DimgxTestCase(TestCase):

    # ---- Public hooks --------------------------------------------------

    def setUp(self):
        super().setUp()
        self.longMessage = True
        self.maxDiff = None
        self._dc = FauxDockerClient()

    def test_extractall(self):
        specs = (
            ( 'getto:dachoppa', slice(None), 'ffd384a2a277c9c1183e5f28da244cc0f4fe92d45e273eaf142dcc4e8fd0e5ef', 0 ),
            ( 'getto:dachoppa', slice(None, None, -1), 'b0e0a8950b060d8cbe6a990ee693a60a3004aea4130c8735cee1bd96706b0173', -1 ),
            ( 'greatest:hits', slice(None), '2b4042d4244b34da51f3a9b761e20f717809c8d68cf53e9c03b2a2e41dae71ca', 0 ),
            ( 'greatest:hits', slice(None, None, -1), '896e1e38159e7f408bada39e8c095fcd8a171ea9de7e2b7363b5bff505a93842', -1 ),
        )

        self._check_specs(specs)

    def test_extractempty(self):
        specs = (
            ( 'getto:dachoppa', ( 0x0, 0x1, 0x2, 0x3, 0x4, 0x5, 0x6, 0x7, 0x8, 0x9, 0xa, 0xb, 0xc ), _EMTPY_TAR_SHA256, 0 ),
            ( 'getto:dachoppa', ( 0xc, 0xb, 0xa, 0x9, 0x8, 0x7, 0x6, 0x5, 0x4, 0x3, 0x2, 0x1, 0x0 ), _EMTPY_TAR_SHA256, -1 ),
            ( 'getto:dachoppa', (), _EMTPY_TAR_SHA256, 0 ),
            ( 'greatest:hits', ( 0x1, 0x2, 0x3, 0x4, 0x5, 0x6, 0x7, 0x8, 0x9, 0xa, 0xc, 0xe ), _EMTPY_TAR_SHA256, 0 ),
            ( 'greatest:hits', ( 0xe, 0xc, 0xa, 0x9, 0x8, 0x7, 0x6, 0x5, 0x4, 0x3, 0x2, 0x1 ), _EMTPY_TAR_SHA256, -1 ),
            ( 'greatest:hits', (), _EMTPY_TAR_SHA256, 0 ),
        )

        self._check_specs(specs)

    def test_extractcombos_path0(self):
        specs = (
            ( 'getto:dachoppa', ( 0xd, ), 'ffd384a2a277c9c1183e5f28da244cc0f4fe92d45e273eaf142dcc4e8fd0e5ef', 0 ),
            ( 'getto:dachoppa', ( 0xe, ), '9dc4223cfbbd67074f22187b5b79ef2b980ec84dea77e71622db26df31284cc3', 0 ),
            ( 'getto:dachoppa', ( 0xf, ), 'b0e0a8950b060d8cbe6a990ee693a60a3004aea4130c8735cee1bd96706b0173', 0 ),
            ( 'getto:dachoppa', ( 0xd, 0xe ), 'ffd384a2a277c9c1183e5f28da244cc0f4fe92d45e273eaf142dcc4e8fd0e5ef', 0 ),
            ( 'getto:dachoppa', ( 0xd, 0xf ), 'ffd384a2a277c9c1183e5f28da244cc0f4fe92d45e273eaf142dcc4e8fd0e5ef', 0 ),
            ( 'getto:dachoppa', ( 0xe, 0xd ), '9dc4223cfbbd67074f22187b5b79ef2b980ec84dea77e71622db26df31284cc3', 1 ),
            ( 'getto:dachoppa', ( 0xe, 0xf ), '9dc4223cfbbd67074f22187b5b79ef2b980ec84dea77e71622db26df31284cc3', 0 ),
            ( 'getto:dachoppa', ( 0xf, 0xd ), 'b0e0a8950b060d8cbe6a990ee693a60a3004aea4130c8735cee1bd96706b0173', 1 ),
            ( 'getto:dachoppa', ( 0xf, 0xe ), 'b0e0a8950b060d8cbe6a990ee693a60a3004aea4130c8735cee1bd96706b0173', 1 ),
            ( 'getto:dachoppa', ( 0xd, 0xe, 0xf ), 'ffd384a2a277c9c1183e5f28da244cc0f4fe92d45e273eaf142dcc4e8fd0e5ef', 0 ),
            ( 'getto:dachoppa', ( 0xd, 0xf, 0xe ), 'ffd384a2a277c9c1183e5f28da244cc0f4fe92d45e273eaf142dcc4e8fd0e5ef', 0 ),
            ( 'getto:dachoppa', ( 0xe, 0xd, 0xf ), '9dc4223cfbbd67074f22187b5b79ef2b980ec84dea77e71622db26df31284cc3', 1 ),
            ( 'getto:dachoppa', ( 0xe, 0xf, 0xd ), '9dc4223cfbbd67074f22187b5b79ef2b980ec84dea77e71622db26df31284cc3', 2 ),
            ( 'getto:dachoppa', ( 0xf, 0xd, 0xe ), 'b0e0a8950b060d8cbe6a990ee693a60a3004aea4130c8735cee1bd96706b0173', 1 ),
            ( 'getto:dachoppa', ( 0xf, 0xe, 0xd ), 'b0e0a8950b060d8cbe6a990ee693a60a3004aea4130c8735cee1bd96706b0173', 2 ),
        )

        self._check_specs(specs)

    def test_extractcombos_path1(self):
        specs = (
            ( 'greatest:hits', ( 0xf, ), '0591d5a0e036416347fb488aa8306e763faa6b914bce257ed9cb6aaa9d42a3ff', 0 ),
            ( 'greatest:hits', ( 0xd, ), '0614535361515191a68e012e02e62535977222ac5cc7804180a10d11356b00b8', 0 ),
            ( 'greatest:hits', ( 0xb, ), 'd0be37a7140825eeb7d18d8074bfba677976803af19926e8f922043971e98041', 0 ),
            ( 'greatest:hits', ( 0x0, ), 'da7eff6919c889afbc4f3e3894556dcae52dbc5e36c20a54743b0027e0422a52', 0 ),
            ( 'greatest:hits', ( 0xd, 0xf ), '55dd2704dfb4ba7f9e6735f6c82277da8a2255b9124c287454301f94be3d5d64', 0 ),
            ( 'greatest:hits', ( 0xb, 0xf ), '0a80831b9aa9a123065ddd8a33a69ffe75bcba99c3b109fb10c7f81bf8670de4', 0 ),
            ( 'greatest:hits', ( 0x0, 0xf ), 'b355fac743bd0f412e268fc205a0c103dae1e9021372e3c58be7aaf9ac3ea692', 0 ),
            ( 'greatest:hits', ( 0xf, 0xd ), '0591d5a0e036416347fb488aa8306e763faa6b914bce257ed9cb6aaa9d42a3ff', 1 ),
            ( 'greatest:hits', ( 0xb, 0xd ), 'd0be37a7140825eeb7d18d8074bfba677976803af19926e8f922043971e98041', 0 ),
            ( 'greatest:hits', ( 0x0, 0xd ), 'da7eff6919c889afbc4f3e3894556dcae52dbc5e36c20a54743b0027e0422a52', 0 ),
            ( 'greatest:hits', ( 0xf, 0xb ), '590469262fef5872b6b9b81a80ec83f4e482cc7c26005e7837029cdea5187d7e', 1 ),
            ( 'greatest:hits', ( 0xd, 0xb ), '8e8a38b8e2026892f2671aa745723ac4f36d427106fb92b275f22af4d0419288', 1 ),
            ( 'greatest:hits', ( 0x0, 0xb ), 'da7eff6919c889afbc4f3e3894556dcae52dbc5e36c20a54743b0027e0422a52', 0 ),
            ( 'greatest:hits', ( 0xf, 0x0 ), '5ec6a9055436b3bdd916198c063a8ba4df9ed1e22ef997f0db3750418c501184', 1 ),
            ( 'greatest:hits', ( 0xd, 0x0 ), 'a57177b137895fa39a6b0f6f888866baf7892b9028e46b7194c4be3870c65c1c', 1 ),
            ( 'greatest:hits', ( 0xb, 0x0 ), '6ecc356781844c21fd55b6f1b5ecb3029268b6e725a0bdc7ef2ff507295c7678', 1 ),
            ( 'greatest:hits', ( 0xb, 0xd, 0xf ), 'b04706534b989cfdbd64549bd9e0497f662ceda222f9fbb019bd96eaa2089156', 0 ),
            ( 'greatest:hits', ( 0x0, 0xd, 0xf ), '2b4042d4244b34da51f3a9b761e20f717809c8d68cf53e9c03b2a2e41dae71ca', 0 ),
            ( 'greatest:hits', ( 0xd, 0xb, 0xf ), '93e0bc9543178b5845437768c24d542671f5f182cc00f0d91e19d0b7340e3b7c', 1 ),
            ( 'greatest:hits', ( 0x0, 0xb, 0xf ), 'b355fac743bd0f412e268fc205a0c103dae1e9021372e3c58be7aaf9ac3ea692', 0 ),
            ( 'greatest:hits', ( 0xd, 0x0, 0xf ), '545481e062ff37ba07e0b1d2f66225d1e0ddb664b0370288e8ba84705ae8f7a6', 1 ),
            ( 'greatest:hits', ( 0xb, 0x0, 0xf ), '1c7a59ea0776d3903210588d5204f8f39deb7e73784318aba0a4ba9be2bf873d', 1 ),
            ( 'greatest:hits', ( 0xb, 0xf, 0xd ), '0a80831b9aa9a123065ddd8a33a69ffe75bcba99c3b109fb10c7f81bf8670de4', 0 ),
            ( 'greatest:hits', ( 0x0, 0xf, 0xd ), 'b355fac743bd0f412e268fc205a0c103dae1e9021372e3c58be7aaf9ac3ea692', 0 ),
            ( 'greatest:hits', ( 0xf, 0xb, 0xd ), '590469262fef5872b6b9b81a80ec83f4e482cc7c26005e7837029cdea5187d7e', 1 ),
            ( 'greatest:hits', ( 0x0, 0xb, 0xd ), 'da7eff6919c889afbc4f3e3894556dcae52dbc5e36c20a54743b0027e0422a52', 0 ),
            ( 'greatest:hits', ( 0xf, 0x0, 0xd ), '5ec6a9055436b3bdd916198c063a8ba4df9ed1e22ef997f0db3750418c501184', 1 ),
            ( 'greatest:hits', ( 0xb, 0x0, 0xd ), '6ecc356781844c21fd55b6f1b5ecb3029268b6e725a0bdc7ef2ff507295c7678', 1 ),
            ( 'greatest:hits', ( 0xd, 0xf, 0xb ), '90fb48afd21ff7894234b0fa705e25fabb4ad1ed4ca5f495f6f21a629f3b06d1', 2 ),
            ( 'greatest:hits', ( 0x0, 0xf, 0xb ), 'b355fac743bd0f412e268fc205a0c103dae1e9021372e3c58be7aaf9ac3ea692', 0 ),
            ( 'greatest:hits', ( 0xf, 0xd, 0xb ), '590469262fef5872b6b9b81a80ec83f4e482cc7c26005e7837029cdea5187d7e', 2 ),
            ( 'greatest:hits', ( 0x0, 0xd, 0xb ), 'da7eff6919c889afbc4f3e3894556dcae52dbc5e36c20a54743b0027e0422a52', 0 ),
            ( 'greatest:hits', ( 0xf, 0x0, 0xb ), '5ec6a9055436b3bdd916198c063a8ba4df9ed1e22ef997f0db3750418c501184', 1 ),
            ( 'greatest:hits', ( 0xd, 0x0, 0xb ), 'a57177b137895fa39a6b0f6f888866baf7892b9028e46b7194c4be3870c65c1c', 1 ),
            ( 'greatest:hits', ( 0xd, 0xf, 0x0 ), '7b3b9dead3ab21ad60a8331eee646704252e7150950f69b934e59fb1f4508bce', 2 ),
            ( 'greatest:hits', ( 0xb, 0xf, 0x0 ), '8a125ec03923bc5664a340074fb1cc4225c4a12c049cc8107d6d36f55b131507', 2 ),
            ( 'greatest:hits', ( 0xf, 0xd, 0x0 ), '5ec6a9055436b3bdd916198c063a8ba4df9ed1e22ef997f0db3750418c501184', 2 ),
            ( 'greatest:hits', ( 0xb, 0xd, 0x0 ), '6ecc356781844c21fd55b6f1b5ecb3029268b6e725a0bdc7ef2ff507295c7678', 2 ),
            ( 'greatest:hits', ( 0xf, 0xb, 0x0 ), '896e1e38159e7f408bada39e8c095fcd8a171ea9de7e2b7363b5bff505a93842', 2 ),
            ( 'greatest:hits', ( 0xd, 0xb, 0x0 ), '85653c0007e63dfe1759e0364ac0a0fbac3566240bc1662e14c7bbceb51379c4', 2 ),
            ( 'greatest:hits', ( 0x0, 0xb, 0xd, 0xf ), '2b4042d4244b34da51f3a9b761e20f717809c8d68cf53e9c03b2a2e41dae71ca', 0 ),
            ( 'greatest:hits', ( 0xb, 0x0, 0xd, 0xf ), 'f638ed20cdbec81c66d52d04584a8235845b31803d99b99acf379639f23eb69a', 1 ),
            ( 'greatest:hits', ( 0x0, 0xd, 0xb, 0xf ), '2b4042d4244b34da51f3a9b761e20f717809c8d68cf53e9c03b2a2e41dae71ca', 0 ),
            ( 'greatest:hits', ( 0xd, 0x0, 0xb, 0xf ), '545481e062ff37ba07e0b1d2f66225d1e0ddb664b0370288e8ba84705ae8f7a6', 1 ),
            ( 'greatest:hits', ( 0xb, 0xd, 0x0, 0xf ), 'f638ed20cdbec81c66d52d04584a8235845b31803d99b99acf379639f23eb69a', 2 ),
            ( 'greatest:hits', ( 0xd, 0xb, 0x0, 0xf ), 'cd5e09e033946e3973d4f0ed852b6d3570207308414d25caba132ac292d2a4fc', 2 ),
            ( 'greatest:hits', ( 0x0, 0xb, 0xf, 0xd ), 'b355fac743bd0f412e268fc205a0c103dae1e9021372e3c58be7aaf9ac3ea692', 0 ),
            ( 'greatest:hits', ( 0xb, 0x0, 0xf, 0xd ), '1c7a59ea0776d3903210588d5204f8f39deb7e73784318aba0a4ba9be2bf873d', 1 ),
            ( 'greatest:hits', ( 0x0, 0xf, 0xb, 0xd ), 'b355fac743bd0f412e268fc205a0c103dae1e9021372e3c58be7aaf9ac3ea692', 0 ),
            ( 'greatest:hits', ( 0xf, 0x0, 0xb, 0xd ), '5ec6a9055436b3bdd916198c063a8ba4df9ed1e22ef997f0db3750418c501184', 1 ),
            ( 'greatest:hits', ( 0xb, 0xf, 0x0, 0xd ), '8a125ec03923bc5664a340074fb1cc4225c4a12c049cc8107d6d36f55b131507', 2 ),
            ( 'greatest:hits', ( 0xf, 0xb, 0x0, 0xd ), '896e1e38159e7f408bada39e8c095fcd8a171ea9de7e2b7363b5bff505a93842', 2 ),
            ( 'greatest:hits', ( 0x0, 0xd, 0xf, 0xb ), '2b4042d4244b34da51f3a9b761e20f717809c8d68cf53e9c03b2a2e41dae71ca', 0 ),
            ( 'greatest:hits', ( 0xd, 0x0, 0xf, 0xb ), '545481e062ff37ba07e0b1d2f66225d1e0ddb664b0370288e8ba84705ae8f7a6', 1 ),
            ( 'greatest:hits', ( 0x0, 0xf, 0xd, 0xb ), 'b355fac743bd0f412e268fc205a0c103dae1e9021372e3c58be7aaf9ac3ea692', 0 ),
            ( 'greatest:hits', ( 0xf, 0x0, 0xd, 0xb ), '5ec6a9055436b3bdd916198c063a8ba4df9ed1e22ef997f0db3750418c501184', 1 ),
            ( 'greatest:hits', ( 0xd, 0xf, 0x0, 0xb ), '7b3b9dead3ab21ad60a8331eee646704252e7150950f69b934e59fb1f4508bce', 2 ),
            ( 'greatest:hits', ( 0xf, 0xd, 0x0, 0xb ), '5ec6a9055436b3bdd916198c063a8ba4df9ed1e22ef997f0db3750418c501184', 2 ),
            ( 'greatest:hits', ( 0xb, 0xd, 0xf, 0x0 ), '2be5f33da3bc8e20dad2d145dd299413f259e3b7b57eef5e712d87aedaa351b8', 3 ),
            ( 'greatest:hits', ( 0xd, 0xb, 0xf, 0x0 ), '4ee28e3b555460263a8d33f952dacf49d5cb9a0d8e387e1fe9d621fe621a2f4e', 3 ),
            ( 'greatest:hits', ( 0xb, 0xf, 0xd, 0x0 ), '8a125ec03923bc5664a340074fb1cc4225c4a12c049cc8107d6d36f55b131507', 3 ),
            ( 'greatest:hits', ( 0xf, 0xb, 0xd, 0x0 ), '896e1e38159e7f408bada39e8c095fcd8a171ea9de7e2b7363b5bff505a93842', 3 ),
            ( 'greatest:hits', ( 0xd, 0xf, 0xb, 0x0 ), '66686153e86459d84092603ce70401d9f7413c4bf4399cd10bf2203a08bfbf29', 3 ),
            ( 'greatest:hits', ( 0xf, 0xd, 0xb, 0x0 ), '896e1e38159e7f408bada39e8c095fcd8a171ea9de7e2b7363b5bff505a93842', 3 ),
        )

        self._check_specs(specs)

    def test_fauxclientsanity(self):
        self.assertEqual(self._dc.images('<does not exist>', all=True), [])

        with self.assertRaises(APIError) as cm:
            self._dc.get_image('<does not exist>')

        self.assertEqual(cm.exception.args[0].args[0], '404 Client Error: Not Found')

        with self.assertRaises(APIError) as cm:
            self._dc.get_image('')

        self.assertEqual(cm.exception.args[0].args[0], '500 Server Error')

        exc = ZeroDivisionError
        dc = FauxDockerClient(exc)
        self.assertRaises(exc, dc.get_image, None)

    def test_normalizeimage(self):
        images = [
            {
                'Created': '2015-05-01T12:34:56.789012345Z',
                'Id': '0123456789ABCDEFfedcba98765432100123456789abcdefFEDCBA9876543210',
                'Parent': 'FEDCBA98765432100123456789abcdeffedcba98765432100123456789ABCDEF',
                'RepoTags': [ '<none>:<none>' ],
                'Size': 0,
                'VirtualSize': 0,
            }, {
                'Created': 1431216000,
                'Id': 'fedcba9876543210FEDCBA98765432100123456789abcdef0123456789ABCDEF',
                'ParentId': '0123456789abcdef0123456789ABCDEFfedcba9876543210FEDCBA9876543210',
                'RepoTags': [ 'foo:bar', 'baz:latest' ],
                'Size': 0,
                'VirtualSize': 0,
            }
        ]

        normalized_images = [
            {
                ':created_dt': datetime(2015, 5, 1, 12, 34, 56, 789012, TZ_UTC),
                ':id': '0123456789abcdeffedcba98765432100123456789abcdeffedcba9876543210',
                ':parent_id': 'fedcba98765432100123456789abcdeffedcba98765432100123456789abcdef',
                ':short_id': '0123456789ab',
                ':repo_tags': [],
            }, {
                ':created_dt': datetime(2015, 5, 10, 0, 0, 0, 0, TZ_UTC),
                ':id': 'fedcba9876543210fedcba98765432100123456789abcdef0123456789abcdef',
                ':parent_id': '0123456789abcdef0123456789abcdeffedcba9876543210fedcba9876543210',
                ':short_id': 'fedcba987654',
                ':repo_tags': [ 'foo:bar', 'baz', 'baz:latest' ],
            }
        ]

        for i, ni in zip(images, normalized_images):
            ni.update(i)
            normalized_image = normalizeimage(i, copy=True)
            self.assertIsNot(normalized_image, i)

            denormalized_image = denormalizeimage(normalized_image, copy=True)
            self.assertIsNot(denormalized_image, normalized_image)

            self.assertNotEqual(normalized_image, i)
            self.assertEqual(normalized_image, ni)
            self.assertNotEqual(denormalized_image, ni)
            self.assertEqual(denormalized_image, i)

        image = deepcopy(images[0])
        self.assertIs(normalizeimage(image), image)
        self.assertIs(denormalizeimage(image), image)

    # --- Protected methods ----------------------------------------------

    def _check_specs(self, specs):
        for image_id, indexes, hexdigest, top_most_layer in specs:
            hash_tar = self._get_hash_tar(image_id, indexes, top_most_layer)
            self.assertEqual(hash_tar.hash_obj.hexdigest(), hexdigest, msg='image: {}; indexes: {}'.format(image_id, indexes))

    def _dump_tars(self, specs, dump_dir=curdir):
        expanded_dump_dir = expandvars(expanduser(dump_dir))

        hashes_to_indexes = {}

        with open(ospath_join(expanded_dump_dir, '_dumped_entries.py'), 'wb') as dump_py_file:
            for image_id, indexes, _, top_most_layer in specs:
                hash_tar = self._get_hash_tar(image_id, indexes, top_most_layer)
                actual_hexdigest = hash_tar.hash_obj.hexdigest()

                with open(ospath_join(expanded_dump_dir, '{}.tar'.format(actual_hexdigest)), 'wb') as dump_tar_file:
                    try:
                        index_list = hashes_to_indexes[actual_hexdigest]
                    except KeyError:
                        index_list = hashes_to_indexes[actual_hexdigest] = []

                    index_list.append(indexes)
                    dump_tar_file.write(hash_tar.getvalue())

                print("( '{}', ( {} ), '{}', {} ),".format(image_id, ', '.join(( '0x{:1x}'.format(i) for i in indexes )), actual_hexdigest, min(enumerate(indexes), key=itemgetter(1))[0]), file=dump_py_file)

            for k, v in iteritems(hashes_to_indexes):
                print('# {} -> {}'.format(k, v), file=dump_py_file)

    def _get_hash_tar(self, image_id, indexes, top_most_layer):
        target_file = HashedBytesIo()

        with TarFile(mode='w', fileobj=target_file) as tar_file:
            layers_dict = inspectlayers(self._dc, image_id)

            if isinstance(indexes, slice):
                layers = layers_dict[':layers'][indexes]
            else:
                if indexes:
                    self.assertLess(top_most_layer, len(indexes), msg='image: {}; indexes: {}'.format(image_id, indexes))
                    self.assertGreaterEqual(top_most_layer, -len(indexes), msg='image: {}; indexes: {}'.format(image_id, indexes))
                    self.assertEqual(indexes[top_most_layer], min(indexes), msg='image: {}; indexes: {}'.format(image_id, indexes))

                layers = [ layers_dict[':layers'][i] for i in indexes ]

            extractlayers(self._dc, layers, tar_file, top_most_layer)

        target_file.seek(0)

        return target_file

# ---- Initialization ----------------------------------------------------

if __name__ == '__main__':
    from unittest import main
    main()
