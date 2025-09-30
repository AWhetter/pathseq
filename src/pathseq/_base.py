from __future__ import annotations

import abc
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

from ._ast import ParsedSequence, RangesEndName, RangesInName, RangesStartName
from ._error import ParseError
from ._file_num_seq import FileNumSequence
from ._from_disk import find_on_disk
from ._parse_loose_path_sequence import ParsedLooseSequence

Segment: TypeAlias = Union[str, os.PathLike[str]]
PurePathT_co = TypeVar(
    "PurePathT_co", covariant=True, bound=pathlib.PurePath, default=pathlib.PurePath
)
T = TypeVar("T", ParsedSequence, RangesEndName, RangesInName, RangesStartName)


class BasePurePathSequence(abc.ABC, Sequence[PurePathT_co]):
    """A generic class that represents a path sequence.

    Raises:
        NotASequenceError: When the given path does not represent a sequence.
        ParseError: When the given path is not a valid path sequence.
    """

    _pathlib_type: ClassVar[type[pathlib.PurePath]] = pathlib.PurePath
    _path: PurePathT_co
    _parsed: ParsedSequence | ParsedLooseSequence

    @overload
    def __init__(self: BasePurePathSequence[pathlib.PurePath], path: str) -> None: ...

    @overload
    def __init__(
        self: BasePurePathSequence[PurePathT_co], path: PurePathT_co
    ) -> None: ...

    def __init__(self, path: PurePathT_co | str) -> None:
        if isinstance(path, str):
            self._path = self._pathlib_type(path)  # type: ignore[assignment]
        else:
            self._path = path
        self._parsed = self._parse(self._path.name)

    @abc.abstractmethod
    def _parse(self, name: str) -> ParsedSequence | ParsedLooseSequence:
        pass

    # General properties
    def __eq__(self, other: object) -> bool:
        """Check for equality with another object.

        Two path sequences are considered equal if they contain the same paths
        in the same order, even if their string representation differs:

        .. code-block:: pycon
            >>> seq_a = PathSequence("/path/to/image.1-3####.exr")
            >>> seq_b = PathSequence("/path/to/image.1,2,3####.exr")
            >>> seq_a == seq_b
            True
        """
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
        """A tuple giving access to the sequence's various components.

        Example:
        .. code-block:: pycon

            >>> s = PathSequence('/path/to/image.1-3####.exr')
            >>> s.parts
            ('/', 'path', 'to', 'image.1-3####.exr')

        See also:
            :attr:`pathlib.PurePath.parts`
        """
        return self._path.parts

    @property
    def drive(self) -> str:
        """A string representing the drive letter or name.

        Example:
        .. code-block:: pycon
            >>> PurePathSequence(PureWindowsPath('c:/Program Files/image.1-3####.exr')).drive
            'c:'
            >>> PurePathSequence(PurePosixPath('/etc/image.1-3####.exr')).drive
            ''

        See also:
            :attr:`pathlib.PurePath.drive`
        """
        return self._path.drive

    @property
    def root(self) -> str:
        r"""A string representing the (local or global) root, if any.

        Example:
        .. code-block:: pycon
            >>> PurePathSequence(PureWindowsPath('c:/Program Files/image.1-3####.exr')).root
            '\\'
            >>> PurePathSequence(PurePosixPath('/etc/image.1-3####.exr')).root
            '/'

        See also:
            :attr:`pathlib.PurePath.root`
        """
        return self._path.root

    @property
    def anchor(self) -> str:
        r"""The concatenation of the drive and root.

        Example:
        .. code-block:: pycon
            >>> PurePathSequence(PureWindowsPath('c:/Program Files/image.1-3####.exr')).anchor
            'c:\\'
            >>> PurePathSequence(PurePosixPath('/etc/image.1-3####.exr')).anchor
            '/'

        See also:
            :attr:`pathlib.PurePath.anchor`
        """
        return self._path.anchor

    @property
    def name(self) -> str:
        """A string representing the final path component, excluding the drive and root.

        Given that a sequence's final path component must be the sequence's files,
        the name will always be a valid sequence string.

        Example:
        .. code-block:: pycon
            >>> PurePathSequence('/path/to/image.1-3####.exr').name
            'image.1-3####.exr'

        See also:
            :attr:`pathlib.PurePath.name`
        """
        return self._path.name

    @property
    def suffix(self) -> str:
        """The file extension of the paths in the sequence.

        A strict path sequence will always have a file extension.
        Therefore this will never return the empty string.

        See also:
            :attr:`pathlib.PurePath.suffix`
        """
        suffixes = self.suffixes
        if not suffixes:
            return ""

        return suffixes[-1]

    @property
    def suffixes(self) -> Sequence[str]:
        """A list of the file extensions of any path in the sequence.

        See also:
            :attr:`pathlib.PurePath.suffixes`
        """
        return self._parsed.suffixes

    @property
    def stem(self) -> str:
        """The final path component, without any ranges, suffixes, or range strings.

        Example:
        .. code-block:: pycon
            >>> PurePathSequence('/path/to/images.1-3####.exr').stem
            'images'
        """
        return self._parsed.stem

    @property
    def parents(self) -> Sequence[pathlib.PurePath]:
        """An immutable sequence providing access to the logical ancestors of the sequence.

        Example:
        .. code-block:: pycon
            >>> s = PurePathSequence(PureWindowsPath('c:/path/to/images.1-3####.exr'))
            >>> s[0]
            PureWindowsPath('c:/path/to')
            >>> s[1]
            PureWindowsPath('c:/path')
            >>> s[2]
            PureWindowsPath('c:/')

        See also:
            :attr:`pathlib.PurePath.parents`
        """
        return self._path.parents

    @property
    def parent(self) -> pathlib.PurePath:
        """The logical parent of the sequence.

        Example:
        .. code-block:: pycon
            >>> s = PurePathSequence(PurePosixPath('/a/b/c/d.1-3#.exr'))
            >>> s.parent
            PurePosixPath('/a/b/c')

        See also:
            :attr:`pathlib.PurePath.parent`
        """
        return self._path.parent

    def as_posix(self) -> str:
        r"""Return a string representation of the sequence with forward slashes (/).

        Example:
        .. code-block:: pycon
            >>> s = PurePathSequence(PureWindowsPath('c:\\windows\\images.1-3#.exr'))
            >>> str(s)
            'c:\\windows\\images.1-3#.exr'
            >>> s.as_posix()
            'c:/windows/images.1-3#.exr'

        See also:
            :meth:`pathlib.PurePath.as_posix`
        """
        return self._path.as_posix()

    def is_relative_to(self, other: pathlib.PurePath) -> bool:
        """Return whether or not all files in this sequence are relative to the other path.

        See also:
            :meth:`pathlib.PurePath.is_relative_to`

        Raises:
            ValueError: If this path sequence is given.
                The paths in a sequence cannot be relative to a sequence.
        """
        if self._path == other:
            raise ValueError("Cannot check if a path sequence is relative to itself")

        return self._path.is_relative_to(other) and not self._path == other

    if sys.version_info >= (3, 12):

        def relative_to(self, other: Segment, *, walk_up: bool = False) -> Self:
            """Compute a version of this path relative to the path represented by ``other``.

            Raises:
                ValueError: When this sequence cannot be relative to the given path.
            """
            if other == str(self):
                raise ValueError("Cannot make a path sequence relative to itself")

            return self.with_segments(self._path.relative_to(other, walk_up=walk_up))
    else:

        def relative_to(self, other: Segment) -> Self:
            """Compute a version of this path relative to the path represented by ``other``.

            Raises:
                ValueError: When this sequence cannot be relative to the given path.
            """
            if other == str(self):
                raise ValueError("Cannot make a path sequence relative to itself")

            return type(self)(self._path.relative_to(other))

    def with_name(self, name: str) -> Self:
        """Return a new sequence with the :attr:`~.name` changed.

        Given that a sequence's final path component must be the sequence's files,
        the given name must also be a valid sequence string.
        In addition, unlike :meth:`pathlib.PurePath.with_name`,
        a :exc:`ValueError` will never be raised because a path sequence
        must always have a name.

        Raises:
            NotASequenceError: When the given name does not represent a sequence.
            ParseError: When the resulting path is not a valid path sequence.
        """
        return self.with_segments(self._path.with_name(name))

    def with_stem(self, stem: str) -> Self:
        """Return a new path with the :attr:`~.stem` changed.

        Unlike :meth:`pathlib.PurePath.with_name`,
        a :exc:`ValueError` will never be raised because a path sequence
        must always have a stem, even if it was previously empty.

        Example:
        .. code-block:: pycon
            >>> p = PurePathSequence('images.#1-3.exr')
            >>> p.with_stem('textures')
            PurePathSequence('textures.#1-3.exr')
        """
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
        """Create a new sequence object of the same type by combining the given `pathsegments`.

        See also:
            :meth:`pathlib.PurePath.with_segments`
        """
        return type(self)(self._path.__class__(*pathsegments))  # type: ignore[abstract]

    # Sequence operations
    @overload
    def __getitem__(self, index: int) -> PurePathT_co: ...

    @overload
    def __getitem__(self, index: slice) -> Sequence[PurePathT_co]: ...

    def __getitem__(self, index: int | slice) -> PurePathT_co | Sequence[PurePathT_co]:
        """Return one or more paths from this path sequence.

        Note:
            Negative slice steps are not supported at this time.

        Returns:
            PurePath: When indexed with an integer.
            Sequence: An immutable sequence of paths from this path sequence
                when indexed with a :class:`slice`.
        """
        if isinstance(index, slice):
            return tuple(itertools.islice(self, *index.indices(len(self))))

        if not self:
            raise IndexError("Path sequence is empty so index is out of range")

        file_num_seqs = [x.file_nums for x in self._parsed.ranges]
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
        """Return whether the given object exists in this path sequence."""
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

    def __iter__(self) -> Iterator[PurePathT_co]:
        """Iterate over the paths in this sequence."""
        iterators = (iter(x) for x in self.file_num_seqs)
        # TODO: Swap this out for manual looping so that are aren't using mega amounts of memory
        for result in itertools.product(*iterators):
            # https://github.com/python/typeshed/issues/13490
            yield self.format(*result)  # type: ignore[arg-type]

    def __len__(self) -> int:
        """Return the length of this sequence.

        If the sequence has any empty ranges, then its length is zero.

        Example:
        .. code-block:: pycon
            >>> len(PurePathSequence('images.####.exr'))
            0
        """
        result = 1

        for x in self._parsed.ranges:
            result *= len(x.file_nums)

        return result

    # PathSeq specific operations
    def format(self, *numbers: int | Decimal) -> PurePathT_co:
        """Return a path for the given file number(s) in the sequence.

        Args:
            The number to use in place of each range in the string.

        Example:
        .. code-block:: pycon
            >>> p = PurePathSequence('images.1-3#.exr')
            >>> p.format(5)
            PurePath('images.5.exr')
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

    @abc.abstractmethod
    def with_file_num_seqs(
        self, *seqs: FileNumSequence[int] | FileNumSequence[Decimal]
    ) -> Self:
        """Return a new sequence with the :attr:`~.file_num_seqs <file number sequences>` changed.

        Raises:
            TypeError: If the given number of file number sequences does not match
                the sequence's number of file number sequences.
        """

    def has_subsamples(self) -> bool:
        """Check whether this path sequences contains any decimal file numbers."""
        return any(r.has_subsamples(r) for r in self._parsed.ranges)


PathT_co = TypeVar("PathT_co", covariant=True, bound=pathlib.Path)


class BasePathSequence(BasePurePathSequence[PathT_co], abc.ABC):
    """A sequence of Path objects.

    Raises:
        NotASequenceError: When the given path does not represent a sequence,
            but a regular path.
        ParseError: When the given path is not a valid path sequence.
    """

    _pathlib_type: ClassVar[type[pathlib.Path]] = pathlib.Path

    def expanduser(self) -> Self:
        """Return a new sequence with expanded ``~`` and ``~user`` constructs.

        The expansion will be as returned by :func:`os.path.expanduser`.

        Raises:
            RuntimeError: If a home directory can't be resolved.
        """
        return self.with_segments(self._path.expanduser())

    def absolute(self) -> Self:
        """Return a new sequence with the path made absolute.

        Normalisation and symlink resolution is not performed.
        """
        return self.with_segments(self._path.absolute())

    def with_existing_paths(self) -> Self:
        """Create a sequence using the ranges of files that exist on disk.

        Each file number sequence in the path sequence will be ordered numerically.

        Raises:
            IncompleteDimensionError: When one or more dimensions in
            a multi-dimension sequence does not have a consistent number of
            files in each other dimension.
        """
        seqs = find_on_disk(self._path, self._parsed)
        return self.with_file_num_seqs(*seqs)
