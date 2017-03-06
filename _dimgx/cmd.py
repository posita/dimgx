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

# ---- Imports -----------------------------------------------------------

from argparse import (
    ArgumentParser,
    ArgumentTypeError,
)
from collections import OrderedDict
from errno import errorcode
from functools import wraps
from logging import (
    DEBUG,
    ERROR,
    INFO,
    WARNING,
    basicConfig as logging_basicConfig,
    getLevelName as logging_getLevelName,
    getLogger,
)
from os import (
    O_CREAT,
    O_EXCL,
    O_TRUNC,
    O_WRONLY,
    SEEK_CUR,
    environ,
    fdopen,
    fstat,
    lseek,
    open as os_open,
)
from os.path import (
    extsep as ospath_extsep,
    splitext as ospath_splitext,
)
from re import (
    IGNORECASE,
    compile as re_compile,
)
from stat import S_ISREG
from sys import (
    argv as sys_argv,
    exit as sys_exit,
    stdout,
)
from tarfile import open as tarfile_open
from docker import AutoVersionClient
from docker.utils import kwargs_from_env
from humanize import naturalsize
from dimgx import (
    inspectlayers,
    extractlayers as dimgx_extractlayers,
    patch_broken_tarfile_29760,
)
from _dimgx import (
    logexception,
    naturaltime,
)
from _dimgx.version import __release__

# ---- Constants ---------------------------------------------------------

__all__ = ()

DOCKER_TLS_VERIFY = environ.get('DOCKER_TLS_VERIFY', None)
DOCKER_TLS_VERIFY = DOCKER_TLS_VERIFY if DOCKER_TLS_VERIFY else None

_LOGGER = getLogger(__name__.lstrip('_'))
_LAYER_RE_STR = r'(?:[0-9A-Fa-f]{1,64})'
_LAYER_SPEC_RE = re_compile(r'^(?P<l>{layer_re})(?::(?P<r>{layer_re}))?$'.format(layer_re=_LAYER_RE_STR), IGNORECASE)
_TARGET_STDOUT = '-'
_CMP_BZIP2 = 'bz2'
_CMP_GZIP = 'gz'
_CMP_NONE = None
_DEFAULT_CMP_LVL = 9
_DEFAULT_LOG_FMT = '%(levelname)-8s: %(message)s'
_LOG_LEVELS_BY_NAME = OrderedDict(( ( logging_getLevelName(l), l ) for l in ( ERROR, WARNING, INFO, DEBUG ) ))
_DEFAULT_LOG_LVL = logging_getLevelName(WARNING)
_EXIT_EXEC = 2
_EXIT_LAYER_SPEC = 3

_USAGE = """
%(prog)s [options] [-l LAYER_SPEC] ... [-t PATH] IMAGE_SPEC
%(prog)s -h # for help
"""

_DESCRIPTION = """
Docker IMaGe layer eXtractor (and flattener)
"""

_EPILOG = """
Diagnostics: 1 for a problem encountered while parsing the command arguments; {} for an execution error; {} for a LAYER_SPEC that doesn\'t reference a known layer (if strict layer specifications are enabled).
""".format(_EXIT_EXEC, _EXIT_LAYER_SPEC)

_LAYER_GROUP_DESCRIPTION = """
Layers are specified as (partial) Docker image IDs.
Layers may also be specified as ranges in the form "i:j" (where "i" and "j" are indexes or image IDs).
The range "j:i" is equivalent to the reverse of the range "i:j".
Ranges are inclusive, meaning "i:i" is equivalent to "i".
If no layers are specified, all layers are inferred, starting with the root (i.e., primogenitor), and ending with IMAGE_SPEC.
Layers are extracted in order, which means that files from layers specified later in the command line will overwrite (or block) those from earlier specifications where there is a conflict.
Ordering is resolved before retrieval so that each distinct layer is only extracted once.
"""

_TARGET_GROUP_DESCRIPTION = """
If no target is provided, information about the specified layers is written to STDOUT, one line per layer.
If a target is provided, the specified layers will be extracted and written to the target as a tar archive.
"""

# ---- Decorators --------------------------------------------------------

# ========================================================================
def exitonraise(f):
    @wraps(f)
    def _wrapper(*_args, **_kw):
        try:
            return f(*_args, **_kw)
        except:  # pylint: disable=bare-except
            sys_exit(_EXIT_EXEC)

    return _wrapper

# ---- Functions ---------------------------------------------------------

# ========================================================================
def buildparser(cls=ArgumentParser):
    parser = cls(description=_DESCRIPTION, epilog=_EPILOG, usage=_USAGE)
    parser.add_argument('-V', '--version', action='version', version='%(prog)s {}'.format(__release__))
    parser.add_argument('image', help='the name or ID of the Docker image', metavar='IMAGE_SPEC')

    layer_group = parser.add_argument_group(description=_LAYER_GROUP_DESCRIPTION)
    layer_group.add_argument('-l', '--layers', action='append', help='the selected layer(s) (defaults to all layers in ascending order)', metavar='LAYER_SPEC', type=layertype)
    layer_group.add_argument('-r', '--reverse', action='store_true', dest='reverse', help='reverse the layer order from that specified')
    layer_group.add_argument('-R', '--no-reverse', action='store_false', dest='reverse', help='preserve the layer order as specified (default)')
    layer_group.add_argument('-s', '--strict', action='store_true', dest='strict', help='treat any layer specification that doesn\'t reference at least one known layer as an error')
    layer_group.add_argument('-S', '--no-strict', action='store_false', dest='strict', help='ignore any layer specification that doesn\'t reference a known layer (default))')

    target_group = parser.add_argument_group(description=_TARGET_GROUP_DESCRIPTION)
    target_group.add_argument('-t', '--target', action='store', help='the path to which to write the archive ("{}" for STDOUT)'.format(_TARGET_STDOUT.replace('%', '%%')), metavar='PATH')
    target_group.add_argument('-q', '--quiet', action='store_true', dest='quiet', help='when no target is specified, print only the image IDs')
    target_group.add_argument('-Q', '--no-quiet', action='store_false', dest='quiet', help='when no target is specified, print the image IDs with additional information in a table (default)')
    target_group.add_argument('-w', '--force', action='store_true', dest='force', help='overwrite the target archive if it already exists')
    target_group.add_argument('-W', '--no-force', action='store_false', dest='force', help='don\'t overwrite the target archive if it already exists (default)')

    compress_group = parser.add_argument_group()
    compress_group.add_argument('-j', '--bzip2', action='store_const', const=_CMP_BZIP2, dest='compression', help='compress the target archive with bzip2 compression')
    compress_group.add_argument('-z', '--gzip', action='store_const', const=_CMP_GZIP, dest='compression', help='compress the target archive with gzip compression')
    compress_group.add_argument('-C', '--no-compress', action='store_const', const=_CMP_NONE, default=_CMP_NONE, dest='compression', help='do not compress the target archive (default)')
    compress_group.add_argument('--compress-level', choices=list(range(10)), default=_DEFAULT_CMP_LVL, help='the desired compression level for the archive (defaults to {})'.format(_DEFAULT_CMP_LVL), metavar='0..9', type=int)

    log_group = parser.add_argument_group()
    log_group.add_argument('--log-level', choices=list(_LOG_LEVELS_BY_NAME), default=_DEFAULT_LOG_LVL, help='the desired logging level (defaults to "{}")'.format(_DEFAULT_LOG_LVL.replace('%', '%%')))
    log_group.add_argument('--log-format', default=_DEFAULT_LOG_FMT, help='a logging format compatible with Python\'s "logging" module (defaults to "{}")'.format(_DEFAULT_LOG_FMT.replace('%', '%%')), metavar='FORMAT_SPEC')

    return parser

# ========================================================================
def extractlayers(dc, args, layers, top_most_layer_id):
    target_path = args.target
    flags = O_WRONLY

    if target_path == _TARGET_STDOUT:
        target_fd = stdout.fileno()
    else:
        flags |= O_CREAT | O_TRUNC

        if not args.force:
            flags |= O_EXCL

        target_fd = logexception(_LOGGER, ERROR, 'unable to open target file "{}": {{e}}'.format(target_path), os_open, target_path, flags, 0o666)

    with fdopen(target_fd, 'wb') as target_file:
        if hasattr(target_file, 'seekable'):
            seekable = target_file.seekable()
        else:
            try:
                seekable = not lseek(target_fd, 0, SEEK_CUR) < 0 \
                    and S_ISREG(fstat(target_fd).st_mode)
            except OSError as e:
                if errorcode.get(e.errno) != 'ESPIPE':
                    raise

                seekable = False

        open_args = { 'fileobj': target_file }

        if args.compression is None:
            open_args['mode'] = 'w' if seekable else 'w|'
        else:
            if seekable:
                mode = 'w:{}'
                open_args['compresslevel'] = args.compress_level
                _, ext = ospath_splitext(target_path)

                if ext.lower() != '{}{}'.format(ospath_extsep, args.compression):
                    _LOGGER.warning('target name "%s" doesn\'t match compression type ("%s")', target_path, args.compression)
            else:
                mode = 'w|{}'
                _LOGGER.warning('target "%s" is not seekable, ignoring compression level (%d)', target_path, args.compress_level)

            open_args['mode'] = mode.format(args.compression)

        with tarfile_open(**open_args) as tar_file:
            dimgx_extractlayers(dc, layers, tar_file, top_most_layer_id)

# ========================================================================
def layerspec2index(args, layers, layer_spec_part):
    if layer_spec_part is None:
        return None

    try:
        return layers[layer_spec_part]
    except KeyError:
        pass

    no_layer_msg = '"%s" does not resolve to any layer associated with image "%s"'

    if args.strict:
        _LOGGER.error(no_layer_msg, layer_spec_part, args.image)
        sys_exit(_EXIT_LAYER_SPEC)

    _LOGGER.warning(no_layer_msg, layer_spec_part, args.image)

    return None

# ========================================================================
def layertype(value):
    matches = _LAYER_SPEC_RE.search(value)

    if not matches:
        raise ArgumentTypeError('"{}" is not a valid LAYER_SPEC'.format(value))

    return ( matches.group('l'), matches.group('r'), value )

# ========================================================================
def main():
    import _dimgx
    _dimgx._logexception = exitonraise(_dimgx._logexception)  # WARNING: monkey patch; pylint: disable=protected-access
    args = buildparser().parse_args(sys_argv[1:])
    logging_basicConfig(format=args.log_format)
    getLogger().setLevel(logging_getLevelName(args.log_level))
    patch_broken_tarfile_29760()
    dc_kw = kwargs_from_env()

    # TODO: hack to work around github:docker/docker-py#706
    if DOCKER_TLS_VERIFY == '0':
        dc_kw['tls'].assert_hostname = False

    dc = AutoVersionClient(**dc_kw)
    layers_dict = inspectlayers(dc, args.image)
    top_most_layer_id, selected_layers = selectlayers(args, layers_dict)

    if not selected_layers:
        _LOGGER.warning('no known layers selected')

    if args.target is None:
        printlayerinfo(args, selected_layers)
    else:
        extractlayers(dc, args, selected_layers, top_most_layer_id)

# ========================================================================
def printlayerinfo(args, layers, outfile=stdout):
    if args.quiet:
        for l in layers:
            print(l[':short_id'], file=outfile)

        return

    total_size = 0
    fields_fmt = '\t'.join([ '{:<23}' ] + [ '{:<15}' ] * 5)
    print(fields_fmt.format('REPO TAG', 'IMAGE ID', 'PARENT ID', 'CREATED', 'LAYER SIZE', 'VIRTUAL SIZE'), file=outfile)

    total_size = sum(( l['Size'] for l in layers ))

    for layer in layers:
        try:
            image_tag = layer[':repo_tags'][0]
        except IndexError:
            image_tag = '-'

        image_id = layer[':short_id']
        parent_id = layer[':parent_id'][:12].lower()

        if not parent_id:
            parent_id = '-'

        created = naturaltime(layer[':created_dt'])
        layer_size = naturalsize(layer['Size'])
        virt_size = naturalsize(total_size)
        print(fields_fmt.format(image_tag, image_id, parent_id, created, layer_size, virt_size), file=outfile)
        total_size -= layer['Size']

# ========================================================================
def selectlayers(args, layers):
    layer_specs = args.layers

    if layer_specs is None:
        selected_indexes = list(range(len(layers[':layers'])))

        if args.reverse:
            selected_indexes.reverse()
    else:
        selected_indexes = []
        last_num_selected_indexes = num_selected_indexes = len(selected_indexes)

        for l, r, v in layer_specs:
            last_num_selected_indexes = num_selected_indexes
            li = layerspec2index(args, layers, l)
            ri = layerspec2index(args, layers, r)

            if li is None:
                continue

            if r is None:
                selected_indexes.append(li)
            elif ri is None:
                continue
            elif ri < li:
                selected_indexes.extend(reversed(range(ri, li + 1)))  # upper bounds are inclusive
            else:
                selected_indexes.extend(range(li, ri + 1))  # upper bounds are inclusive

            num_selected_indexes = len(selected_indexes)

            if num_selected_indexes == last_num_selected_indexes:
                empty_layer_range_msg = '"%s" resolves to an empty range'

                if args.strict:
                    _LOGGER.error(empty_layer_range_msg, v)
                    sys_exit(_EXIT_LAYER_SPEC)
                else:
                    _LOGGER.warning(empty_layer_range_msg, v)

        if not args.reverse:
            selected_indexes.reverse()

    # Take the last of each index specified (so we don't have to look at
    # each distinct layer more than once)
    seen = OrderedDict()

    for i in selected_indexes:
        if i not in seen:
            seen[i] = None  # use OrderedDict as an ordered set

    top_most_layer_id = None if not seen else layers[':layers'][min(seen)][':id']
    selected_layers = [ layers[':layers'][i] for i in seen ]

    return top_most_layer_id, selected_layers
