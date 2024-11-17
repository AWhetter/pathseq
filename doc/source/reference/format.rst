Format of Sequence Strings
==========================

The name of a path sequence has three components:
the stem, the ranges, and the suffixes.

.. code-block:: text

   /directory/file.1001-1010#.tar.gz
              ^--------------------^
              |name                |
            --^--^-----------^-----^---
            |stem            |suffixes|

There are three types of sequences:

* Ranges start name: Where the ranges come before the stem and suffixes.
* Ranges in name: Where the ranges come after the stem and before the suffixes.
* Ranges end name: Where the ranges come after the stem and suffixes.

.. tip::

   Putting the frame ranges between the stem
   and the file suffixes, all separated by a ".",
   is recommended for best compatibility with VFX software.

   .. todo::

      And to make usage of stem and suffix easier (See "composition of a name").
      Maybe we should only support ranges in this particular location...

   .. code-block:: text

      file.1001-1010#.exr
      file.1001-1010#.tar.gz

   In file sequences with multi-dimension ranges,
   it is recommended to separate ranges with a "_"
   so that it is clearer that there are two ranges in the resulting file paths
   rather than a single range with subframes.

   .. code-block:: text

      # Good
      file.1011-1019<UDIM>_1-5#.tar.gz  # file.1011_1.tar.gz
      file.1011-1019<UDIM>_1-5x0.5#.#.tar.gz  # file.1011_1.5.tar.gz

      # Bad
      file.1011-1019<UDIM>.1-5#.#.tar.gz
      # In file.1011.5.tar.gz, it is unclear if there's number from two ranges (1001 and 5),
      # or a single subframes (1011.5).


Grammars
--------

Frame ranges
~~~~~~~~~~~~

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

File Sequences
~~~~~~~~~~~~~~

.. note::

   File sequences, cannot be parsed with an unambiguous context free grammar.
   The fact that strings of arbitrary characters can exist either side of the frame ranges
   means that a valid file sequence can always be parsed both as
   a list of arbitrary characters and as a set of ranges surrounded by arbitrary characters.

   Considering that it takes :math:`O(n^3)` time to parse unambiguous grammars,
   we take an informal approach to parsing file sequences.

File sequences are parsed by a two step process consisting of tokenisation
and parsing those tokens with a
`Deterministic Finite State Machine <https://en.wikipedia.org/wiki/Deterministic_finite_automaton>`_.
That state machine is as follows:

.. kroki:: format.pikchr
   :type: pikchr
   :align: left

* .. kroki::
     :type: pikchr
     :align: left
     :class: legend-image

     oval "stem" fit

  This is some text to the side maybe?
* .. kroki::
     :type: pikchr
     :align: left
     :class: legend-image

     box "prefix" fit

  This is some text to the side maybe?
* .. kroki::
     :type: pikchr
     :align: left
     :class: legend-image

     oval "range" fit

  This is some text to the side maybe?
* .. kroki::
     :type: pikchr
     :align: left
     :class: legend-image

     box "inter-range" fit

  This is some text to the side maybe?
* .. kroki::
     :type: pikchr
     :align: left
     :class: legend-image

     box "postfix" fit

  This is some text to the side maybe?
* .. kroki::
     :type: pikchr
     :align: left
     :class: legend-image

     oval "suffixes" fit

  This is some text to the side maybe?


Compatibility with VFX Software
-------------------------------

This format was chosen for its compatibility with software commonly used in
the VFX industry.


Frame Number Formats
~~~~~~~~~~~~~~~~~~~~

In pathseq, a ``#`` always represents a single digit of padding.
Subframes can also be included by adding a ``#`` for each digit after a decimal point
(eg. ``####.##`` would render frame ``1.5`` as ``0001.50``).

.. todo::

   Comment on the lack of support for sequences in directories elsewhere,
   and thus here.


Blender
^^^^^^^

Source: https://docs.blender.org/manual/en/latest/advanced/command_line/arguments.html#render-options

In output strings, ``#`` and ``@`` both represent a single digit of padding.

So Blender supports pathseq format without the need for conversion,
but paths originating from Blender may need to be passed through :func:`~pathseq.convert.from_blender`.

.. warning::

    Blender does not support subframe output.


fileseq
^^^^^^^

Source: https://fileseq.readthedocs.io/en/latest/

The convention of a ``#`` representing four digits of padding originates from
the now defunct Shake (https://web.archive.org/web/20080303091032/http://manuals.info.apple.com/en/Shake_4_Tutorials.pdf),
and possibly even earlier.

The open source file sequence library ``fileseq`` implements a mode toggle
so that it can support both this style of 4-digit padding
and a ``#`` representing a single digit of padding.
In both modes, ``fileseq`` allows mixing ``#`` with the Blender-like ``@`` symbol
to represent a single digit of padding.

.. TODO: And other range formats.


Houdini
^^^^^^^

Source: https://www.sidefx.com/docs/houdini/render/expressions.html

Houdini's allows the use of powerful expressions in file path parameters
for both reading and writing files.

* ``$Fd``, where ``d`` is an optional number of digits.
* ``$FF`` can be use to represent fractional frame numbers,
  but is not recommended due to limitations in the representation of floating point numbers.
* Plus more complex expressions.

These expressions are unique to Houdini and, unfortunately,
the format of the expressions does not overlap with the path formats of other DCCs (Digital Content Creation tools).
Therefore, use of both :func:`~pathseq.convert.from_houdini`
and :func:`~pathseq.convert.to_houdini` are required for compatibility with Houdini.


Katana
^^^^^^

Sources:

* https://learn.foundry.com/katana/Content/rg/2d_nodes/imagewrite.html
* https://learn.foundry.com/katana/Content/ug/viewing_renders/catalog_tab.html

In input and output strings, "#" is a single character of digits.


Maya
^^^^

**File texture node**:

Source: https://help.autodesk.com/view/MAYAUL/2022/ENU/?guid=GUID-309A77DA-F5ED-4474-8413-317D7AB241E6

# * Not clear...but seems to be "#" any number of digits.

.. code-block:: text

   name.#.ext
   name.ext.#
   name.#


**fcheck**:

Source: https://help.autodesk.com/view/MAYAUL/2022/ENU/?guid=GUID-6379FC90-954B-4530-AB36-998B6F1E0315

.. code-block:: text

   myimage@.ext
   myimage.@.ext
   @myimage.ext
   myimage.@
   myimage.ext.@


Nuke
^^^^

Sources:

* Read: https://learn.foundry.com/nuke/content/reference_guide/image_nodes/read.html
* Write: https://learn.foundry.com/nuke/content/reference_guide/image_nodes/write.html

# * "#" is a single character of digits.
# * "%04d" is printf-style formatting.

USD
^^^

Source: https://openusd.org/release/api/_usd__page__value_clips.html#Usd_ValueClips_Metadata

In USD Value Clips, a ``#`` represents a single character of digits.


UDIM Formats
~~~~~~~~~~~~

MaterialX Specification (v1.38)
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Source: https://materialx.org/Specification.html

The "Filename Substitutions" section of the MaterialX Specification
describes two tokens for representing UDIMs in file names.

* ``<UDIM>``: Originating from Mari, this token represents a
  four digit number that is calculated as follows:
  :math:`UDIM = 1001 + U + V * 10`.
  :math:`U` is he integer portion of the u coordinate,
  and :math:`V` is the integer portion of the v coordinate.
* ``<UVTILE>``: Originating from Mudbox, this token represents the string
  "u*U*_v*V*", where *U* is :math:`1+` the integer portion of the u coordinate,
  and *V* is :math:`1+` the integer portion of the v coordinate.

Many other DCCs support these tokens.

Arnold
^^^^^^

Source: https://help.autodesk.com/view/ARNOL/ENU/?guid=arnold_user_guide_ac_filename_tokens_ac_token_udim_html

All match MaterialX spec: https://materialx.org/Specification.html (Arnold only supports <UDIM>)

Blender
^^^^^^^

Source: https://docs.blender.org/manual/en/latest/modeling/meshes/uv/workflows/udims.html#file-substitution-tokens

All match MaterialX spec: https://materialx.org/Specification.html (Arnold only supports <UDIM>)

Houdini
^^^^^^^

Source: https://www.sidefx.com/docs/houdini/vex/functions/expand_udim.html

All match MaterialX spec: https://materialx.org/Specification.html (Arnold only supports <UDIM>)

Houdini additionally uses:
* ``%(UDIM)d``: Same as <UDIM> but with user specified padding
* ``%(U)d``: The UVTILE style u-coordinate (int(u)+1), with user specified padding
* ``%(V)d``: The UVTILE style v-coordinate (int(v)+1), with user specified padding
* ``%(UVTILE)d``: Same as <UVTILE> but with user specified padding

Mari
^^^^

Source: https://learn.foundry.com/mari/Content/tutorials/tutorial_5/tutorial_exporting_importing.html

All match MaterialX spec: https://materialx.org/Specification.html (Arnold only supports <UDIM>)

Maya
^^^^

Source: https://help.autodesk.com/view/MAYAUL/2022/ENU/?guid=GUID-309A77DA-F5ED-4474-8413-317D7AB241E6

All match MaterialX spec: https://materialx.org/Specification.html (Arnold only supports <UDIM>)

# Maya additionally uses:
# * u<u>_v<v>: Zero indexed UV tile style u and v coordinate

Mudbox
^^^^^^

.. TODO


USD
^^^

Source: https://openusd.org/docs/UsdPreviewSurface-Proposal.html#UsdPreviewSurfaceProposal-TextureReader

All match MaterialX spec: https://materialx.org/Specification.html (Arnold only supports <UDIM>)


ZBrush
^^^^^^

.. TODO
