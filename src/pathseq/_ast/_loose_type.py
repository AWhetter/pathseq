from __future__ import annotations

from dataclasses import dataclass
from typing import Literal, Self, TypeAlias, Union

from ._base import (
    non_recursive_asdict,
    stringify_parsed_sequence,
    Ranges,
)


@dataclass(frozen=True)
class RangesStartName:
    """A parsed loose path sequence where the range starts a path's name."""

    prefix: Literal[""]
    """An optional single character separator between the ranges and the previous component.

    This is always empty for file names where the ranges start the name,
    but is included so that :class:`~.RangesStartName`, :class:`~.RangesInName`,
    and :class:`~.RangesEndName` all have the same attributes.
    """
    ranges: Ranges
    """The file numbers of the files in the sequence and their formatting."""
    postfix: str
    """An optional single character separator between the ranges and the next component.

    In sequences where the ranges start the name,
    this separates the :ref:`ranges <format-loose-range>` from the
    :ref:`stem <format-loose-stem>`.
    """
    stem: str
    """The name of the sequence, without the prefix, ranges, postfix, and suffixes."""
    suffixes: tuple[str, ...]
    """The file extensions of the files in the path sequence.

    Each suffix includes the leading "``.``".
    """

    def __str__(self) -> str:
        return stringify_parsed_sequence(self)

    def with_stem(self, stem: str) -> Self:
        """Return a new parsed sequence with the :attr:`~.RangesStartName.stem` changed.

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


@dataclass(frozen=True)
class RangesInName:
    """A parsed loose range sequence where the range follows a path's stem."""

    stem: str
    """The name of the sequence, without the prefix, ranges, postfix, and suffixes."""
    prefix: str
    """An optional single character separator between the ranges and the previous component.

    In sequences where the ranges are in the name,
    this separates the :ref:`ranges <format-loose-range>` from the
    :ref:`stem <format-loose-stem>`.
    """
    ranges: Ranges
    """The file numbers of the files in the sequence and their formatting."""
    postfix: str
    """An optional single character separator between the ranges and the next component.

    In sequences where the ranges are in the name,
    this separates the :ref:`ranges <format-loose-range>` from the
    :ref:`suffixes <format-loose-suffixes>`.
    """
    suffixes: tuple[str, ...]
    """The file extensions of the files in the path sequence.

    Each suffix includes the leading "``.``".
    """

    def __str__(self) -> str:
        return stringify_parsed_sequence(self)

    def with_stem(self, stem: str) -> Self:
        """Return a new parsed sequence with the :attr:`~.RangesInName.stem` changed.

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


@dataclass(frozen=True)
class RangesEndName:
    """A parsed loose range sequence where the range ends a path's name."""

    stem: str
    """The name of the sequence, without the prefix, ranges, postfix, and suffixes."""
    suffixes: tuple[str, ...]
    """The file extensions of the files in the path sequence.

    Each suffix includes the leading "``.``".
    """
    prefix: str
    """An optional single character separator between the ranges and the previous component.

    In sequences where the ranges are in the name,
    this separates the :ref:`ranges <format-loose-range>` from the
    :ref:`suffixes <format-loose-suffixes>`.
    """
    ranges: Ranges
    """The file numbers of the files in the sequence and their formatting."""
    postfix: Literal[""]
    """An optional single character separator between the ranges and the next component.

    This is always empty for file names where the ranges end the name,
    but is included so that :class:`~.RangesStartName`, :class:`~.RangesInName`,
    and :class:`~.RangesEndName` all have the same attributes.
    """

    def __str__(self) -> str:
        return stringify_parsed_sequence(self)

    def with_stem(self, stem: str) -> Self:
        """Return a new parsed sequence with the :attr:`~.RangesEndName.stem` changed."""
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


ParsedLooseSequence: TypeAlias = Union[RangesStartName, RangesInName, RangesEndName]
