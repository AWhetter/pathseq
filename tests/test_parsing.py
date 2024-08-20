import pytest

from pathseq._parse_path_sequence import (
    parse_path_sequence,
    PaddedRange,
    RangesEndName,
    RangesInName,
    RangesStartName,
)
from pathseq import FileNumSet, NotASequenceError


class TestPathSequence:
    @pytest.mark.parametrize("seq,expected", [
        pytest.param(
            "#.file.exr",
            RangesStartName(
                "",
                [
                    PaddedRange(
                        "",
                        "#",
                    ),
                ],
                ".",
                "file",
                [".exr"],
            ),
            id="#.file.exr",
        ),
        pytest.param(
            "1-10#.file.exr",
            RangesStartName(
                "",
                [
                    PaddedRange(
                        FileNumSet.from_str("1-10"),
                        "#",
                    ),
                ],
                ".",
                "file",
                [".exr"],
            ),
            id="1-10#.file.exr",
        ),
        pytest.param(
            "1-10x2#.file.exr",
            RangesStartName(
                "",
                [
                    PaddedRange(
                        FileNumSet.from_str("1-10x2"),
                        "#",
                    ),
                ],
                ".",
                "file",
                [".exr"],
            ),
            id="1-10x2#.file.exr",
        ),
    ])
    def test_starts(self, seq, expected):
        parsed = parse_path_sequence(seq)
        assert parsed == expected

    @pytest.mark.parametrize("seq,expected", [
        pytest.param(
            "file.#.exr",
            RangesInName(
                "file",
                ".",
                [
                    PaddedRange(
                        "",
                        "#",
                    ),
                ],
                "",
                [".exr"],
            ),
            id="file.#.exr",
        ),
        pytest.param(
            "file.1-10#.exr",
            RangesInName(
                "file",
                ".",
                [
                    PaddedRange(
                        FileNumSet.from_str("1-10"),
                        "#",
                    ),
                ],
                "",
                [".exr"],
            ),
            id="file.1-10#.exr",
        ),
        pytest.param(
            "file.1-10x2#.exr",
            RangesInName(
                "file",
                ".",
                [
                    PaddedRange(
                        FileNumSet.from_str("1-10x2"),
                        "#",
                    ),
                ],
                "",
                [".exr"],
            ),
            id="file.1-10x2#.exr",
        ),
    ])
    def test_in(self, seq, expected):
        parsed = parse_path_sequence(seq)
        assert parsed == expected

    @pytest.mark.parametrize("seq,expected", [
        pytest.param(
            "file.exr.#",
            RangesEndName(
                "file",
                [".exr"],
                ".",
                [
                    PaddedRange(
                        "",
                        "#",
                    ),
                ],
                "",
            ),
            id="file.exr.#",
        ),
        pytest.param(
            "file.exr.1-10#",
            RangesEndName(
                "file",
                [".exr"],
                ".",
                [
                    PaddedRange(
                        FileNumSet.from_str("1-10"),
                        "#",
                    ),
                ],
                "",
            ),
            id="file.exr.1-10#",
        ),
        pytest.param(
            "file.exr.1-10x2#",
            RangesEndName(
                "file",
                [".exr"],
                ".",
                [
                    PaddedRange(
                        FileNumSet.from_str("1-10x2"),
                        "#",
                    ),
                ],
                "",
            ),
            id="file.exr.1-10x2#",
        ),
    ])
    def test_ends(self, seq, expected):
        parsed = parse_path_sequence(seq)
        assert parsed == expected


    @pytest.mark.parametrize("seq", [
        "file",
        "dir",
        "file.exr",
        ".file.exr",
        ".file",
        "file.1.exr",
    ])
    def test_not_a_sequence(self, seq):
        with pytest.raises(NotASequenceError):
            parse_path_sequence(seq)
