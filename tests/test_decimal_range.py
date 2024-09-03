import decimal

from hypothesis import assume, given
from hypothesis.strategies import (
    booleans,
    composite,
    decimals,
    integers,
    just,
    one_of,
    sampled_from,
    tuples,
)
import pytest

from pathseq._decimal_range import DecimalRange


@composite
def infinite_decimals(draw):
    values = one_of(
        just(decimal.Decimal("NaN")),
        just(decimal.Decimal("sNaN")),
        just(decimal.Decimal("-Infinity")),
        just(decimal.Decimal("Infinity")),
    )
    return draw(values)


@composite
def special_decimals(draw):
    values = one_of(
        infinite_decimals(),
        just(decimal.Decimal("+0")),
        just(decimal.Decimal("-0")),
        just(decimal.Decimal("0")),
    )
    return draw(values)


@composite
def invalid_ranges(draw):
    values = one_of(
        tuples(infinite_decimals(), decimals(), decimals()),
        tuples(decimals(), infinite_decimals(), decimals()),
        tuples(decimals(), decimals(), special_decimals()),
    )
    return draw(values)


@composite
def valid_ranges(draw, max_len=10000):
    places = draw(integers(0, 6))
    valid_start = decimals(allow_nan=False, allow_infinity=False, places=places)
    start = draw(valid_start)

    # Only allow ranges that we can loop over in a sensible amount of time
    diffs = decimals(
        max_value=1500, allow_nan=False, allow_infinity=False, places=places
    )
    diff = draw(diffs)
    if draw(booleans()):
        diff = -diff
    stop = start + diff

    valid_step = decimals(
        max_value=diff / max_len, allow_nan=False, allow_infinity=False, places=places
    ).filter(lambda x: not x.is_zero())
    step = draw(valid_step)

    try:
        len(DecimalRange(start, stop, step))
    except (decimal.InvalidOperation, OverflowError):
        # Ignore extreme values that result in invalid operations.
        # Such scenarios aren't legitimate use cases.
        assume(False)

    assume("E" not in str(start))
    assume("E" not in str(stop))
    assume("E" not in str(step))

    return (start, stop, step)


@given(invalid_ranges())
def test_invalid_init_values(values):
    with pytest.raises(ValueError):
        DecimalRange(*values)


@given(valid_ranges())
def test_properties(values):
    start, stop, step = values
    range_ = DecimalRange(start, stop, step)
    assert range_.start == start
    assert range_.stop == stop
    assert range_.step == step


@given(valid_ranges())
def test_bool(values):
    range_ = DecimalRange(*values)
    try:
        next(iter(range_))
        assert bool(range_)
    except StopIteration:
        assert not bool(range_)


# TODO: This test is too slow
@pytest.mark.skip
@given(valid_ranges())
def test_len(values):
    range_ = DecimalRange(*values)
    len_ = sum(1 for _ in range_)
    assert len(range_) == len_


@composite
def ranges_with_index(draw):
    values = draw(valid_ranges())
    range_ = DecimalRange(*values)
    assume(bool(range_))
    index = draw(integers(min_value=0, max_value=len(range_) - 1))
    return (range_, index)


@given(ranges_with_index())
def test_contains_truthy(range_and_index):
    range_, index = range_and_index

    value = range_.start + range_.step * index
    if value in range_:
        assert True
    elif range_.start == pytest.approx(value):
        # Floating point precision means that we didn't quite hit the mark.
        # So test the iter search code path.
        assert pytest.approx(value) in range_
    else:
        # Assert the failed condition so that pytest gives debuggable output.
        assert value in range_


@given(
    valid_ranges(),
    decimals(allow_nan=False, allow_infinity=False).filter(
        lambda x: x.as_integer_ratio()[1] != 1
    ),
)
def test_contains_falsey(values, index):
    range_ = DecimalRange(*values)

    value = range_.start + range_.step * index
    if value != range_.start:
        assert value not in range_


def test_eq_and_hash():
    pass


def test_iter_and_reversed():
    pass


def test_count():
    pass


def test_index():
    pass
