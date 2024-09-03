from collections.abc import Iterable, Set
import decimal
from typing import TypeVar

from ._decimal_range import DecimalRange

T = TypeVar("T", int, decimal.Decimal)


class ArithmeticSequence(Set[T]):
    def __init__(self, start: T, end: T | None = None, step: T | None = None) -> None:
        end = end if end is not None else start
        step = step if step is not None else start.__class__(1)

        # Normalise to a positive step value
        if step < 0:
            start, end = (end, start)
            step = -step

        stop: T
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

        if isinstance(start, int):
            self._range = range(start, stop, step)
        else:
            self._range = DecimalRange(start, stop, step)

        self._end = end

    @property
    def start(self) -> T:
        return self._range.start

    @property
    def end(self) -> T:
        return self._end

    @property
    def step(self) -> T:
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

    def __contains__(self, item: T) -> bool:
        return item in self._range

    def __iter__(self) -> Iterable[T]:
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
            return ",".join(self)

        return result

    def __repr__(self) -> str:
        if self._step == 1:
            return f"{self.__class__.__name__}({self.start}, {self.end})"

        return f"{self.__class__.__name__}({self.start}, {self.end}, {self.step})"
