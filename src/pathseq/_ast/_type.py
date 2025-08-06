from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal
import itertools
from typing import Self

from ._base import (
    non_recursive_asdict,
    splice_numbers_onto_ranges,
    stringify_parsed_sequence,
    PaddedRange,
)


@dataclass(frozen=True)
class ParsedSequence:
    stem: str
    prefix_separator: str
    ranges: tuple[PaddedRange | str]
    suffixes: tuple[str]

    def __str__(self):
        return stringify_parsed_sequence(self)

    def with_stem(self, stem: str) -> Self:
        kwargs = non_recursive_asdict(self)
        kwargs["stem"] = stem
        if not stem and self.stem:
            kwargs["prefix_separator"] = ""
        return self.__class__(**kwargs)

    def with_suffix(self, suffix: str) -> Self:
        kwargs = non_recursive_asdict(self)
        if suffix:
            if not suffix.startswith("."):
                raise ValueError(f"Invalid suffix '{suffix}'")

            add_suffixes = tuple(f".{s}" for s in suffix.split(".")[1:])
            kwargs["suffixes"] = self.suffixes[:-1] + add_suffixes
        else:
            kwargs["suffixes"] = self.suffixes[:-1]

        return self.__class__(**kwargs)

    def format(self, *numbers: int | Decimal | None) -> str:
        spliced = splice_numbers_onto_ranges(
            numbers,
            self.ranges[::2],
            self.ranges[1::2],
        )

        return (
            self.stem
            + self.prefix_separator
            + "".join(str(x) for x in spliced)
            + "".join(self.suffixes)
        )

    def as_glob(self) -> str:
        to_splice = "*" * len(self.ranges[::2])
        inter_ranges = self.ranges[1::2]
        spliced = itertools.chain.from_iterable(
            itertools.zip_longest(to_splice, inter_ranges, fillvalue="")
        )

        return (
            self.stem
            + self.prefix_separator
            + "".join(spliced),
            + "".join(self.suffixes)
        )
