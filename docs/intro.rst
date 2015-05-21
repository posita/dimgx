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

Introduction
============

``dimgx`` (pronounced *DIH-muhj-EHKS* [#pronunciation]_) is a :doc:`command line tool <cli>` and :doc:`pure Python module <py>` for extracting `Docker <https://www.docker.com/whatisdocker/>`_ `image <https://docs.docker.com/terms/image/>`__ `layers <https://docs.docker.com/terms/layer/>`__ and flattening them into a single tar archive.

.. [#pronunciation] World Book Online (WBO) style `pronunciation respelling <https://en.wikipedia.org/wiki/Pronunciation_respelling_for_English>`__.

License
-------

``dimgx`` is licensed under the `MIT License <http://opensource.org/licenses/MIT>`_.
Source code is `available on GitHub <https://github.com/posita/py-dimgx>`__.

Installation
------------

Installation can be performed via ``pip`` (which will download and install the `latest release <https://pypi.python.org/pypi/dimgx/>`__):

.. code-block:: sh

  % pip install dimgx
  ...

Alternately, you can download the sources (e.g., `from GitHub <https://github.com/posita/py-dimgx>`__) and run ``setup.py``:

.. code-block:: sh

  % git clone https://github.com/posita/py-dimgx
  ...
  % cd py-dimgx
  % python setup.py install
  ...

Requirements
------------

A modern version of Python is required:

* `cPython <https://www.python.org/>`_ (2.7 or 3.3+)

* `PyPy <http://pypy.org/>`_ (Python 2.7 or 3.3+ compatible)

Python 2.6 will *not* work.

``dimgx`` has the following dependencies (which will be installed automatically):

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

Motivation
----------

I was messing around with Docker and wanted to extract my changes from several distinct image layers without having to get the root image layer.
I found that doing so was possible (but cumbersome) using the ``docker`` command and other utilities. [#cumbersome]_
I wanted to learn more about `Docker's Python API <https://github.com/docker/docker-py>`__ and needed a small project to familiarize myself with some other stuff, so this seemed like a perfect opportunity.

.. [#cumbersome] There very well might be efficient ways to do this without something like ``dimgx``, but, being a relative newcomer to Docker, I am ignorant of them.

Similar Tools
-------------

Check out Jason Wilder's |docker-squash|_, which probably has more features and fewer bugs.
For example, ``dimgx`` does not provide any reimport functionality.
However, ``dimgx`` does not require running as ``root`` to preserve permissions, nor does it rely on external tools like the ``tar`` command.

.. |docker-squash| replace:: ``docker-squash``
.. _`docker-squash`: http://jasonwilder.com/blog/2014/08/19/squashing-docker-images/
