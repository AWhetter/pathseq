***********************************
Converting Between Sequence Formats
***********************************

Different applications and use cases can require different formats of
sequence strings.
PathSeq supports converting a path sequence to other formats by overriding the
:class:`~pathseq.Formatter` class.

Without any changes, the Formatter class will format
a path sequence into a string without any changes.

.. code-block:: pycon

    >>> seq = PathSequence("image.1-5#.exr")
    >>> pathseq.Formatter().format(seq.parsed)
    'image.1-5#.exr'

To convert to another format, the methods of a Formatter can be overriden.
For example, a basic formatter for Houdini strings might look like this:

.. code-block:: pycon

    >>> class HoudiniFormatter(pathseq.Formatter):
    ...   def range(self, range_):
    ...       return "$F"
    ...
    >>> seq = PathSequence("image.1-5#.exr")
    >>> HoudiniFormatter().format(seq.parsed)
    'image.$F.exr'

There is a method on the Formatter for each attribute on a parsed sequence.
So any part of a path sequence can be changed.

.. code-block:: pycon

    >>> class DemoFormatter(pathseq.Formatter):
    ...     def stem(self, stem):
    ...         return "stem"
    ...     def prefix(self, prefix):
    ...         return "|prefix"
    ...     def range(self, range_):
    ...         return "|range"
    ...     def inter_range(self, inter_range):
    ...         return "|inter_range"
    ...     def postfix(self, postfix):
    ...         return "|postfix"
    ...     def suffixes(self, suffixes):
    ...         return "|suffixes"
    ...
    >>> seq = PathSequence("image.1-5#.exr")
    >>> DemoFormatter().format(seq.parsed)
    'stem|prefix|range|suffixes'

The order of the parts in a :ref:`loose <loose-format>` can even be changed
by overriding the :meth:`~pathseq.Formatter.format` or
:meth:`~pathseq.Formatter.ranges` methods.
For example, a naive formatter to convert a loose format range into
a :ref:`simple <simple-format>` might look like this:

.. code-block:: pycon

    >>> class ToSimpleFormatter(pathseq.Formatter):
    ...     def format(self, seq):
    ...         return (
    ...             self.stem(seq.stem)
    ...             + self.prefix(seq.prefix or ".")
    ...             + self.ranges(seq.ranges)
    ...             + self.suffixes(seq.suffixes)
    ...         )
    ...
    >>> seq = LoosePathSequence("1-5#image.exr")
    >>> ToSimpleFormatter().format(seq.parsed)
    'image.1-5#.exr'
