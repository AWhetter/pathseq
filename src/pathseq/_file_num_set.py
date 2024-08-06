from __future__ import annotations

from collections.abc import Iterable, Set
import decimal
import re
from typing import overload, Self, TypeVar

import lark
from typing_extensions import (
    TypeGuard,  # PY310
)

from ._decimal_range import DecimalRange

T = TypeVar("T", int, decimal.Decimal)


# TODO: Maybe we can delete these.
FILE_NUM_RE = re.compile(r"-?\d+(?:\.\d+)?")
RANGE_RE = re.compile(
    r"""
    (-?\d+(?:\.\d+)?)
    (?:                       # optional range
        -                     #   range delimiter
        (-?\d+(?:\.\d+)?)     #   end frame
        (?:                   #   optional stepping
            x                 #     step type
            (\d+(?:\.\d+)?)   #     step value
        )?
    )?
""", re.VERBOSE)

GRAMMAR = r"""
    start: ranges

    ranges: range ("," range)*

    range: FILE_NUM ["-" FILE_NUM ["x" NUM]]

    FILE_NUM: "-"? NUM
    NUM: /
        (0|[1-9][0-9]*)       # the digits
        (\.0|\.[0-9]*[1-9])?  # the subsamples
    /x
"""

@lark.v_args(inline=True)
class SequenceReducer(lark.Transformer):
    def start(self, seq):
        return seq

    def ranges(self, ranges):
        return ranges

    def range(self, start, end, step):
        args = (
            start,
            end or start,
            step or "1",
        )
        type_ = int
        if any("." in arg for arg in args):
            type_ = decimal.Decimal

        return _ArithmeticSequence(*(type_(arg) for arg in args))


_PARSER = lark.Lark(GRAMMAR, parser="lalr", transformer=SequenceReducer())


class _ArithmeticSequence(Set[T]):
    def __init__(self, start: T, end: T | None = None, step: T | None = None) -> None:
        end = end if end is not None else start
        step = step if step is not None else start.__class__(1)

        # Normalise to a positive step value
        if step < 0:
            start, end = (end, start)
            step = -step

        # We treat the end as inclusive, ranges don't.
        stop: T
        if start < end:
            remainder = divmod(end - start, step)
            stop = end + remainder
            # Normalise the end value to match the step
            end -= remainder
        elif start == end:
            stop = end + step
        else:
            stop = end

        if isinstance(start, int):
            self._range = range(start, stop, step)
        else:
            self._range = DecimalRange(start, stop, step)

        self._end = end

    @property
    def start(self) -> T:
        return self._range.start

    @property
    def end(self) -> T:
        return self._end

    @property
    def step(self) -> T:
        return self._step

    def __contains__(self, item: T) -> bool:
        return item in self._range

    def __iter__(self) -> Iterable[T]:
        return iter(self._range)

    def __len__(self) -> int:
        return len(self._range)

    def __str__(self) -> str:
        if len(self) == 1:
            return str(self.start)

        result = f"{self.start}-{self.end}"
        if self.step != 1:
            result += f"x{self.step}"
        elif len(self) == 2:
            return ",".join(self)

        return result


# TODO: Do something smarter (eg for overlapping sequences, or even logarithmic sequences)
# [1,2,11,12,21,22,31,32] -> [1-31x10,2-32x10]
def _seqs_from_nums(numbers: Iterable[T]) -> Iterable[_ArithmeticSequence[T]]:
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
            seqs.append(_ArithmeticSequence(start, previous, step))
            start = current
            step = None

        previous = current

    # Handle the last range
    if step is not None:
        seqs.append(_ArithmeticSequence(start, previous, step))

    return seqs


class FileNumSet(Set[T]):
    # TODO: For now, only accept arithmetic sequences
    # TODO: Order and consolidate the ranges
    def __init__(self, ranges: Iterable[_ArithmeticSequence[T]]) -> None:
        self._ranges = tuple(ranges)

    @classmethod
    def from_str(cls, set_str: str) -> Self:
        ranges = _PARSER.parse(set_str)
        return cls(ranges)

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
        raise NotImplemented

    def __str__(self) -> str:
        return ",".join(str(rng) for rng in self._ranges if rng)

    @staticmethod
    def has_subsamples(file_num_set: FileNumSet[T]) -> TypeGuard[FileNumSet[decimal.Decimal]]:
        if not file_num_set:
            return False

        return isinstance(next(iter(file_num_set)), decimal.Decimal)