from collections.abc import Iterator, Sequence
import decimal
from typing import overload, Protocol, Self, TypeVar

from ._ast import FileNumT
from ._decimal_range import DecimalRange


FileNumT_cov = TypeVar("FileNumT_cov", covariant=True)


class RangeProtocol(Protocol[FileNumT_cov]):
    @property
    def start(self) -> FileNumT_cov: ...
    @property
    def step(self) -> FileNumT_cov: ...

    def __iter__(self) -> Iterator[FileNumT_cov]: ...

    def __len__(self) -> int: ...


def remove_exponent(d: decimal.Decimal) -> decimal.Decimal:
    """Remove the exponent and trailing zeros from the given decimal."""
    return d.quantize(decimal.Decimal(1)) if d == d.to_integral() else d.normalize()


class ArithmeticSequence(Sequence[FileNumT]):
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
                stop = end + (step - remainder)
                end -= remainder
            else:
                stop = end + step
        elif start == end:
            # We treat the end as inclusive, ranges don't.
            stop = end + step
            # Normalise to a step of 1
            step = start.__class__(1)
        else:
            stop = end

        self._range: RangeProtocol[FileNumT]
        self._end: FileNumT
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

    def __eq__(self, other: object) -> bool:
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
        return any(item == x for x in self._range)

    def __iter__(self) -> Iterator[FileNumT]:
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

    def __getitem__(self, index: int | slice) -> FileNumT | Self:
        if isinstance(index, slice):
            start_i, stop_i, step = index.indices(len(self))
            if step > 0:
                if start_i >= stop_i:
                    raise IndexError("slice creates an empty arithemtic sequence")
            else:
                if start_i <= stop_i:
                    raise IndexError("slice creates an empty arithemtic sequence")

            start = self[index.start]
            try:
                stop = self[index.stop + 1]
            except IndexError:
                stop = self.end

            return self.__class__(start, stop, self.step * index.step)

        if index < 0:
            index += len(self)
            if index < 0:
                raise IndexError("index out of range")
        elif index >= len(self):
            raise IndexError("index out of range")

        return self._range.start + index * self._range.step
