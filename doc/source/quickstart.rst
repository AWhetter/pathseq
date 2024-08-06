**********
Quickstart
**********

First, start by importing pathseq:

.. code-block:: pycon

    >>> import pathseq

* Basic parsing of each pad string
* Looping over paths in a sequence

.. code-block:: pycon

    >>> seq = PathSequence("/path/to/images.1-5####.exr")
    >>> for path in seq:
    ...     print(path)
    ...
    PosixPath("/path/to/images.0001.exr")
    PosixPath("/path/to/images.0002.exr")
    PosixPath("/path/to/images.0003.exr")
    PosixPath("/path/to/images.0004.exr")
    PosixPath("/path/to/images.0005.exr")

* Multi-dimension ranges (eg animated UDIMs)

.. code-block:: pycon

    >>> anim_udims = PathSequence("/path/to/textures.1011-1012<UDIM>_1-3#.tex")
    >>> for path in seq:
    ...     print(path)
    ...
    PosixPath("/path/to/images.1011_0001.exr")
    PosixPath("/path/to/images.1011_0002.exr")
    PosixPath("/path/to/images.1011_0003.exr")
    PosixPath("/path/to/images.1012_0001.exr")
    PosixPath("/path/to/images.1012_0002.exr")
    PosixPath("/path/to/images.1012_0003.exr")

* Conversions
* Basic hashing, and mutability
* Joining and parenting

.. code-block:: pycon

    >>> seq.parent
    PosixPath("/path/to")
    >>> seq3 = seq.parent / PathSequence("images.1-5####.exr")
    >>> seq3 == seq
    True

* Type checking (has_subsamples)

* Composition of a sequence (name, ranges + separators, suffixes)
* Reformatting and setting new ranges
* Complex equality and normalisation

* API reference
* Grammar