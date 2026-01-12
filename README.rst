pathseq
=======

.. image:: https://readthedocs.org/projects/pathseq/badge/?version=latest
    :target: https://pathseq.readthedocs.org
    :alt: Documentation

.. image:: https://github.com/AWhetter/pathseq/actions/workflows/main.yml/badge.svg?branch=main
    :target: https://github.com/AWhetter/pathseq/actions/workflows/main.yml?query=branch%3Amain
    :alt: Github Build Status

.. image:: https://img.shields.io/pypi/v/pathseq.svg
    :target: https://pypi.org/project/pathseq/
    :alt: PyPI Version

.. image:: https://img.shields.io/pypi/pyversions/pathseq.svg
    :target: https://pypi.org/project/pathseq/
    :alt: Supported Python Versions

A pathlib-first library for working with file sequences.

* Multi-dimension ranges (eg animated udims)
* pathlib-first API
* Support for UDIM tokens


Getting Started
---------------

The following section demonstrates how to install ``pathseq`` and some basic usage.
Full documentation is available here: https://pathseq.readthedocs.io/en/latest/


Installation
~~~~~~~~~~~~

``pathseq`` can be installed from PyPI:

.. code-block:: bash

    pip install pathseq


Usage
~~~~~

For more detailed usage, see the documentation:
https://pathseq.readthedocs.io/en/latest/

Now, let's get started:

.. code-block:: pycon

    >>> from pathseq import PathSequence
    >>> seq = PathSequence("tests/fixtures/simple/images.1-5####.exr")
    >>> for path in seq:
    ...     path
    ...
    PosixPath('tests/fixtures/simple/images.0001.exr')
    PosixPath('tests/fixtures/simple/images.0002.exr')
    PosixPath('tests/fixtures/simple/images.0003.exr')
    PosixPath('tests/fixtures/simple/images.0004.exr')
    PosixPath('tests/fixtures/simple/images.0005.exr')

    >>> seq2 = PathSequence("tests/fixtures/simple/images.####.exr").with_existing_paths()
    >>> seq2 == seq
    True

    >>> seq.parent
    PosixPath('tests/fixtures/simple')
    >>> seq3 = seq.parent / PathSequence("images.1-5####.exr")
    >>> seq3 == seq
    True

    >>> anim_udims = PathSequence("/path/to/textures.1011-1012<UDIM>_1-3#.tex")
    >>> for path in anim_udims:
    ...     path
    ...
    PosixPath('/path/to/textures.1011_1.tex')
    PosixPath('/path/to/textures.1011_2.tex')
    PosixPath('/path/to/textures.1011_3.tex')
    PosixPath('/path/to/textures.1012_1.tex')
    PosixPath('/path/to/textures.1012_2.tex')
    PosixPath('/path/to/textures.1012_3.tex')

A wide range of sequence string formats are supported:

.. code-block:: pycon

    >>> from pathseq import LoosePathSequence
    >>> seq = LoosePathSequence("/path/to/images.1-5####.exr")

    >>> seq = LoosePathSequence("/path/to/1-5####_images.exr")
    >>> seq[0]
    PosixPath('/path/to/0001_images.exr')
    >>> seq.suffixes
    ('.exr',)

    >>> LoosePathSequence("/path/to/1-5####_archives.tar.gz").suffixes
    ('.tar', '.gz')

    >>> seq = LoosePathSequence("/path/to/images.exr.1-5####")
    >>> seq[0]
    PosixPath('/path/to/images.exr.0001')
    >>> seq.suffixes
    ('.exr',)

    >>> LoosePathSequence("/path/to/images.1001-1005<UDIM>.exr")[0]
    PosixPath('/path/to/images.1001.exr')

    >>> LoosePathSequence("/path/to/images.1001-1005<UVTILE>.exr")[0]
    PosixPath('/path/to/images.u1_v1.exr')


Contributing
------------

Running the tests
~~~~~~~~~~~~~~~~~

Tests are executed through `tox <https://tox.readthedocs.io/en/latest/>`_.

.. code-block:: bash

    tox


Code Style
~~~~~~~~~~

Code is formatted using `black <https://github.com/python/black>`_.

You can check your formatting using black's check mode:

.. code-block:: bash

    tox -e format

You can also get black to format your changes for you:

.. code-block:: bash

    tox -e format -- src/ tests/


Release Notes
~~~~~~~~~~~~~

Release notes are managed through `towncrier <https://towncrier.readthedocs.io/en/stable/index.html>`_.
When making a pull request you will need to create a news fragment to document your change:

.. code-block:: bash

    tox -e release_notes -- create --help


Versioning
----------

We use `SemVer <https://semver.org/>`_ for versioning.
For the versions available, see the `tags on this repository <https://github.com/AWhetter/pathseq/tags>`_.


License
-------

This project is licensed under the MIT License.
See the `LICENSE.rst <LICENSE.rst>`_ file for details.
