from __future__ import annotations

from typing_extensions import (
    Self,  # PY311
)

from ._ast import ParsedLooseSequence
from ._base import BasePurePathSequence, PurePathT_co
from ._error import ParseError
from ._parse_loose_path_sequence import parse_path_sequence


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

        If there is no suffix, this will be the empty string.

        .. code-block:: pycon

            >>> LoosePurePathSequence('file1-3###').suffix
            ''
        """
        return super().suffix

    def with_suffix(self, suffix: str) -> Self:
        """Return a new path sequence with the suffix changed.

        If the given suffix is the empty string, the existing suffix will be removed.
        But if the path sequence has only one suffix,
        then a :exc:`ValueError` will be raised because removing the suffix will result in
        an invalid path sequence.

        Args:
            suffix: The new suffix to replace the existing suffix with.

        Raises:
            ValueError: If the given suffix would result in an invalid path sequence.
        """
        parsed = self._parsed.with_suffix(suffix)
        try:
            return self.with_segments(self._path.parent, str(parsed))
        except ParseError:
            raise ValueError(
                f"Cannot use suffix '{suffix}' because"
                " it would result in an invalid path sequence"
            )

    @property
    def stem(self) -> str:
        """The final path component, without any pre-range separator, ranges, post-range separator, or suffixes.

        .. code-block:: pycon

            >>> LoosePurePathSequence('/path/to/images.1-3####.exr').stem
            'images'
            >>> LoosePurePathSequence('/path/to/1-3####_images.exr').stem
            'images'
            >>> LoosePurePathSequence('/path/to/images.exr.1-3####').stem
            'images'

        If the ranges do not start or end the path then,
        unlike :attr:`pathlib.PurePath.stem`, this will never contain a suffix
        if the range is in the path and the paths have multiple suffixes:

        .. code-block:: pycon

            >>> LoosePurePathSequence('/path/to/images.1-3####.tar.gz').stem
            'images'
            >>> LoosePurePathSequence('/path/to/1-3####_images.tar.gz').stem
            'images.tar'
            >>> LoosePurePathSequence('/path/to/images.tar.gz.1-3####').stem
            'images.tar'

        If the paths have no stem, then the empty string is returned:

        .. code-block:: pycon

            >>> LoosePurePathSequence('1-3#.tar.gz').stem
            ''
        """
        return super().stem
