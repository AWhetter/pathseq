import dataclasses
from decimal import Decimal

from ._base import PaddedRange, Ranges, splice_strings_onto_ranges
from ._loose_type import ParsedLooseSequence
from ._type import ParsedSequence


class Formatter:
    def stem(self, stem: str) -> str:
        return stem

    def prefix(self, prefix: str) -> str:
        return prefix

    def range(self, range_: PaddedRange[int] | PaddedRange[Decimal]) -> str:
        return str(range_)

    def inter_range(self, inter_range: str) -> str:
        return inter_range

    def ranges(self, ranges: Ranges) -> str:
        return splice_strings_onto_ranges(
            (self.range(range_) for range_ in ranges.ranges),
            (self.inter_range(inter_range) for inter_range in ranges.inter_ranges),
        )

    def suffixes(self, suffixes: tuple[str, ...]) -> str:
        return "".join(suffixes)

    def format(self, seq: ParsedSequence | ParsedLooseSequence) -> str:
        return "".join(
            getattr(self, field.name)(getattr(seq, field.name))
            for field in dataclasses.fields(seq)
        )
