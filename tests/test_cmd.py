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

from argparse import ArgumentParser
from io import StringIO
from os import linesep
from unittest import TestCase
from _dimgx.cmd import (
    buildparser,
    printlayerinfo,
    selectlayers,
)
from _dimgx.version import __version__
from dimgx import inspectlayers
from tests.fauxdockerclient import FauxDockerClient

#---- Constants ----------------------------------------------------------

__all__ = ()

#---- Classes ------------------------------------------------------------

#=========================================================================
class FakeSystemExit(Exception):
    pass

#=========================================================================
class FakeExitingArgumentParser(ArgumentParser):

    #---- Constructor ----------------------------------------------------

    #=====================================================================
    def __init__(self, *args, **kw):
        ArgumentParser.__init__(self, *args, **kw)
        self.buf = StringIO()

    #---- Public hook methods --------------------------------------------

    #=====================================================================
    def exit(self, status=0, message=None):
        try:
            return ArgumentParser.exit(self, status, message)
        except SystemExit:
            raise FakeSystemExit(status)

    #---- Private hook methods -------------------------------------------

    #=====================================================================
    def _print_message(self, message, file=None): # pylint: disable=redefined-outer-name,unused-argument
        return ArgumentParser._print_message(self, message, self.buf)

#=========================================================================
class CommandTestCase(TestCase):

    #---- Public hook methods --------------------------------------------

    #=====================================================================
    def setUp(self):
        super().setUp()
        self.longMessage = True
        self.maxDiff = None
        self._parser = buildparser(FakeExitingArgumentParser)
        self._dc = FauxDockerClient()

    #=====================================================================
    def tearDown(self):
        super().tearDown()
        self._parser.buf.close()

    #=====================================================================
    def test_layerspecs(self):
        path_ids = FauxDockerClient.SHORT_IDS_BY_PATH[0]
        image_spec = '52d7263f000f'

        specs = (
            {
                'args': ( '-q', image_spec ),
                'layer_ids': path_ids,
            }, {
                'args': ( '-r', '-q', image_spec ),
                'layer_ids': path_ids[::-1],
            }, {
                'args': ( '-l', 'ffffffffffff', '-q', image_spec ),
                'layer_ids': [],
            }, {
                'args': ( '-l', '2b32db6c0000:ffffffffffff', '-q', image_spec ),
                'layer_ids': [],
            }, {
                'args': ( '-l', 'ffffffffffff:52d7263f000f', '-q', image_spec ),
                'layer_ids': [],
            }, {
                'args': (  '-l', '52d7263f000f', '-l', 'ffffffffffff', '-q', image_spec ),
                'layer_ids': path_ids[0x0:0x1],
            }, {
                'args': (  '-l', 'ffffffffffff', '-l', '52d7263f000f', '-q', image_spec ),
                'layer_ids': path_ids[0x0:0x1],
            }, {
                'args': (  '-l', '52d7263f000f', '-q', image_spec ),
                'layer_ids': path_ids[0x0:0x1],
            }, {
                'args': (  '-l', '52d7263f000f:52d7263f000f', '-q', image_spec ),
                'layer_ids': path_ids[0x0:0x1],
            }, {
                'args': (  '-l', '5a48f220000e:52d7263f000f', '-q', image_spec ),
                'layer_ids': path_ids[0x0:0x2],
            }, {
                'args': (  '-l', '52d7263f000f:5a48f220000e', '-r', '-q', image_spec ),
                'layer_ids': path_ids[0x0:0x2],
            }, {
                'args': (  '-l', '52d7263f000f:5a48f220000e', '-q', image_spec ),
                'layer_ids': path_ids[0x1::-1],
            }, {
                'args': (  '-l', '5a48f220000e:52d7263f000f', '-r', '-q', image_spec ),
                'layer_ids': path_ids[0x1::-1],
            }, {
                'args': ( '-l', '2b32db6c0000', '-l', '52d7263f000f', '-l', 'ff304d2a0001', '-l', '5a48f220000e', '-q', image_spec ),
                'layer_ids': [ path_ids[0x1], path_ids[0xe], path_ids[0x0], path_ids[0xf] ],
            }, {
                'args': ( '-l', '2b32db6c0000', '-l', '52d7263f000f', '-l', 'ff304d2a0001', '-l', '5a48f220000e', '-r', '-q', image_spec ),
                'layer_ids': [ path_ids[0xf], path_ids[0x0], path_ids[0xe], path_ids[0x1] ],
            }, {
                'args': ( '-l', 'ff304d2a0001', '-l', 'f62dd7680002', '-l', 'ff304d2a0001', '-l', '0c2ccea2000a', '-q', image_spec ),
                'layer_ids': [ path_ids[0x5], path_ids[0xe], path_ids[0xd] ],
            }, {
                'args': ( '-l', 'ff304d2a0001', '-l', 'f62dd7680002', '-l', 'ff304d2a0001', '-l', '0c2ccea2000a', '-r', '-q', image_spec ),
                'layer_ids': [ path_ids[0xe], path_ids[0xd], path_ids[0x5] ],
            }, {
                'args': ( '-l', 'f62dd7680002', '-l', '149dccab0003:2b32db6c0000', '-q', image_spec ),
                'layer_ids': path_ids[0xf:0xb:-1],
            }, {
                'args': ( '-l', 'f62dd7680002', '-l', '149dccab0003:2b32db6c0000', '-r', '-q', image_spec ),
                'layer_ids': [ path_ids[0xd], path_ids[0xc], path_ids[0xe], path_ids[0xf] ],
            }, {
                'args': ( '-l', 'ff304d2a0001', '-q', image_spec ),
                'layer_ids': path_ids[0xe:0xf],
            }, {
                'args': ( '-l', '2b32db6c0000:ff304d2a0001', '-q', image_spec ),
                'layer_ids': path_ids[0xe:],
            }, {
                'args': ( '-l', '2b32db6c0000:ff304d2a0001', '-r', '-q', image_spec ),
                'layer_ids': path_ids[0xf:0xd:-1],
            }, {
                'args': ( '-l', 'ff304d2a0001:2b32db6c0000', '-q', image_spec ),
                'layer_ids': path_ids[0xf:0xd:-1],
            }, {
                'args': ( '-l', 'ff304d2a0001:2b32db6c0000', '-r', '-q', image_spec ),
                'layer_ids': path_ids[0xe:],
            }, {
                'args': ( '-l', 'ff304d2a0001:52d7263f000f', '-q', image_spec ),
                'layer_ids': path_ids[:0xf],
            }, {
                'args': ( '-l', 'ff304d2a0001:52d7263f000f', '-r', '-q', image_spec ),
                'layer_ids': path_ids[0xe::-1],
            }, {
                'args': ( '-l', '52d7263f000f:ff304d2a0001', '-q', image_spec ),
                'layer_ids': path_ids[0xe::-1],
            }, {
                'args': ( '-l', '52d7263f000f:ff304d2a0001', '-r', '-q', image_spec ),
                'layer_ids': path_ids[:0xf],
            }
        )

        for spec in specs:
            args = self._parser.parse_args(spec['args'])
            layers_dict = inspectlayers(self._dc, args.image)
            top_most_layer_id, selected_layers = selectlayers(args, layers_dict)
            layer_ids = spec['layer_ids']

            if top_most_layer_id is not None:
                self.assertEqual(top_most_layer_id[:12], max(spec['layer_ids'], key=lambda i: i[-4:]), msg='spec: {!r}; selected_layers: {!r}'.format(spec, selected_layers))

            self.assertEqual(len(layer_ids), len(selected_layers), msg='spec: {!r}; selected_layers: {!r}'.format(spec, selected_layers))

            for layer_id, selected_layer in zip(layer_ids, selected_layers):
                self.assertEqual(layer_id, selected_layer['Id'][:len(layer_id)], msg='spec: {!r}; selected_layers: {!r}'.format(spec, selected_layers))

            outfile = StringIO()
            printlayerinfo(args, selected_layers, outfile)
            outfile.seek(0)
            self.assertEqual([ l.strip() for l in outfile ], layer_ids)

    #=====================================================================
    def test_version(self):
        try:
            self._parser.parse_args(( '-V', ))
        except FakeSystemExit:
            self.assertTrue(self._parser.buf.getvalue().endswith(' ' + __version__ + linesep))
        else:
            self.assertFail('-V did not cause exit')

        try:
            self._parser.parse_args(( '--version', ))
        except FakeSystemExit:
            self.assertTrue(self._parser.buf.getvalue().endswith(' ' + __version__ + linesep))
        else:
            self.assertFail('--version did not cause exit')

#---- Initialization -----------------------------------------------------

if __name__ == '__main__':
    from unittest import main
    main()
