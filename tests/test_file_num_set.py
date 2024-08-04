from itertools import chain

import pytest

from pathseq import FileNumSet


def _valid_int_ranges():
    test_cases = [
        ("1-10", range(1, 11)),
        ("1001-1500", range(1001, 1501)),
        ("1-10x2", range(1, 11, 2)),
        ("1001-1500x2", range(1001, 1501, 2)),
        ("1-10,20-30", chain(range(1, 11), range(20, 31)))
    ]
    for set_str, file_nums in test_cases:
        yield pytest.param((set_str, file_nums), id=set_str)


@pytest.fixture(params=list(_valid_int_ranges()))
def valid_int_ranges(request):
    return request.param


class TestFromStr:
    def test_valid_int(self, valid_int_ranges):
        set_str, expected = valid_int_ranges
        file_num_set = FileNumSet.from_str(set_str)
        assert set(file_num_set) == set(expected)


class TestFromFileNums:
    def test_valid_ints(self, valid_int_ranges):
        expected, file_nums = valid_int_ranges
        file_num_set = FileNumSet.from_file_nums(file_nums)
        assert str(file_num_set) == expected

    def test_handles_duplicates(self, valid_int_ranges):
        expected, file_nums = valid_int_ranges
        file_num_set = FileNumSet.from_file_nums(chain(file_nums, file_nums))
        assert str(file_num_set) == expected