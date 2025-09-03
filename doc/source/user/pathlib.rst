Compared to :mod:`pathlib`
==========================

* Not a filesystem path. Sequences are an ordered sequence of filesystem paths.
  * No __bytes__ because not a filesystem path.
  * No __fspath__ because not a filesystem path.
  * No as_uri because not a filesystem path.

* Omitted methods on PurePathSequence
* Omitted methods on PathSequence

* Class hierarchy
* PurePathSequences vs PathSequences

Composition of a name
---------------------

The name file of a file in a regular :mod:`pathlib.Path` object has two components:
the stem and suffix.

.. code-block:: text

   /directory/file.tar.gz
              ^---------^
              |name     |
              ^------^^-^----┐
              |stem  ||suffix|

In a path sequence, this remains the same:

.. code-block:: pycon

    >>> seq = pathseq.PathSequence("/directory/file.1001-1010#.tar.gz")
    >>> seq.stem
    'file'
    >>> seq.suffix
    '.gz'
    >>> seq.name
    'file.1001-1010#.tar.gz'

However, the complete parsing of a file sequence requires many components:
the prefix, the padded ranges, the suffixes, and the separators between those components.
