class ParseError(ValueError):
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


class NotASequenceError(ValueError):
    def __init__(self, seq: str) -> None:
        message = f"{seq} is not a file sequence"
        super().__init__(message)


class IncompleteDimensionError(Exception):
    """A multi-dimension sequence does not contain a consistent number of files across a dimension.

    Example:

    .. code-block:: pycon

        >>> for path in PathSequence("file.1001_1-3#.exr"):
        ...     path.touch()
        ...
        >>> for path in PathSequence("file.1002_1-2#.exr"):
        ...     path.touch()
        ...
        >>> PathSequence.from_disk("file.<UDIM>_#.exr")
        Traceback (most recent call last):
          File "<stdin>", line 1, in <module>
        IncompleteDimensionError: TODO
    """
