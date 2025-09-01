from __future__ import annotations

import decimal

import lark

from ._arithmetic_sequence import ArithmeticSequence
from ._ast import FileNumT
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


@lark.v_args(inline=True)
class _RangeReducer(lark.Transformer[lark.Token, list[ArithmeticSequence]]):
    def start(self, seq: list[ArithmeticSequence]) -> list[ArithmeticSequence]:
        return seq

    def ranges(
        self, range_: ArithmeticSequence, *ranges: ArithmeticSequence
    ) -> list[ArithmeticSequence]:
        # TODO: Normalise the type of all ranges
        result = [range_]
        if ranges:
            result.extend(ranges)

        return result

    def range(self, start: str, end: str | None, step: str | None):
        args = [start]
        if end is not None:
            args.append(end)
            if step is not None:
                args.append(step)

        type_: type[int] | type[decimal.Decimal] = int
        if any("." in arg for arg in args):
            type_ = decimal.Decimal

        return ArithmeticSequence(*(type_(arg) for arg in args))


def parse_file_num_set(set_: str) -> list[ArithmeticSequence[FileNumT]]:
    try:
        ranges = _PARSER.parse(set_)
    except lark.UnexpectedInput as exc:
        raise ParseError(set_, exc.column)

    return _RangeReducer().transform(ranges)
