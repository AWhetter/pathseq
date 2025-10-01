from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal
import re
from typing import Self

from ._base import (
    non_recursive_asdict,
    splice_numbers_onto_ranges,
    splice_strings_onto_ranges,
    stringify_parsed_sequence,
    PaddedRange,
)


@dataclass(frozen=True)
class ParsedSequence:
    """A parsed path sequence."""

    stem: str
    prefix: str
    ranges: tuple[PaddedRange[int] | PaddedRange[Decimal], ...]
    inter_ranges: tuple[str, ...]
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
        kwargs = non_recursive_asdict(self)
        if suffix:
            if not suffix.startswith("."):
                raise ValueError(f"Invalid suffix '{suffix}'")

            add_suffixes = tuple(f".{s}" for s in suffix.split(".")[1:])
            kwargs["suffixes"] = self.suffixes[:-1] + add_suffixes
        else:
            kwargs["suffixes"] = self.suffixes[:-1]

        return self.__class__(**kwargs)

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

        return self.stem + self.prefix + spliced + "".join(self.suffixes)

    # TODO: Replace the need for the following two methods
    # with some kind of formatting functionality.
    def as_glob(self) -> str:
        """Get a glob pattern to match paths in this sequence."""
        to_splice = "*" * len(self.ranges)
        spliced = splice_strings_onto_ranges(to_splice, self.inter_ranges)

        return self.stem + self.prefix + spliced + "".join(self.suffixes)

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
            + re.escape("".join(self.suffixes))
        )
