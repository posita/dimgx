.. -*- encoding: utf-8; mode: rst -*-
    >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>><<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<
    >>>>>>>>>>>>>>>> IMPORTANT: READ THIS BEFORE EDITING! <<<<<<<<<<<<<<<<
    >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>><<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<
    Please keep each sentence on its own unwrapped line.
    It looks like crap in a text editor, but it has no effect on rendering, and it allows much more useful diffs.
    Thank you!

Copyright and other protections apply.
Please see the accompanying |LICENSE|_ and |CREDITS|_ file(s) for rights and restrictions governing use of this software.
All rights not expressly waived or licensed are reserved.
If those files are missing or appear to be modified from their originals, then please contact the author before viewing or using this software in any capacity.

.. |LICENSE| replace:: ``LICENSE``
.. _`LICENSE`: LICENSE
.. |CREDITS| replace:: ``CREDITS``
.. _`CREDITS`: CREDITS

.. image:: https://travis-ci.org/posita/dimgx.svg?branch=v0.2.4
    :target: https://travis-ci.org/posita/dimgx?branch=v0.2.4
    :alt: [Build Status]

.. image:: https://coveralls.io/repos/posita/dimgx/badge.svg?branch=v0.2.4
    :target: https://coveralls.io/r/posita/dimgx?branch=v0.2.4
    :alt: [Coverage Status]

Curious about integrating your project with the above services?
Jeff Knupp (|@jeffknupp|_) `describes how <http://www.jeffknupp.com/blog/2013/08/16/open-sourcing-a-python-project-the-right-way/>`__.

.. |@jeffknupp| replace:: **@jeffknupp**
.. _`@jeffknupp`: https://github.com/jeffknupp

``dimgx`` - Docker IMaGe layer eXtractor (and flattener)
========================================================

.. image:: https://img.shields.io/pypi/v/dimgx/0.2.4.svg
    :target: https://pypi.python.org/pypi/dimgx
    :alt: [v0.2.4 Version]

.. image:: https://readthedocs.org/projects/dimgx/badge/?version=v0.2.4
    :target: https://dimgx.readthedocs.org/en/v0.2.4/
    :alt: [v0.2.4 Documentation]

.. image:: https://img.shields.io/pypi/l/dimgx/0.2.4.svg
    :target: http://opensource.org/licenses/MIT
    :alt: [v0.2.4 License]

.. image:: https://img.shields.io/pypi/pyversions/dimgx/0.2.4.svg
    :target: https://pypi.python.org/pypi/dimgx
    :alt: [v0.2.4 Supported Python Versions]

.. image:: https://img.shields.io/pypi/implementation/dimgx/0.2.4.svg
    :target: https://pypi.python.org/pypi/dimgx
    :alt: [v0.2.4 Supported Python Implementations]

.. image:: https://img.shields.io/pypi/status/dimgx/0.2.4.svg
    :target: https://pypi.python.org/pypi/dimgx
    :alt: [v0.2.4 Development Stage]

..

``dimgx`` extracts and flattens `Docker <https://www.docker.com/whatisdocker/>`_ `image <https://docs.docker.com/terms/image/>`__ `layers <https://docs.docker.com/terms/layer/>`__.
It is licensed under the `MIT License <http://opensource.org/licenses/MIT>`_.
Source code is `available on GitHub <https://github.com/posita/dimgx>`__.
See `the docs <https://dimgx.readthedocs.org/en/v0.2.4/>`__ for more information.

Examples
--------

.. code-block:: console

    % dimgx -h
    usage:
    dimgx [options] [-l LAYER_SPEC] ... [-t PATH] IMAGE_SPEC
    dimgx -h # for help

    Docker IMaGe layer eXtractor (and flattener)
    ...

..

.. code-block:: console

    % dimgx nifty-box # show layers for "nifty-box[:latest]"
    REPO TAG                IMAGE ID        PARENT ID       CREATED         LAYER SIZE      VIRTUAL SIZE
    nifty-box               6667bbd4093c    82e5dcafc08c    18 hours ago    18.8 MB         144.0 MB
    -                       82e5dcafc08c    cd5e80677a53    18 hours ago    1.8 kB          125.2 MB
    -                       cd5e80677a53    df2a0347c9d0    18 hours ago    0 Bytes         125.2 MB
    debian:jessie           df2a0347c9d0    39bb80489af7    21 hours ago    0 Bytes         125.2 MB
    -                       39bb80489af7    -               21 hours ago    125.2 MB        125.2 MB

..

.. code-block:: console

    % dimgx -l df2a:82ef nifty-box # show only the second through fourth layers
    IMAGE TAG               IMAGE ID        PARENT ID       CREATED         LAYER SIZE      VIRTUAL SIZE
    -                       82e5dcafc08c    cd5e80677a53    18 hours ago    1.8 kB          125.2 MB
    -                       cd5e80677a53    df2a0347c9d0    18 hours ago    0 Bytes         125.2 MB
    debian:jessie           df2a0347c9d0    39bb80489af7    21 hours ago    0 Bytes         125.2 MB

..

.. code-block:: console

    % dimgx -l cd5e:6667 -t nifty.tar nifty-box # extract the third through fifth layers
    % du -hs nifty.tar
     18M    nifty.tar

Issues
------

``dimgx`` does what I want, so I'm just maintaining it at this point.
If you find a bug, or want a feature, please `file an issue <https://github.com/posita/dimgx/issues>`__ (if it hasn't already been filed).
If you're willing and able, consider `contributing <https://dimgx.readthedocs.org/en/v0.2.4/contrib.html>`__.
