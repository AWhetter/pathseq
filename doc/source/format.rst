Format of Sequence Strings
==========================

PathSeq's chosen sequence format is a simple, unambiguous format that maximises
compatibility across VFX DCCs (Digital Content Creation software).

.. seealso::

   See :ref:`adr-001` for more information about why this format was chosen.

Path Sequences
--------------

Like in :mod:`pathlib`,
the name of a path sequence is the final component in a path.

.. figure:: /_static/name.svg
   :figclass: solid-background
   :width: 90%


A sequence's name represents the file names of all files in the sequence.
The name has four components:

* The stem
* An optional prefix
* The ranges
* The suffixes

.. figure:: /_static/name_breakdown.svg
   :figclass: solid-background
   :width: 90%

.. tip::

   Including a prefix as ``.`` is recommended for best compatibility with VFX software.

   .. code-block:: text

      file.1001-1010#.exr
      file.1001-1010#.tar.gz

Supporting multiple ranges in a sequence requires an additional component:
an inter-range separator.

.. figure:: /_static/multi_range_breakdown.svg
   :figclass: solid-background
   :width: 90%

.. tip::

   Using ``_`` as an inter-range separator is recommended for best
   compatibility with VFX software.
   For the same reason, it is recommended to place the frame number after UDIMs
   for animated texture sequences.

   .. code-block:: text

      file.1-5#_1001-1010#.vdb
      file.1001-1005<UDIM>_1001-1010#.exr

.. warning::

   It is recommended to not use ``.`` as an inter-range separator,
   so that it is clearer that there are two ranges in the resulting file paths
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


Specification
~~~~~~~~~~~~~

File sequences are parsed by a two step process consisting of tokenisation
and parsing those tokens with a
`Deterministic Finite State Machine <https://en.wikipedia.org/wiki/Deterministic_finite_automaton>`_.
That state machine is as follows:

.. figure:: /_static/format.svg
   :figclass: solid-background
   :width: 90%

* .. kroki::
     :type: pikchr
     :align: left
     :class: legend-image solid-background

     oval "stem" fit

  Similar to :attr:`python:pathlib.PurePath.stem`.
  This is the final path component without the ranges and all suffixes.
* .. kroki::
     :type: pikchr
     :align: left
     :class: legend-image solid-background

     box "prefix" fit

  An optional ``.`` or ``_`` that separates the stem from the ranges.
* .. kroki::
     :type: pikchr
     :align: left
     :class: legend-image solid-background

     oval "range" fit

  A range, as defined in `Frame Ranges`_.
* .. kroki::
     :type: pikchr
     :align: left
     :class: legend-image solid-background

     box "inter-range" fit

  An arbitrary string that separates the ranges.
  Typically this is a ``_``, but may be more complex.
* .. kroki::
     :type: pikchr
     :align: left
     :class: legend-image solid-background

     oval "suffixes" fit

  The file suffixes, including the leading ``.``.


.. _range_string_format:

Frame Ranges
------------

Frame ranges consist of the range string, and the pad string.

.. figure:: /_static/range_string_breakdown.svg
   :figclass: solid-background
   :width: 50%

**Range strings**:

Range string consist of comma separated ranges,
where each range is of the format ``START-ENDxSTEP``,
where ``END`` is inclusive and ``xSTEP`` is optional.

So the range string ``1-5`` represents the numbers 1, 2, 3, 4, 5.
The range string ``1-5x2`` represents the numbers 1, 3, 5..

**Pad string**:

A pad string represents how the numbers in the range should be formatted
when putting a number from the range into a file path.

The most basic form of a pad string is a string of ``#`` characters.
The number of ``#`` represents the minimum with of the formatted number.
If the stringified number is smaller than the width,
then it will be zero padded.
If the stringified number is larger than the width,
it will exceed the given width.
A ``-`` sign to indicate a negative number is counted in the width.

.. list-table::

   * - Frame range string
     - Formats to
   * - ``1####``
     - ``0001``
   * - ``1001#``
     - ``1001``
   * - ``-1####``
     - ``-001``

.. warning::

   Some DCCs support the use of the "@" character as a single digit pad string.
   PathSeq does not support this character because it has conflicting definitions
   between DCCs.
   Users are encouraged to preprocess "@" characters out of sequence strings
   passed to PathSeq if this character may be present as a pad character.


Pad strings can also use MaterialX tokens (https://materialx.org/Specification.html).
The "Filename Substitutions" section of the specification
describes two tokens for representing UDIMs in file names.

* ``<UDIM>``: This is equivalent to ``####``.

  Using ``<UDIM>`` can be useful to indicate which ranges in an
  animated texture sequence are the UDIMs
  and which are the frame numbers.
  As an example, ``texture.1001-1010<UDIM>_1001-1010####.tex``
  is clearer than ``texture.1001-1010####_1001-1010####.tex``.

* ``<UVTILE>``: Originating from Mudbox, this token represents the string
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

   Using ``<UDIM>`` is recommended over ``<UVTILE>`` for best compatibility with VFX software.


Grammar
~~~~~~~

Frame ranges are simple enough to form an unambiguous
`Context Free Grammar <https://en.wikipedia.org/wiki/Context-free_grammar>`_.

.. productionlist:: frame_ranges
   ranges: range ("," range)*
   range: FILE_NUM ["-" FILE_NUM ["x" NUM]]
   FILE_NUM: "-"? NUM
   NUM: /
       (0|[1-9][0-9]*)       # the digits
       (\.0|\.[0-9]*[1-9])?  # the subsamples
   /x


Compatibility with VFX Software
-------------------------------

This format was chosen for its compatibility with software commonly used in
the VFX industry.

The "File Compatible" column notes whether pathseq can represent
a file sequence output by the DCC.

DCCs often support different sequence string formats depending on whether the
file sequence is being read or written by the DCC.
Therefore this table separately notes
whether a strict pathseq sequence string be passed to the DCC
directly for the DCC to use to read a file sequence (Read Compatible),
and whether a strict pathseq sequence string be passed to the DCC
directly for the DCC to use to write a file sequence (Write Compatible).

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
   but ``file.#.ext`` format must be used for pathseq's strict format.

Loose Format
------------

The PathSeq API has the concept of a "loose" format.
Whereas the normal sequence string format maximises simplicity
and compatibility across VFX software,
the loose format prioritises compatibility in parsing more sequence strings.
This compatibility comes at a cost of complexity,
and a loose sequence string will likely be less compatible across VFX software.

The loose format is a flexible format that is useful
when parsing sequence strings from unknown sources.
It can parse the most sequence strings,
but those strings may only work for one DCC.
This format can be useful when there isn't a guarantee that the
sequence string being parsed is in the simple format.

In `Path Sequences`_ we saw that in the strict format,
a sequence's name has four components:
the stem, an optional prefix, the ranges, inter-range strings, and the suffixes.
The loose format has an additional component, the postfix,
to support additional characters after the ranges but before the next component.

.. figure:: /_static/loose_name_breakdown.svg
   :figclass: solid-background
   :width: 90%

In addition, ranges can be placed anywhere in the sequence string.
The placement of the range in the strings creates three varieties of loose sequence strings,
based on where the ranges are placed in the string.

The ranges can be at the start of the sequence string:

.. figure:: /_static/starts_name_breakdown.svg
   :figclass: solid-background
   :width: 90%

The ranges can be inside the sequence string:

.. figure:: /_static/loose_name_breakdown.svg
   :figclass: solid-background
   :width: 90%

Finally, the ranges can be at the end of the sequence string:

.. figure:: /_static/ends_name_breakdown.svg
   :figclass: solid-background
   :width: 90%

.. warning::

   Because the stem or suffix are allowed to be empty, the loose format is ambiguous.
   For example, ``#.tar.gz`` could be represented as a sequence where
   the range starts the string and has a blank stem,
   or the range starts the string and has a stem of "tar",
   or the range is in the string and has a blank stem and prefix.

   Therefore the loose format can only make a best guess at how to interpret a sequence string.
   The strict format can be parsed consistently.

.. attention:: Hidden file sequences (starting with .)

   File sequences starting with a "." have unintuitive behaviour.
   For example:

   .. code:: text

      .1-5#file.ext

   In this case, the range is considered "in" the string, where the "." is the stem.

   .. TODO: Maybe it should just be a prefix though?


Specification
~~~~~~~~~~~~~

Like strict file sequences,
loose file sequences are parsed by a two step process consisting of tokenisation
and parsing those tokens with a
`Deterministic Finite State Machine <https://en.wikipedia.org/wiki/Deterministic_finite_automaton>`_.
That state machine is as follows:

.. figure:: /_static/adrs/all_formats.svg
   :figclass: solid-background

* .. kroki::
     :type: pikchr
     :align: left
     :class: legend-image solid-background

     oval "stem" fit

  Similar to :attr:`python:pathlib.PurePath.stem`.
  This is the final path component without the ranges and all suffixes.
* .. kroki::
     :type: pikchr
     :align: left
     :class: legend-image solid-background

     box "prefix" fit

  An optional ``.`` or ``_`` that separates the stem or suffixes from the ranges.
* .. kroki::
     :type: pikchr
     :align: left
     :class: legend-image solid-background

     oval "range" fit

  A range, as defined in `Frame Ranges`_.
* .. kroki::
     :type: pikchr
     :align: left
     :class: legend-image solid-background

     box "inter-range" fit

  An arbitrary string that separates the ranges.
  Typically this is a ``_``, but may be more complex.
* .. kroki::
     :type: pikchr
     :align: left
     :class: legend-image solid-background

     box "postfix" fit

  An optional ``.`` or ``_`` that separates the ranges from the stem or suffixes.
* .. kroki::
     :type: pikchr
     :align: left
     :class: legend-image solid-background

     oval "suffixes" fit

  The file suffixes, including the leading ``.``.
