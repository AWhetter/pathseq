from __future__ import annotations

import dataclasses
from dataclasses import dataclass
from typing import Literal, Self, TypeAlias, Union

from ._file_num_set import FileNumSet


def _stringify_parsed_sequence(seq: ParsedSequence) -> str:
    result = ""
    for field in dataclasses.fields(seq):
        value = getattr(seq, field.name)
        if isinstance(value, list):
            for item in value:
                result += str(item)
        else:
            result += value

    return result


@dataclass(frozen=True)
class RangesStartName:
    prefix_separator: Literal[""]
    ranges: tuple[PaddedRange | str]
    postfix: str
    stem: str
    suffixes: tuple[str]

    def __str__(self):
        return _stringify_parsed_sequence(self)

    def with_stem(self, stem: str) -> Self:
        kwargs = dataclasses.asdict(self)
        kwargs["stem"] = stem
        if not stem and self.stem:
            kwargs["postfix"] = ""
        return self.__class__(**kwargs)

    def with_suffix(self, suffix: str) -> Self:
        if suffix:
            if not suffix.startswith(".") or suffix == ".":
                raise ValueError(f"Invalid suffix '{suffix}'")

            kwargs = dataclasses.asdict(self)
            add_suffixes = tuple(f".{s}" for s in suffix.split("."))
            kwargs["suffixes"] = self.suffixes[:-1] + add_suffixes
            return self.__class__(**kwargs)

        if self.suffixes:
            kwargs = dataclasses.asdict(self)
            kwargs["suffixes"] = self.suffixes[:-1]
            return self.__class__(**kwargs)

        return self


@dataclass(frozen=True)
class RangesInName:
    stem: str
    prefix_separator: str
    ranges: tuple[PaddedRange | str]
    postfix: str
    suffixes: tuple[str]

    def __str__(self):
        return _stringify_parsed_sequence(self)

    def with_stem(self, stem: str) -> Self:
        kwargs = dataclasses.asdict(self)
        kwargs["stem"] = stem
        if not stem and self.stem:
            kwargs["prefix_separator"] = ""
        return self.__class__(**kwargs)

    def with_suffix(self, suffix: str) -> Self:
        if suffix:
            if not suffix.startswith("."):
                raise ValueError(f"Invalid suffix '{suffix}'")

            kwargs = dataclasses.asdict(self)
            add_suffixes = tuple(f".{s}" for s in suffix.split("."))
            kwargs["suffixes"] = self.suffixes[:-1] + add_suffixes
            return self.__class__(**kwargs)

        if self.suffixes:
            kwargs = dataclasses.asdict(self)
            kwargs["suffixes"] = self.suffixes[:-1]
            if not kwargs["suffixes"]:
                kwargs["postfix"] = ""
            return self.__class__(**kwargs)

        return self


@dataclass(frozen=True)
class RangesEndName:
    stem: str
    suffixes: tuple[str]
    prefix_separator: str
    ranges: tuple[PaddedRange | str]
    postfix: Literal[""]

    def __str__(self):
        return _stringify_parsed_sequence(self)

    def with_stem(self, stem: str) -> Self:
        kwargs = dataclasses.asdict(self)
        kwargs["stem"] = stem
        return self.__class__(**kwargs)

    def with_suffix(self, suffix: str) -> Self:
        if suffix:
            if not suffix.startswith("."):
                raise ValueError(f"Invalid suffix '{suffix}'")

            kwargs = dataclasses.asdict(self)
            add_suffixes = tuple(f".{s}" for s in suffix.split("."))
            kwargs["suffixes"] = self.suffixes[:-1] + add_suffixes
            return self.__class__(**kwargs)

        if self.suffixes:
            kwargs = dataclasses.asdict(self)
            kwargs["suffixes"] = self.suffixes[:-1]
            if not kwargs["suffixes"]:
                kwargs["prefix_separator"] = ""
            return self.__class__(**kwargs)

        return self


ParsedSequence: TypeAlias = Union[RangesStartName, RangesInName, RangesEndName]


@dataclass(frozen=True)
class PaddedRange:
    file_num_set: FileNumSet | Literal[""]
    pad_format: str
