from __future__ import annotations

from decimal import Decimal

from typing_extensions import (
    Self,  # PY311
)

from ._ast import PaddedRange
from ._base import BasePurePathSequence, PathT_co
from ._file_num_seq import FileNumSequence
from ._parse_loose_path_sequence import parse_path_sequence, ParsedLooseSequence


class LoosePurePathSequence(BasePurePathSequence[PathT_co]):
    """A generic class that represents a path sequence in the system's path flavour.

    Instantiating this class creates either a :class:`PurePosixPathSequence`
    or a :class:`PureWindowsPathSequence`.

    Differences:
    * No __bytes__ because not a filesystem path.
    * No __fspath__ because not a filesystem path.
    * No as_uri because not a filesystem path.
    * No __truediv__ (only __rtruediv__) or joinpath because sequences are supported only in
      the last part of the path.
    * No match because not a filesystem path that can be matched against.

    Raises:
        NotASequenceError: When the given path does not represent a sequence.
    """

    _parsed: ParsedLooseSequence

    def _parse(self, name: str) -> ParsedLooseSequence:
        return parse_path_sequence(name)

    @property
    def parsed(self) -> ParsedLooseSequence:
        return self._parsed

    def with_file_num_seqs(
        self, *seqs: FileNumSequence[int] | FileNumSequence[Decimal]
    ) -> Self:
        if len(seqs) != len(self._parsed.ranges):
            raise TypeError(
                f"Need {len(self._parsed.ranges)} sequences, but got {len(seqs)}"
            )

        new_ranges = tuple(
            PaddedRange(seq, range_.pad_format)
            for seq, range_ in zip(seqs, self._parsed.ranges)
        )
        new = self._parsed.__class__(
            stem=self._parsed.stem,
            prefix_separator=self._parsed.prefix_separator,  # type: ignore[arg-type]
            ranges=new_ranges,
            inter_ranges=self._parsed.inter_ranges,
            postfix=self._parsed.postfix,  # type: ignore[arg-type]
            suffixes=self._parsed.suffixes,
        )
        return self.__class__(self._path.with_name(str(new)))
