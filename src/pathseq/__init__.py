"""A pathlib-first library for working with file sequences."""

from ._ast import (
    FileNumT,
    PaddedRange,
    ParsedLooseSequence,
    ParsedSequence,
    Ranges,
    RangesEndName,
    RangesInName,
    RangesStartName,
)
from ._base import BasePathSequence, BasePurePathSequence, PathT_co, PurePathT_co
from ._error import IncompleteDimensionError, NotASequenceError, ParseError
from ._file_num_seq import FileNumSequence
from ._loose_path_sequence import LoosePathSequence
from ._loose_pure_path_sequence import LoosePurePathSequence
from ._path_sequence import PathSequence
from ._pure_path_sequence import PurePathSequence

__version__ = "0.1.0"

__all__ = (
    "BasePathSequence",
    "BasePurePathSequence",
    "FileNumSequence",
    "FileNumT",
    "IncompleteDimensionError",
    "LoosePathSequence",
    "LoosePurePathSequence",
    "NotASequenceError",
    "PaddedRange",
    "ParsedLooseSequence",
    "ParseError",
    "ParsedSequence",
    "PathSequence",
    "PathT_co",
    "PurePathSequence",
    "PurePathT_co",
    "Ranges",
    "RangesEndName",
    "RangesInName",
    "RangesStartName",
)
