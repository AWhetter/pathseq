from collections.abc import Iterable, Sequence, Set
import decimal
from typing import overload, Self

from ._ast import FileNumT
from ._decimal_range import DecimalRange


def remove_exponent(d: decimal.Decimal) -> decimal.Decimal:
    """Remove the exponent and trailing zeros from the given decimal."""
    return d.quantize(decimal.Decimal(1)) if d == d.to_integral() else d.normalize()


class ArithmeticSequence(Set[FileNumT], Sequence[FileNumT]):
    def __init__(
        self, start: FileNumT, end: FileNumT | None = None, step: FileNumT | None = None
    ) -> None:
        end = end if end is not None else start
        step = step if step is not None else start.__class__(1)

        # Normalise to a positive step value
        if step < 0:
            start, end = (end, start)
            step = -step

        stop: FileNumT
        if start < end:
            # Normalise the end value to match the step
            remainder = divmod(end - start, step)[1]
            if remainder:
                stop = end + remainder
                end -= remainder
            else:
                stop = end + step
        elif start == end:
            # We treat the end as inclusive, ranges don't.
            stop = end + step
        else:
            stop = end

        self._range: range | DecimalRange
        self._end: int | decimal.Decimal
        if isinstance(start, int):
            self._range = range(start, stop, step)
            self._end = end
        else:
            self._range = DecimalRange(
                remove_exponent(start), remove_exponent(stop), remove_exponent(step)
            )
            self._end = remove_exponent(end)

    @property
    def start(self) -> FileNumT:
        return self._range.start

    @property
    def end(self) -> FileNumT:
        return self._end

    @property
    def step(self) -> FileNumT:
        return self._range.step

    def __eq__(self, other):
        if not isinstance(other, ArithmeticSequence):
            return NotImplemented

        return (
            isinstance(self.start, other.start.__class__)
            and self.start == other.start
            and self.end == other.end
            and self.step == other.step
        )

    def __hash__(self) -> int:
        return hash((type(self), self.start, self.end, self.step))

    def __contains__(self, item: object) -> bool:
        return item in self._range

    def __iter__(self) -> Iterable[FileNumT]:
        return iter(self._range)

    def __len__(self) -> int:
        return len(self._range)

    def __str__(self) -> str:
        if len(self) == 1:
            return str(self.start)

        result = f"{self.start}-{self.end}"
        if self.step != 1:
            result += f"x{self.step}"
        elif len(self) == 2:
            return ",".join(str(x) for x in self)

        return result

    def __repr__(self) -> str:
        if self.step == 1:
            return f"{self.__class__.__name__}({self.start}, {self.end})"

        return f"{self.__class__.__name__}({self.start}, {self.end}, {self.step})"

    @overload
    def __getitem__(self, index: int) -> FileNumT: ...

    @overload
    def __getitem__(self, index: slice) -> Self: ...

    # TODO: Implement slice
    def __getitem__(self, index):
        if index > len(self):
            raise IndexError(index)

        return self._range.start + index * self._range.step
