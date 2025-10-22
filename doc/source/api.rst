API Reference
=============

.. automodule:: pathseq

   Path sequence classes come in two variations depending on the format
   of sequence string they support:
   :ref:`simple <simple-format>`, which prioritises simplicity to guarantee behaviour;
   or :ref:`loose <loose-format>`, which prioritises compatibility with the most file names. 
   Both variations share common base classes.

   .. figure:: /_static/inheritance.svg
      :figclass: solid-background
      :width: 90%

   If you aren't sure with variation is right for you,
   choose :ref:`simple <simple-format>` if you have control over the format of
   sequence strings that you support,
   and choose :ref:`loose <loose-format>` if you don't.

   Like :mod:`pathlib`, both variants come in a `pure <Pure Path Sequences>`_
   and `concrete <Concrete Path Sequences>`_ form.
   Pure path sequences contain :class:`pathlib.PurePath` objects,
   and concrete path sequences contain :class:`pathlib.Path` objects.


   Pure Path Sequences
   -------------------

   .. autotypevar:: PurePathT_co

   .. autoclass:: BasePurePathSequence
      :show-inheritance:
      :members:


   Concrete Path Sequences
   -----------------------

   .. autotypevar:: PathT_co

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

   .. autotypevar:: FileNumT

   .. autoclass:: FileNumSequence()
      :show-inheritance:
      :members:
