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

from io import StringIO
from unittest import TestCase
from _dimgx.cmd import (
    buildparser,
    printlayerinfo,
    selectlayers,
)
from dimgx import inspectlayers
from tests.fauxdockerclient import FauxDockerClient

#---- Constants ----------------------------------------------------------

__all__ = ()

#---- Classes ------------------------------------------------------------

#=========================================================================
class CommandTestCase(TestCase):

    #---- Public hook methods --------------------------------------------

    #=====================================================================
    def setUp(self):
        super().setUp()
        self.longMessage = True
        self.maxDiff = None
        self._parser = buildparser()
        self._dc = FauxDockerClient()

    #=====================================================================
    def test_layerspecs(self):
        path_ids = self._dc.ids_by_path[0]
        image_spec = path_ids[-1]

        specs = (
            {
                'args': ( '-q', image_spec ),
                'layer_ids': path_ids,
            }, {
                'args': ( '-r', '-q', image_spec ),
                'layer_ids': path_ids[::-1],
            }, {
                'args': (  '-l', '15', '-q', image_spec ),
                'layer_ids': [ path_ids[0xf] ],
            }, {
                'args': (  '-l', '15:15', '-q', image_spec ),
                'layer_ids': [ path_ids[0xf] ],
            }, {
                'args': (  '-l', '15:16', '-q', image_spec ),
                'layer_ids': [ path_ids[0xf] ],
            }, {
                'args': ( '-l-1', '-q', image_spec ),
                'layer_ids': [ path_ids[0xf] ],
            }, {
                'args': ( '-l-1:-1', '-q', image_spec ),
                'layer_ids': [ path_ids[0xf] ],
            }, {
                'args': (  '-l', '16:-1', '-q', image_spec ),
                'layer_ids': [ path_ids[0xf] ],
            }, {
                'args': ( '-l-1:16', '-q', image_spec ),
                'layer_ids': [ path_ids[0xf] ],
            }, {
                'args': (  '-l', '16:{}'.format(path_ids[0xf]), '-q', image_spec ),
                'layer_ids': [ path_ids[0xf] ],
            }, {
                'args': (  '-l', '{}:16'.format(path_ids[0xf]), '-q', image_spec ),
                'layer_ids': [ path_ids[0xf] ],
            }, {
                'args': ( '-l-1:{}'.format(path_ids[0xf]), '-q', image_spec ),
                'layer_ids': [ path_ids[0xf] ],
            }, {
                'args': (  '-l', '{}:-1'.format(path_ids[0xf]), '-q', image_spec ),
                'layer_ids': [ path_ids[0xf] ],
            }, {
                'args': (  '-l', '14:16', '-q', image_spec ),
                'layer_ids': [ path_ids[0xe], path_ids[0xf] ],
            }, {
                'args': (  '-l', '{}:-2'.format(path_ids[0xf]), '-r', '-q', image_spec ),
                'layer_ids': [ path_ids[0xe], path_ids[0xf] ],
            }, {
                'args': (  '-l', '1:-17', '-q', image_spec ),
                'layer_ids': [ path_ids[0x1], path_ids[0x0] ],
            }, {
                'args': (  '-l', '{}:-15'.format(path_ids[0x0]), '-r', '-q', image_spec ),
                'layer_ids': [ path_ids[0x1], path_ids[0x0] ],
            }, {
                'args': ( '-l', '0', '-l', '-1', '-l', '1', '-l', '-2', '-q', image_spec ),
                'layer_ids': [ path_ids[0x0], path_ids[0xf], path_ids[0x1], path_ids[0xe] ],
            }, {
                'args': ( '-l', '0', '-l', '-1', '-l', '1', '-l', '-2', '-r', '-q', image_spec ),
                'layer_ids': [ path_ids[0xe], path_ids[0x1], path_ids[0xf], path_ids[0x0] ],
            }, {
                'args': ( '-l-10:10', '-q', image_spec ),
                'layer_ids': path_ids[0x6:0xb],
            }, {
                'args': ( '-l6:-6', '-q', image_spec ),
                'layer_ids': path_ids[0x6:0xb],
            }, {
                'args': ( '-l6:-6', '-r', '-q', image_spec ),
                'layer_ids': path_ids[0xa:0x5:-1],
            }, {
                'args': ( '-l-6:6',  '-l', '6:-6', '-q', image_spec ),
                'layer_ids': path_ids[0x6:0xb],
            }, {
                'args': ( '-l-6:6',  '-l', '6:-6', '-r', '-q', image_spec ),
                'layer_ids': path_ids[0x6:0xb],
            }, {
                'args': ( '-l', path_ids[0x1], '-l', path_ids[0x2], '-l', path_ids[0x1], '-l', path_ids[0xa], '-q', image_spec ),
                'layer_ids': [ path_ids[0x2], path_ids[0x1], path_ids[0xa] ],
            }, {
                'args': ( '-l', path_ids[0x1], '-l', path_ids[0x2], '-l', path_ids[0x1], '-l', path_ids[0xa], '-r', '-q', image_spec ),
                'layer_ids': [ path_ids[0xa], path_ids[0x2], path_ids[0x1] ],
            }, {
                'args': ( '-l', path_ids[0x2], '-l', '{}:{}'.format(path_ids[0x3], path_ids[0x0]), '-q', image_spec ),
                'layer_ids': [ path_ids[0x3], path_ids[0x2], path_ids[0x1], path_ids[0x0] ],
            }, {
                'args': ( '-l', path_ids[0x2], '-l', '{}:{}'.format(path_ids[0x3], path_ids[0x0]), '-r', '-q', image_spec ),
                'layer_ids': [ path_ids[0x0], path_ids[0x1], path_ids[0x3], path_ids[0x2] ],
            }, {
                'args': ( '-l', path_ids[0x1], '-q', image_spec ),
                'layer_ids': [ path_ids[0x1] ],
            }, {
                'args': ( '-l', '{}:0'.format(path_ids[0x1]), '-q', image_spec ),
                'layer_ids': [ path_ids[0x1], path_ids[0x0] ],
            }, {
                'args': ( '-l', '{}:-1'.format(path_ids[0x1]), '-q', image_spec ),
                'layer_ids': path_ids[0x1:],
            }, {
                'args': ( '-l', '{}:{}'.format(path_ids[0x0], path_ids[0x1]), '-q', image_spec ),
                'layer_ids': [ path_ids[0x0], path_ids[0x1] ],
            }, {
                'args': ( '-l', '{}:{}'.format(path_ids[0x1], path_ids[0xf]), '-q', image_spec ),
                'layer_ids': path_ids[0x1:],
            }
        )

        for spec in specs:
            args = self._parser.parse_args(spec['args'])
            layers_dict = inspectlayers(self._dc, args.image)
            top_most_layer_id, selected_layers = selectlayers(args, layers_dict)
            layer_ids = spec['layer_ids']
            self.assertEqual(top_most_layer_id[:12], max(spec['layer_ids'], key=lambda i: i[-4:]), msg='spec: {!r}; selected_layers: {!r}'.format(spec, selected_layers))
            self.assertEqual(len(layer_ids), len(selected_layers), msg='spec: {!r}; selected_layers: {!r}'.format(spec, selected_layers))

            for layer_id, selected_layer in zip(layer_ids, selected_layers):
                self.assertEqual(layer_id, selected_layer['Id'][:len(layer_id)], msg='spec: {!r}; selected_layers: {!r}'.format(spec, selected_layers))

            outfile = StringIO()
            printlayerinfo(args, selected_layers, outfile)
            outfile.seek(0)
            self.assertEqual([ l.strip() for l in outfile ], layer_ids)

#---- Initialization -----------------------------------------------------

if __name__ == '__main__':
    from unittest import main
    main()
