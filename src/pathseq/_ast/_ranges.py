from __future__ import annotations

from dataclasses import dataclass
import decimal
from typing import Generic, TypeGuard

from ._formatter import Formatter
from ._util import pad
from .._file_num_seq import FileNumSequence, FileNumT


@dataclass(frozen=True)
class PaddedRange(Generic[FileNumT]):
    file_nums: FileNumSequence[FileNumT]
    """The file numbers of each file in the sequence."""
    pad_format: str
    """The definition of how a file number is formatted in each file's name in the sequence."""

    def __str__(self) -> str:
        return str(self.file_nums) + self.pad_format

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}({self})"

    def format(self, number: int | decimal.Decimal) -> str:
        """Format the given number using the range's padding rules."""
        if self.pad_format == "<UVTILE>":
            # udim = 1000+(v*10)+(u+1)
            u = (number - 1) % 10
            v = (number - 1000 - u - 1) // 10
            return f"u{u + 1}_v{v + 1}"

        pad_format = self.pad_format
        if self.pad_format == "<UDIM>":
            pad_format = "####"

        if "." in pad_format:
            head, tail = pad_format.split(".", 1)
            return pad(number, len(head), len(tail))

        return pad(number, len(pad_format))

    @staticmethod
    def has_subsamples(
        range_: PaddedRange[int] | PaddedRange[decimal.Decimal],
    ) -> TypeGuard[PaddedRange[decimal.Decimal]]:
        """Check whether this file number sequence contains any decimal numbers."""
        return range_.file_nums.has_subsamples(range_.file_nums)


@dataclass(frozen=True)
class Ranges:
    ranges: tuple[PaddedRange[int] | PaddedRange[decimal.Decimal], ...]
    """Each :ref:`range specifier <format-simple-ranges>` in the sequence."""
    inter_ranges: tuple[str, ...]
    """The inter-range separators between each range in the sequence.

    The number of inter-range separators is guaranteed to be ``1 - len(self.ranges)``.
    """

    def __post_init__(self) -> None:
        if len(self.inter_ranges) != len(self.ranges) - 1:
            raise ValueError(
                "The number of inter-range strings given does not match"
                " the number of range strings minus one."
            )

    def __str__(self) -> str:
        return Formatter().ranges(self)

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}({self})"
