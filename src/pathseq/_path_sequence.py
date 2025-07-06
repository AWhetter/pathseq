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


class PathSequence(PurePathSequence):
    """blah

    TODO: Note that path sequences are not filesystem paths and therefore
    only a subset of filesystem operations are available.
    """
    _pathlib_type = pathlib.Path

    def expanduser(self) -> Self:
        pass

    def absolute(self) -> Self:
        pass

    def resolve(self, strict: bool = True) -> Self:
        pass

    @classmethod
    def from_disk(cls, pattern: Self | str) -> Self:
        """Create a sequence using the range of files or directories on disk."""
        # TODO: What about when not all of the files in a dimension exist?

    @classmethod
    def glob(cls, pattern: str | pathlib.PurePath) -> Iterable[Self | pathlib.Path]:
        """Glob the given relative pattern, yielding all matching paths and sequences."""


class PosixPathSequence(PurePosixPathSequence, PathSequence):
    pass


class WindowsPathSequence(PureWindowsPathSequence, PathSequence):
    pass
