from decimal import Decimal
import functools
import operator
import pathlib
import re
from typing import TypeVar

from ._ast import (
    RangesStartName,
    RangesInName,
    RangesEndName,
    ParsedSequence,
    PaddedRange,
)
from ._error import IncompleteDimensionError
from ._file_num_seq import FileNumSequence


def find_on_disk(
    path: pathlib.Path,
    parsed: ParsedSequence | RangesStartName | RangesInName | RangesEndName,
) -> tuple[PaddedRange, ...]:
    """Find the ranges of files that exist on disk for the given path.

    Each file number sequence in the path sequence will be ordered numerically.

    Raises:
        IncompleteDimensionError: When one or more dimensions in
        a multi-dimension sequence does not have a consistent number of
        files in each other dimension.
    """
    num_ranges = len(parsed.ranges)
    file_str_sets: list[set[str]] = [set() for _ in range(num_ranges)]
    paths = path.parent.glob(parsed.as_glob())
    pattern = re.compile(parsed.as_regex())
    num_paths = 0
    for found in paths:
        match = pattern.fullmatch(str(found.name))
        if not match:
            continue

        file_nums = []
        for i in range(num_ranges):
            group_name = f"range{i}"
            group = match.group(group_name)
            file_nums.append(group)

        if len(file_nums) != num_ranges:
            continue

        num_paths += 1
        for file_num, file_str_set in zip(file_nums, file_str_sets):
            file_str_set.add(file_num)

    expected = functools.reduce(operator.mul, (len(nums) for nums in file_str_sets), 1)
    if num_paths != expected:
        raise IncompleteDimensionError(
            f"Sequence '{path}' contains an inconsistent number of files across one or more dimensions."
        )

    file_num_seqs = []
    for file_str_set in file_str_sets:
        file_num_seq: FileNumSequence[int] | FileNumSequence[Decimal]
        if any("." in file_str for file_str in file_str_set):
            file_num_seq = FileNumSequence.from_file_nums(
                sorted(Decimal(file_str) for file_str in file_str_set)
            )
        else:
            file_num_seq = FileNumSequence.from_file_nums(
                sorted(int(file_str) for file_str in file_str_set)
            )

        file_num_seqs.append(file_num_seq)

    return tuple(
        PaddedRange(file_num_seq, range_.pad_format)  # type: ignore[misc]
        for file_num_seq, range_ in zip(file_num_seqs, parsed.ranges)
    )
