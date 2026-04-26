***********************************
Converting Between Sequence Formats
***********************************

Different applications and use cases can require different formats of
sequence strings.
The page on :doc:`format` describes what PathSeq accepts as input,
and PathSeq outputs to the same format by default.
You can output a path sequence to another format by overriding the
:class:`~pathseq.Formatter` class.

Without any changes, the Formatter class will use the default formatting behaviour
to format a path sequence into a string.

.. code-block:: pycon

    >>> from pathseq import Formatter, PathSequence
    >>>
    >>> seq = PathSequence("image.1-5#.exr")
    >>> str(seq)
    'image.1-5#.exr'
    >>> Formatter().format(seq.parsed)
    'image.1-5#.exr'

To convert to another format, the methods of a Formatter can be overriden.
For example, a basic formatter for Houdini strings might look like this:

.. code-block:: pycon

    >>> class MyHoudiniFormatter(Formatter):
    ...   def range(self, range_):
    ...       return "$F"
    ...
    >>> seq = PathSequence("image.1-5#.exr")
    >>> MyHoudiniFormatter().format(seq.parsed)
    'image.$F.exr'

There is a method on the Formatter for each attribute on a parsed sequence.
So any part of a path sequence can be changed.

.. code-block:: pycon

    >>> class DemoFormatter(Formatter):
    ...     def stem(self, stem):
    ...         return "stem"
    ...     def pre_range(self, pre_range):
    ...         return "|pre_range"
    ...     def range(self, range_):
    ...         return "|range"
    ...     def inter_range(self, inter_range):
    ...         return "|inter_range"
    ...     def post_range(self, post_range):
    ...         return "|post_range"
    ...     def suffixes(self, suffixes):
    ...         return "|suffixes"
    ...
    >>> seq = PathSequence("image.1-5#.exr")
    >>> DemoFormatter().format(seq.parsed)
    'stem|pre_range|range|suffixes'

The order of the parts in a :ref:`loose <loose-format>` can even be changed
by overriding the :meth:`~pathseq.Formatter.format` or
:meth:`~pathseq.Formatter.ranges` methods.
For example, a naive formatter to convert a loose format range into
a :ref:`simple <simple-format>` might look like this:

.. code-block:: pycon

    >>> class ToSimpleFormatter(Formatter):
    ...     def format(self, seq):
    ...         return (
    ...             self.stem(seq.stem)
    ...             + self.pre_range(seq.pre_range or ".")
    ...             + self.ranges(seq.ranges)
    ...             + self.suffixes(seq.suffixes)
    ...         )
    ...
    >>> seq = LoosePathSequence("1-5#image.exr")
    >>> ToSimpleFormatter().format(seq.parsed)
    'image.1-5#.exr'
