**************************
Format of Sequence Strings
**************************

PathSeq's chosen sequence format is a simple, unambiguous format that maximises
compatibility across VFX DCCs (Digital Content Creation software).

.. seealso::

   See :ref:`adr-001` for more information about why this format was chosen.


.. _simple-format:

Path Sequences
==============

Like in :mod:`pathlib`,
the name of a path sequence is the final component in a path.

.. code-block:: text

   /directory/ file.1001-1010#.tar.gz
              ├──────────────────────┤
              │         name         │
              └──────────────────────┘

Unlike a :class:`pathlib.Path`, a path sequence's name
represents the name of not one file but of all the files in the sequence.
The name has four components:

* The stem
* An optional prefix
* The ranges
* The suffixes

.. code-block:: text

   /directory/ file . 1001-1010# .tar.gz
             ┌┴────┼─┼──────────┼───────┴┐
             │    ┌┘ └───┐      │        │
             │stem│prefix│ranges│suffixes│
             ├────┴──────┴──────┴────────┤
             │           name            │
             └───────────────────────────┘

Supporting multiple ranges in a sequence requires an additional component:
an inter-range separator.

.. code-block:: text

   /directory/ file . 1001-1002<UDIM> _ 1001-1010# .tar.gz
         ┌────┴────┼─┼───────────────┼─┼──────────┼───────┴┐
         │    ┌────┘ │          ┌────┘ └────┐     │        │
         │stem│prefix│   range  │inter-range│range│suffixes│
         └────┴──────┼──────────┴───────────┴─────┼────────┘
                     │           ranges           │
                     └────────────────────────────┘


.. _format-simple-stem:

Stem
----

The stem is the name of a path sequence, without the prefix, ranges, and suffixes.
A non-empty stem MUST be present in the name of a path sequence.

The stem MUST NOT contain a valid :ref:`range string <format-simple-range>`,
or by definition it would be considered part of the ranges.

The stem MUST NOT end with a "``-``" or digit,
otherwise there is no clear end to the stem and the start of the ranges.
For example, in ``file-1.1-5#.tar.gz`` it is unclear whether the stem and range are
``file`` and ``-1.1-5#`` respectively, or ``file-1`` and ``1-5#``.

.. note::

   Although this ambiguity is removed when a prefix separator of "``_``" is included,
   ending the stem with a digit is still forbidden
   to prevent complexity in an API that implements this format.
   For example, if it were possible to rename a path sequence by
   removing or changing the prefix, doing that may not be possible unless
   the stem is changed first.


.. _format-simple-prefix:

Prefix
------

The prefix is a single character that separates the :ref:`stem <format-simple-stem>`
from the :ref:`ranges <format-simple-range>`.

The name of a path sequence MAY contain a single prefix character.

The prefix character MUST be one of "``.``" or "``_``".

.. tip::

   Including a prefix as "``.``" is RECOMMENDED for best compatibility with VFX software.

   .. code-block:: text

      file.1001-1010#.exr
      file.1001-1010#.tar.gz


.. _format-simple-range:

Range
-----

The range is a concice representation of the file numbers of each file
in the sequence plus a definition of how those numbers are formatted
in the resulting file names.

A range MUST be present in the name of a path sequence.
A range consists of the ranges specifier, and the padding.

.. code-block:: text

    1001-1010,1020-1030 ####
   ├───────────────────┼────┴──┐
   │      ranges       │padding│
   └───────────────────┴───────┘


.. _format-simple-ranges:

Ranges Specifier
~~~~~~~~~~~~~~~~

The ranges specifier is a concice representation of the file numbers of each file
in the sequence.

The ranges specifier is OPTIONAL.
When no ranges specifier is present, the path sequence is considered empty.

A ranges specifier consists of comma separated range specifiers,
where each range specifier is of the format ``START-ENDxSTEP``.
``START`` is REQUIRED, and ``END`` and ``xSTEP`` are OPTIONAL.

``START`` is the first value in the range,
``END`` is the last value in the range (in other words, ``END`` is inclusive),
and ``STEP`` represents the difference between numbers in the range.
When ``STEP`` is not present, it defaults to 1.

More formally, a range specifier represents a
`finite Arithmetic Progression <https://en.wikipedia.org/wiki/Arithmetic_progression>`_.

So the range specifier "``1-5``" represents the numbers 1, 2, 3, 4, 5.
The range specifier "``1-5x2``" represents the numbers 1, 3, 5.


.. _format-simple-padding:

Padding
~~~~~~~

The padding string is definition of how a file number is formatted
in each file names contained in the sequence.

The padding is a REQUIRED part of the ranges.

A pad string represents how the numbers in the range should be formatted
when putting a number from the range into a file path.

A pad string can be a string of "``#``" characters, or a MaterialX token.


``#`` characters
^^^^^^^^^^^^^^^^

The most basic form of a pad string is a string of "``#``" characters.
The number of "``#``" represents the minimum with of the formatted number.
If the stringified number is smaller than the width,
then it will be zero padded.
If the stringified number is larger than the width,
it will exceed the given width.

A "``-``" sign, to indicate a negative number, is counted in the width.

.. list-table::

   * - Frame range string
     - Formats to
   * - ``1####``
     - ``0001``
   * - ``1001#``
     - ``1001``
   * - ``-1####``
     - ``-001``

.. note::

   Some DCCs support the use of the "@" character as a single digit pad string.
   PathSeq does not support this character because it has conflicting definitions
   between DCCs.
   Users are encouraged to preprocess "@" characters out of sequence strings
   passed to PathSeq if this character may be present as a pad character.


MaterialX tokens
^^^^^^^^^^^^^^^^

Pad strings can also use MaterialX tokens (https://materialx.org/Specification.html).
The "Filename Substitutions" section of the specification
describes two tokens for representing UDIMs in file names.

* ``<UDIM>``: This is equivalent to ``####``.

  Using ``<UDIM>`` can be useful to indicate which ranges in an
  animated texture sequence are the UDIMs
  and which are the frame numbers.
  As an example, ``texture.1001-1010<UDIM>_1001-1010####.tex``
  is clearer than ``texture.1001-1010####_1001-1010####.tex``.

* ``<UVTILE>``: This token represents the string
  ":math:`\text{u}U\text{_v}V`", where :math:`U` is :math:`1+` the integer portion of the u coordinate,
  and :math:`V` is :math:`1+` the integer portion of the v coordinate.

.. list-table::

   * - Frame range string
     - Formats to
   * - ``1001<UDIM>``
     - ``1001``
   * - ``1001<UVTILE>``
     - ``u1_v1``
   * - ``1002<UVTILE>``
     - ``u2_v1``
   * - ``1010<UVTILE>``
     - ``u1_v2``
   * - ``1011<UVTILE>``
     - ``u2_v2``

.. tip::

   Using ``<UDIM>`` is RECOMMENDED over ``<UVTILE>`` for best compatibility with VFX software.


.. _format-simple-inter-range:

Inter-range Separator
---------------------

An inter-range separator separates one range from another in a multi-range path sequence.
A non-empty inter-range separator MUST exist between each range.

An inter-range separator MUST NOT be a single "``.``" character,
so that it is clear when there are two ranges in the resulting file paths
rather than a single range with subframes.

.. code-block:: text

   # Good
   file.1011-1019<UDIM>_1-5#.tar.gz  # file.1011_1.tar.gz
   file.1011-1019<UDIM>_1-5x0.5#.#.tar.gz  # file.1011_1.5.tar.gz

   # Bad
   file.1011-1019<UDIM>.1-5#.tar.gz
   # In file.1011.5.tar.gz, it is unclear if there's numbers from two ranges (1001 and 5),
   # or a single subframe (1011.5).
   file.1011-1019<UDIM>1-5#.tar.gz
   # In file.10115.tar.gz, it looks like there is only a single frame number.

.. tip::

   Using ``_`` as an inter-range separator is recommended for best
   compatibility with VFX software.
   For the same reason, it is recommended to place the frame number after UDIMs
   for animated texture sequences.

   .. code-block:: text

      file.1-5#_1001-1010#.vdb
      file.1001-1005<UDIM>_1001-1010#.exr

An inter-range separator MUST NOT contain a valid :ref:`range string <format-simple-range>`,
or by definition it would itself be part of the ranges.

An inter-range separator MUST NOT end with a "``-``" or digit,
otherwise there is no clear end to the separator and the start of the next range.
Similarly, an inter-range separator MUST NOT start with a digit,
or a "``.``" and digits,
otherwise there is no clear end of the previous range and start to the separator.


.. _format-simple-suffixes:

Suffixes
--------

Suffixes MUST be present in the name of the sequence.
The file suffixes represent the file extension of the files in the path sequence.
The suffixes include the leading "``.``".

The suffixes MUST NOT contain a valid :ref:`range string <format-simple-range>`,
or by definition they would be part of the ranges.

The suffixes MUST NOT start with a "``.``" and digits
otherwise there is no clear end of the previous range and start to the suffixes.


Parsing
-------

File sequences are parsed by a two step process consisting of tokenisation
and parsing those tokens with a
`Deterministic Finite State Machine <https://en.wikipedia.org/wiki/Deterministic_finite_automaton>`_.
That state machine is as follows:

.. figure:: /_static/format.svg
   :figclass: solid-background
   :width: 90%


Range Grammar
-------------

Ranges are simple enough to form an unambiguous
`Context Free Grammar <https://en.wikipedia.org/wiki/Context-free_grammar>`_.

.. productionlist:: frame_ranges
   ranges: range ("," range)*
   range: FILE_NUM ["-" FILE_NUM ["x" NUM]]
   FILE_NUM: "-"? NUM
   NUM: (0|[1-9][0-9]*)
      : (\.0|\.[0-9]*[1-9])?


.. _compatibility:

Compatibility with VFX Software
-------------------------------

This format was chosen for its compatibility with software commonly used in
the VFX industry.

The "**File Compatible**" column notes whether pathseq can represent
a file sequence output by the DCC.

DCCs often support different sequence string formats depending on whether the
file sequence is being read or written by the DCC.
Therefore this table separately notes
whether a simple pathseq sequence string be passed to the DCC
directly for the DCC to use to read a file sequence (**Read Compatible**),
and whether a simple pathseq sequence string be passed to the DCC
directly for the DCC to use to write a file sequence (**Write Compatible**).

.. list-table::
   :header-rows: 1

   * - Software
     - File Compatible
     - Read Compatible
     - Write Compatible
     - Notes
   * - Arnold
     - N/A
     - ✔
     - N/A
     -
   * - Blender
     - ✔ [#]_
     - N/A
     - ✔
     -
   * - fileseq
     - N/A
     - ✔ [#]_
     - N/A
     -
   * - Houdini
     - Partial
     - ✗
     - ✗
     - [#]_
   * - Katana
     - ✔
     - N/A
     - ✔
     -
   * - Mari
     - ✔
     - ✗
     - ✗
     - [#]_
   * - Maya (file texture node)
     - N/A
     - ✔
     - N/A
     -
   * - Maya (fcheck)
     - Partial [#]_
     - ✔
     - ✔
     -
   * - Mudbox
     - ✔
     - ✗
     - ✗
     -
   * - Nuke
     - ✔
     - ✔
     - ✔
     -
   * - USD
     - N/A
     - ✔
     - N/A
     -
   * - ZBrush
     - ✔
     - ✗
     - ✗
     -

Notes:

.. [#] Blender supports writing sequences that start with a range,
   which would not be compatible with pathseq format.
   But, unlike other formats, such ranges need to be passed as an absolute path
   so aren't as well supported by Blender.
.. [#] fileseq treats ``#`` as 4 digits of padding by default.
   It must be passed an argument to treat ``#`` as a single digit of padding.
.. [#] Houdini expressions use their own syntax (See :ref:`houdini_file_seq`).
   Houdini syntax is infinitely flexible,
   but it can be used to express the same sequences as pathseq.
.. [#] Mari supports only ``$UDIM`` but files are output as interpreted by ``<UDIM>``.
.. [#] fcheck supports writing sequences as ``file#.ext`` and ``#file.ext``,
   but ``file.#.ext`` format must be used for pathseq's simple format.


.. _loose-format:

Loose Path Sequences
====================

The PathSeq API has the concept of a "loose" format.
Whereas the normal sequence string format maximises simplicity
and compatibility across VFX software,
the loose format prioritises compatibility in parsing more sequence strings.
This compatibility comes at a cost of complexity,
and a loose sequence string will likely be cross-compatible between VFX software.

The loose format is a flexible format that is useful
when parsing sequence strings from unknown sources.
It can parse the most sequence strings,
but those strings may only work for one DCC.
This format can be useful when there isn't a guarantee that the
sequence string being parsed is in the simple format.

In `Path Sequences`_ we saw that in the simple format,
a sequence's name has five components:
the stem, an optional prefix, the ranges, inter-range strings, and the suffixes.
The loose format has an additional component, the OPTIONAL postfix,
to support additional characters after the ranges but before the next component.

.. code-block:: text

   /directory/ file . 1001-1002<UDIM> _ 1001-1010# _final .tar.gz
         ┌────┴────┼─┼───────────────┼─┼──────────┼──────┼───────┴─┐
         │    ┌────┘ │          ┌────┘ └────┐     │      └┐        │
         │stem│prefix│   range  │inter-range│range│postfix│suffixes│
         └────┴──────┼──────────┴───────────┴─────┼───────┴────────┘
                     │           ranges           │
                     └────────────────────────────┘

In addition, ranges can be placed anywhere in a loose sequence string.
The placement of the ranges in the strings creates three varieties of loose sequence strings,
based on where the ranges are placed.

The ranges can be at the start of the name:

.. code-block:: text

   /directory/ 1001-1002<UDIM> _ 1001-1010# _ filename .tar.gz
              ├───────────────┼─┼──────────┼─┼────────┼───────┴──┐
              │          ┌────┘ └────┐     │ └─────┐  └─┐        │
              │   range  │inter-range│range│postfix│stem│suffixes│
              ├──────────┴───────────┴─────┼───────┴────┴────────┘
              │           ranges           │
              └────────────────────────────┘

The ranges can be inside the name:

.. code-block:: text

   /directory/ file . 1001-1002<UDIM> _ 1001-1010# _final .tar.gz
         ┌────┴────┼─┼───────────────┼─┼──────────┼──────┼───────┴─┐
         │    ┌────┘ │          ┌────┘ └────┐     │      └┐        │
         │stem│prefix│   range  │inter-range│range│postfix│suffixes│
         └────┴──────┼──────────┴───────────┴─────┼───────┴────────┘
                     │           ranges           │
                     └────────────────────────────┘

Finally, the ranges can be at the end of the name:

.. code-block:: text

   /directory/ file .tar.gz . 1001-1002<UDIM> _ 1001-1010#
        ┌─────┴────┼───────┼─┼───────────────┼─┼──────────┤
        │    ┌─────┘  ┌────┘ │          ┌────┘ └────┐     │
        │stem│suffixes│prefix│   range  │inter-range│range│
        └────┴────────┴──────┼──────────┴───────────┴─────┤
                             │           ranges           │
                             └────────────────────────────┘

.. warning::

   Because the stem or suffix are allowed to be empty, the loose format is ambiguous.
   For example, ``#.tar.gz`` could be represented as a sequence where
   the range starts the string and has a blank stem,
   or the range starts the string and has a stem of "tar" and prefix of ".",
   or the range is in the string and has a blank stem and prefix.

   Therefore the loose format can only make a best guess at how to interpret a sequence string.
   The simple format can be parsed consistently.


.. _format-loose-stem:

Stem
----

The stem is the name of a path sequence, without the prefix, ranges, postfix, and suffixes.
A non-empty stem MAY be present in the name of a path sequence.

The stem MUST NOT contain a valid :ref:`range string <format-simple-range>`,
or by definition it would be considered part of the ranges.

The stem MAY start or end with a "``-``", or digit, or "``.``" and digits,
but this is NOT RECOMMENDED because it creates abiguity when parsing
a file in the sequence.

.. note::

   Path sequences that represent a sequence of hidden files (files starting with a ``.``)
   are interpreted as though the stem starts with "``.``".

   In this example, where the ranges are in the name, the stem is ``.``:

   .. code:: text

      .1-5#.ext

   In this example, where the ranges are in the name, the stem is ``.``:

   .. code:: text

      .1-5#.ext

   In this example, where the ranges end the name, the stem is ``.tar``.

   .. code:: text

      .tar.gz1-5#


.. _format-loose-prefix:

Prefix
------

Path sequences where the name starts with a range MUST NOT contain a prefix.
Path sequences where the ranges exist inside or at the end of the name
MAY contain a single prefix character.

The prefix separates the ranges from the previous component in the name.

The prefix character MUST be one of "``.``" or "``_``".


.. _format-loose-range:

Range
-----

A range MUST be present in the name of a path sequence.
It follows the same format as for simple path sequences (see :ref:`format-simple-range`).


.. _format-loose-inter-range:

Inter-range Separator
---------------------

An inter-range separator separates one range from another in a multi-range path sequence.
A non-empty inter-range separator MAY exist between each range.
Omitting the inter-range separator is NOT RECOMMENDED in multi-range sequences
because it creates abiguity when parsing a file in the sequence.

An inter-range separator MUST NOT contain a valid :ref:`range string <format-simple-range>`,
or by definition it would itself be part of the ranges.

An inter-range separator MAY end with a "``-``" or digit,
but this is NOT RECOMMENDED because it creates abiguity when parsing
a file in the sequence.
Similarly, an inter-range separator MAY start with a digit,
or a "``.``" and digits,
but this is NOT RECOMMENDED either because it creates abiguity when parsing
a file in the sequence.


.. _format-loose-postfix:

Postfix
-------

The prefix is a single character that separates the :ref:`ranges <format-loose-range>`
from the next component of the sequence's name.

The rules that define what is a valid postfix, depend on the type of path sequence.

In path sequences where the ranges start the name:

* The sequence MAY contain a postfix.
* If present, the postfix MUST be a "``_``", or it would be part of the stem.
  If it contained a "``.``" then by definition it would be part of the suffixes.

In path sequences where the ranges exist inside of the name:

* A postfix MAY be present.
* The postfix can be of any length of any length.
* The postfix MUST NOT contain a "``.``", or by definition it would be part of the suffixes.
* The postfix MAY start with digits,
  but this is NOT RECOMMENDED because it creates abiguity when parsing
  a file in the sequence.

In path sequences where the name ends with a range:

* A postfix CANNOT be present, otherwise the ranges would exist inside of the name.


.. _format-loose-suffixes:

Suffixes
--------

The file suffixes represent the file extension of the files in the path sequence.

Suffixes MAY be present in the name of the sequence.
The suffixes include the leading "``.``".

The suffixes MUST NOT contain a valid :ref:`range string <format-simple-range>`,
or by definition they would be part of the ranges.

The suffixes MUST NOT start with a "``.``" and digits
otherwise there is no clear end of the previous range and start to the suffixes.


Parsing
-------

Like simple file sequences,
loose file sequences are parsed by a two step process consisting of tokenisation
and parsing those tokens with a
`Deterministic Finite State Machine <https://en.wikipedia.org/wiki/Deterministic_finite_automaton>`_.
That state machine is as follows:

.. figure:: /_static/adrs/all_formats.svg
   :figclass: solid-background
