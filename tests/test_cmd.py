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

from io import StringIO
from unittest import TestCase
from _dimgx.cmd import (
    buildparser,
    printlayerinfo,
    selectlayers,
)

#---- Classes ------------------------------------------------------------

#=========================================================================
class CommandTestCase(TestCase):

    #---- Constructor ----------------------------------------------------

    #=====================================================================
    def setUp(self):
        super().setUp()
        self.longMessage = True
        self._parser = buildparser()

        # Build some fake layers for testing
        self._fake_layers = {}
        layers_list = []
        last_layer_id = ''

        for i in range(0, 0x10):
            layer_chr = '{:1x}'.format(i)
            layer_id = layer_chr * 64
            layer = {
                'Created': '2015-05-{:02d}T{:02d}:00:00Z'.format(i + 10, i),
                'Id': layer_id,
                'Parent': last_layer_id,
                'Size': int(layer_chr * 7, 16),
            }
            self._fake_layers[layer_id[:12]] = i
            self._fake_layers[layer_id] = i
            layers_list.append(layer)
            last_layer_id = layer_id

        layers_list = tuple(layers_list)

        for k, v in iteritems(self._fake_layers):
            self.assertEqual(k, layers_list[v]['Id'][:len(k)], msg='( k, v ): {!r}'.format(( k, v )))

        self._fake_layers['layers_list'] = layers_list

    #---- Hook methods ---------------------------------------------------

    #=====================================================================
    def test_layerspecs(self):
        specs = (
            {
                'args': ( '-q', 'IMAGE_SPEC', ),
                'layer_ids': ( '000000000000', '111111111111', '222222222222', '333333333333', '444444444444', '555555555555', '666666666666', '777777777777', '888888888888', '999999999999', 'aaaaaaaaaaaa', 'bbbbbbbbbbbb', 'cccccccccccc', 'dddddddddddd', 'eeeeeeeeeeee', 'ffffffffffff' ),
            }, {
                'args': ( '-r', '-q', 'IMAGE_SPEC', ),
                'layer_ids': ( 'ffffffffffff', 'eeeeeeeeeeee', 'dddddddddddd', 'cccccccccccc', 'bbbbbbbbbbbb', 'aaaaaaaaaaaa', '999999999999', '888888888888', '777777777777', '666666666666', '555555555555', '444444444444', '333333333333', '222222222222', '111111111111', '000000000000' ),
            }, {
                'args': ( '-l15', '-q', 'IMAGE_SPEC' ),
                'layer_ids': ( 'ffffffffffff', ),
            }, {
                'args': ( '-l15:15', '-q', 'IMAGE_SPEC' ),
                'layer_ids': ( 'ffffffffffff', ),
            }, {
                'args': ( '-l15:16', '-q', 'IMAGE_SPEC' ),
                'layer_ids': ( 'ffffffffffff', ),
            }, {
                'args': ( '-l-1', '-q', 'IMAGE_SPEC' ),
                'layer_ids': ( 'ffffffffffff', ),
            }, {
                'args': ( '-l-1:-1', '-q', 'IMAGE_SPEC' ),
                'layer_ids': ( 'ffffffffffff', ),
            }, {
                'args': ( '-l16:-1', '-q', 'IMAGE_SPEC' ),
                'layer_ids': ( 'ffffffffffff', ),
            }, {
                'args': ( '-l-1:16', '-q', 'IMAGE_SPEC' ),
                'layer_ids': ( 'ffffffffffff', ),
            }, {
                'args': ( '-l16:ffffffffffff', '-q', 'IMAGE_SPEC' ),
                'layer_ids': ( 'ffffffffffff', ),
            }, {
                'args': ( '-lffffffffffff:16', '-q', 'IMAGE_SPEC' ),
                'layer_ids': ( 'ffffffffffff', ),
            }, {
                'args': ( '-l-1:ffffffffffff', '-q', 'IMAGE_SPEC' ),
                'layer_ids': ( 'ffffffffffff', ),
            }, {
                'args': ( '-lffffffffffff:-1', '-q', 'IMAGE_SPEC' ),
                'layer_ids': ( 'ffffffffffff', ),
            }, {
                'args': ( '-l14:16', '-q', 'IMAGE_SPEC' ),
                'layer_ids': ( 'eeeeeeeeeeee', 'ffffffffffff' ),
            }, {
                'args': ( '-lffffffffffff:-2', '-r', '-q', 'IMAGE_SPEC' ),
                'layer_ids': ( 'eeeeeeeeeeee', 'ffffffffffff' ),
            }, {
                'args': ( '-l1:-17', '-q', 'IMAGE_SPEC' ),
                'layer_ids': ( '111111111111', '000000000000' ),
            }, {
                'args': ( '-l000000000000:-15', '-r', '-q', 'IMAGE_SPEC' ),
                'layer_ids': ( '111111111111', '000000000000' ),
            }, {
                'args': ( '-l', '0', '-l', '-1', '-l', '1', '-l', '-2', '-q', 'IMAGE_SPEC' ),
                'layer_ids': ( '000000000000', 'ffffffffffff', '111111111111', 'eeeeeeeeeeee' ),
            }, {
                'args': ( '-l', '0', '-l', '-1', '-l', '1', '-l', '-2', '-r', '-q', 'IMAGE_SPEC' ),
                'layer_ids': ( 'eeeeeeeeeeee', '111111111111', 'ffffffffffff', '000000000000' ),
            }, {
                'args': ( '-l-10:10', '-q', 'IMAGE_SPEC' ),
                'layer_ids': ( '666666666666', '777777777777', '888888888888', '999999999999', 'aaaaaaaaaaaa' ),
            }, {
                'args': ( '-l6:-6', '-q', 'IMAGE_SPEC' ),
                'layer_ids': ( '666666666666', '777777777777', '888888888888', '999999999999', 'aaaaaaaaaaaa' ),
            }, {
                'args': ( '-l6:-6', '-r', '-q', 'IMAGE_SPEC' ),
                'layer_ids': ( 'aaaaaaaaaaaa', '999999999999', '888888888888', '777777777777', '666666666666' ),
            }, {
                'args': ( '-l-6:6', '-l6:-6', '-q', 'IMAGE_SPEC' ),
                'layer_ids': ( '666666666666', '777777777777', '888888888888', '999999999999', 'aaaaaaaaaaaa' ),
            }, {
                'args': ( '-l-6:6', '-l6:-6', '-r', '-q', 'IMAGE_SPEC' ),
                'layer_ids': ( '666666666666', '777777777777', '888888888888', '999999999999', 'aaaaaaaaaaaa' ),
            }, {
                'args': ( '-l', '111111111111', '-l', '222222222222', '-l', '111111111111', '-l', 'aaaaaaaaaaaa', '-q', 'IMAGE_SPEC' ),
                'layer_ids': ( '222222222222', '111111111111', 'aaaaaaaaaaaa' ),
            }, {
                'args': ( '-l', '111111111111', '-l', '222222222222', '-l', '111111111111', '-l', 'aaaaaaaaaaaa', '-r', '-q', 'IMAGE_SPEC' ),
                'layer_ids': ( 'aaaaaaaaaaaa', '222222222222', '111111111111' ),
            }, {
                'args': ( '-l', '222222222222', '-l', '333333333333:000000000000', '-q', 'IMAGE_SPEC' ),
                'layer_ids': ( '333333333333', '222222222222', '111111111111', '000000000000' ),
            }, {
                'args': ( '-l', '222222222222', '-l', '333333333333:000000000000', '-r', '-q', 'IMAGE_SPEC' ),
                'layer_ids': ( '000000000000', '111111111111', '333333333333', '222222222222' ),
            }, {
                'args': ( '-l', '010101010101', '-q', 'IMAGE_SPEC' ),
                'layer_ids': (),
            }, {
                'args': ( '-l', '010101010101:0', '-q', 'IMAGE_SPEC' ),
                'layer_ids': (),
            }, {
                'args': ( '-l', '010101010101:-1', '-q', 'IMAGE_SPEC' ),
                'layer_ids': (),
            }, {
                'args': ( '-l', '000000000000:010101010101', '-q', 'IMAGE_SPEC' ),
                'layer_ids': (),
            }, {
                'args': ( '-l', '010101010101:ffffffffffff', '-q', 'IMAGE_SPEC' ),
                'layer_ids': (),
            }
        )

        for spec in specs:
            args = self._parser.parse_args(spec['args'])
            selected_layers = selectlayers(args, self._fake_layers)
            layer_ids = spec['layer_ids']
            self.assertEqual(len(layer_ids), len(selected_layers), msg='spec: {!r}; selected_layers: {!r}'.format(spec, selected_layers))

            for layer_id, selected_layer in zip(layer_ids, selected_layers):
                self.assertEqual(layer_id, selected_layer['Id'][:len(layer_id)], msg='spec: {!r}; selected_layers: {!r}'.format(spec, selected_layers))

            outfile = StringIO()
            printlayerinfo(args, selected_layers, outfile)
            outfile.seek(0)
            self.assertEqual(tuple(( l.strip() for l in outfile )), layer_ids)
