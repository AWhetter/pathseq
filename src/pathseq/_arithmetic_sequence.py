from collections.abc import Iterable, Iterator, Sequence, Set
import decimal
import math
from typing import Any, overload, Protocol, Self, TypeVar

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
            try:
                start = self[index.start]
            except IndexError:
                # We don't allow empty ArithmeticSequence objects.
                # Maybe we need a better exception type here.
                raise

            try:
                end = self[index.stop - 1]
            except IndexError:
                end = self.end

            return self.__class__(start, end, self.step * index.step)

        if index > len(self):
            raise IndexError(index)

        return self._range.start + index * self._range.step

    def isdisjoint(self, other: Iterable[Any]) -> bool:
        if isinstance(other, ArithmeticSequence):
            return self._quick_isdisjoint(other)

        # Resort to a slow check
        return super().isdisjoint(other)

    def _quick_isdisjoint(self, other: Self) -> bool:
        # For
        # a_n = a_1 + d_1(n-1)
        # b_m = b_1 + d_2(m-1)
        a = self
        b = other
        a1 = a.start
        b1 = b.start
        d1 = a.step
        d2 = b.step
        # the following condition must be met:
        # a_1 + d_1(n-1) = b_1 + d_2(m-1)
        # d_1 * n - d_2 * m = b_1 - a_1

        # Calculate the difference between the first terms
        difference = b1 - a1

        # Convert differences to integers for GCD calculation
        d1_int = int(d1) if d1 % 1 == 0 else None
        d2_int = int(d2) if d2 % 1 == 0 else None

        # Check if the GCD of the common differences divides the difference
        if d1_int is not None and d2_int is not None:
            gcd = math.gcd(d1_int, d2_int)
            if gcd == 0:
                return False
            if difference % gcd != 0:
                return False
        else:
            # Handle the case where differences are not integers
            # Convert the equation to integer coefficients
            assert isinstance(d1, decimal.Decimal)
            assert isinstance(d2, decimal.Decimal)
            a_exp = remove_exponent(d1).as_tuple().exponent
            assert isinstance(a_exp, int)
            b_exp = remove_exponent(d2).as_tuple().exponent
            assert isinstance(b_exp, int)
            scale_factor = 10 ** max(a_exp, b_exp)
            d1_scaled = int(d1 * scale_factor)
            d2_scaled = int(d2 * scale_factor)
            difference_scaled = int(difference * scale_factor)

            # Calculate the GCD of the scaled differences
            gcd_scaled = math.gcd(d1_scaled, d2_scaled)
            if gcd_scaled == 0:
                return False

            # Check if the scaled difference is divisible by the scaled GCD
            if difference_scaled % gcd_scaled != 0:
                return False

            # Find the smallest common term
            common_term_scaled = (
                a1 * scale_factor + (difference_scaled // gcd_scaled) * d1_scaled
            )
            common_term = decimal.Decimal(common_term_scaled) / decimal.Decimal(
                scale_factor
            )

            # Check if the common term is within the bounds of both sequences
            if common_term <= a.end and common_term <= b.end:
                return True

        return False
