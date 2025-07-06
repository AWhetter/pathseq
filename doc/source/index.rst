:mod:`pathseq`
==============

:mod:`pathseq` is a pathlib-first library for working with file sequences.

.. code-block:: pycon

    >>> from pathseq import PathSequence
    >>> seq = PathSequence("/path/to/images.1-5####.exr")
    >>> for path in seq:
    ...     path
    ...
    PosixPath('/path/to/images.0001.exr')
    PosixPath('/path/to/images.0002.exr')
    PosixPath('/path/to/images.0003.exr')
    PosixPath('/path/to/images.0004.exr')
    PosixPath('/path/to/images.0005.exr')

    >>> seq2 = PathSequence.from_disk("/path/to/images.####.exr")
    >>> seq2 == seq
    True

    >>> seq.parent
    PosixPath('/path/to')
    >>> seq3 = seq.parent / PathSequence("images.1-5####.exr")
    >>> seq3 == seq
    True

    >>> anim_udims = PathSequence("/path/to/textures.1011-1012<UDIM>_1-3#.tex")
    >>> for path in anim_udims:
    ...     path
    ...
    PosixPath('/path/to/images.1011_1.exr')
    PosixPath('/path/to/images.1011_2.exr')
    PosixPath('/path/to/images.1011_3.exr')
    PosixPath('/path/to/images.1012_1.exr')
    PosixPath('/path/to/images.1012_2.exr')
    PosixPath('/path/to/images.1012_3.exr')


Documentation
-------------

.. toctree::
    :hidden:

    quickstart
    user/index
    reference/index
    contributor
    decisions/index

.. TODO
