import decimal

from hypothesis import assume, given
import hypothesis.strategies as st
import pytest

from pathseq._file_num_seq._decimal_range import DecimalRange


def scale_to_integer_range(r1: DecimalRange, r2: DecimalRange) -> tuple[range, range]:
    max_exponent = max(
        (
            -x.as_tuple().exponent
            for x in (r1.start, r1.stop, r1.step, r2.start, r2.stop, r2.step)
        ),
        default=0,
    )
    return (
        range(
            int(r1.start.scaleb(max_exponent)),
            int(r1.stop.scaleb(max_exponent)),
            int(r1.step.scaleb(max_exponent)),
        ),
        range(
            int(r2.start.scaleb(max_exponent)),
            int(r2.stop.scaleb(max_exponent)),
            int(r2.step.scaleb(max_exponent)),
        ),
    )


@st.composite
def infinite_decimals(draw):
    values = st.one_of(
        st.just(decimal.Decimal("NaN")),
        st.just(decimal.Decimal("sNaN")),
        st.just(decimal.Decimal("-Infinity")),
        st.just(decimal.Decimal("Infinity")),
    )
    return draw(values)


@st.composite
def special_decimals(draw):
    values = st.one_of(
        infinite_decimals(),
        st.just(decimal.Decimal("+0")),
        st.just(decimal.Decimal("-0")),
        st.just(decimal.Decimal("0")),
    )
    return draw(values)


@st.composite
def invalid_ranges(draw):
    values = st.one_of(
        st.tuples(infinite_decimals(), st.decimals(), st.decimals()),
        st.tuples(st.decimals(), infinite_decimals(), st.decimals()),
        st.tuples(st.decimals(), st.decimals(), special_decimals()),
    )
    return draw(values)


@st.composite
def valid_ranges(draw, max_len=10000):
    places = draw(st.integers(0, 6))
    valid_start = st.decimals(
        min_value=-max_len,
        max_value=max_len,
        allow_nan=False,
        allow_infinity=False,
        places=places,
    )
    start = draw(valid_start)

    # Only allow ranges that we can loop over in a sensible amount of time
    diffs = st.decimals(
        min_value=-max_len,
        max_value=max_len,
        allow_nan=False,
        allow_infinity=False,
        places=places,
    )
    diff = draw(diffs)
    stop = start + diff

    # Step must be nonzero and such that the number of elements does not exceed max_len.
    abs_diff = abs(diff)
    if abs_diff == 0:
        min_step = decimal.Decimal("1")
    else:
        min_step = abs_diff / decimal.Decimal(max_len)
    valid_step = st.decimals(
        min_value=min_step,
        max_value=abs_diff if abs_diff != 0 else decimal.Decimal("1"),
        allow_nan=False,
        allow_infinity=False,
        places=places,
    ).filter(lambda x: not x.is_zero())
    step = draw(valid_step)
    # Randomly flip sign of step to allow negative steps
    if draw(st.booleans()):
        step = -step

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


@given(valid_ranges())
def test_len(values):
    range_ = DecimalRange(*values)
    len_ = sum(1 for _ in range_)
    assert len(range_) == len_


@given(valid_ranges())
def test_contains(values):
    r = DecimalRange(*values)
    last_item = None
    for v in r:
        assert v in r
        last_item = v

    if last_item is not None:
        not_in_range = last_item + r.step
        assert not_in_range not in r
    else:
        assert r.start not in r
        assert r.stop not in r


@given(valid_ranges(), valid_ranges())
def test_eq_and_hash(values1, values2):
    r1 = DecimalRange(*values1)
    r2 = DecimalRange(*values2)
    # Reflexivity
    assert r1 == r1
    assert hash(r1) == hash(r1)
    # Symmetry and hash equality for equal objects.
    # Match the behaviour of built-in range, which also only considers
    # start and step for hashing, and ignores stop.
    ri1, ri2 = scale_to_integer_range(r1, r2)
    if ri1 == ri2:
        assert r1 == r2
        assert r2 == r1
        assert hash(r1) == hash(r2)
    else:
        # Hash collisions are possible, so we don't assert hash(r1) != hash(r2)
        assert r1 != r2


@given(valid_ranges())
def test_iter_and_reversed(values):
    r = DecimalRange(*values)
    items = list(r)
    expected = []
    current = r.start
    while (r.step > 0 and current < r.stop) or (r.step < 0 and current > r.stop):
        expected.append(current)
        current += r.step

    assert items == expected
    assert list(reversed(r)) == expected[::-1]


@given(valid_ranges())
def test_count(values):
    r = DecimalRange(*values)
    last_item = None
    # For each value in the range, count should be 1
    for v in r:
        assert r.count(v) == 1
        last_item = v

    # For a value not in the range, count should be 0
    if last_item is not None:
        not_in_range = last_item + r.step
        assert r.count(not_in_range) == 0
    else:
        # For empty range, any value should have count 0
        assert r.count(r.start) == 0
        assert r.count(r.stop) == 0


@given(valid_ranges())
def test_index(values):
    r = DecimalRange(*values)
    last_item = None
    # For each value in the range, index should return its position
    for idx, v in enumerate(r):
        assert r.index(v) == idx
        last_item = v

    # For a value not in the range, index should raise ValueError
    if last_item is not None:
        not_in_range = last_item + r.step
        with pytest.raises(ValueError):
            r.index(not_in_range)
