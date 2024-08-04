import pytest

from pathseq import PurePathSequence


class TestEq:
    @pytest.mark.parametrize(
        "path1,path2", [
           ("/directory/file.#.exr", "/directory/file.#.exr"),
           ("/directory/file.<UDIM>.exr", "/directory/file.<UDIM>.exr"),
           ("/directory/file.<UVTILE>.exr", "/directory/file.<UVTILE>.exr"),
           ("/directory/file.<UDIM>_#.#.exr", "/directory/file.<UDIM>_#.#.exr"),
           ("/directory/file.1001-1010#.exr", "/directory/file.1001-1010#.exr"),
           ("/directory/file.1001-1010x0.25#.#.exr", "/directory/file.1001-1010x0.25#.#.exr"),
        ]

    )
    def test_simple_truthy(self, path1, path2):
        assert PurePathSequence(path1) == PurePathSequence(path2)

    @pytest.mark.parametrize(
        "path1,path2", [
           ("/directory/file.#.exr", "/directory/notafile.#.exr"),
           ("/directory/file.#.exr", "/notadirectory/file.#.exr"),
           ("/directory/file.1001-1010#.exr", "/directory/file.1001-1005#.exr"),
           ("/directory/file.1011-1019#.exr", "/directory/file.1011-1019<UDIM>.exr"),
        ]

    )
    def test_simple_falsey(self, path1, path2):
        assert PurePathSequence(path1) != PurePathSequence(path2)

    @pytest.mark.parametrize(
        "path1,path2", [
           ("/directory/file.1001-1010x2#.exr", "/directory/file.1001-1009x2#.exr"),
           ("/directory/file.1001-1010.1x0.25#.#.exr", "/directory/file.1001-1010x0.25#.#.exr"),
        ]

    )
    @pytest.mark.xfail
    def test_normalised_ranges(self, path1, path2):
        assert PurePathSequence(path1) == PurePathSequence(path2)