from itertools import chain

import pytest

from pathseq import FileNumSequence


class Ranges:
    def __init__(self, *args):
        self._args = args

    def __iter__(self):
        return iter(chain.from_iterable(self._args))


def _valid_int_ranges():
    test_cases = [
        ("1-10", range(1, 11), "1-10"),
        ("1001-1500", range(1001, 1501), "1001-1500"),
        ("1-10x2", range(1, 11, 2), "1-9x2"),
        ("1001-1500x2", range(1001, 1501, 2), "1001-1499x2"),
        ("1-10,20-30", Ranges(range(1, 11), range(20, 31)), "1-10,20-30"),
        (
            "1-10,20-30,40-50",
            Ranges(range(1, 11), range(20, 31), range(40, 51)),
            "1-10,20-30,40-50",
        ),
    ]
    for seq_str, file_nums, normalised_str in test_cases:
        yield pytest.param((seq_str, file_nums, normalised_str), id=seq_str)


@pytest.fixture(params=list(_valid_int_ranges()))
def valid_int_ranges(request):
    return request.param


class TestFromStr:
    def test_valid_int(self, valid_int_ranges):
        seq_str, expected, _ = valid_int_ranges
        file_num_seq = FileNumSequence.from_str(seq_str)
        assert set(file_num_seq) == set(expected)


class TestFromFileNums:
    def test_valid_ints(self, valid_int_ranges):
        _, file_nums, expected = valid_int_ranges
        file_num_seq = FileNumSequence.from_file_nums(file_nums)
        assert str(file_num_seq) == expected

    def test_preserves_duplicates(self, valid_int_ranges):
        _, file_nums, expected = valid_int_ranges
        file_num_seq = FileNumSequence.from_file_nums(chain(file_nums, file_nums))
        assert str(file_num_seq) == f"{expected},{expected}"

    @pytest.mark.parametrize(
        "str_a,str_b",
        [
            ("1,2,3", "1-3"),
            ("2,4,6", "2-6x2"),
            ("-3,-2,-1", "-3--1"),
        ],
    )
    def test_consolidation(self, str_a, str_b):
        nums_a = FileNumSequence.from_str(str_a)
        nums_b = FileNumSequence.from_str(str_b)
        assert nums_a == nums_b
