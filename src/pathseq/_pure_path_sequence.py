from __future__ import annotations

from decimal import Decimal

from typing_extensions import (
    Self,  # PY311
)

from ._ast import PaddedRange, ParsedSequence
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

    def with_file_num_seqs(
        self, *seqs: FileNumSequence[int] | FileNumSequence[Decimal]
    ) -> Self:
        """Return a new sequence with the :attr:`~.file_num_seqs <file number sequences>` changed.

        Raises:
            TypeError: If the given number of file number sequences does not match
                the sequence's number of file number sequences.
        """
        if len(seqs) != len(self._parsed.ranges):
            raise TypeError(
                f"Need {len(self._parsed.ranges)} sequences, but got {len(seqs)}"
            )

        new_ranges = tuple(
            PaddedRange(seq, range_.pad_format)
            for seq, range_ in zip(seqs, self._parsed.ranges)
        )
        new = self._parsed.__class__(
            self._parsed.stem,
            self._parsed.prefix_separator,
            new_ranges,
            self._parsed.inter_ranges,
            self._parsed.suffixes,
        )
        return self.__class__(self._path.with_name(str(new)))
