from __future__ import annotations

from collections.abc import Iterable, Sequence, Set
import decimal
from typing import overload, Self

from typing_extensions import (
    TypeGuard,  # PY310
)

from ._arithmetic_sequence import ArithmeticSequence, FileNumT
from ._parse_file_num_set import parse_file_num_set


@overload
def _seqs_from_nums(
    numbers: Iterable[int | decimal.Decimal],
) -> Iterable[ArithmeticSequence[decimal.Decimal]]: ...


@overload
def _seqs_from_nums(numbers: Iterable[int]) -> Iterable[ArithmeticSequence[int]]: ...


def _seqs_from_nums(numbers):
    numbers = sorted(set(numbers))
    if not numbers:
        return []

    seqs = []
    start = numbers[0]
    previous = numbers[0]
    step = None

    for current in numbers[1:]:
        current_step = current - previous

        if step is None:
            step = current_step

        if current_step == 1:
            # Continue contiguous range
            pass
        elif step == current_step:
            # Continue stepped range
            pass
        else:
            # Close off the current range
            seqs.append((start, previous, step))
            start = current
            step = None

        previous = current

    # Handle the last range
    if step is not None:
        seqs.append((start, previous, step))

    if any(isinstance(x, decimal.Decimal) for x in numbers):
        seqs = [
            ArithmeticSequence(
                decimal.Decimal(start),
                decimal.Decimal(stop),
                decimal.Decimal(step) if step is not None else None,
            )
            for (start, stop, step) in seqs
        ]
    else:
        seqs = [ArithmeticSequence(*seq) for seq in seqs]

    return seqs


# TODO: Are there other inherited methods that we could override for speed?
class FileNumSet(Set[FileNumT], Sequence[FileNumT]):
    # TODO: For now, only accept arithmetic sequences
    # TODO: Order and consolidate the ranges
    def __init__(self, ranges: Iterable[ArithmeticSequence[FileNumT]]) -> None:
        self._ranges: tuple[ArithmeticSequence[FileNumT]] = tuple(ranges)

    @classmethod
    def from_str(cls, set_str: str) -> Self:
        """Parse a range string in a file number set.

        Args:
            set_str: The range string to parse (eg '1001-1005,1010-1015').

        Returns:
            The resulting file number set.
        """
        return cls(parse_file_num_set(set_str))

    @overload
    @classmethod
    def from_file_nums(
        cls, file_nums: Iterable[int | decimal.Decimal]
    ) -> FileNumSet[decimal.Decimal]: ...

    @overload
    @classmethod
    def from_file_nums(cls, file_nums: Iterable[int]) -> FileNumSet[int]: ...

    @classmethod
    def from_file_nums(cls, file_nums):
        """Create a file number set from an iterable from file numbers.

        The given numbers are deduplicated and sorted before being put into a set.

        Args:
            file_nums: The file numbers to turn into a set.

        Returns:
            The resulting file number set.
        """
        return cls(_seqs_from_nums(file_nums))

    def __contains__(self, item: object) -> bool:
        """Return True if the given item is a file number in this set."""
        if not self._ranges:
            return False

        return any(item in rng for rng in self._ranges)

    def __iter__(self) -> Iterable[FileNumT]:
        """Iterate over the file numbers in the set.

        Yields:
            Each file number in the set.
        """
        # TODO: What about overlapping ranges?
        for rng in self._ranges:
            yield from rng

    def __len__(self) -> int:
        """Get the number of file numbers in this set."""
        return sum(len(rng) for rng in self._ranges)

    def __eq__(self, other) -> bool:
        """Check for equality with another object.

        File number sets are considered equal when they contain
        the same items in the same order.
        """
        # TODO: Do we want to be equal to other sets and/or sequences?
        if not isinstance(other, FileNumSet):
            return NotImplemented

        # TODO: Implement range normalisation so that we don't need to iterate over everything
        # return str(self) == str(other)
        try:
            return all(r1 == r2 for r1, r2 in zip(self, other, strict=True))
        except ValueError:
            return False

    def __hash__(self) -> int:
        return hash((type(self), self._ranges))

    @overload
    def __getitem__(self, index: int) -> FileNumT: ...

    @overload
    def __getitem__(self, index: slice) -> Self: ...

    def __getitem__(self, index):
        if isinstance(index, int):
            for rng in self._ranges:
                if index < len(rng):
                    return rng[index]
            else:
                raise IndexError(index)

        raise NotImplementedError

    def __str__(self) -> str:
        ranges = [str(rng) for rng in self._ranges if rng]
        return ",".join(ranges)

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}({self})"

    @staticmethod
    def has_subsamples(
        file_num_set: FileNumSet[FileNumT],
    ) -> TypeGuard[FileNumSet[decimal.Decimal]]:
        """Check whether this file number set contains any decimal numbers."""
        if not file_num_set:
            return False

        return isinstance(next(iter(file_num_set)), decimal.Decimal)
