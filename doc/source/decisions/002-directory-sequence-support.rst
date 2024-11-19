.. _adr-002:

[ADR-002] Directory Sequence Support
====================================

:bdg-success:`Accepted`

Context and Problem Statement
-----------------------------

As seen in the research of :ref:`adr-001`,
few (or indeed any) DCCs explicitly mention support for sequences of directories.

Supporting sequences of directories will complicate the API in the following ways:

* It will not be intuitive as to whether ``.with_paddings``
  will affect all pad strings in the path, or just those for the right most child.
* The return type of ``.parent`` and ``.parents`` will change from
  ``pathlib.Path`` and ``Sequence[pathlib.Path]`` to
  ``pathlib.Path | pathseq.PathSequence`` and ``Sequence[pathlib.Path | pathseq.PathSequence]``
  respectively.
* Methods like ``.is_relative_to`` and ``.relative_to`` will not make sense
  with directory sequences are used.


Considered Options
------------------

* We will support directory sequences
* We will not support directory sequences.


Decision Outcome
----------------

We will not support directory sequences because it would complicate the API significantly,
for what seems like a rare use case.
