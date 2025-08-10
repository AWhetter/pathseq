from collections.abc import Iterable
import decimal
import math


class DecimalRange:
    def __init__(
        self, start: decimal.Decimal, stop: decimal.Decimal, step: decimal.Decimal
    ) -> None:
        self._start = start
        self._stop = stop
        self._step = step

        if not (start.is_finite() and stop.is_finite()):
            raise ValueError(
                f"{self.__class__.__name__}() can only accept finite start and stop numbers"
            )

        if not step.is_normal():
            raise ValueError(
                f"{self.__class__.__name__}() can only accept normal step numbers"
            )

    @property
    def start(self) -> decimal.Decimal:
        return self._start

    @property
    def stop(self) -> decimal.Decimal:
        return self._stop

    @property
    def step(self) -> decimal.Decimal:
        return self._step

    def __bool__(self) -> bool:
        return bool(len(self))

    def __contains__(self, key: object) -> bool:
        if type(key) is not decimal.Decimal:
            return any(key == v for v in self)

        if self._step > 0:
            if not (self._start <= key < self._stop):
                return False
        else:
            if not (self._stop < key <= self._start):
                return False

        # x_n = a + d(n-1)
        # key = start + step * (n-1)
        # key - start = step * (n-1)
        # (key - start) / step = (n-1)
        # (key - start) / step + 1 = n
        # where n must be an integer
        n_minus_one = (key - self._start) / self._step
        return n_minus_one.as_integer_ratio()[1] == 1

    def __eq__(self, value: object) -> bool:
        if not isinstance(value, DecimalRange):
            return NotImplemented

        if len(self) != len(value):
            return False

        if not len(self):
            return True

        if self.start != value.start:
            return False

        if len(self) == 1:
            return True

        return self.step == value.step

    def __hash__(self) -> int:
        length = len(self)
        to_hash: tuple[int, decimal.Decimal | None, None]
        if length:
            to_hash = (length, self.start, None)
        else:
            to_hash = (length, None, None)
        return hash(to_hash)

    def __iter__(self) -> Iterable[decimal.Decimal]:
        current = self._start
        if self._step > 0:
            while current < self._stop:
                yield current
                current += self._step
        else:
            while current > self._stop:
                yield current
                current += self._step

    def __len__(self) -> int:
        # x_n = a + d(n-1)
        # stop > start + step * (n-1)
        # stop - start > step * (n-1)
        # (stop - start) / step > (n-1)
        # (stop - start) / step + 1 > n

        if self._step > 0 and self._start < self._stop:
            n_minus_one = (self._stop - self._start) / self._step
            num, denom = n_minus_one.as_integer_ratio()
            # stop is part of the range, but the range is non-inclusive
            if denom == 1:
                return num

            return math.floor(n_minus_one + 1)

        if self._step < 0 and self._start > self._stop:
            n_minus_one = (self._stop - self._start) / self._step
            num, denom = n_minus_one.as_integer_ratio()
            # stop is part of the range, but the range is non-inclusive
            if denom == 1:
                return num

            return math.floor(n_minus_one + 1)

        return 0

    def __repr__(self) -> str:
        if self._step == 1:
            return f"{self.__class__.__name__}({self._start}, {self._stop})"

        return f"{self.__class__.__name__}({self._start}, {self._stop}, {self._step})"

    def __reversed__(self) -> Iterable[decimal.Decimal]:
        if not len(self):
            return iter(())

        new_stop = self._start - self._step
        new_start = new_stop + self._step * len(self)
        return iter(self.__class__(new_start, new_stop, -self._step))

    def count(self, value: decimal.Decimal) -> int:
        return 1 if value in self else 0

    def index(self, value: decimal.Decimal) -> int:
        # x_n = a + d(n-1)
        # value = start + step * (n-1)
        # value - start = step * (n-1)
        # (value - start) / step = (n-1)
        # (value - start) / step + 1 = n
        # where n is an integer
        # We don't +1 because we want 0-indexing.
        if value not in self:
            raise ValueError(f"{self.__class__.__name__}.index(x): x not in range")

        return int((value - self._start) // self._step)
