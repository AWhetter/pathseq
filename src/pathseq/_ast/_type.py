from __future__ import annotations

from decimal import Decimal
import itertools

from dataclasses import dataclass
from typing import Self

from ._base import non_recursive_asdict, stringify_parsed_sequence, PaddedRange


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
        if suffix:
            if not suffix.startswith("."):
                raise ValueError(f"Invalid suffix '{suffix}'")

            kwargs = non_recursive_asdict(self)
            add_suffixes = tuple(f".{s}" for s in suffix.split("."))
            kwargs["suffixes"] = self.suffixes[:-1] + add_suffixes
            return self.__class__(**kwargs)

        if self.suffixes:
            kwargs = non_recursive_asdict(self)
            kwargs["suffixes"] = self.suffixes[:-1]
            return self.__class__(**kwargs)

        return self

    def to_str_with_file_numbers(self, *numbers: int | Decimal | None) -> str:
        len_numbers = len(numbers)
        expected_numbers = len(self.ranges[::2])
        if len_numbers != expected_numbers:
            raise TypeError(
                f"Expected {expected_numbers} file numbers. Got {len_numbers}"
            )

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
