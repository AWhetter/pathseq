from __future__ import annotations

from collections.abc import Iterable, Iterator, Sequence
import decimal
import itertools
from typing import Generic, overload, Self

from typing_extensions import (
    TypeGuard,  # PY310
)

from ._arithmetic_sequence import ArithmeticSequence
from ._ast import FileNumT
from ._parse_file_num_seq import parse_file_num_seq


class FileNumSequenceIterator(Generic[FileNumT]):
    def __init__(self, ranges: tuple[ArithmeticSequence[FileNumT], ...]):
        self._ranges_iter: Iterator[ArithmeticSequence[FileNumT]] = iter(ranges)
        self._range_iter: Iterator[FileNumT] = iter(())

    def __iter__(self) -> Self:
        return self

    def __next__(self) -> FileNumT:
        try:
            return next(self._range_iter)
        except StopIteration:
            range_ = next(self._ranges_iter)
            self._range_iter = iter(range_)
            return next(self._range_iter)


def _seqs_from_nums(
    numbers: Iterable[FileNumT],
) -> Iterable[ArithmeticSequence[FileNumT]]:
    if not numbers:
        return []

    numbers = iter(numbers)
    seqs = []
    start = next(numbers)
    previous = start
    step = None

    for current in numbers:
        if current == previous:
            continue

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

    return [ArithmeticSequence(*seq) for seq in seqs]


def _consolidate_ranges(
    ranges: Iterable[ArithmeticSequence[FileNumT]],
) -> tuple[ArithmeticSequence[FileNumT], ...]:
    filtered = (r for r in ranges if len(r))
    try:
        new_ranges = [next(filtered)]
    except StopIteration:
        return ()

    for range_b in filtered:
        range_a = new_ranges[-1]
        difference = range_b.start - range_a.end
        if difference == range_a.step:
            # Can we merge this entire range into the previous range?
            if range_a.step == range_b.step:
                new_ranges[-1] = range_a.__class__(
                    range_a.start, range_b.end, range_a.step
                )
                continue

            # Otherwise we can move at most one item to the previous range
            # without changing the order of file numbers.
            new_ranges[-1] = range_a.__class__(
                range_a.start, range_b.start, range_a.step
            )
            range_b = range_b.__class__(
                range_b.start + range_b.step, range_b.end, range_b.step
            )
            if not range_b:
                continue
        # Consolidate neighbouring numbers into a range in the hope that
        # another lone number is next and can be consolidated into the range as well.
        elif len(range_a) == 1 and len(range_b) == 1:
            new_ranges[-1] = range_a.__class__(range_a.start, range_b.start, difference)
            continue

        new_ranges.append(range_b)

    return tuple(new_ranges)


class FileNumSequence(Sequence[FileNumT]):
    def __init__(self, ranges: Iterable[ArithmeticSequence[FileNumT]]) -> None:
        self._ranges: tuple[ArithmeticSequence[FileNumT], ...] = _consolidate_ranges(
            ranges
        )

    @classmethod
    def from_str(
        cls, seq: str
    ) -> FileNumSequence[int] | FileNumSequence[decimal.Decimal]:
        """Parse a range string in a file number sequence.

        Args:
            seq_str: The range string to parse (eg '1001-1005,1010-1015').

        Returns:
            The resulting file number sequence.
        """
        return cls(parse_file_num_seq(seq))  # type: ignore[arg-type]

    @classmethod
    def from_file_nums(cls, file_nums: Iterable[FileNumT]) -> FileNumSequence[FileNumT]:
        """Create a file number sequence from an iterable of file numbers.

        The given numbers are put into the sequence in the order they are given.

        Args:
            file_nums: The file numbers to turn into a sequence.

        Returns:
            The resulting file number sequence.
        """
        return cls(_seqs_from_nums(file_nums))

    def __contains__(self, item: object) -> bool:
        """Return True if the given item is a file number in this sequence."""
        if not self._ranges:
            return False

        return any(item in rng for rng in self._ranges)

    def __iter__(self) -> Iterator[FileNumT]:
        """Iterate over the file numbers in the sequence.

        Yields:
            Each file number in the sequence.
        """
        return FileNumSequenceIterator(self._ranges)

    def __len__(self) -> int:
        """Get the number of file numbers in this sequence."""
        return sum(len(rng) for rng in self._ranges)

    def __eq__(self, other: object) -> bool:
        """Check for equality with another object.

        File number sequences are considered equal when they contain
        the same items in the same order.
        """
        if not isinstance(other, FileNumSequence):
            return NotImplemented

        return self._ranges == other._ranges

    def __hash__(self) -> int:
        return hash((type(self), self._ranges))

    @overload
    def __getitem__(self, index: int) -> FileNumT: ...

    @overload
    def __getitem__(self, index: slice) -> Sequence[FileNumT]: ...

    def __getitem__(self, index: int | slice) -> FileNumT | Sequence[FileNumT]:
        if isinstance(index, slice):
            return tuple(itertools.islice(self, *index.indices(len(self))))

        for rng in self._ranges:
            range_len = len(rng)
            if index < range_len:
                return rng[index]
            index -= range_len
        else:
            raise IndexError(index)

    def __str__(self) -> str:
        return ",".join(str(rng) for rng in self._ranges)

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}({self})"

    @staticmethod
    def has_subsamples(
        file_num_seq: FileNumSequence[int] | FileNumSequence[decimal.Decimal],
    ) -> TypeGuard[FileNumSequence[decimal.Decimal]]:
        """Check whether this file number sequence contains any decimal numbers."""
        if not file_num_seq:
            return False

        return isinstance(next(iter(file_num_seq)), decimal.Decimal)
