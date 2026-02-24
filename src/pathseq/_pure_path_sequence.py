from __future__ import annotations

from decimal import Decimal

from typing_extensions import (
    Self,  # PY311
)

from ._ast import PaddedRange, ParsedSequence, Ranges
from ._base import BasePurePathSequence, PathT_co
from ._file_num_seq import FileNumSequence
from ._parse_path_sequence import parse_path_sequence


class PurePathSequence(BasePurePathSequence[PathT_co]):
    """A sequence of PurePath objects.

    Raises:
        NotASequenceError: When the given path does not represent a sequence,
            but a regular path.
        ParseError: When the given path is not a valid path sequence.
    """

    _parsed: ParsedSequence

    def _parse(self, name: str) -> ParsedSequence:
        return parse_path_sequence(name)

    @property
    def parsed(self) -> ParsedSequence:
        """The parsed sequence string, as a tree of objects."""
        return self._parsed
