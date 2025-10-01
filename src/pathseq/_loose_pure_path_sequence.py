from __future__ import annotations

from decimal import Decimal

from typing_extensions import (
    Self,  # PY311
)

from ._ast import PaddedRange
from ._base import BasePurePathSequence, PurePathT_co
from ._file_num_seq import FileNumSequence
from ._parse_loose_path_sequence import parse_path_sequence, ParsedLooseSequence


class LoosePurePathSequence(BasePurePathSequence[PurePathT_co]):
    """A sequence of PurePath objects.

    Raises:
        NotASequenceError: When the given path does not represent a sequence,
            but a regular path.
        ParseError: When the given path is not a valid path sequence.
    """

    _parsed: ParsedLooseSequence

    def _parse(self, name: str) -> ParsedLooseSequence:
        return parse_path_sequence(name)

    @property
    def parsed(self) -> ParsedLooseSequence:
        """The parsed sequence string, as a tree of objects."""
        return self._parsed

    @property
    def suffix(self) -> str:
        """The file extension of the paths in the sequence.

        Example:
        If there is no suffix, this will be the empty string.
        .. code-block:: pycon
            >>> LoosePurePathSequence('file1-3###').suffix
            ''

        See also:
            :attr:`pathlib.PurePath.suffix`
        """
        return super().suffix

    @property
    def stem(self) -> str:
        """The final path component, without any ranges, suffixes, or range strings.

        Example:
        .. code-block:: pycon
            >>> LoosePurePathSequence('/path/to/images.1-3####.exr').stem
            'images'
            >>> LoosePurePathSequence('/path/to/1-3####.images.exr').stem
            'images'
            >>> LoosePurePathSequence('/path/to/images.exr.1-3####').stem
            'images'

        Unlike :attr:`pathlib.PurePath.stem`, this will never contain a suffix
        if the paths have multiple suffixes.

        Example:
        .. code-block:: pycon
            >>> PurePathSequence('/path/to/images.tar.gz.1-3####').stem
            'images'

        If the paths have no stem, then the empty string is returned.
        Example:
        .. code-block:: pycon
            >>> LosePurePathSequence('1-3#.tar.gz').stem
            ''
        """
        return super().stem

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
            stem=self._parsed.stem,
            prefix=self._parsed.prefix,  # type: ignore[arg-type]
            ranges=new_ranges,
            inter_ranges=self._parsed.inter_ranges,
            postfix=self._parsed.postfix,  # type: ignore[arg-type]
            suffixes=self._parsed.suffixes,
        )
        return self.__class__(self._path.with_name(str(new)))
