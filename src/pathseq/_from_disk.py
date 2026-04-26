from collections.abc import Iterator, Sequence
from decimal import Decimal
import enum
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
)
from ._file_num_seq import FileNumSequence
from ._formatters import GlobFormatter, RegexFormatter

PathT = TypeVar("PathT", bound=pathlib.Path)


class Completeness(enum.Enum):
    FULL = enum.auto()
    PARTIAL = enum.auto()
    EMPTY = enum.auto()


def _find_on_disk(
    path: PathT,
    parsed: ParsedSequence | RangesStartName | RangesInName | RangesEndName,
) -> Iterator[tuple[PathT, Sequence[str]]]:
    # Handle single file sequences first
    if not parsed.ranges.ranges:
        if path.exists():
            yield path, []
        return

    num_ranges = len(parsed.ranges.ranges)
    glob_pattern = GlobFormatter().format(parsed)
    paths = path.parent.glob(glob_pattern)
    pattern = re.compile(RegexFormatter().format(parsed))
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

        yield found, file_nums


def find_on_disk(
    path: pathlib.Path,
    parsed: ParsedSequence | RangesStartName | RangesInName | RangesEndName,
) -> tuple[Sequence[FileNumSequence[int] | FileNumSequence[Decimal]], Completeness]:
    """Find the ranges of paths that exist on disk for the given path sequence.

    Each file number sequence in the path sequence will be ordered numerically.
    """
    file_str_sets: list[set[str]] = [set() for _ in parsed.ranges.ranges]
    num_paths = 0
    for _, file_nums in _find_on_disk(path, parsed):
        num_paths += 1
        for file_num, file_str_set in zip(file_nums, file_str_sets):
            file_str_set.add(file_num)

    if not file_str_sets:
        if num_paths == 1:
            return [], Completeness.FULL
        return [], Completeness.EMPTY

    expected = functools.reduce(operator.mul, (len(nums) for nums in file_str_sets), 1)
    completeness: Completeness
    if num_paths == 0:
        completeness = Completeness.EMPTY
    elif num_paths != expected:
        completeness = Completeness.PARTIAL
    else:
        completeness = Completeness.FULL

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

    return file_num_seqs, completeness


def iter_on_disk(
    path: PathT,
    parsed: ParsedSequence | RangesStartName | RangesInName | RangesEndName,
) -> Iterator[PathT]:
    for path, _ in _find_on_disk(path, parsed):
        yield path
