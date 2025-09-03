"""A pathlib-like library for working with file sequences."""

from ._error import IncompleteDimensionError, NotASequenceError, ParseError
from ._file_num_seq import FileNumSequence
from ._loose_path_sequence import LoosePathSequence
from ._loose_pure_path_sequence import LoosePurePathSequence
from ._path_sequence import PathSequence
from ._pure_path_sequence import PurePathSequence

__version__ = "0.1.0"

__all__ = (
    "FileNumSequence",
    "IncompleteDimensionError",
    "LoosePathSequence",
    "LoosePurePathSequence",
    "NotASequenceError",
    "ParseError",
    "PathSequence",
    "PurePathSequence",
)
