from __future__ import annotations

from collections.abc import Iterable, Sequence
from decimal import Decimal
import os
import pathlib
from typing import NamedTuple, overload, Union

from typing_extensions import (
    Self,  # PY311
    TypeAlias,  # PY310
    TypeGuard,  # PY310
)

from ._file_num_set import FileNumSet, GRAMMAR as RANGE_GRAMMAR, SequenceReducer
from ._parsing import parse_path_sequence

Segment: TypeAlias = Union[str, os.PathLike[str], "PurePathSequence"]


# TODO: What about sequences that do not have the range baked into the string?
class PurePathSequence:
    """A generic class that represents a path sequence in the system's path flavour.

    Instantiating this class creates either a :class:`PurePosixPathSequence`
    or a :class:`PureWindowsPathSequence`.

    Differences:
    * No __bytes__ because not a filesystem path.
    * No __fspath__ because not a filesystem path.
    * No as_uri because not a filesystem path.
    """
    def __new__(cls, *args, **kwargs):
        if cls is PurePathSequence:
            cls = PureWindowsPathSequence if os.name == "nt" else PurePosixPathSequence
        return object.__new__(cls)

    def __init__(self, *pathsegments: Segment) -> None:
        self._path = pathlib.PurePath(*pathsegments)
        self._parsed = None

    def _parsed_name(self):
        if not self._parsed:
            name = self._path.name
            self._parsed = parse_path_sequence(name)

        return self._parsed

    # General properties
    def __eq__(self, other: object) -> bool:
        if not isinstance(other, self.__class__):
            return NotImplemented

        return self._parsed_name == other._parsed_name

    # TODO: Sequences with the same range should match.
    # TODO: Ranges don't have these so maybe sequences shouldn't either
    def __lt__(self, other: object) -> bool:
        if not isinstance(other, self.__class__):
            return NotImplemented

        return self._path < other._path

    def __le__(self, other: object) -> bool:
        if not isinstance(other, self.__class__):
            return NotImplemented

        return self._path <= other._path

    def __gt__(self, other: object) -> bool:
        if not isinstance(other, self.__class__):
            return NotImplemented

        return self._path > other._path

    def __ge__(self, other: object) -> bool:
        if not isinstance(other, self.__class__):
            return NotImplemented

        return self._path >= other._path

    def __repr__(self):
        return "{}({!r})".format(self.__class__.__name__, self.as_posix())

    def __str__(self):
        return str(self._path)

    def __hash__(self):
        return hash((type(self), self._path))

    # Path operations
    # TODO: Remove and explain why
    def __truediv__(self, key):
        try:
            return self.with_segments(self, key)
        except TypeError:
            return NotImplemented

    def __rtruediv__(self, key):
        try:
            return self.with_segments(key, self)
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

    # TODO: What about when there is only the name and ranges?
    @property
    def suffix(self) -> str:
        parsed = self._parsed_name()
        return parsed.suffixes[-1]

    @property
    def suffixes(self) -> Sequence[str]:
        parsed = self._parsed_name()
        return parsed.suffixes

    # TODO: What about when there is only the suffixes and ranges?
    @property
    def stem(self) -> str:
        parsed = self._parsed_name()
        return parsed.stem

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

    def match(self, path_pattern: str, *, case_sensitive: bool | None = None) -> bool:
        raise NotImplementedError

    def relative_to(self, other: Segment, *, walk_up: bool = False) -> Self:
        return self._path.relative_to(other, walk_up=walk_up)

    def with_name(self, name: str) -> Self:
        return self.with_segments(self._path.with_name(name))

    def with_stem(self, stem: str) -> Self:
        return self.with_segments(self._path.with_stem(stem))

    def with_suffix(self, suffix: str) -> Self:
        raise NotImplementedError

    def joinpath(self, *other: Segment) -> Self:
        raise NotImplementedError

    def with_segments(self, *pathsegments: Segment) -> Self:
        return type(self)(*pathsegments)

    # Sequence specific methods
    # TODO: Should we inherit from Sequence or similar?
    @overload
    def __getitem__(self, index: int) -> pathlib.PurePath:
        ...

    @overload
    def __getitem__(self, index: slice) -> Self:
        ...

    def __getitem__(self, index):
        pass

    def __iter__(self) -> Iterable[pathlib.PurePath]:
        # TODO: Note order of iteration over multi-dimension ranges
        ranges: list[FileNumSet | None] = [
            x.file_num_set for x in self._parsed_name().ranges[::2]
        ]

        if not ranges:
            yield self._path
            return

        iterators = [iter(x if x is not None else (None,)) for x in ranges]
        result = [next(iterator) for iterator in iterators]
        while True:
            # Exhaust the first iterator
            iterator = iterators[0]
            for x in iterator:
                result[0] = x
                yield self.path(*result)

            for i, iterator in enumerate(iterators[1:], start=1):
                try:
                    result[i] = next(iterator)
                except StopIteration:
                    pass
                else:
                    # The earlier ranges have been exhausted, so reset them.
                    iterators[:i] = [iter(x if x is not None else (None,)) for x in ranges[:i]]
                    result[:i] = [next(iterator) for iterator in iterators[:i]]
                    break
            else:
                # All ranges have been exhausted
                break

    def __len__(self) -> int:
        result = 1

        for x in self._parsed_name():
            if isinstance(x, PaddedRange):
                # TODO: Note that an unset range is considered hardcoded.
                if x.file_num_set is not None:
                    result *= len(x.file_num_set)

        return result

    # TODO: Document how 'name' is constructed (stem, padding, suffix)
    @property
    def padding(self) -> str:
        """The right-most padding of the final path component.

        Returns:
            The empty string when there is no padding.
        """

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
    def from_paths(self, paths: Iterable[os.PathLike[str]]) -> Iterable[Self | pathlib.PurePath]:
        """Create one or more path sequences from a list of paths."""

    def path(self, *numbers: int | Decimal | None) -> Self | pathlib.PurePath:
        """Return a path for the given file number(s) in the sequence.

        None means don't fill in this range.
        """

    # TODO: Or just via part objects?
    def file_num_sets(self) -> tuple[FileNumSet] | None:
        """All file number sets in the final path component."""

    def with_file_num_sets(self, sets: Iterable[FileNumSet]) -> Self:
        pass

    # TODO: Make these classes generic
    @staticmethod
    def has_subsamples(seq: Self) -> TypeGuard[Self[Decimal]]:
        pass


class PurePosixPathSequence(PurePathSequence):
    pass


class PureWindowsPathSequence(PurePathSequence):
    pass
