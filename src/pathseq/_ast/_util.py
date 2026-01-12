from __future__ import annotations

import dataclasses
import decimal
from typing import Any


def non_recursive_asdict(datacls: Any) -> dict[str, Any]:
    """Like :func:`dataclasses.asdict` but does not recurse into attributes."""
    return {
        field.name: getattr(datacls, field.name)
        for field in dataclasses.fields(datacls)
    }


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


def _quantize(
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
    number: int | decimal.Decimal, width: int = 0, decimal_places: int | None = None
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
        number = _quantize(number, decimal_places, decimal.ROUND_HALF_EVEN)

    parts = str(number).split(".", 1)
    parts[0] = parts[0].zfill(width)
    return ".".join(parts)
