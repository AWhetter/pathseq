from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal
import re
from typing import Literal, Self

from ._base import (
    non_recursive_asdict,
    splice_numbers_onto_ranges,
    splice_strings_onto_ranges,
    stringify_parsed_sequence,
    PaddedRange,
)


@dataclass(frozen=True)
class RangesStartName:
    prefix_separator: Literal[""]
    ranges: tuple[PaddedRange[int] | PaddedRange[Decimal], ...]
    inter_ranges: tuple[str, ...]
    postfix: str
    stem: str
    suffixes: tuple[str, ...]

    def __str__(self) -> str:
        return stringify_parsed_sequence(self)

    def with_stem(self, stem: str) -> Self:
        kwargs = non_recursive_asdict(self)
        kwargs["stem"] = stem
        if not stem and self.stem and self.suffixes:
            kwargs["postfix"] = ""
        return self.__class__(**kwargs)

    def with_suffix(self, suffix: str) -> Self:
        if suffix:
            if not suffix.startswith(".") or suffix == ".":
                raise ValueError(f"Invalid suffix '{suffix}'")

            kwargs = non_recursive_asdict(self)
            add_suffixes = tuple(f".{s}" for s in suffix[1:].split("."))
            kwargs["suffixes"] = self.suffixes[:-1] + add_suffixes
            return self.__class__(**kwargs)

        if self.suffixes:
            kwargs = non_recursive_asdict(self)
            kwargs["suffixes"] = self.suffixes[:-1]
            return self.__class__(**kwargs)

        return self

    def format(self, *numbers: int | Decimal | None) -> str:
        spliced = splice_numbers_onto_ranges(
            numbers,
            self.ranges,
            self.inter_ranges,
        )

        return spliced + self.postfix + self.stem + "".join(self.suffixes)

    def as_glob(self) -> str:
        to_splice = "*" * len(self.ranges)
        spliced = splice_strings_onto_ranges(to_splice, self.inter_ranges)

        return spliced + self.postfix + self.stem + "".join(self.suffixes)

    def as_regex(self) -> str:
        to_splice = [
            f"(?P<range{i}>{range_.as_regex()})" for i, range_ in enumerate(self.ranges)
        ]
        spliced = splice_strings_onto_ranges(
            to_splice, [re.escape(x) for x in self.inter_ranges]
        )

        return spliced + re.escape(self.postfix + self.stem + "".join(self.suffixes))


@dataclass(frozen=True)
class RangesInName:
    stem: str
    prefix_separator: str
    ranges: tuple[PaddedRange[int] | PaddedRange[Decimal], ...]
    inter_ranges: tuple[str, ...]
    postfix: str
    suffixes: tuple[str, ...]

    def __str__(self) -> str:
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
            add_suffixes = tuple(f".{s}" for s in suffix[1:].split("."))
            kwargs["suffixes"] = self.suffixes[:-1] + add_suffixes
            return self.__class__(**kwargs)

        if self.suffixes:
            kwargs = non_recursive_asdict(self)
            kwargs["suffixes"] = self.suffixes[:-1]
            if not kwargs["suffixes"]:
                kwargs["postfix"] = ""
            return self.__class__(**kwargs)

        return self

    def format(self, *numbers: int | Decimal | None) -> str:
        spliced = splice_numbers_onto_ranges(
            numbers,
            self.ranges,
            self.inter_ranges,
        )

        return (
            self.stem
            + self.prefix_separator
            + spliced
            + self.postfix
            + "".join(self.suffixes)
        )

    def as_glob(self) -> str:
        to_splice = "*" * len(self.ranges)
        spliced = splice_strings_onto_ranges(to_splice, self.inter_ranges)

        return (
            self.stem
            + self.prefix_separator
            + spliced
            + self.postfix
            + "".join(self.suffixes)
        )

    def as_regex(self) -> str:
        to_splice = [
            f"(?P<range{i}>{range_.as_regex()})" for i, range_ in enumerate(self.ranges)
        ]
        spliced = splice_strings_onto_ranges(
            to_splice, [re.escape(x) for x in self.inter_ranges]
        )

        return (
            re.escape(self.stem + self.prefix_separator)
            + spliced
            + re.escape(self.postfix + "".join(self.suffixes))
        )


@dataclass(frozen=True)
class RangesEndName:
    stem: str
    suffixes: tuple[str, ...]
    prefix_separator: str
    ranges: tuple[PaddedRange[int] | PaddedRange[Decimal], ...]
    inter_ranges: tuple[str, ...]
    postfix: Literal[""]

    def __str__(self) -> str:
        return stringify_parsed_sequence(self)

    def with_stem(self, stem: str) -> Self:
        kwargs = non_recursive_asdict(self)
        kwargs["stem"] = stem
        return self.__class__(**kwargs)

    def with_suffix(self, suffix: str) -> Self:
        if suffix:
            if not suffix.startswith("."):
                raise ValueError(f"Invalid suffix '{suffix}'")

            kwargs = non_recursive_asdict(self)
            add_suffixes = tuple(f".{s}" for s in suffix[1:].split("."))
            kwargs["suffixes"] = self.suffixes[:-1] + add_suffixes
            return self.__class__(**kwargs)

        if self.suffixes:
            kwargs = non_recursive_asdict(self)
            kwargs["suffixes"] = self.suffixes[:-1]
            return self.__class__(**kwargs)

        return self

    def format(self, *numbers: int | Decimal | None) -> str:
        spliced = splice_numbers_onto_ranges(
            numbers,
            self.ranges,
            self.inter_ranges,
        )

        return self.stem + "".join(self.suffixes) + self.prefix_separator + spliced

    def as_glob(self) -> str:
        to_splice = "*" * len(self.ranges)
        spliced = splice_strings_onto_ranges(to_splice, self.inter_ranges)

        return self.stem + "".join(self.suffixes) + self.prefix_separator + spliced

    def as_regex(self) -> str:
        to_splice = [
            f"(?P<range{i}>{range_.as_regex()})" for i, range_ in enumerate(self.ranges)
        ]
        spliced = splice_strings_onto_ranges(
            to_splice, [re.escape(x) for x in self.inter_ranges]
        )

        return (
            re.escape(self.stem + "".join(self.suffixes) + self.prefix_separator)
            + spliced
        )
