.. _adr-004:

[ADR-004] Supporting Single Path Sequences
==========================================

:bdg-success:`Accepted`

Context and Problem Statement
-----------------------------

This proposal is to make the ranges in a sequence optional,
such that a sequence with no ranges (i.e. a single file) is still considered a valid sequence.

Use cases for this include:

#. Retrieving a sequence string from an unknown source,
   and not knowing whether it will be a single file or a sequence.
   For example, a user may have a sequence string stored in a database, and want to
   use pathseq to loop over the files in that sequence. If the sequence string is for
   a single file, they would still want to be able to use pathseq to loop over it.

   Where this type of pattern has been seen before,
   users have typically run the equivalent of ``.with_existing_paths``
   immediately after creating the sequence.

#. Retrieving a sequence string from an unknown source,
   not knowing whether it will be a single file or a sequence,
   and wanting to update the unknown source with updated information
   about which files exist on disk.

Currently, a sequence with only empty ranges is considered to be empty.
A single path sequence would have no ranges, and would be considered as having one file.
These two definitions are somewhat in conflict,
and so introducing single path sequences would erode the concept of a sequence.

PathSeq defines a "stem" slightly differently to pathlib.
In pathlib, the stem of a path is the final path component without its suffix.
In PathSeq, the stem of a path is the final path component without the ranges and any suffixes.
This difference is achievable because the ranges are an additional component
that creates a clear separation between the stem from the suffixes.
In single path sequences, there is no clear separation between the stem and suffixes,
hence why pathlib behaves the way it does.
pathlib puts the burden on users to parse the stem and suffixes themselves,
and PathSeq would ideally do the same,
else risk users reporting unintuitive/inconsistent parsing of suffixes
(e.g. "file.tar.gz" having a stem of "file.tar" and suffixes of ".gz"
instead of a stem of "file" and suffixes of ".tar.gz").

.. note::

   This is already an issue for loose path sequences
   where the ranges exist at the start or end of the sequence string,
   and therefore there is no separation between the stem and suffixes.
   The loose format already warns users that ambiguity exists throughout
   the API of ``LoosePathSequence``,
   so the effect on loose path sequences is not considered significant.

Supporting single path sequences does not significantly complicate the implementation.
Wherever we support sequences of an unknown number of ranges
we already support sequences with no ranges.

A ``PathSequence`` cannot accurately reflect every sequence of paths.
For example, files ``file.1_1.exr``, ``file.1_2.exr``, and ``file.2_2.exr``
would be represented as ``file.1-2#_1-2.exr`` in a ``PathSequence``.


Considered Options
------------------

* Change the return type of ``.with_existing_paths`` from ``PathSequence`` to ``PathSequence | None``.

  * We cannot gurantee that every path in the returned ``PathSequence`` will exist.
    This may create a source of confusion for users,
    and require them to recheck whether the paths in the sequence exist on disk.

  * Users would have to check the type of the return value before using it
    or iterating over it.
    This applies even for those users that are always using a sequence with ranges.

  * Proper use of ``.with_existing_paths`` can be type checked.

  * For users that aren't using type checking,
    improper use of ``.with_existing_paths`` could go unnoticed until
    it is called on a single path sequence for which the file does not exist.

  * The first use case would be written as:

    .. code-block:: python

       def do_something_with_sequence(seq: str):
           paths: Iterable[Path] = PathSequence(seq).with_existing_paths() or ()
           for path in paths:
               if not path.exists():
                   continue

               # do something with the file
               ...

  * The second use case would not be well supported.

  * This method would be demonstrated to users as:

    .. code-block:: pycon

       >>> seq = PathSequence("tests/fixtures/simple/images.1-5####.exr")
       >>> for path in seq:
       ...     path.touch(exist_ok=True)
       ...
       >>> seq2 = PathSequence("tests/fixtures/simple/images.####.exr")
       >>> paths = seq2.with_existing_paths() or ()
       >>> for path in paths:
       ...    path
       ...
       PosixPath('tests/fixtures/simple/images.0001.exr')
       PosixPath('tests/fixtures/simple/images.0002.exr')
       PosixPath('tests/fixtures/simple/images.0003.exr')
       PosixPath('tests/fixtures/simple/images.0004.exr')
       PosixPath('tests/fixtures/simple/images.0005.exr')

* ``.with_existing_paths`` will raise an error if it is called on a single file sequence
  for which the file does not exist.

  * We cannot gurantee that every path in the returned ``PathSequence`` will exist.
    This may create a source of confusion for users,
    and require them to recheck whether the paths in the sequence exist on disk.

  * Proper use of ``.with_existing_paths`` cannot be type checked.

  * For users that aren't using type checking,
    improper use of ``.with_existing_paths`` could go unnoticed until
    it is called on a single path sequence for which the file does not exist.

  * The first use case would be written as:

    .. code-block:: python

       def do_something_with_sequence(seq: str):
           paths: Iterable[Path]
           try:
               paths = PathSequence(seq).with_existing_paths()
           except FileNotFoundError:
               paths = ()

           for path in paths:
               if not path.exists():
                   continue

               # do something with the path
               ...

  * The second use case would not be well supported.

  * This method would be demonstrated to users as:

    .. code-block:: pycon

       >>> seq = PathSequence("tests/fixtures/simple/images.1-5####.exr")
       >>> for path in seq:
       ...     path.touch(exist_ok=True)
       ...
       >>> seq = PathSequence("tests/fixtures/simple/images.####.exr")
       >>> try:
       ...     paths = seq2.with_existing_paths()
       ... except FileNotFoundError:
       ...     paths = ()
       ...
       >>> for path in paths:
       ...    path
       ...
       PosixPath('tests/fixtures/simple/images.0001.exr')
       PosixPath('tests/fixtures/simple/images.0002.exr')
       PosixPath('tests/fixtures/simple/images.0003.exr')
       PosixPath('tests/fixtures/simple/images.0004.exr')
       PosixPath('tests/fixtures/simple/images.0005.exr')

* Change the return type of ``.with_existing_paths`` from ``PathSequence`` to ``tuple[Self, Completeness]``,
  where the ``Completeness`` enum indicates whether the all paths in the sequence exist or not.

  * Users do not need to check the type of the return value before using it
    or iterating over it.
    Unless a user is assuming that they are always using a sequence with ranges,
    they would need to check the completeness value.

  * Proper use of ``.with_existing_paths`` can be type checked.

  * For users that aren't using type checking,
    improper use of ``.with_existing_paths`` could go unnoticed until
    it is called on a single path sequence for which the file does not exist.

  * The return value of this ``.with_`` method would be different from
    the other ``.with_`` methods, which has a high risk of creating confusion.
    The method could be renamed to ``.resize_from_existing_paths``
    to make this distinction clearer.

  * A ``PathSequence`` will never have to represent paths that must exist on disk,
    only sequences of paths that _could_ exist on disk.

  * The first use case would be written as:

    .. code-block:: python

       def do_something_with_sequence(seq: str):
           paths: Iterable[Path]
           paths, complete = PathSequence(seq).with_existing_paths()
           # Skips a path that doesn't exist
           if complete != Completeness.Empty:
               for path in paths:
                   # do something with the path
                   ...

  * The second use case would be well supported because
    the returned sequence reflects the ranges that exist on disk
    and information about whether the sequence is complete or not.

    .. code-block:: python

       def do_something_with_sequence(seq: str):
           paths: Iterable[Path]
           paths, complete = PathSequence(seq).with_existing_paths()
           update_db(paths, complete)

  * This method would be demonstrated to users as:

    .. code-block:: pycon

       >>> seq = PathSequence("tests/fixtures/simple/images.1-5####.exr")
       >>> for path in seq:
       ...     path.touch(exist_ok=True)
       ...
       >>> seq2 = PathSequence("tests/fixtures/simple/images.####.exr")
       >>> paths, complete = seq2.with_existing_paths()
       >>> for path in paths:
       ...    path
       ...
       PosixPath('tests/fixtures/simple/images.0001.exr')
       PosixPath('tests/fixtures/simple/images.0002.exr')
       PosixPath('tests/fixtures/simple/images.0003.exr')
       PosixPath('tests/fixtures/simple/images.0004.exr')
       PosixPath('tests/fixtures/simple/images.0005.exr')

* Add an ``.iter_existing_paths`` method that always returns an iterable of paths.

  This method will ignore the file number sequences in the path sequence,
  and iterate over all paths that could be represented by the sequence string and exist on disk.
  Users who wish the file number sequences to be taken into account
  can use the existing ``.__iter__`` method and filter the results by whether they exist on disk.

  * Proper use of ``.iter_existing_paths`` can be type checked.

  * For users that aren't using type checking,
    the returned iterable will be empty if the file does not exist.

  * A ``PathSequence`` will never have to represent paths that must exist on disk,
    only sequences of paths that _could_ exist on disk.

  * The first use case would be written as:

    .. code-block:: python

       def do_something_with_sequence(seq: str):
           files: Iterable[Path] = PathSequence(seq).iter_existing_paths()
           for file in files:
               # do something with the file
               ...

  * The second use case would not be well supported.

  * This would be demonstrated to users as:

    .. code-block:: pycon

       >>> seq = PathSequence("tests/fixtures/simple/images.1-5####.exr")
       >>> for path in seq:
       ...     path.touch(exist_ok=True)
       ...
       >>> seq2 = PathSequence("tests/fixtures/simple/images.####.exr")
       >>> for path in seq2.iter_existing_paths():
       ...    path
       ...
       PosixPath('tests/fixtures/simple/images.0001.exr')
       PosixPath('tests/fixtures/simple/images.0002.exr')
       PosixPath('tests/fixtures/simple/images.0003.exr')
       PosixPath('tests/fixtures/simple/images.0004.exr')
       PosixPath('tests/fixtures/simple/images.0005.exr')

* We will not support single path sequences.
  and instead raise an error if a PathSequence is constructed with a single file sequence.

  * Users will not have to worry about whether ``.with_existing_paths`` can be used safely.
    Checking is done upon creation of the sequence.

  * The methods that construct an instance of ``BasePurePathSequence`` will
    need to raise an error if the sequence string is for a single file.
    Users already need to be aware of a ``ParseError`` being raised in these methods,
    so this is not a significant change to the API.

  * The first use case would be written as:

    .. code-block:: python

       def do_something_with_sequence(seq: str):
           paths: Iterable[Path]
           try:
               paths = PathSequence(seq).with_existing_paths()
           except NotASequenceError:
               paths = [path] if (path := Path(seq)).exists() else []

           for path in paths:
               # do something with the path
               ...

  * The second use case would not be well supported.

  * This would be demonstrated to users as:

    .. code-block:: pycon

       >>> seq = PathSequence("tests/fixtures/simple/images.1-5####.exr")
       >>> for path in seq:
       ...     path.touch(exist_ok=True)
       ...
       >>> seq2 = PathSequence("tests/fixtures/simple/images.####.exr")
       >>> try:
       ...     paths = seq2.with_existing_paths()
       ... except NotASequenceError:
       ...     paths = [path] if (path := Path(str(seq2))).exists() else []
       ...
       >>> for path in paths:
       ...    path
       ...
       PosixPath('tests/fixtures/simple/images.0001.exr')
       PosixPath('tests/fixtures/simple/images.0002.exr')
       PosixPath('tests/fixtures/simple/images.0003.exr')
       PosixPath('tests/fixtures/simple/images.0004.exr')
       PosixPath('tests/fixtures/simple/images.0005.exr')


Decision Outcome
----------------

We will support single path sequences in ``LoosePathSequence``
by adding an ``.iter_existing_paths`` method,
and replacing ``.with_existing_paths`` with a ``.resize_from_existing_paths`` method.
In ``LoosePathSequence``, ambiguity already exists in the API and users are less concerned about
consistency and simplicity.

``PathSequence`` will not support single path sequences.
