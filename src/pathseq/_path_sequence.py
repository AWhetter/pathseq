from __future__ import annotations

from collections.abc import Iterable
from decimal import Decimal
import functools
import operator
import pathlib
import re
from typing import ClassVar, overload, TypeVar

from typing_extensions import (
    Self,  # PY311+
)

from ._ast import PaddedRange
from ._error import IncompleteDimensionError
from ._file_num_seq import FileNumSequence
from ._parse_path_sequence import parse_path_sequence
from ._pure_path_sequence import PurePathSequence

PathT = TypeVar("PathT", bound=pathlib.Path, default=pathlib.Path)
PathT_co = TypeVar("PathT_co", covariant=True, bound=pathlib.Path, default=pathlib.Path)


class PathSequence(PurePathSequence[PathT_co]):
    """blah

    TODO: Note that path sequences are not filesystem paths and therefore
    only a subset of filesystem operations are available.
    """

    _pathlib_type: ClassVar[type[pathlib.Path]] = pathlib.Path
    _path: PathT_co

    @overload
    def __init__(self: PathSequence[pathlib.Path], path: str) -> None: ...

    @overload
    def __init__(self: PathSequence[PathT_co], path: PathT_co) -> None: ...

    def __init__(self, path: PathT_co | str) -> None:
        super().__init__(path)

    def expanduser(self) -> Self:
        return self.__class__(self._path.expanduser())

    def absolute(self) -> Self:
        return self.__class__(self._path.absolute())

    @overload
    @classmethod
    def from_disk(
        cls: type[PurePathSequence[pathlib.PurePath]], path: str
    ) -> PurePathSequence[pathlib.PurePath]: ...

    @overload
    @classmethod
    def from_disk(
        cls: type[PurePathSequence[PathT]], path: PathT
    ) -> PurePathSequence[PathT]: ...

    @classmethod
    def from_disk(
        cls, path: str | PathT
    ) -> PurePathSequence[pathlib.PurePath] | PurePathSequence[PathT]:
        """Create a sequence using the ranges of files that exist.

        Each file number sequence in the path sequence will be ordered.

        Raises:
            IncompleteDimensionError: When one dimension in a multi-dimension sequence
            does not have a consistent number of files in each other dimension.
        """
        if isinstance(path, str):
            _path = cls._pathlib_type(path)
        else:
            _path = path

        parsed = parse_path_sequence(_path.name)
        file_str_sets: list[set[str]] = [set() for _ in range(len(parsed.ranges))]
        paths = _path.parent.glob(parsed.as_glob())
        pattern = re.compile(parsed.as_regex())
        num_paths = 0
        for found in paths:
            raw_tokens = pattern.split(found.name)
            if not raw_tokens:
                continue

            num_paths += 1
            assert raw_tokens[0], "Expected a stem but got a range"
            assert raw_tokens[-1], "Expected file suffixes but path ends with a range"

            for i, raw_token in enumerate(raw_tokens[1:]):
                if i % 2 == 1:
                    file_str_sets[i // 2].add(raw_token)

        expected = functools.reduce(
            operator.mul, (len(nums) for nums in file_str_sets), 1
        )
        if num_paths != expected:
            raise IncompleteDimensionError(
                f"Sequence '{path}' contains an inconsistent number of files across one or more dimensions."
            )

        file_num_seqs = []
        for file_str_set in file_str_sets:
            file_num_seq: FileNumSequence[int] | FileNumSequence[Decimal]
            if any("." in file_str for file_str in file_str_set):
                file_num_seq = FileNumSequence.from_file_nums(
                    sorted(Decimal(file_str) for file_str in file_str_set)
                )
            else:
                file_num_seq = FileNumSequence.from_file_nums(
                    sorted(int(file_str) for file_str in file_str_set)
                )

            file_num_seqs.append(file_num_seq)

        new = parsed.__class__(
            parsed.stem,
            parsed.prefix_separator,
            tuple(
                PaddedRange(file_num_seq, range_.pad_format)  # type: ignore[misc]
                for file_num_seq, range_ in zip(file_num_seqs, parsed.ranges)
            ),
            parsed.inter_ranges,
            parsed.suffixes,
        )
        return cls(_path.with_name(str(new)))

    @classmethod
    def glob(cls, pattern: str | pathlib.PurePath) -> Iterable[Self | pathlib.Path]:
        """Glob the given relative pattern, yielding all matching paths and sequences."""
        raise NotImplementedError
