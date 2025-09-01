from __future__ import annotations

from collections.abc import Iterable
import pathlib
from typing import ClassVar, overload, TypeVar

from typing_extensions import (
    Self,  # PY311+
)

from ._pure_path_sequence import PurePathSequence

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

    @classmethod
    def from_disk(cls, path: PathT_co | str) -> Self:
        """Create a sequence using the ranges of files that exist.

        Raises:
            IncompleteDimensionError: When one dimension in a multi-dimension sequence
            does not have a consistent number of files in each other dimension.
        """
        # pattern = self._parsed.as_glob()
        # paths = self._pathlib_type.parent.glob(pattern)
        # TODO: then regex match, then parse into range sets
        raise NotImplementedError

    @classmethod
    def glob(cls, pattern: str | pathlib.PurePath) -> Iterable[Self | pathlib.Path]:
        """Glob the given relative pattern, yielding all matching paths and sequences."""
        raise NotImplementedError
