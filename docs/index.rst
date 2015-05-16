.. -*-mode: rst; encoding: utf-8-*-
   >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>><<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<
   >>>>>>>>>>>>>>>> IMPORTANT: READ THIS BEFORE EDITING! <<<<<<<<<<<<<<<<
   >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>><<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<
   Please keep each sentence on its own unwrapped line.
   It looks like crap in a text editor, but it has no effect on rendering, and it allows much more useful diffs.
   Thank you!

.. toctree::
   :maxdepth: 3
   :hidden:

   dimgx

``dimgx`` - Extract and Flatten Docker Image Layers
===================================================

``dimgx`` (pronounced *DIH-muhj-EHKS* [#pronunciation]_) is a pure Python module and command line tool for extracting `Docker <https://www.docker.com/whatisdocker/>`_ `image <https://docs.docker.com/terms/image/>`__ `layers <https://docs.docker.com/terms/layer/>`__ and flattening them into a single tar archive.

.. [#pronunciation] World Book Online (WBO) style `pronunciation respelling <https://en.wikipedia.org/wiki/Pronunciation_respelling_for_English>`__.

This can be useful for debugging a |Dockerfile|_ or extracting a supplemental root file system for extending a base image:

.. code-block:: sh

   % cat Dockerfile
   FROM debian:jessie
   ADD mychanges.tar.xz # extracted with dimgx

.. |Dockerfile| replace:: ``Dockerfile``
.. _`Dockerfile`: https://docs.docker.com/reference/builder/

License
-------

Copyright |(c)| 2014-2015 `Matt Bogosian`_ (|@posita|_).

.. |(c)| unicode:: u+a9
.. _`Matt Bogosian`: mailto:mtb19@columbia.edu?Subject=dimgx
.. |@posita| replace:: **@posita**
.. _`@posita`: https://github.com/posita

This software is licensed under the `MIT License <http://opensource.org/licenses/MIT>`_.
Source code is `available on GitHub <https://github.com/posita/py-dimgx>`__.
Please see the accompanying |LICENSE|_ (or |LICENSE.txt|_) file for rights and restrictions governing use of this software.
All rights not expressly waived or licensed are reserved.
If such a file did not accompany this software, then please contact the author before viewing or using this software in any capacity.

.. |LICENSE| replace:: ``LICENSE``
.. _`LICENSE`: _sources/LICENSE.txt
.. |LICENSE.txt| replace:: ``LICENSE.txt``
.. _`LICENSE.txt`: _sources/LICENSE.txt

Requirements
------------

``dimgx`` has the following dependencies:

* one of:

  * `cPython <https://www.python.org/>`_ (2.7 or 3.3+)

  * `PyPy <http://pypy.org/>`_ (Python 2.7 or 3.3+ compatible)

* |docker-py|_

* |future|_

* |humanize|_

* |python-dateutil|_

.. |docker-py| replace:: ``docker-py``
.. _`docker-py`: https://docker-py.readthedocs.org/

.. |future| replace:: ``future``
.. _`future`: http://python-future.org/

.. |humanize| replace:: ``humanize``
.. _`humanize`: https://github.com/jmoiron/humanize

.. |python-dateutil| replace:: ``python-dateutil``
.. _`python-dateutil`: https://dateutil.readthedocs.org/en/latest/

Examples
--------

.. code-block:: sh

   % dimgx
   usage:
   dimgx [options] [-l LAYER_SPEC] ... [-t PATH] IMAGE_SPEC
   dimgx -h # for help
   dimgx: error: too few arguments

Extract and flatten the first three layers of the image named ``nifty-box`` into an archive called ``nifty.tar``:

.. code-block:: sh

   % dimgx -l 0:2 -r -t nifty.tar nifty-box

Extract and flatten the most recent three layers of the image named ``nifty-box`` into an archive with bzip2 compression written to ``STDOUT`` (note that there is no space after the ``-l`` option when a range begins with a negative index; this is to work around a `limitation <https://docs.python.org/2/library/argparse.html#arguments-containing>`__ of Python's :py:mod:`argparse` module):

.. code-block:: sh

   % dimgx -l-3:-1 -r -t - --bzip2 nifty-box >nifty.tar.bz2

LZMA2 compression is not supported natively, but output can be piped to an external utility:

.. code-block:: sh

   % dimgx -t - nifty-box | xz -9c >nifty.tar.xz

Omit the target (the ``-t`` option) to display the layer extraction order (and some other information) without performing any retrieval or extraction:

.. code-block:: sh

   % dimgx -l 1:2 -l 6:5 -l 3 nifty-box
   IMAGE ID        PARENT ID       CREATED         LAYER SIZE      VIRTUAL SIZE
   41b730702607    3cb35ae859e7    12 days ago     0 Bytes         0 Bytes
   60aa72e3db11    41b730702607    2 days ago      0 Bytes         0 Bytes
   0bb92bb75744    51a39b466ad7    34 minutes ago  1.7 kB          1.7 kB
   51a39b466ad7    fec4e64b2b57    2 days ago      0 Bytes         1.7 kB
   390ac3ff1e87    60aa72e3db11    2 days ago      1.7 kB          3.4 kB

Image IDs can be used in lieu of or mixed with indexes:

.. code-block:: sh

   % dimgx -l 41b730702607:2 -l 6:51a39b466ad7 -l 390ac3ff1e87 nifty-box
   IMAGE ID        PARENT ID       CREATED         LAYER SIZE      VIRTUAL SIZE
   41b730702607    3cb35ae859e7    12 days ago     0 Bytes         0 Bytes
   60aa72e3db11    41b730702607    2 days ago      0 Bytes         0 Bytes
   0bb92bb75744    51a39b466ad7    34 minutes ago  1.7 kB          1.7 kB
   51a39b466ad7    fec4e64b2b57    2 days ago      0 Bytes         1.7 kB
   390ac3ff1e87    60aa72e3db11    2 days ago      1.7 kB          3.4 kB

Limitations
-----------

* Files deleted from one layer to another are `handled specially <http://aufs.sourceforge.net/aufs.html#Incompatible%20with%20an%20Ordinary%20Filesystem>`__ in ``aufs`` (the copy-on-write file system used by Docker).
  This is represented in exported archives by creating a zero-length, read-only file called ``.wh.[NAME]``.
  For example when exporting a layer where one removed ``/tmp/foo``, the corresponding archive would contain the file ``tmp/.wh.foo``:

  .. code-block:: sh

     % tar tpvf .../layer.tar tmp/foo
     tar: tmp/foo: Not found in archive
     tar: Error exit delayed from previous errors.
     % tar tpvf .../layer.tar tmp/.wh.foo
     -r--r--r--  0 0      0           0 May 11 15:59 tmp/.wh.foo

  It is assumed that there are no legitimate files on the layered file system with names that start with "``.wh.``" (what ``aufs`` refers to as a "whiteout marker" or simply a "whiteout").
  Where entire subtrees are deleted, only one ``.wh.[NAME]`` entry is created for the top-most directory.
  Renaming or moving a file or directory is treated as a copy-and-delete.

  ``dimgx`` tries to take this into account and do the right thing.
  It does not export files it thinks are whiteout markers.
  However, unpredictable results can occur when specifying layers out of their original order.
  Consider the case where the first layer contains a new file ``/tmp/foo``, the second case renames that file to ``/tmp/bar``, and the third layer creates a directory ``/tmp/foo``.
  If the extraction order is reversed, the flattened archive will contain two identical files ``/tmp/foo`` and ``/tmp/bar``.
  This is because the second layer's deletion of ``/tmp/foo`` (recall that a rename or move is treated as a copy-and-delete) is applied to the third layer's directory, not the first layer's file.

  Avoid extracting layers except in the order in which they were created if any of them has any deletes, renames, or moves.
  `Ye have been warned. <https://d28mt5n9lkji5m.cloudfront.net/i/VmWDmZlxqR.jpg>`__
  If you decide to do it anyway, and are confused about the results ``--log-level DEBUG`` should help you figure out why things are what they are.

* Currently, all ancestor layers are retrieved for the most recent specified layer, even if some of those layers will not affect the target archive.
  In other words, for retrieval purposes, ``-l 0:5`` will fetch just as much data as ``-l 5:5``.
  This inefficiency is a limitation of |docker.Client.get_image|_.
  As of this writing, |docker-py|_ does not provide a mechanism to retrieve individual layers without also retrieving their ancestors.
  This can be frustrating when all you want is a very small layer with a very large parent.

.. |docker.Client.get_image| replace:: ``docker.Client.get_image()``
.. _`docker.Client.get_image`: https://docker-py.readthedocs.org/en/latest/api/#get_image

* No thought has been given to i18n.

It is unlikely that I will tackle (m)any of these warts, but `PRs are welcome <#submissions>`__.

Submissions
-----------

``dimgx`` does what I want, so I'm just maintaining it at this point.
If you find a bug, or want a feature, please `file an issue <https://github.com/posita/py-dimgx/issues>`__ (if it hasn't already been filed).
If you're willing and able, consider submitting a pull request (PR) with a fix.
There are only a few guidelines:

* Try to follow the source conventions as you observe them.
  (Note: I have purposely avoided aspects of `PEP8 <https://www.python.org/dev/peps/pep-0008/>`_, in part because I have adopted conventions developed from my experiences with other languages, but mostly because I'm growing older and more stubborn.)

..

* Provide unit tests where feasible and appropriate.

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

Motivation
----------

I was messing around with Docker and wanted to extract my changes from several distinct image layers without having to get the root image layer.
I found that doing so was possible (but cumbersome) using the ``docker`` command and other utilities. [#cumbersome]_
I wanted to learn more about `Docker's Python API <https://github.com/docker/docker-py>`__ and needed a small project to familiarize myself with some other stuff, so this seemed like a perfect opportunity.

.. [#cumbersome] There very well might be efficient ways to do this without something like ``dimgx``, but, being a relative newcomer to Docker, I am ignorant of them.

.. only:: html

Similar Tools
-------------

Check out Jason Wilder's |docker-squash|_, which probably has more features and is likely more mature.
For example, ``dimgx`` does not provide any reimport functionality.
However, ``dimgx`` does not require running as ``root`` to preserve permissions, nor does it rely on external tools like the ``tar`` command.

.. |docker-squash| replace:: ``docker-squash``
.. _`docker-squash`: http://jasonwilder.com/blog/2014/08/19/squashing-docker-images/

Indexes
-------

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
