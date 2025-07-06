from __future__ import annotations

import decimal
from decimal import Decimal
import itertools

import dataclasses
from dataclasses import dataclass
from typing import Literal, Self

from ._file_num_set import FileNumSet


def _stringify_parsed_sequence(seq: ParsedSequence) -> str:
    result = ""
    for field in dataclasses.fields(seq):
        value = getattr(seq, field.name)
        if isinstance(value, list):
            for item in value:
                result += str(item)
        else:
            result += value

    return result


@dataclass(frozen=True)
class ParsedSequence:
    stem: str
    prefix_separator: str
    ranges: tuple[PaddedRange | str]
    suffixes: tuple[str]

    def __str__(self):
        return _stringify_parsed_sequence(self)

    def with_stem(self, stem: str) -> Self:
        kwargs = dataclasses.asdict(self)
        kwargs["stem"] = stem
        if not stem and self.stem:
            kwargs["prefix_separator"] = ""
        return self.__class__(**kwargs)

    def with_suffix(self, suffix: str) -> Self:
        if suffix:
            if not suffix.startswith("."):
                raise ValueError(f"Invalid suffix '{suffix}'")

            kwargs = dataclasses.asdict(self)
            add_suffixes = tuple(f".{s}" for s in suffix.split("."))
            kwargs["suffixes"] = self.suffixes[:-1] + add_suffixes
            return self.__class__(**kwargs)

        if self.suffixes:
            kwargs = dataclasses.asdict(self)
            kwargs["suffixes"] = self.suffixes[:-1]
            return self.__class__(**kwargs)

        return self

    def to_str_with_file_numbers(self, *numbers: int | Decimal | None) -> str:
        len_numbers = len(numbers)
        expected_numbers = len(self.ranges[::2])
        if len_numbers != expected_numbers:
            raise TypeError(f"Expected {expected_numbers} file numbers. Got {len_numbers}")

        to_splice = list(numbers)
        for i, (number, _range) in enumerate(zip(numbers, self.ranges[::2])):
            if number is None:
                to_splice[i] = _range
            else:
                to_splice[i] = _range.to_str_with_file_number(number)

        spliced = list(
            itertools.chain.from_iterable(
                itertools.zip_longest(to_splice, self.ranges[1::2], fillvalue="")
            )
        )

        return (
            self.stem
            + self.prefix_separator
            + "".join(str(x) for x in spliced)
            + "".join(self.suffixes)
        )


@dataclass(frozen=True)
class PaddedRange:
    file_num_set: FileNumSet | Literal[""]
    pad_format: str

    def __str__(self):
        return str(self.file_num_set) + self.pad_format

    def to_str_with_file_number(self, number: int | Decimal) -> str:
        if self.pad_format == "<UVTILE>":
            raise NotImplementedError

        pad_format = self.pad_format
        if self.pad_format == "<UDIM>":
            pad_format = "####"

        if "." in pad_format:
            head, tail = pad_format.split(".", 1)
            return pad(number, len(head), len(tail))

        return pad(number, len(pad_format))


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
        rounding: str = decimal.ROUND_HALF_EVEN
        ) -> decimal.Decimal:
    """
    Round a decimal value to given number of decimal places

    Args:
        number (decimal.Decimal): Decimal number to round
        decimal_places (int): Number of decimal places in return value
        rounding (str): decimal.Decimal rounding mode. See rounding argument of
            https://docs.python.org/2/library/decimal.html#decimal.Context

    Returns:
        decimal.Decimal:
    """
    quantize_exponent = decimal.Decimal(1).scaleb(-decimal_places)
    nq = number.quantize(quantize_exponent, rounding=rounding)
    if nq.is_zero():
        return nq.copy_abs()
    return nq

def pad(number: int | Decimal, width: int | None = 0, decimal_places: int | None = None) -> str:
    """
    Return the zero-padded string of a given number.

    Args:
        number (str, int, float, or decimal.Decimal): the number to pad
        width (int): width for zero padding the integral component
        decimal_places (int): number of decimal places to use in frame range

    Returns:
        str:
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
        return str(number).partition(".")[0].zfill(width)  # type:ignore[arg-type]

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

    number = str(number)

    parts = number.split(".", 1)
    parts[0] = parts[0].zfill(width)
    return ".".join(parts)
