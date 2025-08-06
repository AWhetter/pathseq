"""A pathlib-like library for working with file sequences."""

from ._error import NotASequenceError, ParseError
from ._file_num_set import FileNumSet
from ._loose_path_sequence import (
    LoosePathSequence,
    LoosePosixPathSequence,
    LooseWindowsPathSequence,
)
from ._loose_pure_path_sequence import (
    LoosePurePathSequence,
    LoosePurePosixPathSequence,
    LoosePureWindowsPathSequence,
)
from ._path_sequence import PathSequence, PosixPathSequence, WindowsPathSequence
from ._pure_path_sequence import (
    PurePathSequence,
    PurePosixPathSequence,
    PureWindowsPathSequence,
)

__version__ = "0.1.0"

__all__ = (
    "FileNumSet",
    "LoosePathSequence",
    "LoosePosixPathSequence",
    "LoosePurePathSequence",
    "LoosePurePosixPathSequence",
    "LoosePureWindowsPathSequence",
    "LooseWindowsPathSequence",
    "NotASequenceError",
    "ParseError",
    "PathSequence",
    "PosixPathSequence",
    "PurePathSequence",
    "PurePosixPathSequence",
    "PureWindowsPathSequence",
    "WindowsPathSequence",
)
