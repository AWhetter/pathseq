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


class TestSuffix:
    @pytest.mark.parametrize(
        "path_str,expected", [
            ("file.#.exr", ".exr"),
            ("file.#.tar.gz", ".gz"),
            ("file.#", ""),
            ("file.<UDIM>.tif", ".tif"),
        ]
    )
    def test_recommended_format(self, path_str, expected):
        path = PurePathSequence(path_str)
        assert path.suffix == expected

    @pytest.mark.parametrize(
        "path_str,expected", [
            ("file.#.#.exr", ".exr"),
            ("file.#.#.tar.gz", ".gz"),
            ("file.#.#", ""),
            ("file.1-10x0.5#.exr", ".exr"),
            ("file.1-10x0.5#.#.exr", ".exr"),
            ("file.1-10x0.5#.tar.gz", ".gz"),
            ("file.1-10x0.5#.#.tar.gz", ".gz"),
            ("file.1-10x0.5#", ""),
            ("file.1-10x0.5#.#", ""),
        ]
    )
    def test_recommended_with_subsamples(self, path_str, expected):
        path = PurePathSequence(path_str)
        assert path.suffix == expected


class TestSuffixes:
    @pytest.mark.parametrize(
        "path_str,expected", [
            ("file.#.exr", [".exr"]),
            ("file.#.tar.gz", [".tar", ".gz"]),
            ("file.#", []),
            ("file.<UDIM>.tif", [".tif"]),
        ]
    )
    def test_recommended_format(self, path_str, expected):
        path = PurePathSequence(path_str)
        assert path.suffix == expected


    @pytest.mark.parametrize(
        "path_str,expected", [
            ("file.#.#.exr", [".exr"]),
            ("file.#.#.tar.gz", [".tar", ".gz"]),
            ("file.#.#", []),
            ("file.1-10x0.5#.exr", [".exr"]),
            ("file.1-10x0.5#.#.exr", [".exr"]),
            ("file.1-10x0.5#.tar.gz", [".tar", ".gz"]),
            ("file.1-10x0.5#.#.tar.gz", [".tar", ".gz"]),
            ("file.1-10x0.5#", []),
            ("file.1-10x0.5#.#", []),
        ]
    )
    def test_recommended_with_subsamples(self, path_str, expected):
        path = PurePathSequence(path_str)
        assert path.suffix == expected


class TestStem:
    @pytest.mark.parametrize(
        "path_str,expected", [
            ("file.#.exr", "file"),
            ("file.#.tar.gz", "file"),
            ("file.#", "file"),
            ("file.<UDIM>.tif", "file"),
        ]
    )
    def test_recommended_format(self, path_str, expected):
        path = PurePathSequence(path_str)
        assert path.suffix == expected

    @pytest.mark.parametrize(
        "path_str,expected", [
            ("file.#.#.exr", "file"),
            ("file.#.#.tar.gz", "file"),
            ("file.#.#", "file"),
            ("file.1-10x0.5#.exr", "file"),
            ("file.1-10x0.5#.#.exr", "file"),
            ("file.1-10x0.5#.tar.gz", "file"),
            ("file.1-10x0.5#.#.tar.gz", "file"),
            ("file.1-10x0.5#", "file"),
            ("file.1-10x0.5#.#", "file"),
        ]
    )
    def test_recommended_with_subsamples(self, path_str, expected):
        path = PurePathSequence(path_str)
        assert path.suffix == expected


class WithName:
    def test_simple(self):
        old = "file.1-10#.exr"
        new = "new.1-5#.exr"

        old_path = PurePathSequence("/directory") / old
        new_path = PurePathSequence("/directory") / new
        assert old_path.with_name(new) == new_path

    def test_with_no_name(self):
        with pytest.raises(ValueError):
            PurePathSequence("/").with_name("file.1-10#.exr")

    def test_empty(self):
        pass


class WithStem:
    def test_simple(self):
        old = "file.1-10#"
        new = "new.1-5#"

        old_path = PurePathSequence("/directory") / f"{old}.exr"
        new_path = PurePathSequence("/directory") / f"{new}.exr"
        assert old_path.with_stem(new) == new_path

    def test_with_no_name(self):
        with pytest.raises(ValueError):
            PurePathSequence("/").with_stem("file.1-10#")

    def test_empty(self):
        pass


class WithSuffix:
    def test_simple(self):
        stem = "file.1-10#.exr"
        new_suffix = ".jpg"

        old_path = PurePathSequence("/directory") / stem
        new_path = PurePathSequence("/directory") / f"{stem}{new_suffix}"
        assert old_path.with_suffix(new_suffix) == new_path


    def test_with_no_name(self):
        with pytest.raises(ValueError):
            PurePathSequence("/").with_suffix(".exr")


    def test_with_no_suffix(self):
        stem = "file.1-10#"
        new_suffix = ".exr"

        old_path = PurePathSequence("/directory") / stem
        new_path = PurePathSequence("/directory") / f"{stem}{new_suffix}"
        assert old_path.with_suffix(new_suffix) == new_path

    def test_empty(self):
        pass

# TODO: Test __iter__ and __len__