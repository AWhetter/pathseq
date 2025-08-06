import pathlib

import pytest

from pathseq import LoosePurePathSequence


class TestEqAndHash:
    @pytest.mark.parametrize(
        "path1,path2",
        [
            ("/directory/file.#.exr", "/directory/file.#.exr"),
            ("/directory/file.<UDIM>.exr", "/directory/file.<UDIM>.exr"),
            ("/directory/file.<UVTILE>.exr", "/directory/file.<UVTILE>.exr"),
            ("/directory/file.<UDIM>_#.#.exr", "/directory/file.<UDIM>_#.#.exr"),
            ("/directory/file.1001-1010#.exr", "/directory/file.1001-1010#.exr"),
            (
                "/directory/file.1001-1010x0.25#.#.exr",
                "/directory/file.1001-1010x0.25#.#.exr",
            ),
        ],
    )
    def test_simple_truthy(self, path1, path2):
        seq1 = LoosePurePathSequence(path1)
        seq2 = LoosePurePathSequence(path2)
        assert seq1 == seq2
        assert len({seq1, seq1}) == 1

    @pytest.mark.parametrize(
        "path1,path2",
        [
            ("/directory/file.#.exr", "/directory/notafile.#.exr"),
            ("/directory/file.#.exr", "/notadirectory/file.#.exr"),
            ("/directory/file.1001-1010#.exr", "/directory/file.1001-1005#.exr"),
            ("/directory/file.1011-1019#.exr", "/directory/file.1011-1019<UDIM>.exr"),
        ],
    )
    def test_simple_falsey(self, path1, path2):
        seq1 = LoosePurePathSequence(path1)
        seq2 = LoosePurePathSequence(path2)
        assert seq1 != seq2
        assert len({seq1, seq2}) == 2

    @pytest.mark.parametrize(
        "path1,path2",
        [
            ("/directory/file.1001-1010x2#.exr", "/directory/file.1001-1009x2#.exr"),
            (
                "/directory/file.1001-1010.1x0.25#.#.exr",
                "/directory/file.1001-1010x0.25#.#.exr",
            ),
        ],
    )
    def test_normalised_ranges(self, path1, path2):
        seq1 = LoosePurePathSequence(path1)
        seq2 = LoosePurePathSequence(path2)
        assert seq1 == seq2
        assert len({seq1, seq2}) == 1


class TestRTrueDiv:
    @pytest.mark.parametrize(
        "path_str,seq_str",
        [
            ("/directory", "file.1001-1005#.exr"),
            ("directory", "file.1001-1005#.exr"),
            ("/dir1/dir2", "file.1001-1005#.exr"),
            ("dir1/dir2", "file.1001-1005#.exr"),
        ],
    )
    def test_simple(self, path_str, seq_str):
        result = pathlib.Path(path_str) / LoosePurePathSequence(seq_str)
        expected = LoosePurePathSequence(pathlib.Path(path_str) / seq_str)
        assert result == expected


class TestSuffix:
    @pytest.mark.parametrize(
        "path_str,expected",
        [
            ("file.#.exr", ".exr"),
            ("file.#.tar.gz", ".gz"),
            ("file.<UDIM>.tif", ".tif"),
        ],
    )
    def test_recommended_format(self, path_str, expected):
        path = LoosePurePathSequence(path_str)
        assert path.suffix == expected

    @pytest.mark.parametrize(
        "path_str,expected",
        [
            ("file.#.#.exr", ".exr"),
            ("file.#.#.tar.gz", ".gz"),
            ("file.1-10x0.5#.exr", ".exr"),
            ("file.1-10x0.5#.#.exr", ".exr"),
            ("file.1-10x0.5#.tar.gz", ".gz"),
            ("file.1-10x0.5#.#.tar.gz", ".gz"),
        ],
    )
    def test_recommended_with_subsamples(self, path_str, expected):
        path = LoosePurePathSequence(path_str)
        assert path.suffix == expected


class TestSuffixes:
    @pytest.mark.parametrize(
        "path_str,expected",
        [
            ("file.#.exr", (".exr",)),
            ("file.#.tar.gz", (".tar", ".gz")),
            ("file.<UDIM>.tif", (".tif",)),
        ],
    )
    def test_recommended_format(self, path_str, expected):
        path = LoosePurePathSequence(path_str)
        assert path.suffixes == expected

    @pytest.mark.parametrize(
        "path_str,expected",
        [
            ("file.#.#.exr", (".exr",)),
            ("file.#.#.tar.gz", (".tar", ".gz")),
            ("file.1-10x0.5#.exr", (".exr",)),
            ("file.1-10x0.5#.#.exr", (".exr",)),
            ("file.1-10x0.5#.tar.gz", (".tar", ".gz")),
            ("file.1-10x0.5#.#.tar.gz", (".tar", ".gz")),
        ],
    )
    def test_recommended_with_subsamples(self, path_str, expected):
        path = LoosePurePathSequence(path_str)
        assert path.suffixes == expected

    @pytest.mark.todo
    def test_starts(self):
        pass

    @pytest.mark.todo
    def test_starts_with_subsamples(self):
        pass

    @pytest.mark.todo
    def test_in(self):
        pass

    @pytest.mark.todo
    def test_in_with_subsamples(self):
        pass

    @pytest.mark.todo
    def test_ends(self):
        pass

    @pytest.mark.todo
    def test_ends_with_subsamples(self):
        pass


class TestStem:
    @pytest.mark.parametrize(
        "path_str,expected",
        [
            ("file.#.exr", "file"),
            ("file.#.tar.gz", "file"),
            ("file.<UDIM>.tif", "file"),
        ],
    )
    def test_recommended_format(self, path_str, expected):
        path = LoosePurePathSequence(path_str)
        assert path.stem == expected

    @pytest.mark.parametrize(
        "path_str,expected",
        [
            ("file.#.#.exr", "file"),
            ("file.#.#.tar.gz", "file"),
            ("file.1-10x0.5#.exr", "file"),
            ("file.1-10x0.5#.#.exr", "file"),
            ("file.1-10x0.5#.tar.gz", "file"),
            ("file.1-10x0.5#.#.tar.gz", "file"),
        ],
    )
    def test_recommended_with_subsamples(self, path_str, expected):
        path = LoosePurePathSequence(path_str)
        assert path.stem == expected

    @pytest.mark.todo
    def test_starts(self):
        pass

    @pytest.mark.todo
    def test_starts_with_subsamples(self):
        pass

    @pytest.mark.todo
    def test_in(self):
        pass

    @pytest.mark.todo
    def test_in_with_subsamples(self):
        pass

    @pytest.mark.todo
    def test_ends(self):
        pass

    @pytest.mark.todo
    def test_ends_with_subsamples(self):
        pass


class TestWithName:
    def test_simple(self):
        old = "file.1-10#.exr"
        new = "new.1-5#.exr"

        old_path = "/directory" / LoosePurePathSequence(old)
        new_path = "/directory" / LoosePurePathSequence(new)
        assert old_path.with_name(new) == new_path

    def test_empty(self):
        with pytest.raises(ValueError):
            LoosePurePathSequence("/file.1-10#.exr").with_name("")


class TestWithStem:
    @pytest.mark.parametrize(
        "seq_str,new_stem,expected_seq_str",
        [
            ("file.1-10#.exr", "new", "new.1-10#.exr"),
            ("file1-10#.exr", "new", "new1-10#.exr"),
            ("1-10#.tar.gz", "new", "new1-10#.tar.gz"),
            ("1-10#file.exr", "new", "1-10#new.exr"),
            ("file.exr.1-10#", "new", "new.exr.1-10#"),
            ("file.exr1-10#", "new", "new.exr1-10#"),
        ],
    )
    def test_simple(self, seq_str, new_stem, expected_seq_str):
        seq = "/directory" / LoosePurePathSequence(seq_str)
        expected = "/directory" / LoosePurePathSequence(expected_seq_str)
        assert seq.with_stem(new_stem) == expected

    @pytest.mark.parametrize(
        "seq_str,new_stem,expected_seq_str",
        [
            ("file.1-10#.exr", "", "1-10#.exr"),
            ("file1-10#.exr", "", "1-10#.exr"),
            ("1-10#.tar.gz", "", "1-10#.tar.gz"),
            ("1-10#file.exr", "", "1-10#.exr"),
            ("file.exr.1-10#", "", ".exr.1-10#"),
            ("file.exr1-10#", "", ".exr1-10#"),
        ],
    )
    def test_empty_replacement(self, seq_str, new_stem, expected_seq_str):
        seq = "/directory" / LoosePurePathSequence(seq_str)
        expected = "/directory" / LoosePurePathSequence(expected_seq_str)
        assert seq.with_stem(new_stem) == expected

    @pytest.mark.todo
    def test_starts(self):
        pass

    @pytest.mark.todo
    def test_starts_with_empty_replacement(self):
        pass

    @pytest.mark.todo
    def test_in(self):
        pass

    @pytest.mark.todo
    def test_in_with_empty_replacement(self):
        pass

    @pytest.mark.todo
    def test_ends(self):
        pass

    @pytest.mark.todo
    def test_ends_with_empty_replacement(self):
        pass


class TestWithSuffix:
    @pytest.mark.parametrize(
        "seq_str,new_suffix,expected_seq_str",
        [
            ("file.1-10#.exr", ".new", "file.1-10#.new"),
            ("file1-10#.exr", ".new", "file1-10#.new"),
            ("1-10#.file.exr", ".new", "1-10#.file.new"),
            ("1-10#file.exr", ".new", "1-10#file.new"),
            ("file.exr.1-10#", ".new", "file.new.1-10#"),
            ("file.exr1-10#", ".new", "file.new1-10#"),
        ],
    )
    def test_simple(self, seq_str, new_suffix, expected_seq_str):
        seq = "/directory" / LoosePurePathSequence(seq_str)
        expected = "/directory" / LoosePurePathSequence(expected_seq_str)
        assert seq.with_suffix(new_suffix) == expected

    @pytest.mark.parametrize(
        "seq_str,new_suffix,expected_seq_str",
        [
            ("file.1-10#.exr", "", "file.1-10#"),
            ("file1-10#.exr", "", "file1-10#"),
            ("1-10#.file.exr", "", "1-10#.file"),
            ("1-10#file.exr", "", "1-10#file"),
            ("file.exr.1-10#", "", "file.1-10#"),
            ("file.exr1-10#", "", "file1-10#"),
        ],
    )
    def test_empty(self, seq_str, new_suffix, expected_seq_str):
        seq = "/directory" / LoosePurePathSequence(seq_str)
        expected = "/directory" / LoosePurePathSequence(expected_seq_str)
        assert seq.with_suffix(new_suffix) == expected

    @pytest.mark.todo
    def test_starts(self):
        pass

    @pytest.mark.todo
    def test_starts_with_empty_replacement(self):
        pass

    @pytest.mark.todo
    def test_in(self):
        pass

    @pytest.mark.todo
    def test_in_with_empty_replacement(self):
        pass

    @pytest.mark.todo
    def test_ends(self):
        pass

    @pytest.mark.todo
    def test_ends_with_empty_replacement(self):
        pass


class TestIter:
    @pytest.mark.parametrize(
        "seq_str,expected",
        [
            pytest.param(
                "image.1-5####.exr",
                [f"image.000{x}.exr" for x in range(1, 6)],
                id="images.1-5####.exr",
            ),
            pytest.param(
                "texture.1011-1012####_1-3#.tex",
                [
                    f"texture.{x}_{y}.tex"
                    for x in range(1011, 1013)
                    for y in range(1, 4)
                ],
                id="textures.1011-1012####_1-3#.tex",
            ),
        ],
    )
    def test_simple(self, seq_str, expected):
        seq = LoosePurePathSequence(seq_str)
        assert list(str(x) for x in seq) == expected
