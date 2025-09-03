from __future__ import annotations

from collections.abc import Iterable, Iterator, Sequence
from decimal import Decimal
import itertools
import os
import pathlib
from typing import ClassVar, overload, TypeVar, Union

from typing_extensions import (
    Self,  # PY311
    TypeAlias,  # PY310
)

from ._ast import PaddedRange, ParsedSequence
from ._error import ParseError
from ._file_num_seq import FileNumSequence
from ._parse_path_sequence import parse_path_sequence

Segment: TypeAlias = Union[str, os.PathLike[str]]
PathT_co = TypeVar(
    "PathT_co", covariant=True, bound=pathlib.PurePath, default=pathlib.PurePath
)


class PurePathSequence(Sequence[PathT_co]):
    """A generic class that represents a path sequence.

    Raises:
        NotASequenceError: When the given path does not represent a sequence.
    """

    _pathlib_type: ClassVar[type[pathlib.PurePath]] = pathlib.PurePath
    _path: PathT_co

    @overload
    def __init__(self: PurePathSequence[pathlib.PurePath], path: str) -> None: ...

    @overload
    def __init__(self: PurePathSequence[PathT_co], path: PathT_co) -> None: ...

    def __init__(self, path: PathT_co | str) -> None:
        if isinstance(path, str):
            self._path = self._pathlib_type(path)  # type: ignore[assignment]
        else:
            self._path = path
        self._parsed = parse_path_sequence(self._path.name)

    # General properties
    def __eq__(self, other: object) -> bool:
        if not isinstance(other, self.__class__):
            return NotImplemented

        return self._path.parent == other._path.parent and self._parsed == other._parsed

    def __repr__(self) -> str:
        return "{}({!r})".format(self.__class__.__name__, self.as_posix())

    def __str__(self) -> str:
        return str(self._path)

    def __hash__(self) -> int:
        return hash((type(self), self._path.parent, self._parsed))

    # Path operations
    def __rtruediv__(self, key: Segment) -> Self:
        try:
            return self.with_segments(key, self._path)
        except TypeError:
            return NotImplemented

    @property
    def parts(self) -> tuple[str, ...]:
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
        return type(self)(self._path.__class__(*pathsegments))

    # Sequence operations
    @overload
    def __getitem__(self, index: int) -> PathT_co: ...

    @overload
    def __getitem__(self, index: slice) -> Self: ...

    def __getitem__(self, index: int | slice) -> PathT_co | Self:
        raise NotImplementedError

    def __contains__(self, item: object) -> bool:
        raise NotImplementedError

    def __iter__(self) -> Iterator[PathT_co]:
        iterators = (iter(x) for x in self.file_num_seqs)
        # TODO: Check that this isn't using mega amounts of memory
        for result in itertools.product(*iterators):
            # https://github.com/python/typeshed/issues/13490
            yield self.format(*result)  # type: ignore[arg-type]

    def __len__(self) -> int:
        result = 1

        for x in self._parsed.ranges:
            if isinstance(x, PaddedRange):
                if x.file_nums is None:
                    raise ValueError(
                        "Cannot calculate the length of a path sequence"
                        " with one or more unknown ranges"
                    )

                result *= len(x.file_nums)

        return result

    # PathSeq specific operations

    @property
    def paddings(self) -> tuple[str]:
        """All padding strings in the final path component."""
        raise NotImplementedError

    # TODO: Or maybe set via part objects?
    def with_paddings(self, *paddings: str) -> Self:
        """Set new pads.

        Raises:
            ValueError: When the number of provided padding strings does not match
                the number of padding strings in the final path component.
        """
        raise NotImplementedError

    @classmethod
    def from_paths(cls, paths: Iterable[os.PathLike[str]]) -> Iterable[Self]:
        """Create one or more path sequences from a list of paths."""
        raise NotImplementedError

    def format(self, *numbers: int | Decimal) -> PathT_co:
        """Return a path for the given file number(s) in the sequence.

        Args:
            The number to use in place of each range in the string.
        """
        name = self._parsed.format(*numbers)
        return self._path.with_name(name)

    @property
    def file_num_seqs(
        self,
    ) -> tuple[FileNumSequence[int] | FileNumSequence[Decimal], ...]:
        """All file number sequences in the final path component."""
        ranges = tuple(
            x.file_nums for x in self._parsed.ranges if not isinstance(x.file_nums, str)
        )
        if len(ranges) != len(self._parsed.ranges):
            raise TypeError(
                "Cannot get the file number sequences of a path sequence with incomplete ranges."
            )

        return ranges

    def with_file_num_seqs(
        self, seqs: Iterable[FileNumSequence[int] | FileNumSequence[Decimal]]
    ) -> Self:
        raise NotImplementedError

    def has_subsamples(self) -> bool:
        raise NotImplementedError

    @property
    def parsed(self) -> ParsedSequence:
        return self._parsed
