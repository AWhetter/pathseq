from __future__ import annotations

from dataclasses import dataclass

from typing_extensions import Self  # PY311

from ._base import (
    non_recursive_asdict,
    stringify_parsed_sequence,
    Ranges,
)


@dataclass(frozen=True)
class ParsedSequence:
    """A parsed path sequence."""

    stem: str
    """The name of the sequence, without the prefix, ranges, and suffixes."""
    prefix: str
    """An optional single character separator between the stem and the ranges."""
    ranges: Ranges
    """The file numbers of the files in the sequence and their formatting."""
    suffixes: tuple[str, ...]
    """The file extensions of the files in the path sequence.

    Each suffix includes the leading "``.``".
    """

    def __str__(self) -> str:
        return stringify_parsed_sequence(self)

    def with_stem(self, stem: str) -> Self:
        """Return a new parsed sequence with the :attr:`~.ParsedSequence.stem` changed.

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
