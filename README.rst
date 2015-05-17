.. -*-mode: rst; encoding: utf-8-*-
   >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>><<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<
   >>>>>>>>>>>>>>>> IMPORTANT: READ THIS BEFORE EDITING! <<<<<<<<<<<<<<<<
   >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>><<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<
   Please keep each sentence on its own unwrapped line.
   It looks like crap in a text editor, but it has no effect on rendering, and it allows much more useful diffs.
   Thank you!

.. contents::

Status
======

.. image:: https://pypip.in/version/dimgx/badge.svg
   :target: https://pypi.python.org/pypi/dimgx/
   :alt: Latest Version

.. image:: https://pypip.in/status/dimgx/badge.svg
   :target: https://pypi.python.org/pypi/dimgx/0.1.4
   :alt: Development Status

.. image:: https://pypip.in/license/dimgx/badge.svg
   :target: https://pypi.python.org/pypi/dimgx/0.1.4
   :alt: License

.. image:: https://pypip.in/py_versions/dimgx/badge.svg
   :target: https://pypi.python.org/pypi/dimgx/0.1.4
   :alt: Supported Python versions

.. image:: https://pypip.in/implementation/dimgx/badge.svg
   :target: https://pypi.python.org/pypi/dimgx/0.1.4
   :alt: Supported Python implementations

.. image:: https://travis-ci.org/posita/py-dimgx.svg?branch=v0.1.4
   :target: https://travis-ci.org/posita/py-dimgx?branch=v0.1.4
   :alt: Build Status

.. image:: https://coveralls.io/repos/posita/py-dimgx/badge.svg?branch=v0.1.4
   :target: https://coveralls.io/r/posita/py-dimgx?branch=v0.1.4
   :alt: Coverage Status

.. image:: https://readthedocs.org/projects/dimgx/badge/?version=v0.1.4
   :target: https://dimgx.readthedocs.org/en/v0.1.4/
   :alt: Documentation Status

Curious about integrating your project with the above services?
Jeff Knupp (|@jeffknupp|_) `describes how <http://www.jeffknupp.com/blog/2013/08/16/open-sourcing-a-python-project-the-right-way/>`__.

.. |@jeffknupp| replace:: **@jeffknupp**
.. _`@jeffknupp`: https://github.com/jeffknupp

Notice
======

Copyright |(c)| 2014-2015 `Matt Bogosian`_ (|@posita|_).

.. |(c)| unicode:: u+a9
.. _`Matt Bogosian`: mailto:mtb19@columbia.edu?Subject=dimgx
.. |@posita| replace:: **@posita**
.. _`@posita`: https://github.com/posita

Please see the ``LICENSE`` (or ``LICENSE.txt``) file which accompanied this software for rights and restrictions governing its use.
All rights not expressly waived or licensed are reserved.
If such a file did not accompany this software, then please contact the author before viewing or using this software in any capacity.

**TL;DR**
=========

``dimgx`` extracts and flattens `Docker <https://www.docker.com/whatisdocker/>`_ `image <https://docs.docker.com/terms/image/>`__ `layers <https://docs.docker.com/terms/layer/>`__:

.. code-block:: sh

   % dimgx
   usage:
   dimgx [options] [-l LAYER_SPEC] ... [-t PATH] IMAGE_SPEC
   dimgx -h # for help
   dimgx: error: too few arguments

.. code-block:: sh

   % dimgx nifty-box # show layers for "nifty-box[:latest]"
   IMAGE ID        PARENT ID       CREATED         LAYER SIZE      VIRTUAL SIZE
   3cb35ae859e7    -               16 days ago     125.1 MB        125.1 MB
   41b730702607    3cb35ae859e7    16 days ago     0 Bytes         125.1 MB
   60aa72e3db11    41b730702607    7 days ago      0 Bytes         125.1 MB
   390ac3ff1e87    60aa72e3db11    6 days ago      1.7 kB          125.1 MB
   fec4e64b2b57    390ac3ff1e87    6 days ago      9.4 MB          134.5 MB
   51a39b466ad7    fec4e64b2b57    6 days ago      0 Bytes         134.5 MB
   0bb92bb75744    51a39b466ad7    4 days ago      1.7 kB          134.5 MB

.. code-block:: sh

   % dimgx -l 2:4 nifty-box # show only the second through fourth layers
   IMAGE ID        PARENT ID       CREATED         LAYER SIZE      VIRTUAL SIZE
   60aa72e3db11    41b730702607    7 days ago      0 Bytes         0 Bytes
   390ac3ff1e87    60aa72e3db11    6 days ago      1.7 kB          1.7 kB
   fec4e64b2b57    390ac3ff1e87    6 days ago      9.4 MB          9.4 MB

.. code-block:: sh

   % dimgx -l 2:4 -t nifty.tar nifty-box # extract them
   % du -h nifty.tar
   9.0M    nifty.tar

It is licensed under the `MIT License <http://opensource.org/licenses/MIT>`_.
See `the docs <https://dimgx.readthedocs.org/en/v0.1.4/>`__ for more information.

Submissions
===========

``dimgx`` does what I want, so I'm just maintaining it at this point.
If you find a bug, or want a feature, please `file an issue <https://github.com/posita/py-dimgx/issues>`__ (if it hasn't already been filed).
If you're willing and able, consider submitting a pull request (PR) with a fix.
There are only a few guidelines:

* Try to follow the source conventions as you observe them.
  (Note: I have purposely avoided aspects of `PEP8 <https://www.python.org/dev/peps/pep-0008/>`_, in part because I have adopted conventions developed from my experiences with other languages, but mostly because I'm growing older and more stubborn.)

..

* Provide unit tests where feasible and appropriate.
  Tests can be run with ``./runtests.sh`` (requires `tox <https://tox.readthedocs.org/en/latest/>`__) or ``python setup.py test``.

..

* If you need me, mention me (|@posita|_) in your comment, and describe specifically how I can help.

..

* If you want feedback on a work-in-progress (WIP), create a PR and prefix its title with something like, "``NEED FEEDBACK -``".

..

* If your PR is still in progress, but you aren't blocked on anything, prefix the title with something like, "``WIP -``".

..

* Once you're ready for a merge, resolve any merge conflicts, squash your commits, and provide a useful commit message. [#submissions]_
  Then prefix the PR's title to something like, "``READY FOR MERGE -``".
  I'll try to get to it as soon as I can.

.. [#submissions] `This <https://robots.thoughtbot.com/git-interactive-rebase-squash-amend-rewriting-history>`__ and `this <http://gitready.com/advanced/2009/02/10/squashing-commits-with-rebase.html>`__ may be helpful.
