"""A pathlib-like library for working with file sequences."""
from ._file_num_set import FileNumSet
from ._path_sequence import PathSequence, PosixPathSequence, WindowsPathSequence
from ._pure_path_sequence import PurePathSequence, PurePosixPathSequence, PureWindowsPathSequence

__version__ = "0.1.0"

__all__ = (
    "FileNumSet",
    "PathSequence",
    "PosixPathSequence",
    "PurePathSequence",
    "PurePosixPathSequence",
    "PureWindowsPathSequence",
    "WindowsPathSequence",
)
