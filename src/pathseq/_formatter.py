from decimal import Decimal
import re

from ._ast import Formatter, PaddedRange


class GlobFormatter(Formatter):
    """Format to a glob pattern to match paths in the given sequence."""

    def __init__(self) -> None:
        self._ignore_next_range = False

    def range(self, range_: PaddedRange[int] | PaddedRange[Decimal]) -> str:
        if self._ignore_next_range:
            self._ignore_next_range = False
            return ""

        return "*"

    def inter_range(self, inter_range: str) -> str:
        if not inter_range:
            self._ignore_next_range = True

        return inter_range


class FileNumberFormatter(Formatter):
    def __init__(self, *numbers: int | Decimal) -> None:
        self._numbers = iter(numbers)

    def range(self, range_: PaddedRange[int] | PaddedRange[Decimal]) -> str:
        try:
            number = next(self._numbers)
        except StopIteration:
            raise TypeError(
                "Insufficient number of file numbers given to format sequence"
            )

        return range_.format(number)


class RegexFormatter(Formatter):
    """Format to a regex pattern to match paths in the given sequence."""

    def __init__(self) -> None:
        self._i = 0

    def stem(self, stem: str) -> str:
        return re.escape(super().stem(stem))

    def prefix(self, prefix: str) -> str:
        return re.escape(super().prefix(prefix))

    def _range(self, range_: PaddedRange[int] | PaddedRange[Decimal]) -> str:
        if range_.pad_format == "<UVTILE>":
            return r"u\d+_v\d+"

        pad_format = range_.pad_format
        if range_.pad_format == "<UDIM>":
            pad_format = "####"

        if "." in pad_format:
            head, tail = pad_format.split(".", 1)
            tail_re = r"\.[0-9]*" + r"[0-9]" * len(tail)
        else:
            head = pad_format
            tail_re = ""
            if range_.has_subsamples(range_):
                tail_re = r"(\.[0-9]+)?"

        positive_re = r"([1-9][0-9]*)?" + r"[0-9]" * len(head)
        negative_re = r"-([1-9][0-9]*)?" + r"[0-9]" * (len(head) - 1)

        return f"({positive_re}|{negative_re}){tail_re}"

    def range(self, range_: PaddedRange[int] | PaddedRange[Decimal]) -> str:
        result = f"(?P<range{self._i}>{self._range(range_)})"
        self._i += 1
        return result

    def inter_range(self, inter_range: str) -> str:
        return re.escape(super().inter_range(inter_range))

    def suffixes(self, suffixes: tuple[str, ...]) -> str:
        return re.escape(super().suffixes(suffixes))
