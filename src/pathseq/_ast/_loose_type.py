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
    """A parsed loose path sequence where the range starts a path's name."""

    prefix: Literal[""]
    ranges: tuple[PaddedRange[int] | PaddedRange[Decimal], ...]
    inter_ranges: tuple[str, ...]
    postfix: str
    stem: str
    suffixes: tuple[str, ...]

    def __str__(self) -> str:
        return stringify_parsed_sequence(self)

    def with_stem(self, stem: str) -> Self:
        """Return a new parsed sequence with the :attr:`~.stem` changed.

        If the stem is removed, the postfix will be as well.
        """
        kwargs = non_recursive_asdict(self)
        kwargs["stem"] = stem
        if not stem:
            kwargs["postfix"] = ""
        return self.__class__(**kwargs)

    def with_suffix(self, suffix: str) -> Self:
        """Return a new parsed sequence with the suffix changed.

        Args:
            suffix: The new suffix to replace the existing one with.
                This must start with a "." or be the empty string.

        Raises:
            ValueError: If an invalid suffix is given.
        """
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

    def format(self, *numbers: int | Decimal) -> str:
        """Format the sequence with given numbers using each range's padding rules.

        Raises:
            TypeError: If the number of numbers given does not match the
            number of ranges to be formatted.
        """
        spliced = splice_numbers_onto_ranges(
            numbers,
            self.ranges,
            self.inter_ranges,
        )

        return spliced + self.postfix + self.stem + "".join(self.suffixes)

    def as_glob(self) -> str:
        """Get a glob pattern to match paths in this sequence."""
        to_splice = "*" * len(self.ranges)
        spliced = splice_strings_onto_ranges(to_splice, self.inter_ranges)

        return spliced + self.postfix + self.stem + "".join(self.suffixes)

    def as_regex(self) -> str:
        """Get a regex pattern to match paths in this sequence."""
        to_splice = [
            f"(?P<range{i}>{range_.as_regex()})" for i, range_ in enumerate(self.ranges)
        ]
        spliced = splice_strings_onto_ranges(
            to_splice, [re.escape(x) for x in self.inter_ranges]
        )

        return spliced + re.escape(self.postfix + self.stem + "".join(self.suffixes))


@dataclass(frozen=True)
class RangesInName:
    """A parsed loose range sequence where the range follows a path's stem."""

    stem: str
    prefix: str
    ranges: tuple[PaddedRange[int] | PaddedRange[Decimal], ...]
    inter_ranges: tuple[str, ...]
    postfix: str
    suffixes: tuple[str, ...]

    def __str__(self) -> str:
        return stringify_parsed_sequence(self)

    def with_stem(self, stem: str) -> Self:
        """Return a new parsed sequence with the :attr:`~.stem` changed.

        If the stem is removed, the prefix will be as well.
        """
        kwargs = non_recursive_asdict(self)
        kwargs["stem"] = stem
        if not stem and self.stem:
            kwargs["prefix"] = ""
        return self.__class__(**kwargs)

    def with_suffix(self, suffix: str) -> Self:
        """Return a new parsed sequence with the suffix changed.

        Args:
            suffix: The new suffix to replace the existing one with.
                This must start with a "." or be the empty string.

        Raises:
            ValueError: If an invalid suffix is given.
        """
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

    def format(self, *numbers: int | Decimal) -> str:
        """Format the sequence with given numbers using each range's padding rules.

        Raises:
            TypeError: If the number of numbers given does not match the
            number of ranges to be formatted.
        """
        spliced = splice_numbers_onto_ranges(
            numbers,
            self.ranges,
            self.inter_ranges,
        )

        return self.stem + self.prefix + spliced + self.postfix + "".join(self.suffixes)

    def as_glob(self) -> str:
        """Get a glob pattern to match paths in this sequence."""
        to_splice = "*" * len(self.ranges)
        spliced = splice_strings_onto_ranges(to_splice, self.inter_ranges)

        return self.stem + self.prefix + spliced + self.postfix + "".join(self.suffixes)

    def as_regex(self) -> str:
        """Get a regex pattern to match paths in this sequence."""
        to_splice = [
            f"(?P<range{i}>{range_.as_regex()})" for i, range_ in enumerate(self.ranges)
        ]
        spliced = splice_strings_onto_ranges(
            to_splice, [re.escape(x) for x in self.inter_ranges]
        )

        return (
            re.escape(self.stem + self.prefix)
            + spliced
            + re.escape(self.postfix + "".join(self.suffixes))
        )


@dataclass(frozen=True)
class RangesEndName:
    """A parsed loose range sequence where the range ends a path's name."""

    stem: str
    suffixes: tuple[str, ...]
    prefix: str
    ranges: tuple[PaddedRange[int] | PaddedRange[Decimal], ...]
    inter_ranges: tuple[str, ...]
    postfix: Literal[""]

    def __str__(self) -> str:
        return stringify_parsed_sequence(self)

    def with_stem(self, stem: str) -> Self:
        """Return a new parsed sequence with the :attr:`~.stem` changed."""
        kwargs = non_recursive_asdict(self)
        kwargs["stem"] = stem
        return self.__class__(**kwargs)

    def with_suffix(self, suffix: str) -> Self:
        """Return a new parsed sequence with the suffix changed.

        Args:
            suffix: The new suffix to replace the existing one with.
                This must start with a "." or be the empty string.

        Raises:
            ValueError: If an invalid suffix is given.
        """
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

    def format(self, *numbers: int | Decimal) -> str:
        """Format the sequence with given numbers using each range's padding rules.

        Raises:
            TypeError: If the number of numbers given does not match the
            number of ranges to be formatted.
        """
        spliced = splice_numbers_onto_ranges(
            numbers,
            self.ranges,
            self.inter_ranges,
        )

        return self.stem + "".join(self.suffixes) + self.prefix + spliced

    def as_glob(self) -> str:
        """Get a glob pattern to match paths in this sequence."""
        to_splice = "*" * len(self.ranges)
        spliced = splice_strings_onto_ranges(to_splice, self.inter_ranges)

        return self.stem + "".join(self.suffixes) + self.prefix + spliced

    def as_regex(self) -> str:
        """Get a regex pattern to match paths in this sequence."""
        to_splice = [
            f"(?P<range{i}>{range_.as_regex()})" for i, range_ in enumerate(self.ranges)
        ]
        spliced = splice_strings_onto_ranges(
            to_splice, [re.escape(x) for x in self.inter_ranges]
        )

        return re.escape(self.stem + "".join(self.suffixes) + self.prefix) + spliced
