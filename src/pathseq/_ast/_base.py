from __future__ import annotations

from collections.abc import Sequence
import dataclasses
from dataclasses import dataclass
import decimal
from decimal import Decimal
import itertools
import typing
from typing import Any, Generic, Literal, TypeAlias, TypeGuard, TypeVar, Union

if typing.TYPE_CHECKING:
    from .._file_num_seq import FileNumSequence

FileNumT = TypeVar("FileNumT", int, decimal.Decimal)
FileNum: TypeAlias = Union[int, decimal.Decimal]


def non_recursive_asdict(datacls: Any) -> dict[str, Any]:
    return {
        field.name: getattr(datacls, field.name)
        for field in dataclasses.fields(datacls)
    }


def stringify_parsed_sequence(seq: Any) -> str:
    result = ""
    for field in dataclasses.fields(seq):
        if field.name == "ranges":
            ranges = (str(x) for x in seq.ranges)
            # There's one more range than inter-range strings, so add an extra.
            inter_ranges = itertools.chain(seq.inter_ranges, ("",))
            result += "".join(itertools.chain.from_iterable(zip(ranges, inter_ranges)))
            continue
        elif field.name == "inter_ranges":
            continue

        value = getattr(seq, field.name)
        if isinstance(value, (list, tuple)):
            for item in value:
                result += str(item)
        else:
            result += value

    return result


def splice_numbers_onto_ranges(
    numbers: tuple[int | Decimal | None, ...],
    ranges: Sequence[PaddedRange[int] | PaddedRange[Decimal]],
    inter_ranges: Sequence[str],
) -> str:
    len_numbers = len(numbers)
    expected_numbers = len(ranges)
    if len_numbers != expected_numbers:
        raise TypeError(f"Expected {expected_numbers} file numbers. Got {len_numbers}")

    assert len(inter_ranges) == expected_numbers - 1

    to_splice: list[str] = []
    for number, _range in zip(numbers, ranges):
        if number is None:
            to_splice.append(str(_range))
        else:
            to_splice.append(_range.format(number))

    return splice_strings_onto_ranges(to_splice, inter_ranges)


def splice_strings_onto_ranges(
    strings: Sequence[str], inter_ranges: Sequence[str]
) -> str:
    assert len(strings) == len(inter_ranges) + 1

    spliced = itertools.chain.from_iterable(
        itertools.zip_longest(strings, inter_ranges, fillvalue="")
    )
    return "".join(spliced)


@dataclass(frozen=True)
class PaddedRange(Generic[FileNumT]):
    file_nums: FileNumSequence[FileNumT]
    pad_format: str

    def __str__(self) -> str:
        return str(self.file_nums) + self.pad_format

    def format(self, number: int | Decimal) -> str:
        if self.pad_format == "<UVTILE>":
            raise NotImplementedError

        pad_format = self.pad_format
        if self.pad_format == "<UDIM>":
            pad_format = "####"

        if "." in pad_format:
            head, tail = pad_format.split(".", 1)
            return pad(number, len(head), len(tail))

        return pad(number, len(pad_format))

    def as_regex(self) -> str:
        if self.pad_format == "<UVTILE>":
            return r"u\d+_v\d+"

        pad_format = self.pad_format
        if self.pad_format == "<UDIM>":
            pad_format = "####"

        if "." in pad_format:
            head, tail = pad_format.split(".", 1)
            tail_re = r"\.[0-9]*" + r"[0-9]" * len(tail)
        else:
            head = pad_format
            tail_re = ""
            if self.has_subsamples(self):
                tail_re = r"(\.[0-9]+)?"

        positive_re = r"([1-9][0-9]*)?" + r"[0-9]" * len(head)
        negative_re = r"-([1-9][0-9]*)?" + r"[0-9]" * (len(head) - 1)

        return f"({positive_re}|{negative_re}){tail_re}"

    @staticmethod
    def has_subsamples(
        range_: PaddedRange[int] | PaddedRange[decimal.Decimal],
    ) -> TypeGuard[PaddedRange[decimal.Decimal]]:
        """Check whether this file number sequence contains any decimal numbers."""
        return FileNumSequence[Any].has_subsamples(range_.file_nums)


# The MIT License (MIT)

# Original work Copyright (c) 2015 Matthew Chambers
# Modified work Copyright 2015 Justin Israel

# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:

# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.

# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.

# TODO: Validate that this is doing what we want


def quantize(
    number: decimal.Decimal,
    decimal_places: int,
    rounding: str = decimal.ROUND_HALF_EVEN,
) -> decimal.Decimal:
    """Round a decimal value to given number of decimal places

    Args:
        number: Decimal number to round
        decimal_places: Number of decimal places in return value
        rounding: decimal.Decimal rounding mode. See rounding argument of
            https://docs.python.org/2/library/decimal.html#decimal.Context

    Returns:
        decimal.Decimal:
    """
    quantize_exponent = decimal.Decimal(1).scaleb(-decimal_places)
    nq = number.quantize(quantize_exponent, rounding=rounding)
    if nq.is_zero():
        return nq.copy_abs()
    return nq


def pad(
    number: int | Decimal, width: int = 0, decimal_places: int | None = None
) -> str:
    """Return the zero-padded string of a given number.

    Args:
        number: the number to pad
        width: width for zero padding the integral component
        decimal_places: number of decimal places to use in frame range
    """

    # Make the common case fast. Truncate to integer value as USD does.
    # https://graphics.pixar.com/usd/docs/api/_usd__page__value_clips.html
    # See _DeriveClipTimeString for formatting of templateAssetPath
    # https://github.com/PixarAnimationStudios/USD/blob/release/pxr/usd/usd/clipSetDefinition.cpp
    if decimal_places == 0:
        try:
            number = round(number) or 0
        except TypeError:
            pass
        return str(number).partition(".")[0].zfill(width)

    # USD ultimately uses vsnprintf to format floats for templateAssetPath:
    # _DeriveClipTimeString -> TfStringPrintf -> ArchVStringPrintf -> ArchVsnprintf -> vsnprintf
    # Since glibc 2.17 the printf family of functions rounds floats using the
    # current IEEE rounding mode, by default bankers' rounding (FE_TONEAREST).
    # See https://sourceware.org/bugzilla/show_bug.cgi?id=5044 and man(3) fegetround
    # Also https://www.exploringbinary.com/inconsistent-rounding-of-printed-floating-point-numbers/
    if decimal_places is not None:
        if not isinstance(number, decimal.Decimal):
            number = decimal.Decimal(number)
        number = quantize(number, decimal_places, decimal.ROUND_HALF_EVEN)

    parts = str(number).split(".", 1)
    parts[0] = parts[0].zfill(width)
    return ".".join(parts)
