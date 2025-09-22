from __future__ import annotations

from decimal import Decimal as D
from typing import TypeAlias, TypeVar, Union

import lark

from ._arithmetic_sequence import ArithmeticSequence
from ._error import ParseError

_GRAMMAR = r"""
    start: ranges

    ranges: range ("," range)*

    range: FILE_NUM ["-" FILE_NUM ["x" NUM]]

    FILE_NUM: "-"? NUM
    NUM: /
        (0|[1-9][0-9]*)       # the digits
        (\.0|\.[0-9]*[1-9])?  # the subsamples
    /x
"""
_PARSER = lark.Lark(_GRAMMAR, parser="lalr")
_SeqArgsT: TypeAlias = Union[tuple[str], tuple[str, str], tuple[str, str, str]]
T = TypeVar("T")


@lark.v_args(inline=True)
class _RangeReducer(
    lark.Transformer[
        lark.Token, list[ArithmeticSequence[int]] | list[ArithmeticSequence[D]]
    ]
):
    def start(self, seq: T) -> T:
        return seq

    def ranges(
        self, range_: _SeqArgsT, *ranges: _SeqArgsT
    ) -> list[ArithmeticSequence[int]] | list[ArithmeticSequence[D]]:
        if any("." in arg for arg in range_) or any(
            "." in arg for r in ranges for arg in r
        ):
            return [
                ArithmeticSequence(*tuple(D(arg) for arg in range_)),
                *(ArithmeticSequence(*tuple(D(arg) for arg in r)) for r in ranges),
            ]

        return [
            ArithmeticSequence(*tuple(int(arg) for arg in range_)),
            *(ArithmeticSequence(*tuple(int(arg) for arg in r)) for r in ranges),
        ]

    def range(self, start: str, end: str | None, step: str | None) -> _SeqArgsT:
        assert step is None or end is not None, "Parsed an end but no step"

        args: _SeqArgsT = (start,)
        if end is not None:
            args = (start, end)
            if step is not None:
                args = (start, end, step)

        return args


def parse_file_num_seq(
    seq: str,
) -> list[ArithmeticSequence[int]] | list[ArithmeticSequence[D]]:
    if not seq:
        return []

    try:
        ranges = _PARSER.parse(seq)
    except lark.UnexpectedInput as exc:
        raise ParseError(seq, exc.column)

    return _RangeReducer().transform(ranges)
