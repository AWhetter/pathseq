API Reference
=============

.. automodule:: pathseq

   Path sequence classes come in two variations depending on the format
   of sequence string they support:
   :ref:`simple <simple-format>`, which prioritises simplicity to guarantee behaviour;
   or :ref:`loose <loose-format>`, which prioritises compatibility with more file names. 
   Both variations share common base classes.

   .. figure:: /_static/inheritance.svg
      :figclass: solid-background
      :width: 90%

   If you aren't sure which variation is right for you,
   choose :ref:`simple <simple-format>` if you have control over the format of
   sequence strings that you support,
   and choose :ref:`loose <loose-format>` if you don't.

   The simple and loose variants both come in a `pure <Pure Path Sequences>`_
   and `concrete <Concrete Path Sequences>`_ form, similar to the classes in :mod:`pathlib`.
   Pure path sequences contain :class:`pathlib.PurePath` objects,
   and concrete path sequences contain :class:`pathlib.Path` objects.


   Pure Path Sequences
   -------------------

   .. py:data:: PurePathT_co
      :value: TypeVar(PurePathT_co, bound=pathlib.PurePath, covariant=True)
      :canonical: pathseq._base.PurePathT_co

      The type of pure paths contained in a :class:`~.BasePurePathSequence`.

   .. autoclass:: BasePurePathSequence
      :show-inheritance:
      :members:


   Concrete Path Sequences
   -----------------------

   .. py:data:: PathT_co
      :value: TypeVar(PathT_co, bound=pathlib.Path, covariant=True)
      :canonical: pathseq._base.PathT_co

      The type of concrete paths contained in a :class:`~.BasePathSequence`.

   .. autoclass:: BasePathSequence
      :show-inheritance:
      :members:

   Simple Path Sequences
   ---------------------

   .. autoclass:: PurePathSequence
      :show-inheritance:
      :members:
      :exclude-members: with_file_num_seqs

   .. autoclass:: PathSequence
      :show-inheritance:
      :members:

   Loose Path Sequences
   --------------------

   .. autoclass:: LoosePurePathSequence
      :show-inheritance:
      :members:
      :exclude-members: with_file_num_seqs

   .. autoclass:: LoosePathSequence
      :show-inheritance:
      :members:

   Exceptions
   ----------

   .. autoexception:: IncompleteDimensionError
      :show-inheritance:
      :members:

   .. autoexception:: NotASequenceError
      :show-inheritance:
      :members:

   .. autoexception:: ParseError
      :show-inheritance:
      :members:

   File Number Sequences
   ---------------------

   .. py:data:: FileNumT
      :type: typing.TypeVar
      :value: TypeVar(FileNumT, int, decimal.Decimal)
      :canonical: pathseq._ast._base.FileNumT

      The type of file numbers in a :class:`~.FileNumSequence`.

   .. autoclass:: FileNumSequence()
      :show-inheritance:
      :members:

   Parsed Path Sequences
   ---------------------

   These classes represent a parsed path sequence in a tree structure.
   Access to a parsed sequence can be useful for renaming sequences or
   converting sequence strings between different formats.

   .. seealso::

      See :doc:`format` for the specification of what is valid in each part
      of a sequence.

   .. autoclass:: ParsedSequence
      :members:

   .. py:data:: ParsedLooseSequence
      :value: pathseq.RangesStartName | pathseq.RangesInName | pathseq.RangesEndName

   .. autoclass:: RangesStartName
      :members:

   .. autoclass:: RangesInName
      :members:

   .. autoclass:: RangesEndName
      :members:

   .. autoclass:: PaddedRange
      :members:

   .. autoclass:: Ranges
      :members:
