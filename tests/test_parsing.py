import pytest

from pathseq._parse_path_sequence import (
    parse_path_sequence,
    PaddedRange,
    ParsedSequence,
)
from pathseq import FileNumSet, NotASequenceError, ParseError


class TestPathSequence:
    @pytest.mark.parametrize(
        "seq,expected",
        [
            pytest.param(
                "file.#.exr",
                ParsedSequence(
                    "file",
                    ".",
                    (
                        PaddedRange(
                            "",
                            "#",
                        ),
                    ),
                    (".exr",),
                ),
                id="file.#.exr",
            ),
            pytest.param(
                "file.1-10#.exr",
                ParsedSequence(
                    "file",
                    ".",
                    (
                        PaddedRange(
                            FileNumSet.from_str("1-10"),
                            "#",
                        ),
                    ),
                    (".exr",),
                ),
                id="file.1-10#.exr",
            ),
            pytest.param(
                "file.1-10x2#.exr",
                ParsedSequence(
                    "file",
                    ".",
                    (
                        PaddedRange(
                            FileNumSet.from_str("1-10x2"),
                            "#",
                        ),
                    ),
                    (".exr",),
                ),
                id="file.1-10x2#.exr",
            ),
        ],
    )
    def test_simple(self, seq, expected):
        parsed = parse_path_sequence(seq)
        assert parsed == expected

    @pytest.mark.parametrize(
        "seq,expected",
        [
            pytest.param(
                ".#.exr",
                ParsedSequence(
                    ".",
                    "",
                    (
                        PaddedRange(
                            "",
                            "#",
                        ),
                    ),
                    (".exr",),
                ),
                id=".#.exr",
            ),
            pytest.param(
                ".hidden#.exr",
                ParsedSequence(
                    ".hidden",
                    "",
                    (
                        PaddedRange(
                            "",
                            "#",
                        ),
                    ),
                    (".exr",),
                ),
                id=".hidden#.exr",
            ),
        ],
    )
    def test_hidden_files(self, seq, expected):
        parsed = parse_path_sequence(seq)
        assert parsed == expected

    @pytest.mark.parametrize(
        "seq",
        [
            "#",
            "#.exr",
            "#.tar.gz",
            "#_#",
            "#_file",
            "#_file.exr",
            "#file",
            "#file.exr",
            "#file.tar.gz",
            ".file.exr.#",
            "1-10#_file.exr",
            "1-10x2#_file.exr",
            "file.#",
            "file.#.",
            "file.#.#",
            "file.#..exr",
            "file.#.exr.",
            "file.#.exr.",
            "file.#_",
            "file.1-10x0.5#",
            "file.1-10x0.5#.#",
            "file.exr.#",
            "file.exr.1-10#",
            "file.exr.1-10x2#",
            "file_#",
        ],
    )
    def test_parse_error(self, seq):
        with pytest.raises(ParseError):
            parse_path_sequence(seq)

    @pytest.mark.parametrize(
        "seq",
        [
            "",
            "file",
            "dir",
            "file.exr",
            ".file.exr",
            ".file",
            "file.1.exr",
        ],
    )
    def test_not_a_sequence(self, seq):
        with pytest.raises(NotASequenceError):
            parse_path_sequence(seq)
