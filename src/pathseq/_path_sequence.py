from __future__ import annotations

import pathlib
from typing import ClassVar, overload, TypeVar

from typing_extensions import (
    Self,  # PY311+
)

from ._from_disk import find_on_disk
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
        cls: type[PathSequence[pathlib.Path]], path: str
    ) -> PathSequence[pathlib.Path]: ...

    @overload
    @classmethod
    def from_disk(
        cls: type[PathSequence[PathT]], path: PathT
    ) -> PathSequence[PathT]: ...

    @classmethod
    def from_disk(
        cls, path: str | PathT
    ) -> PathSequence[pathlib.Path] | PathSequence[PathT]:
        """Create a sequence using the ranges of files that exist on disk.

        Each file number sequence in the path sequence will be ordered numerically.

        Raises:
            IncompleteDimensionError: When one or more dimensions in
            a multi-dimension sequence does not have a consistent number of
            files in each other dimension.
        """
        if isinstance(path, str):
            _path = cls._pathlib_type(path)
        else:
            _path = path

        parsed = parse_path_sequence(_path.name)
        ranges = find_on_disk(_path, parsed)
        new = parsed.__class__(
            parsed.stem,
            parsed.prefix_separator,
            ranges,
            parsed.inter_ranges,
            parsed.suffixes,
        )
        return cls(_path.with_name(str(new)))
