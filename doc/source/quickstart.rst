**********
Quickstart
**********

First, start by importing pathseq:

.. code-block:: pycon

    >>> import pathseq
    >>> from pathseq import PathSequence

Iteration
=========

The file paths in a path sequence are looped over in order.

.. code-block:: pycon

    >>> seq = PathSequence("/path/to/image.1-5####.exr")
    >>> for path in seq:
    ...     path
    ...
    PosixPath('/path/to/image.0001.exr')
    PosixPath('/path/to/image.0002.exr')
    PosixPath('/path/to/image.0003.exr')
    PosixPath('/path/to/image.0004.exr')
    PosixPath('/path/to/image.0005.exr')

PathSeq supports multi-dimension sequences (e.g. animated UDIMs).
The file paths are looped over in order like nested for-loops.

.. code-block:: pycon

    >>> anim_udims = PathSequence("/path/to/texture.1011-1012<UDIM>_1-3#.tex")
    >>> for path in anim_udims:
    ...     path
    ...
    PosixPath('/path/to/texture.1011_1.tex')
    PosixPath('/path/to/texture.1011_2.tex')
    PosixPath('/path/to/texture.1011_3.tex')
    PosixPath('/path/to/texture.1012_1.tex')
    PosixPath('/path/to/texture.1012_2.tex')
    PosixPath('/path/to/texture.1012_3.tex')

Subframes are also supported using fixed-precision decimals.

.. code-block:: pycon

    >>> seq = PathSequence("/path/to/image.1.1-1.5x0.1####.exr")
    >>> for path in seq:
    ...     path
    ...
    PosixPath('/path/to/image.0001.1.exr')
    PosixPath('/path/to/image.0001.2.exr')
    PosixPath('/path/to/image.0001.3.exr')
    PosixPath('/path/to/image.0001.4.exr')
    PosixPath('/path/to/image.0001.5.exr')


Range Strings
=============

PathSeq supports common range syntaxes, such as steps:

.. code-block:: pycon

    >>> seq = PathSequence("/path/to/image.1-5x2####.exr")
    >>> for path in seq:
    ...     path
    ...
    PosixPath('/path/to/image.0001.exr')
    PosixPath('/path/to/image.0003.exr')
    PosixPath('/path/to/image.0005.exr')

commas:

.. code-block:: pycon

    >>> seq = PathSequence("/path/to/image.1,5,10####.exr")
    >>> for path in seq:
    ...     path
    ...
    PosixPath('/path/to/image.0001.exr')
    PosixPath('/path/to/image.0005.exr')
    PosixPath('/path/to/image.0010.exr')

and negative numbers:

.. code-block:: pycon

    >>> seq = PathSequence("/path/to/image.-1-1####.exr")
    >>> for path in seq:
    ...     path
    ...
    PosixPath('/path/to/image.-001.exr')
    PosixPath('/path/to/image.0000.exr')
    PosixPath('/path/to/image.0001.exr')
    >>> # Note that the negative sign is included in the padding width.
    >>> seq = PathSequence("/path/to/image.-3--1####.exr")
    >>> for path in seq:
    ...     path
    ...
    PosixPath('/path/to/image.-003.exr')
    PosixPath('/path/to/image.-002.exr')
    PosixPath('/path/to/image.-001.exr')

.. seealso::

    :doc:`/format`


Reading From the Filesystem
===========================

Path sequences can establish their ranges from what's on the filesystem:

.. code-block:: pycon

    >>> seq = PathSequence("tests/fixtures/simple/images.1-5####.exr")
    >>> for path in seq:
    ...     path.touch(exist_ok=True)
    ...
    >>> seq2 = PathSequence("tests/fixtures/simple/images.####.exr")
    >>> seq2.with_existing_paths()
    PathSequence('tests/fixtures/simple/images.1-5####.exr')


Equality and Hashing
====================

Path sequences can be compared for equality.

.. code-block:: pycon

    >>> seq_a = PathSequence("/path/to/image.1-5####.exr")
    >>> seq_b = PathSequence("/path/to/image.1-5####.exr")
    >>> seq_a == seq_b
    True

Path sequences are an ordered sequence of file paths.
So two sequences with different strings that represent the same sequence of file paths,
in the same order, are treated as equal.

.. code-block:: pycon

    >>> seq_a = PathSequence("/path/to/image.1-3####.exr")
    >>> seq_b = PathSequence("/path/to/image.1,2,3####.exr")
    >>> seq_a == seq_b
    True

Convert to a string to check for string equality

.. code-block:: pycon

    >>> seq_a = PathSequence("/path/to/image.1-3####.exr")
    >>> seq_b = PathSequence("/path/to/image.1,2,3####.exr")
    >>> str(seq_a) == str(seq_b)
    False

Path sequences are immutable, so can be hashed and used as dictionary keys or in a set.

.. code-block:: pycon

    >>> seq = PathSequence("/path/to/image.1-5####.exr")
    >>> d = {seq: True}
    >>> s = {seq}


Parenting, Joining, and Splitting
=================================

The parent of a path sequence is always a directory,
and is therefore always returned as a :class:`pathlib.Path`.

.. code-block:: pycon

    >>> seq = PathSequence("/path/to/image.1-5####.exr")
    >>> seq.parent
    PosixPath('/path/to')
    >>> seq = PathSequence("image.1-5####.exr")
    >>> seq.parent
    PosixPath('.')

Like :class:`pathlib.Path`, path sequences can be joined with a ``/``.

.. code-block:: pycon

    >>> seq = PathSequence("/path/to/image.1-5####.exr")
    >>> seq.parent
    PosixPath('/path/to')
    >>> seq.parent / PathSequence("image.1-5####.exr")
    PathSequence('/path/to/image.1-5####.exr')


Like :class:`pathlib.Path`, the name of a path sequence can be split into its parts.

.. code-block:: pycon

    >>> seq = PathSequence("/path/to/image.1-5####.exr")
    >>> seq.name
    'image.1-5####.exr'
    >>> seq.stem
    'image'
    >>> seq.file_num_seqs
    (FileNumSequence(1-5),)
    >>> seq.suffix
    '.exr'
    >>> seq.suffixes
    ('.exr',)

.. seealso::

    :doc:`/format`
    :doc:`/user/convert`
