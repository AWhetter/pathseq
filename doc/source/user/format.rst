***********************
Sequence String Formats
***********************

PathSeq supports two variations of sequence string format.
PathSeq's chosen sequence format is a simple, unambiguous format that maximises
compatibility across VFX DCCs (Digital Content Creation software).
The :ref:`loose format <loose-format>` is a more complex and ambiguous format
that can represent more configurations of file name.

If you aren't sure which variation is right for you,
choose :ref:`simple <simple-format>` if you have control over the format of
sequence strings that you support,
and choose :ref:`loose <loose-format>` if you don't.

.. seealso::

   See :ref:`adr-001` for more information about why the simple format was chosen.

   See :ref:`compatibility` for a review of this format's ability to represent
   file sequences the different DCCs accept or output.


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

.. code-block:: pycon

   >>> PathSequence('/directory/file.1001-1010#.tar.gz').name
   'file.1001-1010#.tar.gz'

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

.. code-block:: pycon

   >>> seq = PathSequence('/directory/file.1001-1010#.tar.gz')
   >>> seq.name
   'file.1001-1010#.tar.gz'
   >>> seq.stem
   'file'
   >>> seq.parsed.prefix
   '.'
   >>> seq.parsed.ranges
   Ranges(1001-1010#)
   >>> seq.suffixes
   ('.tar', '.gz')

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
A non-empty stem will always be present in the name of a path sequence.

.. code-block:: pycon

   >>> PathSequence('/path/to/images.1-3####.exr').stem
   'images'
   >>> PathSequence('/path/to/texture.1011-1013<UDIM>_1-3#.tex').stem
   'texture'


.. _format-simple-prefix:

Prefix
------

The prefix is an optional, single "``.``" or "``_``" character that separates the :ref:`stem <format-simple-stem>`
from the :ref:`ranges <format-simple-range>`.

.. code-block:: pycon

   >>> PathSequence('/path/to/images.1-3####.exr').parsed.prefix
   '.'
   >>> PathSequence('/path/to/images_1-3####.exr').parsed.prefix
   '_'
   >>> PathSequence('/path/to/images1-3####.exr').parsed.prefix
   ''
   >>> PathSequence('/path/to/texture.1011-1013<UDIM>_1-3#.tex').parsed.prefix
   '.'

.. tip::

   Including a prefix as "``.``" is recommended for best compatibility with VFX software.

   .. code-block:: text

      file.1001-1010#.exr
      file.1001-1010#.tar.gz


.. _format-simple-range:

Range
-----

The range is a concice representation of the file numbers of each file
in the sequence plus a definition of how those numbers are formatted
in the resulting file names.

A range will always be present in the name of a path sequence.
A range consists of the ranges specifier, and the padding.

.. code-block:: text

    1001-1010,1020-1030 ####
   ├───────────────────┼────┴──┐
   │      ranges       │padding│
   └───────────────────┴───────┘

.. code-block::

   >>> PathSequence('/path/to/images.1-3####.exr').parsed.ranges
   Ranges(1-3###)
   >>> PathSequence('/path/to/texture.1011-1013<UDIM>_1-3#.tex').parsed.ranges
   Ranges(1011-1013<UDIM>_1-3#)


.. _format-simple-ranges:

Ranges Specifier
~~~~~~~~~~~~~~~~

The ranges specifier is a concice representation of the file numbers of each file
in the sequence.

A ranges specifier consists of comma separated range specifiers,
where each range specifier is of the format ``START-ENDxSTEP``.
``START`` is required, and ``END`` and ``xSTEP`` are optional.

.. code-block:: pycon

   >>> seq = PathSequence('/path/to/images.1-5####.exr')
   >>> seq.file_num_seqs
   (FileNumSequence(1-5),)
   >>> list(FileNumSequence.from_str('1-5')
   [1, 2, 3, 4, 5]
   >>> list(FileNumSequence.from_str('1'))
   [1]
   >>> list(FileNumSequence.from_str('1-5x2'))
   [1, 3, 5]
   >>> list(FileNumSequence.from_str('1-6x2'))
   [1, 3, 5]
   >>> list(FileNumSequence.from_str('1-2x0.5'))
   [Decimal('1'), Decimal('1.5'), Decimal('2.0')]

The ranges specifier is optional.
When no ranges specifier is present, the path sequence is considered empty.

.. code-block:: pycon

   >>> list(PathSequence('/path/to/images.####.exr'))
   []


.. _format-simple-padding:

Padding
~~~~~~~

The padding string (or pad string) is definition of how a file number is formatted
in each file name contained in the sequence.

A pad string can be a string of "``#``" characters, or a MaterialX token.


``#`` characters
^^^^^^^^^^^^^^^^

The most basic form of a pad string is a string of "``#``" characters.
The number of "``#``" represents the minimum with of the formatted number.
If the stringified number is smaller than the width,
then it will be zero padded.

.. code-block:: pycon

   >>> seq = PathSequence('/path/to/images.1-3####.exr').parsed.ranges[0]
   PaddedRange(1-3####)
   >>> PaddedRange((), '####').format(1)
   '0001'
   >>> PaddedRange((), '##').format(1)
   '01'
   >>> PaddedRange((), '####').format(-1)
   '-001'

If the stringified number is larger than the width,
it will exceed the given width.

.. code-block:: pycon

   >>> PaddedRange((), '#').format(1001)
   '1001'

In a negative number the "``-``" sign is counted in the width.

.. code-block:: pycon

   >>> PaddedRange((), '####').format(-1)
   '-001'

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

  .. code-block:: pycon

     >>> PaddedRange((), '<UDIM>').format(1)
     '0001'

* ``<UVTILE>``: This token represents the string
  ":math:`\text{u}U\text{_v}V`", where :math:`U` is :math:`1+` the integer portion of the u coordinate,
  and :math:`V` is :math:`1+` the integer portion of the v coordinate.

  .. code-block:: pycon

     >>> PaddedRange((), '<UVTILE>').format(1001)
     'u1_v1'
     >>> PaddedRange((), '<UVTILE>').format(1002)
     'u2_v1'
     >>> PaddedRange((), '<UVTILE>').format(1010)
     'u1_v2'
     >>> PaddedRange((), '<UVTILE>').format(1011)
     'u2_v2'

.. tip::

   Using ``<UDIM>`` is recommended over ``<UVTILE>`` for best compatibility across VFX software.


.. _format-simple-inter-range:

Inter-range Separator
---------------------

An inter-range separator separates one range from another in a multi-range path sequence.
A non-empty inter-range separator will always exist between each range.

.. code-block::

   >>> PathSequence('/path/to/texture.1011-1013<UDIM>_1-3#.tex').parsed.ranges.inter_ranges
   ('_',)
   >>> PathSequence('texture.1-3#_interrange_1-3#.tex').parsed.ranges.inter_ranges
   ('_interrange_',)

.. tip::

   Using ``_`` as an inter-range separator is recommended for best
   compatibility with VFX software.
   For the same reason, it is recommended to place the frame number after UDIMs
   for animated texture sequences.

   .. code-block:: text

      file.1-5#_1001-1010#.vdb
      file.1001-1005<UDIM>_1001-1010#.exr


.. _format-simple-suffixes:

Suffixes
--------

The file suffixes represent the file extension of the files in the path sequence.
The suffixes include the leading "``.``".
They will always be present.

.. code-block:: pycon

   >>> PathSequence('images.1-3####.exr').suffix
   '.exr'
   >>> PathSequence('images.1-3####.exr').suffixes
   ('.exr',)
   >>> PathSequence('file.1-3####.tar.xz').suffix
   '.xz'
   >>> PathSequence('file.1-3####.tar.xz').suffixes
   ('.tar', '.xz')


.. _loose-format:

Loose Path Sequences
====================

Whereas the simple sequence string format maximises simplicity
and compatibility across VFX software,
the loose format prioritises compatibility in parsing more sequence strings.
This compatibility comes at a cost of complexity and ambiguity.

In `Path Sequences`_ we saw that in the simple format,
a sequence's name has five components:
the stem, an optional prefix, the ranges, inter-range strings, and the suffixes.
The loose format has an additional component — the optional postfix —
to support additional characters after the ranges but before the next component.

.. code-block:: text

   /directory/ file . 1001-1002<UDIM> _ 1001-1010# _final .tar.gz
         ┌────┴────┼─┼───────────────┼─┼──────────┼──────┼───────┴─┐
         │    ┌────┘ │          ┌────┘ └────┐     │      └┐        │
         │stem│prefix│   range  │inter-range│range│postfix│suffixes│
         └────┴──────┼──────────┴───────────┴─────┼───────┴────────┘
                     │           ranges           │
                     └────────────────────────────┘

.. code-block:: pycon

   >>> LoosePathSequence('file.1001-1002<UDIM>_1001-1010#_final.tar.gz').parsed.postfix
   '_final'

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

.. code-block:: pycon

   >>> LoosePathSequence('1001-1002<UDIM>_1001-1010#_filename.tar.gz').parsed
   RangesStartName(...)

The ranges can be inside the name:

.. code-block:: text

   /directory/ file . 1001-1002<UDIM> _ 1001-1010# _final .tar.gz
         ┌────┴────┼─┼───────────────┼─┼──────────┼──────┼───────┴─┐
         │    ┌────┘ │          ┌────┘ └────┐     │      └┐        │
         │stem│prefix│   range  │inter-range│range│postfix│suffixes│
         └────┴──────┼──────────┴───────────┴─────┼───────┴────────┘
                     │           ranges           │
                     └────────────────────────────┘

.. code-block:: pycon

   >>> LoosePathSequence('file.1001-1002<UDIM>_1001-1010#_final.tar.gz').parsed
   RangesInName(...)

Finally, the ranges can be at the end of the name:

.. code-block:: text

   /directory/ file .tar.gz . 1001-1002<UDIM> _ 1001-1010#
        ┌─────┴────┼───────┼─┼───────────────┼─┼──────────┤
        │    ┌─────┘  ┌────┘ │          ┌────┘ └────┐     │
        │stem│suffixes│prefix│   range  │inter-range│range│
        └────┴────────┴──────┼──────────┴───────────┴─────┤
                             │           ranges           │
                             └────────────────────────────┘

.. code-block:: pycon

   >>> LoosePathSequence('file.tar.gz.1001-1002<UDIM>_1001-1010#').parsed
   RangesEndName(...)

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
A non-empty stem may or may not be present in the name of a path sequence.

TODO

.. note::

   Path sequences that represent a sequence of hidden files (files starting with a ``.``)
   are interpreted as though the stem starts with "``.``".

   .. code-block:: pycon

      >>> LoosePathSequence('.1-5#.ext').stem
      '.'
      >>> LoosePathSequence('.tar.gz1-5#').stem
      '.tar'


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
