#!/usr/bin/env sh
#-*- encoding: utf-8; mode: sh; grammar-ext: sh -*-

#=========================================================================
# Copyright and other protections apply. Please see the accompanying
# ``LICENSE`` and ``CREDITS`` files for rights and restrictions governing
# use of this software. All rights not expressly waived or licensed are
# reserved. If those files are missing or appear to be modified from their
# originals, then please contact the author before viewing or using this
# software in any capacity.
#=========================================================================

if [ "${#}" -ne 3 ] ; then
    echo 1>&2 "usage: $( basename "${0}" ) MAJOR MINOR PATCH"

    exit 1
fi

_MY_DIR="$( cd "$( dirname "${0}" )" && pwd )"
_PKG='dimgx'
MAJOR="${1}"
MINOR="${2}"
PATCH="${3}"
VERS="${MAJOR}.${MINOR}.${PATCH}"
TAG="v${VERS}"

set -ex
cd "${_MY_DIR}"
git checkout -b "${VERS}-release"
perl -pi -e 's{^__version__\s*=\s*\(\s*0,\s*0,\s*0\s*\)$}{__version__ = ( '"${MAJOR}"', '"${MINOR}"', '"${PATCH}"' )}g ;' "_${_PKG}/version.py"
perl -pi -e 's{master}{'"${TAG}"'}g ; s{pypi/([^/]+/)'"${_PKG}"'(\.svg)?$}{pypi/\1'"${_PKG}"'/'"${VERS}"'\2}g' README.rst
git commit --all --message "Update version and release ${TAG}."
git tag --sign --force --message "Release ${TAG}." "${TAG}"
