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
# pylint: disable=missing-super-argument

#---- Imports ------------------------------------------------------------

from copy import deepcopy
from datetime import datetime
from unittest import TestCase
from docker.errors import (
    APIError,
    DockerException,
)
from _dimgx import TZ_UTC
from dimgx import (
    denormalizeimage,
    normalizeimage,
)
from tests.fauxdockerclient import FauxDockerClient

#---- Classes ------------------------------------------------------------

#=========================================================================
class DimgxTestCase(TestCase):

    #---- Public hook methods --------------------------------------------

    #=====================================================================
    def setUp(self):
        super().setUp()
        self.longMessage = True
        self.maxDiff = None

    #=====================================================================
    def test_fauxclient(self):
        exc = ZeroDivisionError
        dc = FauxDockerClient(exc)
        self.assertRaises(exc, dc.get_image, None)

    #=====================================================================
    def test_normalizeimage(self):
        images = [
            {
                'Created': '2015-05-01T12:34:56.789012345Z',
                'Id': '0123456789ABCDEFfedcba98765432100123456789abcdefFEDCBA9876543210',
                'Parent': 'FEDCBA98765432100123456789abcdeffedcba98765432100123456789ABCDEF',
                'RepoTags': [ '<none>:<none>' ],
                'Size': 0,
            } , {
                'Created': 1431216000,
                'Id': 'fedcba9876543210FEDCBA98765432100123456789abcdef0123456789ABCDEF',
                'ParentId': '0123456789abcdef0123456789ABCDEFfedcba9876543210FEDCBA9876543210',
                'RepoTags': [ 'foo:bar', 'baz:latest' ],
                'Size': 0,
            }
        ]

        normalized_images = [
            {
                'Created': '2015-05-01T12:34:56.789012345Z',
                'Id': '0123456789ABCDEFfedcba98765432100123456789abcdefFEDCBA9876543210',
                'Parent': 'FEDCBA98765432100123456789abcdeffedcba98765432100123456789ABCDEF',
                'RepoTags': [ '<none>:<none>' ],
                'Size': 0,
                ':created_dt': datetime(2015, 5, 1, 12, 34, 56, 789012, TZ_UTC),
                ':id': '0123456789abcdeffedcba98765432100123456789abcdeffedcba9876543210',
                ':parent_id': 'fedcba98765432100123456789abcdeffedcba98765432100123456789abcdef',
                ':short_id': '0123456789ab',
                ':repo_tags': [],
            }, {
                'Created': 1431216000,
                'Id': 'fedcba9876543210FEDCBA98765432100123456789abcdef0123456789ABCDEF',
                'ParentId': '0123456789abcdef0123456789ABCDEFfedcba9876543210FEDCBA9876543210',
                'Size': 0,
                'RepoTags': [ 'foo:bar', 'baz:latest' ],
                ':created_dt': datetime(2015, 5, 10, 0, 0, 0, 0, TZ_UTC),
                ':id': 'fedcba9876543210fedcba98765432100123456789abcdef0123456789abcdef',
                ':parent_id': '0123456789abcdef0123456789abcdeffedcba9876543210fedcba9876543210',
                ':short_id': 'fedcba987654',
                ':repo_tags': [ 'foo:bar', 'baz:latest', 'baz' ],
            }
        ]

        for i, ni in zip(images, normalized_images):
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

#---- Initialization -----------------------------------------------------

if __name__ == '__main__':
    from unittest import main
    main()
