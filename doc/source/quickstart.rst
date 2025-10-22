**********
Quickstart
**********

First, start by importing pathseq:

.. code-block:: pycon

    >>> import pathseq

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

PathSeq supports multi-dimension sequences (eg animated UDIMs).

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

    >>> seq = PathSequence("/path/to/image.-3--1####.exr")
    >>> for path in seq:
    ...     path
    ...
    PosixPath('/path/to/image.-003.exr')
    PosixPath('/path/to/image.-002.exr')
    PosixPath('/path/to/image.-001.exr')

.. seealso::

    :doc:`/format`


Equality and Hashing
====================

Path sequences can be compared for equality.

.. code-block:: pycon

    >>> seq_a = PathSequence("/path/to/image.1-5####.exr")
    >>> seq_b = PathSequence("/path/to/image.1-5####.exr")
    >>> seq_a == seq_b
    True
    >>> seq_c = PathSequence("image.1-5####.exr")
    >>> seq_d = PathSequence("frame.1-5####.exr")
    >>> seq_c == seq_d
    False

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

Path sequences are immutable, so can be hashed and used as dictionary keys.

.. code-block:: pycon

    >>> seq = PathSequence("/path/to/image.1-5####.exr")
    >>> d = {seq: True}


Parenting and Joining
=====================

The parent of a path sequence is always a directory,
and is therefore always returned as a :class:`pathlib.Path`.

.. code-block:: pycon

    >>> seq = PathSequence("/path/to/image.1-5####.exr")
    >>> seq.parent
    PosixPath('/path/to')

Like :class:`pathlib.Path`, path sequences can be joined with a ``/``.

.. code-block:: pycon

    >>> seq = PathSequence("/path/to/image.1-5####.exr")
    >>> joined = seq.parent / PathSequence("image.1-5####.exr")
    >>> joined == seq
    True
