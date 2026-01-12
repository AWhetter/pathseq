from __future__ import annotations

from collections.abc import Iterable
import dataclasses
from decimal import Decimal
import typing

if typing.TYPE_CHECKING:
    from ._loose_type import ParsedLooseSequence
    from ._ranges import PaddedRange, Ranges
    from ._type import ParsedSequence


def _splice_strings_onto_ranges(
    strings: Iterable[str], inter_ranges: Iterable[str]
) -> str:
    """Format the given range strings and inter-range strings together.

    Raises:
        TypeError: If the given number of strings does not match
            the number of inter-range strings minus one.
    """
    result = ""

    strs = iter(strings)
    for inter_range in inter_ranges:
        try:
            result += next(strs)
        except StopIteration:
            break

        result += inter_range
    else:
        try:
            result += next(strs)
        except StopIteration:
            pass
        else:
            try:
                next(strs)
            except StopIteration:
                return result

    raise TypeError(
        "The number of inter-range strings given does not match"
        " the number of range strings given minus one."
    )


class Formatter:
    """A :class:`Formatter` formats a parsed sequence into a string.

    The purpose of the class is primarily for converting from a
    :ref:`simple <simple-format>` or :ref:`loose <loose-format>` sequence
    into other sequence formats by overriding this class.

    Example:

        .. code-block:: pycon

            >>> class HoudiniFormatter(pathseq.Formatter):
            ...   def range(self, range_):
            ...       return "$F"
            ...
            >>> seq = pathseq.PathSequence("image.1-5#.exr")
            >>> HoudiniFormatter().format(seq.parsed)
            'image.$F.exr'
    """

    def stem(self, stem: str) -> str:
        return stem

    def prefix(self, prefix: str) -> str:
        return prefix

    def range(self, range_: PaddedRange[int] | PaddedRange[Decimal]) -> str:
        return str(range_)

    def inter_range(self, inter_range: str) -> str:
        return inter_range

    def ranges(self, ranges: Ranges) -> str:
        return self.splice_inter_ranges(
            (self.range(range_) for range_ in ranges.ranges),
            (self.inter_range(inter_range) for inter_range in ranges.inter_ranges),
        )

    def postfix(self, postfix: str) -> str:
        return postfix

    def suffixes(self, suffixes: tuple[str, ...]) -> str:
        return "".join(suffixes)

    def format(self, seq: ParsedSequence | ParsedLooseSequence) -> str:
        """Format the given path sequence into a string.

        The parsed sequence is traversed, and each node is formatted
        according to the implementation of the associated method on this class.

        Args:
            seq: The path sequence to format into a string.

        Returns:
            The formatter path sequence.
        """
        return "".join(
            getattr(self, field.name)(getattr(seq, field.name))
            for field in dataclasses.fields(seq)
        )

    def splice_inter_ranges(
        self, strings: Iterable[str], inter_ranges: Iterable[str]
    ) -> str:
        """Format the given range strings and inter-range strings together.

        Raises:
            TypeError: If the given number of strings does not match
                the number of inter-range strings minus one.
        """
        return _splice_strings_onto_ranges(strings, inter_ranges)
