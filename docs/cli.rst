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

Copyright |(c)| 2014-2015 `Matt Bogosian`_ (|@posita|_).

.. |(c)| unicode:: u+a9
.. _`Matt Bogosian`: mailto:mtb19@columbia.edu?Subject=dimgx
.. |@posita| replace:: **@posita**
.. _`@posita`: https://github.com/posita

Please see the accompanying |LICENSE|_ (or |LICENSE.txt|_) file for rights and restrictions governing use of this software.
All rights not expressly waived or licensed are reserved.
If such a file did not accompany this software, then please contact the author before viewing or using this software in any capacity.

.. |LICENSE| replace:: ``LICENSE``
.. _`LICENSE`: _sources/LICENSE.txt
.. |LICENSE.txt| replace:: ``LICENSE.txt``
.. _`LICENSE.txt`: _sources/LICENSE.txt

The ``dimgx`` Command Line Tool
===============================

``dimgx`` can be useful for debugging a |Dockerfile|_ or extracting a supplemental root file system for extending a base image:

.. code-block:: sh

   % cat Dockerfile
   FROM debian:jessie
   ADD mychanges.tar.xz # extracted with dimgx

.. |Dockerfile| replace:: ``Dockerfile``
.. _`Dockerfile`: https://docs.docker.com/reference/builder/

Examples
--------

Help is available via ``-h`` or ``--help``:

.. code-block:: sh

   % dimgx -h
   usage:
   dimgx [options] [-l LAYER_SPEC] ... [-t PATH] IMAGE_SPEC
   dimgx -h # for help

   Docker IMaGe layer eXtractor (and flattener)
   ...

Without the target (the ``-t`` option), ``dimgx`` will display the layer extraction order (and some other information) without performing any retrieval or extraction (in order of greatest to least precidence):

.. code-block:: sh

   % docker images --all
   REPOSITORY          TAG                 IMAGE ID            CREATED             VIRTUAL SIZE
   nifty-box           latest              6667bbd4093c        18 hours ago        144 MB
   <none>              <none>              82e5dcafc08c        18 hours ago        125.2 MB
   <none>              <none>              cd5e80677a53        18 hours ago        125.2 MB
   debian              jessie              df2a0347c9d0        21 hours ago        125.2 MB
   <none>              <none>              39bb80489af7        21 hours ago        125.2 MB
   % dimgx nifty-box
   REPO TAG                IMAGE ID        PARENT ID       CREATED         LAYER SIZE      VIRTUAL SIZE
   nifty-box               6667bbd4093c    82e5dcafc08c    18 hours ago    18.8 MB         144.0 MB
   -                       82e5dcafc08c    cd5e80677a53    18 hours ago    1.8 kB          125.2 MB
   -                       cd5e80677a53    df2a0347c9d0    18 hours ago    0 Bytes         125.2 MB
   debian:jessie           df2a0347c9d0    39bb80489af7    21 hours ago    0 Bytes         125.2 MB
   -                       39bb80489af7    -               21 hours ago    125.2 MB        125.2 MB

Layers can be extracted in any order, and ranges are supported (but see `Limitations`_ below about extracting layers out of order or using the ``-r`` option):

.. code-block:: sh

   % dimgx -l 39bb:df2a -l 6667:82e5 -l cd5e nifty-box
   REPO TAG                IMAGE ID        PARENT ID       CREATED         LAYER SIZE      VIRTUAL SIZE
   -                       cd5e80677a53    df2a0347c9d0    18 hours ago    0 Bytes         144.0 MB
   -                       82e5dcafc08c    cd5e80677a53    18 hours ago    1.8 kB          144.0 MB
   nifty-box               6667bbd4093c    82e5dcafc08c    18 hours ago    18.8 MB         144.0 MB
   debian:jessie           df2a0347c9d0    39bb80489af7    21 hours ago    0 Bytes         125.2 MB
   -                       39bb80489af7    -               21 hours ago    125.2 MB        125.2 MB

Extract and flatten all layers of the image named ``nifty-box`` into a bzip2'ed archive called ``nifty.tar.bz2``:

.. code-block:: sh

   % dimgx --bzip -t nifty.tar.bz2 nifty-box

LZMA2 compression is not supported natively, but output can be piped to an external utility:

.. code-block:: sh

   % dimgx -t - nifty-box | xz -9c >nifty.tar.xz

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
.. |docker-py| replace:: ``docker-py``
.. _`docker-py`: https://docker-py.readthedocs.org/

* No thought has been given to i18n.

It is unlikely that I will tackle (m)any of these warts, but `PRs are welcome <https://github.com/posita/py-dimgx#submissions>`__.
