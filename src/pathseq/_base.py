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

from ._ast import (
    ParsedLooseSequence,
    ParsedSequence,
    RangesEndName,
    RangesInName,
    RangesStartName,
)
from ._error import ParseError
from ._file_num_seq import FileNumSequence
from ._from_disk import find_on_disk
from ._formatter import FileNumberFormatter, RegexFormatter

Segment: TypeAlias = Union[str, os.PathLike[str]]
PurePathT_co = TypeVar(
    "PurePathT_co",
    covariant=True,
    bound=pathlib.PurePath,
)


class BasePurePathSequence(Sequence[PurePathT_co], metaclass=abc.ABCMeta):
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
        """Path sequences are immutable, so can be hashed and used as dictionary keys."""
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

        .. code-block:: pycon

            >>> s = PathSequence('/path/to/image.1-3####.exr')
            >>> s.parts
            ('/', 'path', 'to', 'image.1-3####.exr')
        """
        return self._path.parts

    @property
    def name(self) -> str:
        """A string representing the final path component, excluding the drive and root.

        Given that a sequence's final path component must be the sequence's files,
        the name will always be a valid sequence string.

        .. code-block:: pycon

            >>> PurePathSequence('/path/to/image.1-3####.exr').name
            'image.1-3####.exr'
        """
        return self._path.name

    @property
    def stem(self) -> str:
        """The name, without any ranges, suffixes, or range strings.

        .. code-block:: pycon

            >>> PurePathSequence('/path/to/images.1-3####.exr').stem
            'images'
        """
        return self._parsed.stem

    @property
    def file_num_seqs(
        self,
    ) -> Sequence[FileNumSequence[int] | FileNumSequence[Decimal]]:
        """All file number sequences in the name.

        .. code-block:: pycon

            >>> PurePathSequence('/path/to/texture.1011-1012<UDIM>_1-3#.tex').file_num_seqs
            (FileNumSequence('1011-1012'), FileNumSequence('1-3'))
        """
        ranges = tuple(
            x.file_nums
            for x in self._parsed.ranges.ranges
            if not isinstance(x.file_nums, str)
        )
        if len(ranges) != len(self._parsed.ranges.ranges):
            raise TypeError(
                "Cannot get the file number sequences of a path sequence with incomplete ranges."
            )

        return ranges

    @property
    def suffix(self) -> str:
        """The file extension of the paths in the sequence.

        A simple path sequence will always have a file extension.
        Therefore this will never return the empty string.

        .. code-block:: pycon

            >>> PurePathSequence('/path/to/image.1-3####.exr').suffix
            '.exr'
        """
        suffixes = self.suffixes
        if not suffixes:
            return ""

        return suffixes[-1]

    @property
    def suffixes(self) -> Sequence[str]:
        """A list of the file extensions of any path in the sequence.

        .. code-block:: pycon

            >>> PurePathSequence('/path/to/file.1-3####.tar.gz').suffixes
            ('.tar', '.gz')
        """
        return self._parsed.suffixes

    @property
    def parents(self) -> Sequence[PurePathT_co]:
        """An immutable sequence providing access to the logical ancestors of the sequence.

        .. code-block:: pycon

            >>> s = PurePathSequence(PureWindowsPath('c:/path/to/images.1-3####.exr'))
            >>> s[0]
            PureWindowsPath('c:/path/to')
            >>> s[1]
            PureWindowsPath('c:/path')
            >>> s[2]
            PureWindowsPath('c:/')
        """
        return self._path.parents

    @property
    def parent(self) -> pathlib.PurePath:
        """The logical parent of the sequence.

        .. code-block:: pycon

            >>> s = PurePathSequence(PurePosixPath('/a/b/c/d.1-3#.exr'))
            >>> s.parent
            PurePosixPath('/a/b/c')
        """
        return self._path.parent

    @property
    def drive(self) -> str:
        """A string representing the drive letter or name.

        .. code-block:: pycon

            >>> PurePathSequence(PureWindowsPath('c:/Program Files/image.1-3####.exr')).drive
            'c:'
            >>> PurePathSequence(PurePosixPath('/etc/image.1-3####.exr')).drive
            ''
        """
        return self._path.drive

    @property
    def root(self) -> str:
        r"""A string representing the (local or global) root, if any.

        .. code-block:: pycon

            >>> PurePathSequence(PureWindowsPath('c:/Program Files/image.1-3####.exr')).root
            '\\'
            >>> PurePathSequence(PurePosixPath('/etc/image.1-3####.exr')).root
            '/'
        """
        return self._path.root

    @property
    def anchor(self) -> str:
        r"""The concatenation of the drive and root.

        .. code-block:: pycon

            >>> PurePathSequence(PureWindowsPath('c:/Program Files/image.1-3####.exr')).anchor
            'c:\\'
            >>> PurePathSequence(PurePosixPath('/etc/image.1-3####.exr')).anchor
            '/'
        """
        return self._path.anchor

    def as_posix(self) -> str:
        r"""Return a string representation of the sequence with forward slashes (/).

        .. code-block:: pycon

            >>> s = PurePathSequence(PureWindowsPath('c:\\windows\\images.1-3#.exr'))
            >>> str(s)
            'c:\\windows\\images.1-3#.exr'
            >>> s.as_posix()
            'c:/windows/images.1-3#.exr'
        """
        return self._path.as_posix()

    def is_relative_to(self, other: pathlib.PurePath) -> bool:
        """Return whether or not all files in this sequence are relative to the other path.

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

            .. note::

                `walk_up` is available only in Python 3.12 and newer.

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

        Raises:
            ValueError: When the given name is empty.
                Use :attr:`~.BasePurePathSequence.parent` instead.
            NotASequenceError: When the given name does not represent a sequence.
            ParseError: When the resulting path is not a valid path sequence.
        """
        return self.with_segments(self._path.with_name(name))

    def with_stem(self, stem: str) -> Self:
        """Return a new path with the :attr:`~.stem` changed.

        .. code-block:: pycon

            >>> p = PurePathSequence('images.#1-3.exr')
            >>> p.with_stem('textures')
            PurePathSequence('textures.#1-3.exr')

        Raises:
            ValueError: If the new stem is invalid.
        """
        parsed = self._parsed.with_stem(stem)
        return self.with_segments(self._path.parent, str(parsed))

    @abc.abstractmethod
    def with_file_num_seqs(
        self, *seqs: FileNumSequence[int] | FileNumSequence[Decimal]
    ) -> Self:
        """Return a new sequence with the file number sequences changed.

        Raises:
            TypeError: If the given number of file number sequences does not match
                the sequence's number of file number sequences.
        """

    def path_with_file_nums(self, *numbers: int | Decimal) -> PurePathT_co:
        """Return a path for the given file number(s) in the sequence.

        Args:
            numbers: The number to use in place of each range in the string.

        .. code-block:: pycon

            >>> p = PurePathSequence('images.1-3#.exr')
            >>> p.path_with_file_nums(5)
            PurePath('images.5.exr')
        """
        name = FileNumberFormatter(*numbers).format(self._parsed)
        return self._path.with_name(name)

    def with_suffix(self, suffix: str) -> Self:
        """Return a new path sequence with the suffix changed.

        If the given suffix is the empty string, the existing suffix will be removed.
        But if the path sequence has only one suffix,
        then a :exc:`ValueError` will be raised because removing the suffix will result in
        an invalid path sequence.

        Args:
            suffix: The new suffix to replace the existing suffix with.

        Raises:
            ValueError: If the given suffix would result in an invalid path sequence.
        """
        if not suffix:
            raise ValueError("Simple path format must have a suffix")

        parsed = self._parsed.with_suffix(suffix)
        try:
            return self.with_segments(self._path.parent, str(parsed))
        except ParseError:
            raise ValueError(
                f"Cannot use suffix '{suffix}' because"
                " it would result in an invalid path sequence"
            )

    def with_segments(self, *pathsegments: Segment) -> Self:
        """Create a new sequence object of the same type by combining the given `pathsegments`."""
        return type(self)(self._path.__class__(*pathsegments))  # type: ignore[abstract]

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

        file_num_seqs = [x.file_nums for x in self._parsed.ranges.ranges]
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
            x.file_nums[i]
            for x, i in zip(self._parsed.ranges.ranges, reversed(indexes))
        ]
        return self.path_with_file_nums(*file_nums)

    def __contains__(self, item: object) -> bool:
        """Return whether the given object exists in this path sequence."""
        if not isinstance(item, self._pathlib_type):
            return False

        pattern = re.compile(RegexFormatter().format(self._parsed))

        match = pattern.fullmatch(str(item.name))
        if not match:
            return False

        for i, range_ in enumerate(self._parsed.ranges.ranges):
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
            yield self.path_with_file_nums(*result)  # type: ignore[arg-type]

    def __len__(self) -> int:
        """Return the length of this sequence.

        If the sequence has any empty ranges, then its length is zero.

        .. code-block:: pycon

            >>> len(PurePathSequence('images.####.exr'))
            0
        """
        result = 1

        for x in self._parsed.ranges.ranges:
            result *= len(x.file_nums)

        return result

    def has_subsamples(self) -> bool:
        """Check whether this path sequence contains any decimal file numbers."""
        return any(r.has_subsamples(r) for r in self._parsed.ranges.ranges)


PathT_co = TypeVar("PathT_co", covariant=True, bound=pathlib.Path)


class BasePathSequence(BasePurePathSequence[PathT_co], metaclass=abc.ABCMeta):
    """A sequence of Path objects.

    Raises:
        NotASequenceError: When the given path does not represent a sequence,
            but a regular path.
        ParseError: When the given path is not a valid path sequence.
    """

    _pathlib_type: ClassVar[type[pathlib.Path]] = pathlib.Path

    @overload
    def __init__(self: BasePathSequence[pathlib.Path], path: str) -> None: ...

    @overload
    def __init__(self: BasePathSequence[PathT_co], path: PathT_co) -> None: ...

    def __init__(self, path: PathT_co | str) -> None:
        super().__init__(path)

    def expanduser(self) -> Self:
        """Return a new sequence with expanded ``~`` and ``~user`` constructs.

        The expansion will be as returned by :func:`os.path.expanduser`.

        Raises:
            RuntimeError: If a home directory can't be resolved.
        """
        return self.with_segments(self._path.expanduser())

    def absolute(self) -> Self:
        """Return a new sequence with the sequence's paths made absolute.

        Normalisation and symlink resolution are not performed.
        """
        return self.with_segments(self._path.absolute())

    def with_existing_paths(self) -> Self:
        """Return a new a sequence using the ranges of files that exist on disk.

        Each file number sequence in the path sequence will be ordered numerically.

        Raises:
            IncompleteDimensionError: When one or more dimensions in
                a multi-dimension sequence does not have a consistent number of
                files in each other dimension.
        """
        seqs = find_on_disk(self._path, self._parsed)
        return self.with_file_num_seqs(*seqs)
