.. _adr-003:

[ADR-003] ``PathSequence`` inherits from ``Set``
================================================

:bdg-danger:`Rejected`

Context and Problem Statement
-----------------------------

This proposal is to change the class signature of ``PurePathSequence`` to change from
``PurePathSequence(Sequence[PathT_co])``
to ``PurePathSequence(Sequence[PathT_co], Set[PathT_co])``.

In this proposal we consider the following use cases:

* 10,000 files in a sequence is considered normal, if rare.
  5,000 files is a more common use case.
* Most of the time, a sequence will have been output by a DCC representing files
  in order, due to those files getting rendered in order.
  The sequence string is likely then stored somewhere as-is, and passed to
  pathseq in the same order. In other words, it's considered uncommon
  for the ranges in a range string to be given out of order.
* Path sequences are most commonly used for looping over all paths in the sequence,
  or establishing which files in the sequence exist.
  Neither requires set operations, although we already deduplicate and sort
  the file numbers when establishing which exist on disk.

We have no use case where the order of file numbers matters.

Currently, equality checks benefit from a very basic form of normalisation:

.. code-block:: pycon

    >>> from pathseq import PathSequence
    >>> seq1 = PathSequence("/path/to/images.1-2####.exr")
    >>> seq2 = PathSequence("/path/to/images.1,2####.exr")
    >>> seq1 == seq2
    True

By turning path sequences into a set, more complex forms of normalisation
will allow two sequences with the same file number sets to also compare as equal.
For example:

.. code-block:: pycon

    >>> from pathseq import PathSequence
    >>> seq1 = PathSequence("/path/to/images.1-2,2-4####.exr")
    >>> seq2 = PathSequence("/path/to/images.1-4####.exr")
    >>> seq1 == seq2
    True

Considered Options
------------------

Normalisation
~~~~~~~~~~~~~

Give that we have no use case where the order of file numbers matters,
the complex deduplication of file numbers could be implemented in one of two ways:
with sorting or without sorting.

With sorting would require the arithmetic sequences given to a file number set
to be sorted, before being split such that they don't overlap.
Given the use cases, most of the time the sorting will take :math:`n` time
if we're using a :math:`\Omega(n)` time sort algorithm.
Detecting whether two sequences overlap is simple --
though does require in depth mathemtical concepts -- for integers,
but is more involved for decimals (see Appendix A).
If maintaining this complex code ever becomes a problem,
we would always resort to looping over every item in the sequences.

Without sorting a naive implementation would iterate over every item in the given sequences,
and place them into an ordered set to deduplicate them in :math:`O(n)` time
with :math:`O(n)` memory.
This favours the unusual case, where file numbers are given unordered
because it takes :math:`O(n)` time instead of :math:`O(n\log n)` time,
but at the cost of much more computation in the more common case
where file numers are already ordered.

Sorting would violate the concept of a sequence being ordered,
and therefore normalisation via not sorting is considered superior.

Decision Outcome
----------------

We will not turn PathSequences into sets.
The performance cost and maintenance complexity introduced
does not give rise to enough justified functionality.

Consequences
------------

* The option to do more complex normalisation remains open.
  A subclass of ``PurePathSequence`` or a method on a ``PurePathSequence``
  could perform more complex normalisation as something that the user opts into.
* If use cases for set operations come to light,
  it would still possible to provide set operations without introducing breaking changes,
  by providing ``PurePathSet`` and/or ``OrderedPurePathSet`` classes,
  plus impure and loose equivalents.

Appendix A
----------

Code to check if two arithmetic sequences are disjoint,
implemented as methods on ``ArithmeticSequence``.

.. code-block:: python

    def isdisjoint(self, other: Iterable[Any]) -> bool:
        if isinstance(other, ArithmeticSequence):
            return self._quick_isdisjoint(other)

        # Resort to a slow check
        return super().isdisjoint(other)

    def _quick_isdisjoint(self, other: Self) -> bool:
        # Shortcut
        if self.start > other.end or other.start < self.end:
            return True

        # For
        # a_n = a_1 + d_1(n-1)
        # b_m = b_1 + d_2(m-1)
        a = self
        b = other
        a1 = a.start
        b1 = b.start
        d1 = a.step
        d2 = b.step
        # the following condition must be met:
        # a_1 + d_1(n-1) = b_1 + d_2(m-1)
        # d_1 * n - d_2 * m = b_1 - a_1

        # Calculate the difference between the first terms
        difference = b1 - a1

        # Convert differences to integers for GCD calculation
        d1_int = int(d1) if d1 % 1 == 0 else None
        d2_int = int(d2) if d2 % 1 == 0 else None

        # Check if the GCD of the common differences divides the difference
        if d1_int is not None and d2_int is not None:
            gcd = math.gcd(d1_int, d2_int)
            if gcd == 0:
                return True
            if difference % gcd != 0:
                return True
        else:
            # Handle the case where differences are not integers
            # Convert the equation to integer coefficients
            assert isinstance(d1, decimal.Decimal)
            assert isinstance(d2, decimal.Decimal)
            a_exp = remove_exponent(d1).as_tuple().exponent
            assert isinstance(a_exp, int)
            b_exp = remove_exponent(d2).as_tuple().exponent
            assert isinstance(b_exp, int)
            scale_factor = 10 ** max(a_exp, b_exp)
            d1_scaled = int(d1 * scale_factor)
            d2_scaled = int(d2 * scale_factor)
            difference_scaled = int(difference * scale_factor)

            # Calculate the GCD of the scaled differences
            gcd_scaled = math.gcd(d1_scaled, d2_scaled)
            if gcd_scaled == 0:
                return True

            # Check if the scaled difference is divisible by the scaled GCD
            if difference_scaled % gcd_scaled != 0:
                return True

            # Find the smallest common term
            common_term_scaled = (
                a1 * scale_factor + (difference_scaled // gcd_scaled) * d1_scaled
            )
            common_term = decimal.Decimal(common_term_scaled) / decimal.Decimal(
                scale_factor
            )

            # Check if the common term is within the bounds of both sequences
            if common_term <= a.end and common_term <= b.end:
                return False

        return True
