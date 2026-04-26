***********************
Sequence String Formats
***********************

PathSeq supports two variations of sequence string format.
PathSeq's chosen sequence format is a simple, unambiguous format that maximises
compatibility across VFX DCCs (Digital Content Creation software).
The :ref:`loose format <loose-format>` is a more complex and ambiguous format
that can represent more possible path sequences.

If you aren't sure which variation is right for you,
choose :ref:`simple <simple-format>` if you have control over the format of
sequence strings that you support,
and choose :ref:`loose <loose-format>` if you don't.

.. seealso::

   See :ref:`adr-001` for more information about why the simple format was chosen.

   See :ref:`compatibility` for a review of this format's ability to represent
   file sequences that the different DCCs accept or output.


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
* An optional pre-range separator
* The ranges
* The suffixes

.. code-block:: text

   /directory/ file . 1001-1010# .tar.gz
          ┌───┴────┼─┼──────────┼───────┴┐
          │    ┌───┘ └───┐      │        │
          │stem│pre-range│ranges│suffixes│
          ├────┴─────────┴──────┴────────┤
          │             name             │
          └──────────────────────────────┘

.. code-block:: pycon

   >>> seq = PathSequence('/directory/file.1001-1010#.tar.gz')
   >>> seq.name
   'file.1001-1010#.tar.gz'
   >>> seq.stem
   'file'
   >>> seq.parsed.pre_range
   '.'
   >>> seq.parsed.ranges
   Ranges(1001-1010#)
   >>> seq.suffixes
   ('.tar', '.gz')

Supporting multiple ranges in a sequence requires an additional component:
an inter-range separator.

.. code-block:: text

   /directory/ file . 1001-1002<UDIM> _ 1001-1010# .tar.gz
      ┌───────┴────┼─┼───────────────┼─┼──────────┼───────┴┐
      │    ┌───────┘ |          ┌────┘ └────┐     │        │
      │stem│pre-range│   range  │inter-range│range│suffixes│
      └────┴─────────┼──────────┴───────────┴─────┼────────┘
                     │           ranges           │
                     └────────────────────────────┘


.. _format-simple-stem:

Stem
----

The stem is the name of a path sequence, without the pre-range separator, ranges, and suffixes.
A non-empty stem will always be present in the name of a path sequence.

.. code-block:: pycon

   >>> PathSequence('/path/to/images.1-3####.exr').stem
   'images'
   >>> PathSequence('/path/to/texture.1011-1013<UDIM>_1-3#.tex').stem
   'texture'


.. _format-simple-prerange:

Pre-range Separator
-------------------

The pre-range separator is an optional, single "``.``" or "``_``" character that separates the :ref:`stem <format-simple-stem>`
from the :ref:`ranges <format-simple-range>`.

.. code-block:: pycon

   >>> PathSequence('/path/to/images.1-3####.exr').parsed.pre_range
   '.'
   >>> PathSequence('/path/to/images_1-3####.exr').parsed.pre_range
   '_'
   >>> PathSequence('/path/to/images1-3####.exr').parsed.pre_range
   ''
   >>> PathSequence('/path/to/texture.1011-1013<UDIM>_1-3#.tex').parsed.pre_range
   '.'

.. tip::

   Including a pre-range separator as "``.``" is recommended for best compatibility with VFX software.

   .. code-block:: text

      file.1001-1010#.exr
      file.1001-1010#.tar.gz


.. _format-simple-range:

Range
-----

The range is a concise representation of the file numbers of each file
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
   Ranges(1-3####)
   >>> PathSequence('/path/to/texture.1011-1013<UDIM>_1-3#.tex').parsed.ranges
   Ranges(1011-1013<UDIM>_1-3#)


.. _format-simple-ranges:

Ranges Specifier
~~~~~~~~~~~~~~~~

The ranges specifier is a concise representation of the file numbers of each file
in the sequence.

A ranges specifier consists of comma separated range specifiers,
where each range specifier is of the format ``START-ENDxSTEP``.
``START`` is required, and ``END`` and ``xSTEP`` are optional.

.. code-block:: pycon

   >>> seq = PathSequence('/path/to/images.1-5####.exr')
   >>> seq.file_num_seqs
   (FileNumSequence(1-5),)
   >>> list(FileNumSequence.from_str('1-5'))
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

The padding string (or pad string) is the definition of how a file number is formatted
for each file name contained in the sequence.

A pad string can be a string of "``#``" characters, or a MaterialX token.


``#`` characters
^^^^^^^^^^^^^^^^

The most basic form of a pad string is a string of "``#``" characters.
The number of "``#``" represents the minimum width of the formatted number.
If the stringified number is smaller than the width,
then it will be zero padded.

.. code-block:: pycon

   >>> PathSequence('/path/to/images.1-3####.exr').parsed.ranges
   Ranges(1-3####)
   >>> PaddedRange((), '####').format(1)
   '0001'
   >>> PaddedRange((), '##').format(1)
   '01'

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

* ``<UDIM>``: This token represents 4 digits of padding — the same as ``####`` does.

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
     'u10_v1'
     >>> PaddedRange((), '<UVTILE>').format(1011)
     'u1_v2'

.. tip::

   Using ``<UDIM>`` is recommended over ``<UVTILE>`` for best compatibility across VFX software.


.. _format-simple-inter-range:

Inter-range Separator
---------------------

An inter-range separator separates one range from another in a multi-range path sequence.
There will always be a separator of one or more characters between
each range in a multi-range path sequence.

.. code-block:: pycon

   >>> PathSequence('/path/to/texture.1011-1013<UDIM>_1-3#.tex').parsed.ranges.inter_ranges
   ('_',)

An inter-range separator does not have to be a single character:

.. code-block:: pycon

   >>> PathSequence('texture.1-3#_interrange_1-3#.tex').parsed.ranges.inter_ranges
   ('_interrange_',)


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


.. _compatibility:

Compatibility with VFX Software
-------------------------------

This format maximises compatibility with software commonly used in
the VFX industry.
Any sequence string that is not directly compatible with a DCC
can be converted to a compatible sequence string using :doc:`format conversion <convert>`.

The "**File Compatible**" column notes whether pathseq can represent
a file sequence output by the DCC.

DCCs often support different sequence string formats depending on whether the
file sequence is being read or written by the DCC.
Therefore this table separately notes
whether a simple pathseq sequence string can be passed to the DCC
directly for the DCC to use to read a file sequence (**Read Compatible**),
and whether a simple pathseq sequence string can be passed to the DCC
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

Whereas the simple sequence string format maximises simplicity
and compatibility across VFX software,
the loose format prioritises compatibility with more sequence strings.
This compatibility comes at a cost of complexity and the potential for ambiguity.

In `Path Sequences`_ we saw that in the simple format,
a sequence's name has five components:
the stem, an optional pre-range separator, the ranges, inter-range strings, and the suffixes.
The loose format has an additional component — the optional post-range separator —
to support additional characters after the ranges but before the next component.

.. code-block:: text

   /directory/ file . 1001-1002<UDIM> _ 1001-1010# _final .tar.gz
      ┌───────┴────┼─┼───────────────┼─┼──────────┼──────┼───────┴────┐
      │    ┌───────┘ │          ┌────┘ └────┐     │      └───┐        │
      │stem│pre-range│   range  │inter-range│range│post-range│suffixes│
      └────┴─────────┼──────────┴───────────┴─────┼──────────┴────────┘
                     │           ranges           │
                     └────────────────────────────┘

.. code-block:: pycon

   >>> LoosePathSequence('file.1001-1002<UDIM>_1001-1010#_final.tar.gz').parsed.post_range
   '_final'

In addition, ranges can be placed anywhere in a loose sequence string.
The placement of the ranges in the strings creates three varieties of loose sequence strings,
based on where the ranges are placed.

The ranges can be at the start of the name:

.. code-block:: text

   /directory/ 1001-1002<UDIM> _ 1001-1010# _ filename .tar.gz
              ├───────────────┼─┼──────────┼─┼────────┼───────┴────┐
              │          ┌────┘ └────┐     │ └───────┐└───┐        │
              │   range  │inter-range│range│postrange│stem│suffixes│
              ├──────────┴───────────┴─────┼─────────┴────┴────────┘
              │           ranges           │
              └────────────────────────────┘

.. code-block:: pycon

   >>> LoosePathSequence('1001-1002<UDIM>_1001-1010#_filename.tar.gz').parsed
   RangesStartName(...)

The ranges can be inside the name:

.. code-block:: text

   /directory/ file . 1001-1002<UDIM> _ 1001-1010# _final .tar.gz
      ┌───────┴────┼─┼───────────────┼─┼──────────┼──────┼───────┴────┐
      │    ┌───────┘ │          ┌────┘ └────┐     │      └───┐        │
      │stem│pre-range│   range  │inter-range│range│post-range│suffixes│
      └────┴─────────┼──────────┴───────────┴─────┼──────────┴────────┘
                     │           ranges           │
                     └────────────────────────────┘

.. code-block:: pycon

   >>> LoosePathSequence('file.1001-1002<UDIM>_1001-1010#_final.tar.gz').parsed
   RangesInName(...)

Finally, the ranges can be at the end of the name:

.. code-block:: text

   /directory/ file .tar.gz . 1001-1002<UDIM> _ 1001-1010#
     ┌────────┴────┼───────┼─┼───────────────┼─┼──────────┤
     │    ┌────────┘┌──────┘ │          ┌────┘ └────┐     │
     │stem│suffixes │prerange│   range  │inter-range│range│
     └────┴─────────┴────────┼──────────┴───────────┴─────┤
                             │           ranges           │
                             └────────────────────────────┘

.. code-block:: pycon

   >>> LoosePathSequence('file.tar.gz.1001-1002<UDIM>_1001-1010#').parsed
   RangesEndName(...)

.. warning::

   Because the stem or suffix are allowed to be empty, the loose format is ambiguous.
   For example, ``#.tar.gz`` could be represented as a sequence where
   the range starts the string and has a blank stem,
   or the range is in the string and has a blank stem.

   Therefore the loose format can only make a best guess at how to interpret a sequence string.
   The simple format can be parsed consistently.


.. _format-loose-stem:

Stem
----

Unlike :ref:`stems in the simple format <format-simple-stem>`,
a stem may or may not be present in the name of a loose path sequence.

.. code-block:: pycon

   >>> LoosePathSequence('/path/to/images.1-3####.exr').stem
   'images'
   >>> LoosePathSequence('/path/to/1-3####images.exr').stem
   'images'
   >>> LoosePathSequence('/path/to/images.exr.1-3####').stem
   'images'
   >>> LoosePathSequence('/path/to/texture.1001-1002<UDIM>_1001-1010#_final.tex').stem
   'texture'
   >>> LoosePathSequence('/path/to/1-3####.exr').stem
   ''

.. note::

   Path sequences that represent a sequence of hidden files (files starting with a ``.``)
   are interpreted as though the stem starts with "``.``".

   .. code-block:: pycon

      >>> LoosePathSequence('.1-5#.ext').stem
      '.'
      >>> LoosePathSequence('.tar.gz1-5#').stem
      '.tar'

.. note::

   For ranges that start or end the name of the sequence,
   there is ambiguity in how to interpret the stem and suffixes.
   Like :attr:`pathlib.PurePath.stem`, this will contain a suffix
   if the paths have multiple suffixes:

   .. code-block:: pycon

      >>> LoosePathSequence('file.tar.gz.1-5#').stem
      'file.tar'
      >>> LoosePathSequence('1-5#file.tar.gz').stem
      'file.tar'


.. _format-loose-prerange:

Pre-range Separator
-------------------

Like :ref:`the simple format <format-simple-prerange>`, the pre-range separator separates
the :ref:`ranges <format-loose-range>` from the previous component in the name.

.. code-block:: pycon

   >>> LoosePathSequence('/path/to/images.1-3####.exr').parsed.pre_range
   '.'
   >>> LoosePathSequence('/path/to/images_1-3####.exr').parsed.pre_range
   '_'
   >>> LoosePathSequence('/path/to/images1-3####.exr').parsed.pre_range
   ''
   >>> LoosePathSequence('/path/to/1-3####_images.exr').parsed.pre_range
   ''

Path sequences where the name starts with a range won't contain a pre-range separator
because there is no preceding component to separate from the ranges.

   >>> LoosePathSequence('/path/to/1-3####_images.exr').parsed.pre_range
   ''


.. _format-loose-range:

Range
-----

A range follows the same format as for simple path sequences (see :ref:`format-simple-range`).
A range will always be present in the name of a path sequence,
otherwise it would be a path rather than a path sequence.

.. code-block:: pycon

   >>> LoosePathSequence('/path/to/images.1-3####.exr').parsed.ranges
   Ranges(1-3####)
   >>> LoosePathSequence('/path/to/1-3####.images.exr').parsed.ranges
   Ranges(1-3####)
   >>> LoosePathSequence('/path/to/images.exr.1-3####').parsed.ranges
   Ranges(1-3####)
   >>> LoosePathSequence('/path/to/texture.1011-1013<UDIM>_1-3#.tex').parsed.ranges
   Ranges(1011-1013<UDIM>_1-3#)


.. _format-loose-inter-range:

Inter-range Separator
---------------------

Unlike :ref:`the simple format <format-simple-inter-range>`,
inter-range separators are optional in a loose path sequence.

.. code-block:: pycon

   >>> LoosePathSequence('/path/to/texture.1011-1013<UDIM>_1-3#.tex').parsed.ranges.inter_ranges
   ('_',)

.. caution::

   Omitting the inter-range separator in multi-range sequences
   creates abiguity when parsing a file in the sequence.

   .. code-block:: pycon

      >>> tmp = getfixture('tmp_path')
      >>> seq = tmp / LoosePathSequence('file.1001-1003#1001-1003#.exr')
      >>> seq[0].name
      'file.10011001.exr'
      >>> for path in seq:
      ...     path.touch()
      ...
      >>> seq.resize_from_existing_paths()[0]
      LoosePathSequence('.../file.1001100-1003100x1000#1-3#.exr')

An inter-range separator does not have to be a single character:

.. code-block:: pycon

   >>> LoosePathSequence('/path/to/volume-vid1-50##-frame1-3#.vdb').parsed.ranges.inter_ranges
   ('-frame',)

.. caution::

   Ending an inter-range separator with a "``-``" or digit
   creates abiguity in parsing the next range.
   A ``-`` would make the following range start with a negative number,
   and a digit would affect the starting number of the following range.

   .. code-block:: pycon

      >>> inter_range = '-frame-'
      >>> seq = LoosePathSequence(f'file.1001,1002<UDIM>{inter_range}1-3#.exr')
      >>> seq.parsed.ranges.inter_ranges
      ('-frame',)
      >>> seq.file_num_seqs
      (FileNumSequence(1001,1002), FileNumSequence(-1-3))

.. tip::

   Starting an inter-range separator with a digit,
   or a "``.``" and digits,
   makes it difficult for a person to tell where the range starts and ends from
   a file path in the sequence.

   .. code-block:: pycon

      >>> inter_range = '0frame'
      >>> seq = LoosePathSequence(f'file.1001,1002#{inter_range}1-3#.exr')
      >>> seq[0].name
      'file.10010frame1.exr'


.. _format-loose-postrange:

Post-range Separator
--------------------

The post-range separator separates the :ref:`ranges <format-loose-range>`
from the next component of the sequence's name.

.. code-block:: pycon

   >>> LoosePathSequence('/path/to/images.1-3####_postrange.exr').parsed.post_range
   '_postrange'
   >>> LoosePathSequence('/path/to/1-3####_images.exr').parsed.post_range
   '_'
   >>> LoosePathSequence('/path/to/images.exr.1-3####').parsed.post_range
   ''

In path sequences where the ranges start the name,
if the post-range separator is present then it can only be a "``_``",
else the post-range separator will be part of the stem.

.. code-block:: pycon

   >>> post_range = '_postrange'
   >>> seq = LoosePathSequence(f'/path/to/1-3####{post_range}_images.exr')
   >>> seq.parsed.post_range
   '_'
   >>> seq.stem
   'postrange_images'

.. note::

   If the post-range separator were to contain a "``.``" then it would become part of the suffixes.

   .. code-block:: pycon

      >>> post_range = '.postrange'
      >>> seq = LoosePathSequence(f'/path/to/1-3####{post_range}_images.exr')
      >>> seq.suffixes
      ('.postrange_images', '.exr')
      >>> seq.stem
      ''
      >>> LoosePathSequence(f'/path/to/1-3####{post_range}.images.exr').suffixes
      ('.postrange', '.images', '.exr')

In path sequences where the ranges exist inside of the name,
the post-range separator can be of any length.

.. code-block:: pycon

   >>> LoosePathSequence('/path/to/images.1-3####_postrange.exr').parsed.post_range
   '_postrange'

.. caution::

   Including a "``.``" in the post-range separator means it would become part of the suffixes.

   .. code-block:: pycon

      >>> post_range = 'my.postrange'
      >>> seq = LoosePathSequence(f'/path/to/images.1-3####{post_range}.exr')
      >>> seq.suffixes
      ('.postrange', '.exr')
      >>> seq.parsed.post_range
      'my'

.. tip::

   Starting the post-range separator with digits
   makes it difficult to tell where the range starts and ends from
   a file path in the sequence.

   .. code-block:: pycon

      >>> post_range = '0postrange'
      >>> seq = LoosePathSequence(f'images.1-3#{post_range}.exr')
      >>> seq[0].name
      'images.10postrange.exr'

In path sequences where the name ends with a range there is no pre-range separator,
otherwise the ranges would exist inside of the name.

.. code-block:: pycon

   >>> post_range = 'postrange'
   >>> LoosePathSequence(f'images.exr.1-3#{post_range}').parsed
   RangesInName(...)


.. _format-loose-suffixes:

Suffixes
--------

Unlike in :ref:`the simple format <format-simple-suffixes>`,
file suffixes are optional in a loose path sequence.

.. code-block:: pycon

   >>> LoosePathSequence('images.1-3####.exr').suffix
   '.exr'
   >>> LoosePathSequence('images.1-3####.exr').suffixes
   ('.exr',)
   >>> LoosePathSequence('file.1-3####.tar.xz').suffix
   '.xz'
   >>> LoosePathSequence('file.1-3####.tar.xz').suffixes
   ('.tar', '.xz')
   >>> LoosePathSequence('1-3####.images.exr').suffix
   '.exr'
   >>> LoosePathSequence('1-3####_file.tar.xz').suffixes
   ('.tar', '.xz')
   >>> LoosePathSequence('images.exr.1-3####').suffix
   '.exr'
   >>> LoosePathSequence('images.tar.xz.1-3####').suffixes
   ('.tar', '.xz')


.. tip::

   In path sequences where the ranges exist inside of the name,
   starting the suffixes with a digit, or a "``.``" and digits,
   makes it difficult for a person to tell where the range starts and ends from
   a file path in the sequence.

   .. code-block:: pycon

      >>> suffix = '.3ds'
      >>> seq = LoosePathSequence(f'scenes.1-3#{suffix}')
      >>> seq[0].name
      'scenes.1.3ds'

   Similarly, in path sequences where the ranges end the name,
   ending the suffixes with a digit, or a "``.``" and digits,
   creates abiguity with the following range.

   .. code-block:: pycon

      >>> suffixes = '.tar.bz2'
      >>> tmp = getfixture('tmp_path')
      >>> seq = tmp / LoosePathSequence(f'file{suffixes}.1-3#')
      >>> seq.suffixes
      ('.tar', '.bz')
      >>> seq[0].name
      'file.tar.bz2.1'
      >>> for path in seq:
      ...     path.touch()
      ...
      >>> seq.resize_from_existing_paths()[0].file_num_seqs
      (FileNumSequence(2.1),)
