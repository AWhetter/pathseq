:mod:`pathseq`
==============

:mod:`pathseq` is a pathlib-first library for working with file sequences.

Install PathSeq using pip:

.. code-block:: bash

    $ pip install pathseq

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


.. toctree::
    :hidden:

    quickstart
    user/index
    api
    format
    contributor
    decisions/index
