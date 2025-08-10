from collections.abc import Iterable
import pathlib

from typing_extensions import (
    Self,  # PY311+
)

from ._pure_path_sequence import (
    PurePathSequence,
    PurePosixPathSequence,
    PureWindowsPathSequence,
)


class IncompleteDimensionError(Exception):
    """A multi-dimension sequence does not contain a consistent number of files across a dimension.

    Example:

    .. code-block:: pycon

        >>> for path in PathSequence("file.1001_1-3#.exr"):
        ...     path.touch()
        ...
        >>> for path in PathSequence("file.1002_1-2#.exr"):
        ...     path.touch()
        ...
        >>> PathSequence.from_disk("file.<UDIM>_#.exr")
        Traceback (most recent call last):
          File "<stdin>", line 1, in <module>
        IncompleteDimensionError: TODO
    """


class PathSequence(PurePathSequence):
    """blah

    TODO: Note that path sequences are not filesystem paths and therefore
    only a subset of filesystem operations are available.
    """

    _pathlib_type = pathlib.Path

    def expanduser(self) -> Self:
        return self.__class__(self._path.expanduser())

    def absolute(self) -> Self:
        return self.__class__(self._path.absolute())

    def with_exists(self) -> Self:
        """Create a sequence using the ranges of files that exist.

        Raises:
            IncompleteDimensionError: When one dimension in a multi-dimension sequence
            does not have a consistent number of files in each other dimension.
        """
        # pattern = self._parsed.as_glob()
        # paths = self._pathlib_type.parent.glob(pattern)
        # TODO: then regex match, then parse into range sets

    @classmethod
    def glob(cls, pattern: str | pathlib.PurePath) -> Iterable[Self | pathlib.Path]:
        """Glob the given relative pattern, yielding all matching paths and sequences."""


class PosixPathSequence(PurePosixPathSequence, PathSequence):
    pass


class WindowsPathSequence(PureWindowsPathSequence, PathSequence):
    pass
