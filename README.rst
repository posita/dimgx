.. -*-mode: rst; encoding: utf-8-*-
   >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>><<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<
   >>>>>>>>>>>>>>>> IMPORTANT: READ THIS BEFORE EDITING! <<<<<<<<<<<<<<<<
   >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>><<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<
   Please keep each sentence on its own unwrapped line.
   It looks like crap in a text editor, but it has no effect on rendering, and it allows much more useful diffs.
   Thank you!

Copyright |(c)| 2014-2015 `Matt Bogosian`_ (|@posita|_).

.. |(c)| unicode:: u+a9
.. _`Matt Bogosian`: mailto:mtb19@columbia.edu?Subject=dimgx
.. |@posita| replace:: **@posita**
.. _`@posita`: https://github.com/posita

Please see the accompanying |LICENSE|_ (or |LICENSE.txt|_) file for rights and restrictions governing use of this software.
All rights not expressly waived or licensed are reserved.
If such a file did not accompany this software, then please contact the author before viewing or using this software in any capacity.

.. |LICENSE| replace:: ``LICENSE``
.. _`LICENSE`: LICENSE
.. |LICENSE.txt| replace:: ``LICENSE.txt``
.. _`LICENSE.txt`: LICENSE

.. image:: https://travis-ci.org/posita/py-dimgx.svg?branch=v0.2.3
   :target: https://travis-ci.org/posita/py-dimgx?branch=v0.2.3
   :alt: Build Status

.. image:: https://coveralls.io/repos/posita/py-dimgx/badge.svg?branch=v0.2.3
   :target: https://coveralls.io/r/posita/py-dimgx?branch=v0.2.3
   :alt: Coverage Status

Curious about integrating your project with the above services?
Jeff Knupp (|@jeffknupp|_) `describes how <http://www.jeffknupp.com/blog/2013/08/16/open-sourcing-a-python-project-the-right-way/>`__.

.. |@jeffknupp| replace:: **@jeffknupp**
.. _`@jeffknupp`: https://github.com/jeffknupp

``dimgx`` - Docker IMaGe layer eXtractor (and flattener)
========================================================

.. image:: https://pypip.in/version/dimgx/badge.svg
   :target: https://pypi.python.org/pypi/dimgx/
   :alt: Latest Version

.. image:: https://readthedocs.org/projects/dimgx/badge/?version=v0.2.3
   :target: https://dimgx.readthedocs.org/en/v0.2.3/
   :alt: Documentation

.. image:: https://pypip.in/license/dimgx/badge.svg
   :target: http://opensource.org/licenses/MIT
   :alt: License

.. image:: https://pypip.in/py_versions/dimgx/badge.svg
   :target: https://pypi.python.org/pypi/dimgx/0.2.3
   :alt: Supported Python Versions

.. image:: https://pypip.in/implementation/dimgx/badge.svg
   :target: https://pypi.python.org/pypi/dimgx/0.2.3
   :alt: Supported Python Implementations

.. image:: https://pypip.in/status/dimgx/badge.svg
   :target: https://pypi.python.org/pypi/dimgx/0.2.3
   :alt: Development Stage

``dimgx`` extracts and flattens `Docker <https://www.docker.com/whatisdocker/>`_ `image <https://docs.docker.com/terms/image/>`__ `layers <https://docs.docker.com/terms/layer/>`__:
It is licensed under the `MIT License <http://opensource.org/licenses/MIT>`_.
Source code is `available on GitHub <https://github.com/posita/py-dimgx>`__.
See `the docs <https://dimgx.readthedocs.org/en/v0.2.3/>`__ for more information.

Examples
--------

::

  % dimgx -h
  usage:
  dimgx [options] [-l LAYER_SPEC] ... [-t PATH] IMAGE_SPEC
  dimgx -h # for help

  Docker IMaGe layer eXtractor (and flattener)
  ...

..

::

  % dimgx nifty-box # show layers for "nifty-box[:latest]"
  REPO TAG                IMAGE ID        PARENT ID       CREATED         LAYER SIZE      VIRTUAL SIZE
  nifty-box               6667bbd4093c    82e5dcafc08c    18 hours ago    18.8 MB         144.0 MB
  -                       82e5dcafc08c    cd5e80677a53    18 hours ago    1.8 kB          125.2 MB
  -                       cd5e80677a53    df2a0347c9d0    18 hours ago    0 Bytes         125.2 MB
  debian:jessie           df2a0347c9d0    39bb80489af7    21 hours ago    0 Bytes         125.2 MB
  -                       39bb80489af7    -               21 hours ago    125.2 MB        125.2 MB

..

::

  % dimgx -l df2a:82ef nifty-box # show only the second through fourth layers
  IMAGE TAG               IMAGE ID        PARENT ID       CREATED         LAYER SIZE      VIRTUAL SIZE
  -                       82e5dcafc08c    cd5e80677a53    18 hours ago    1.8 kB          125.2 MB
  -                       cd5e80677a53    df2a0347c9d0    18 hours ago    0 Bytes         125.2 MB
  debian:jessie           df2a0347c9d0    39bb80489af7    21 hours ago    0 Bytes         125.2 MB

..

::

  % dimgx -l cd5e:6667 -t nifty.tar nifty-box # extract the third through fifth layers
  % du -hs nifty.tar
   18M    nifty.tar

Issues
------

``dimgx`` does what I want, so I'm just maintaining it at this point.
If you find a bug, or want a feature, please `file an issue <https://github.com/posita/py-dimgx/issues>`__ (if it hasn't already been filed).
If you're willing and able, consider `contributing <https://dimgx.readthedocs.org/en/v0.2.3/contrib.html>`__.
