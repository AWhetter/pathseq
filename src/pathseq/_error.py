class ParseError(ValueError):
    """Raised when parsing a sequence string fails.

    Args:
        seq: The sequence string that failed parsing.
        column: The index of the character of the part of the string that failed parsing.
        end: The index of the last character of the part of the string that failed parsing.
        reason: A human readable explanation of why parsing failed.
    """

    seq: str
    """The sequence string that failed parsing."""
    column: int
    """The index of the character of the part of the string that failed parsing."""
    end: int
    """The index of the last character of the part of the string that failed parsing."""

    def __init__(
        self, seq: str, column: int, end_column: int = -1, reason: str | None = None
    ):
        self.seq = seq
        self.column = column
        self.end = end_column if end_column >= 1 else (column + 1)

        lines = []
        message = "Invalid sequence"
        if reason:
            message = f"{message}: {reason}"
        lines.append(message)

        prefix = "  "
        lines.append(f"{prefix}{seq}")
        if column >= 0:
            lines.append(f"{prefix}{' ' * column}{'^' * (self.end - column)}")
            message = "\n".join(lines)

        super().__init__(message)


class NotASequenceError(ParseError):
    """Raised when parsing a string that does not represent a sequence, but a regular path.

    In other words, the given sequence string has no :ref:`range <format-simple-range>`
    present.
    """

    def __init__(self, seq: str) -> None:
        super().__init__(seq, 0, len(seq) - 1, reason="No range string is present")


class IncompleteDimensionError(Exception):
    """A multi-dimension sequence does not contain a consistent number of files across a dimension.

    Example:
        .. code-block:: pycon

            >>> tmp = getfixture('tmp_path')
            >>> seq = tmp / PathSequence('file.1001,1002<UDIM>_1-3#.exr')
            >>> for path in seq:
            ...     path.touch()
            ...
            >>> seq.with_existing_paths()
            PathSequence('.../file.1001,1002<UDIM>_1-3#.exr')
            >>> (tmp / 'file.1002_3.exr').unlink()
            >>> seq.with_existing_paths()
            Traceback (most recent call last):
            ...
            pathseq._error.IncompleteDimensionError: Sequence '...file.1001,1002<UDIM>_1-3#.exr' contains an inconsistent number of files across one or more dimensions.
            >>> (tmp / 'file.1001_3.exr').unlink()
            >>> seq.with_existing_paths()
            PathSequence('.../file.1001,1002<UDIM>_1,2#.exr')
    """
