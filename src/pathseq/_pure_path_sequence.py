from __future__ import annotations

from collections.abc import Iterable, Sequence, Set
from decimal import Decimal
import itertools
import os
import pathlib
from typing import overload, TypeVar, Union

from typing_extensions import (
    Self,  # PY311
    TypeAlias,  # PY310
    TypeGuard,  # PY310
)

from ._ast import PaddedRange, ParsedSequence
from ._error import ParseError
from ._file_num_set import FileNumSet
from ._parse_path_sequence import parse_path_sequence

Segment: TypeAlias = Union[str, os.PathLike[str], "PurePathSequence"]
T = TypeVar("T", int, Decimal)


# TODO: Should be a set of pathlib objects
class PurePathSequence(Sequence[T], Set[T]):
    """A generic class that represents a path sequence in the system's path flavour.

    Instantiating this class creates either a :class:`PurePosixPathSequence`
    or a :class:`PureWindowsPathSequence`.

    Raises:
        NotASequenceError: When the given path does not represent a sequence.
    """

    _pathlib_type: type[pathlib.PurePath] = pathlib.PurePath

    def __new__(cls, *args, **kwargs):
        if cls is PurePathSequence:
            cls = PureWindowsPathSequence if os.name == "nt" else PurePosixPathSequence
        return object.__new__(cls)

    def __init__(self, *pathsegments: Segment) -> None:
        self._path = self._pathlib_type(*pathsegments)
        self._parsed = parse_path_sequence(self._path.name)

    # General properties
    def __eq__(self, other: object) -> bool:
        if not isinstance(other, self.__class__):
            return NotImplemented

        return self._path.parent == other._path.parent and self._parsed == other._parsed

    def __repr__(self):
        return "{}({!r})".format(self.__class__.__name__, self.as_posix())

    def __str__(self):
        return str(self._path)

    def __hash__(self):
        return hash((type(self), self._path.parent, self._parsed))

    # Path operations
    def __rtruediv__(self, key):
        try:
            return self.with_segments(key, self._path)
        except TypeError:
            return NotImplemented

    @property
    def parts(self) -> tuple[str]:
        return self._path.parts

    @property
    def drive(self) -> str:
        return self._path.drive

    @property
    def root(self) -> str:
        return self._path.root

    @property
    def anchor(self) -> str:
        return self._path.anchor

    @property
    def name(self) -> str:
        return self._path.name

    # Note: Can be the empty string
    @property
    def suffix(self) -> str:
        suffixes = self.suffixes
        if not suffixes:
            return ""

        return suffixes[-1]

    @property
    def suffixes(self) -> Sequence[str]:
        return self._parsed.suffixes

    # Note: Can be the empty string
    @property
    def stem(self) -> str:
        return self._parsed.stem

    @property
    def parents(self) -> Sequence[pathlib.PurePath]:
        return self._path.parents

    @property
    def parent(self) -> pathlib.PurePath:
        return self._path.parent

    def as_posix(self) -> str:
        return self._path.as_posix()

    def is_reserved(self) -> bool:
        return self._path.is_reserved()

    def is_relative_to(self, other: pathlib.PurePath) -> bool:
        return self._path.is_relative_to(other)

    def relative_to(self, other: Segment, *, walk_up: bool = False) -> Self:
        # TODO: walk_up only valid in Python 3.12+
        # TODO: Need __contains__ because it should not be possible to pass
        # a file that's in this sequence.
        raise NotImplementedError

    def with_name(self, name: str) -> Self:
        return self.with_segments(self._path.with_name(name))

    def with_stem(self, stem: str) -> Self:
        parsed = self._parsed.with_stem(stem)
        return self.with_segments(self._path.parent, str(parsed))

    def with_suffix(self, suffix: str) -> Self:
        """Return a new path sequence with the suffix changed.

        If the given suffix is the empty string, the existing suffix will be removed.
        But if the path sequence has only one suffix,
        then a :exc:`ValueError` will be raised because removing the suffix will result in
        and invalid path sequence.

        Args:
            The new suffix to replace the existing suffix with.

        Raises:
            ValueError: If the given suffix would result in an invalid path sequence.
        """
        if not suffix:
            raise ValueError("Strict path format must have a suffix")

        parsed = self._parsed.with_suffix(suffix)
        try:
            return self.with_segments(self._path.parent, str(parsed))
        except ParseError:
            raise ValueError(
                f"Cannot use suffix '{suffix}' because"
                " it would result in an invalid path sequence"
            )

    def with_segments(self, *pathsegments: Segment) -> Self:
        return type(self)(*pathsegments)

    # Sequence operations
    @overload
    def __getitem__(self, index: int) -> pathlib.PurePath: ...

    @overload
    def __getitem__(self, index: slice) -> Self: ...

    def __getitem__(self, index):
        pass

    def __contains__(self, item) -> bool:
        raise NotImplementedError

    def __iter__(self) -> Iterable[pathlib.PurePath]:
        # TODO: Note order of iteration over multi-dimension ranges
        ranges: list[FileNumSet | None] = [
            x.file_num_set for x in self._parsed.ranges[::2]
        ]

        assert ranges, "Parsed a sequence string without any ranges present."

        iterators = [iter(x if x is not None else (None,)) for x in ranges]
        # TODO: Check that this isn't using mega amounts of memory
        for result in itertools.product(*iterators):
            yield self.format(*result)

    def __len__(self) -> int:
        result = 1

        for x in self._parsed.ranges:
            if isinstance(x, PaddedRange):
                if x.file_num_set is None:
                    raise ValueError(
                        "Cannot calculate the length of a path sequence"
                        " with one or more unknown ranges"
                    )

                result *= len(x.file_num_set)

        return result

    # PathSeq specific operations

    @property
    def paddings(self) -> tuple[str]:
        """All padding strings in the final path component."""

    # TODO: Or maybe set via part objects?
    def with_paddings(self, *paddings: str) -> Self:
        """Set new pads.

        Raises:
            ValueError: When the number of provided padding strings does not match
                the number of padding strings in the final path component.
        """

    @classmethod
    def from_paths(cls, paths: Iterable[os.PathLike[str]]) -> Iterable[Self]:
        """Create one or more path sequences from a list of paths."""

    @overload
    def format(self, *numbers: int | Decimal) -> pathlib.PurePath: ...

    @overload
    def format(self, *numbers: int | Decimal | None) -> Self: ...

    def format(self, *numbers):
        """Return a path for the given file number(s) in the sequence.

        Args:
            The number to use in place of each range in the string.
            A ``None`` means don't fill in this range.
        """
        name = self._parsed.format(*numbers)
        result = self._path.with_name(name)

        if any(number is None for number in numbers):
            return self.__class__(result)

        return result

    def file_num_sets(self) -> tuple[FileNumSet] | None:
        """All file number sets in the final path component."""

    def with_file_num_sets(self, sets: Iterable[FileNumSet]) -> Self:
        pass

    # TODO: Make these classes generic
    @staticmethod
    def has_subsamples(seq: Self) -> TypeGuard[Self[Decimal]]:
        pass

    @property
    def parsed(self) -> ParsedSequence:
        return self._parsed


class PurePosixPathSequence(PurePathSequence):
    pass


class PureWindowsPathSequence(PurePathSequence):
    pass
