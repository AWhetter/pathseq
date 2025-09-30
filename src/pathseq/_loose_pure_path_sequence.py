from __future__ import annotations

from collections.abc import Iterator, Sequence
from decimal import Decimal
import itertools
import os
import pathlib
import re
import sys
from typing import ClassVar, overload, TypeVar, Union

from typing_extensions import (
    Self,  # PY311
    TypeAlias,  # PY310
)

from ._ast import PaddedRange, RangesEndName, RangesInName, RangesStartName
from ._error import ParseError
from ._file_num_seq import FileNumSequence
from ._parse_loose_path_sequence import parse_path_sequence

Segment: TypeAlias = Union[str, os.PathLike[str]]
PathT_co = TypeVar(
    "PathT_co", covariant=True, bound=pathlib.PurePath, default=pathlib.PurePath
)


class LoosePurePathSequence(Sequence[PathT_co]):
    """A generic class that represents a path sequence in the system's path flavour.

    Instantiating this class creates either a :class:`PurePosixPathSequence`
    or a :class:`PureWindowsPathSequence`.

    Differences:
    * No __bytes__ because not a filesystem path.
    * No __fspath__ because not a filesystem path.
    * No as_uri because not a filesystem path.
    * No __truediv__ (only __rtruediv__) or joinpath because sequences are supported only in
      the last part of the path.
    * No match because not a filesystem path that can be matched against.

    Raises:
        NotASequenceError: When the given path does not represent a sequence.
    """

    _pathlib_type: ClassVar[type[pathlib.PurePath]] = pathlib.PurePath
    _path: PathT_co

    @overload
    def __init__(self: LoosePurePathSequence[pathlib.PurePath], path: str) -> None: ...

    @overload
    def __init__(self: LoosePurePathSequence[PathT_co], path: PathT_co) -> None: ...

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
        parsed = self._parsed
        return parsed.suffixes

    # Note: Can be the empty string
    @property
    def stem(self) -> str:
        parsed = self._parsed
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

    if sys.version_info >= (3, 12):

        def relative_to(self, other: Segment, *, walk_up: bool = False) -> Self:
            if other == str(self):
                raise ValueError("Cannot make a path sequence relative to itself")

            return type(self)(self._path.relative_to(other, walk_up=walk_up))
    else:

        def relative_to(self, other: Segment) -> Self:
            if other == str(self):
                raise ValueError("Cannot make a path sequence relative to itself")

            return type(self)(self._path.relative_to(other))

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
        an invalid path sequence.

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

    # Sequence specific methods
    @overload
    def __getitem__(self, index: int) -> PathT_co: ...

    @overload
    def __getitem__(self, index: slice) -> Sequence[PathT_co]: ...

    def __getitem__(self, index: int | slice) -> PathT_co | Sequence[PathT_co]:
        file_num_seqs = [x.file_nums for x in self._parsed.ranges if x.file_nums]
        if len(file_num_seqs) != len(self._parsed.ranges):
            raise ValueError(
                "Cannot index a path sequence with one or more unknown ranges"
            )

        if isinstance(index, slice):
            return tuple(itertools.islice(self, *index.indices(len(self))))

        start = index
        if start < 0:
            start += len(self)
            if start < 0:
                raise IndexError("index out of range")
        elif start > len(self):
            raise IndexError("index out of range")

        indexes = [0 for _ in file_num_seqs]
        for i, file_num_seq in enumerate(reversed(file_num_seqs), start=1):
            next_idx = start % len(file_num_seq)
            indexes[-i] = next_idx
            start -= next_idx

        assert start == 0
        file_nums = [
            x.file_nums[i] for x, i in zip(self._parsed.ranges, reversed(indexes))
        ]
        return self.format(*file_nums)

    def __contains__(self, item: object) -> bool:
        if not isinstance(item, self._pathlib_type):
            return False

        pattern = re.compile(self._parsed.as_regex())

        match = pattern.fullmatch(str(item.name))
        if not match:
            return False

        for i, range_ in enumerate(self._parsed.ranges):
            group_name = f"range{i}"
            group = match.group(group_name)
            assert isinstance(group, str), "Got an unexpected type from regex group"

            file_num_seq = range_.file_nums
            if FileNumSequence.has_subsamples(file_num_seq):
                if Decimal(group) not in file_num_seq:
                    return False
            else:
                if int(group) not in file_num_seq:
                    return False

        return True

    def __iter__(self) -> Iterator[PathT_co]:
        iterators = (iter(x) for x in self.file_num_seqs)
        # TODO: Check that this isn't using mega amounts of memory
        for result in itertools.product(*iterators):
            # https://github.com/python/typeshed/issues/13490
            yield self.format(*result)  # type: ignore[arg-type]

    def __len__(self) -> int:
        result = 1

        for x in self._parsed.ranges:
            result *= len(x.file_nums)

        return result

    # PathSeq specific operations

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
        self, *seqs: FileNumSequence[int] | FileNumSequence[Decimal]
    ) -> Self:
        if len(seqs) != len(self._parsed.ranges):
            raise TypeError(
                f"Need {len(self._parsed.ranges)} sequences, but got {len(seqs)}"
            )

        new_ranges = tuple(
            PaddedRange(seq, range_.pad_format)
            for seq, range_ in zip(seqs, self._parsed.ranges)
        )
        new = self._parsed.__class__(
            stem=self._parsed.stem,
            prefix_separator=self._parsed.prefix_separator,  # type: ignore[arg-type]
            ranges=new_ranges,
            inter_ranges=self._parsed.inter_ranges,
            postfix=self._parsed.postfix,  # type: ignore[arg-type]
            suffixes=self._parsed.suffixes,
        )
        return self.__class__(self._path.with_name(str(new)))

    def has_subsamples(self) -> bool:
        """Check whether this path sequences contains any decimal file numbers."""
        return any(r.has_subsamples(r) for r in self._parsed.ranges)

    @property
    def parsed(self) -> RangesStartName | RangesInName | RangesEndName:
        return self._parsed
