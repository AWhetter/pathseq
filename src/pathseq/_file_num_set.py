from __future__ import annotations

from collections.abc import Iterable, Set
import decimal
from typing import overload, Self

from typing_extensions import (
    TypeGuard,  # PY310
)

from ._arithmetic_sequence import ArithmeticSequence, T
from ._parse_file_num_set import parse_file_num_set


# TODO: Do something smarter (eg for overlapping sequences, or even logarithmic sequences)
# [1,2,11,12,21,22,31,32] -> [1-31x10,2-32x10]
def _seqs_from_nums(numbers: Iterable[T]) -> Iterable[ArithmeticSequence[T]]:
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
            seqs.append(ArithmeticSequence(start, previous, step))
            start = current
            step = None

        previous = current

    # Handle the last range
    if step is not None:
        seqs.append(ArithmeticSequence(start, previous, step))

    return seqs


class FileNumSet(Set[T]):
    # TODO: For now, only accept arithmetic sequences
    # TODO: Order and consolidate the ranges
    def __init__(self, ranges: Iterable[ArithmeticSequence[T]]) -> None:
        self._ranges = tuple(ranges)

    @classmethod
    def from_str(cls, set_str: str) -> Self:
        return cls(parse_file_num_set(set_str))

    @classmethod
    def from_file_nums(cls, file_nums: Iterable[T]) -> Self:
        return cls(_seqs_from_nums(file_nums))

    def __contains__(self, item: object) -> bool:
        if not self._ranges:
            return False

        return any(item in rng for rng in self._ranges)

    def __iter__(self) -> Iterable[T]:
        # TODO: What about overlapping ranges?
        for rng in self._ranges:
            yield from rng

    def __len__(self) -> int:
        return sum(len(rng) for rng in self._ranges)

    def __eq__(self, other) -> bool:
        # TODO: Do we want to be equal to other sets and/or sequences?
        if not isinstance(other, FileNumSet):
            return NotImplemented

        return (
            len(self._ranges) == len(other._ranges)
            and all(r1 == r2 for r1, r2 in zip(self._ranges, other._ranges))
        )

    # TODO: Are there other inherited methods that we could override for speed?

    # TODO: Should we also inherit from Sequence or similar?
    @overload
    def __getitem__(self, index: int) -> T:
        ...

    @overload
    def __getitem__(self, index: slice) -> Self:
        ...

    def __getitem__(self, index):
        raise NotImplementedError

    def __str__(self) -> str:
        ranges = [str(rng) for rng in self._ranges if rng]
        return ",".join(ranges)

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}({self})"

    @staticmethod
    def has_subsamples(file_num_set: FileNumSet[T]) -> TypeGuard[FileNumSet[decimal.Decimal]]:
        if not file_num_set:
            return False

        return isinstance(next(iter(file_num_set)), decimal.Decimal)