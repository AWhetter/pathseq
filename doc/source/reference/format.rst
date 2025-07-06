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

.. code-block:: text

   /directory/file.1-5#.tar.gz
              ^--------------^
              |     name     |

A sequence's name represents the file names of all files in the sequence.
The name has four components:

* The stem
* An optional prefix
* The ranges
* The suffixes

.. figure:: /_static/name_breakdown.svg
   :class: solid-background

.. tip::

   Including a prefix as ``.`` is recommended for best compatibility with VFX software.

   .. code-block:: text

      file.1001-1010#.exr
      file.1001-1010#.tar.gz

Multiple ranges are separated by an inter-range separator.

.. figure:: /_static/multi_range_breakdown.svg
   :class: solid-background

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
      file.1011-1019<UDIM>.1-5#.#.tar.gz
      # In file.1011.5.tar.gz, it is unclear if there's numbers from two ranges (1001 and 5),
      # or a single subframes (1011.5).


Specification
~~~~~~~~~~~~~

File sequences are parsed by a two step process consisting of tokenisation
and parsing those tokens with a
`Deterministic Finite State Machine <https://en.wikipedia.org/wiki/Deterministic_finite_automaton>`_.
That state machine is as follows:

.. figure:: /_static/format.svg
   :class: solid-background

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


Frame Ranges
------------

TODO: Explain padding options

Grammar
~~~~~~~~

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


.. list-table::
   :header-rows: 1

   * - Software
     - Compatible
     - Notes
   * -
     -
     -

Loose Format
------------

The PathSeq API has the concept of a "loose" format.
Whereas the normal sequence string format maximises simplicity,
the loose format trades simplicity for
compatibility in parsing sequence strings from unknown sources.

The loose format is a flexible format that
can parse the most sequence strings,
but those strings may only work for one DCC.
This format can be useful when there isn't a guarantee that the
sequence string to be parsed is in the simple format.

In `Path Sequences`_ we saw that in the strict format,
a sequence's name has four components.
The loose format has an additional component, the postfix.

TODO: name_breakdown.svg but with the additional component

Specification
~~~~~~~~~~~~~

TODO: Talk about the three types (ranges before, in, after).

.. warning::

   The fact that strings of arbitrary characters can exist either side of the frame ranges
   means that a valid file sequence can always be parsed both as
   a list of arbitrary characters and as a set of ranges surrounded by arbitrary characters.

   Therefore the loose format can only make a best guess at how to interpret a 

.. figure:: /_static/adrs/all_formats.svg
   :class: solid-background
