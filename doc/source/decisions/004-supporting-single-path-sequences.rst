.. _adr-004:

[ADR-004] Supporting Single Path Sequences
==========================================

:bdg-danger:`Rejected`

Context and Problem Statement
-----------------------------

This proposal is to make the ranges in a sequence optional,
such that a sequence with no ranges (i.e. a single file) is still considered a valid sequence.

Use cases for this include:

* Retrieving a sequence string from an unknown source,
  and not knowing whether it will be a single file or a sequence.
  For example, a user may have a sequence string stored in a database, and want to
  use pathseq to loop over the files in that sequence. If the sequence string is for
  a single file, they would still want to be able to use pathseq to loop over it.

  Where this type of pattern has been seen before,
  users have typically run the equivalent of ``.with_existing_files``
  immediately after creating the sequence.

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


Considered Options
------------------

* Change the signature of ``.with_existing_files`` from ``PathSequence`` to ``PathSequence | None``.

  Supporting single path sequences would complicate the API in the following ways:

  * Users would have to check the type of the return value before using it.
    This applies even for those users that are always using a sequence with ranges.
    Essentially, users end up needing to check whether the sequence has any ranges
    or not before using ``.with_existing_files``.
    So users may as well check this upon creation of the sequence,
    and not have to worry about it for the rest of the sequence's lifetime.

  * Proper use of ``.with_existing_files`` can be type checked.

  * For users that aren't using type checking,
    improper use of ``.with_existing_files`` could go unnoticed until
    it is called on a single path sequence for which the file does not exist.

  * The common use case would be written as:

    .. code-block:: python

       def do_something_with_sequence(seq: str):
           files: Iterable[Path] = PathSequence(seq).with_existing_files() or ()
           for file in files:
               # do something with the file
               ...

* ``.with_existing_files`` will raise an error if it is called on a single file sequence,
  for which the file does not exist.

  * Proper use of ``.with_existing_files`` cannot be type checked.

  * For users that aren't using type checking,
    improper use of ``.with_existing_files`` could go unnoticed until
    it is called on a single path sequence for which the file does not exist.

  * The common use case would be written as:

    .. code-block:: python

       def do_something_with_sequence(seq: str):
           files: Iterable[Path]
           try:
               files = PathSequence(seq).with_existing_files()
           except FileNotFoundError:
               files = ()

           for file in files:
               # do something with the file
               ...

* We will not support single path sequences.
  and instead raise an error if a PathSequence is constructed with a single file sequence.

  * Users will not have to worry about whether ``.with_existing_files`` can be used safely.
    Checking is done upon creation of the sequence.

  * The methods that construct an instance of ``BasePurePathSequence`` will
    need to raise an error if the sequence string is for a single file.
    Users already need to be aware of a ``ParseError`` being raised in these methods,
    so this is not a significant change to the API.

  * The common use case would be written as:

    .. code-block:: python

       def do_something_with_sequence(seq: str):
           files: Iterable[Path]
           try:
               files = PathSequence(seq).with_existing_files()
           except NotASequenceError:
               files = [path] if (path := Path(seq)).exists() else []

           for file in files:
               # do something with the file
               ...


Decision Outcome
----------------

We will not support single path sequences.
A single file and a path sequence occasionally needs to be treated in differently,
and it's best for users to be aware of this distinction when they create the sequence.
