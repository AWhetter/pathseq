import pytest

from pathseq import IncompleteDimensionError, LoosePathSequence


class TestFromDisk:
    def test_simple_starts(self):
        seq = LoosePathSequence("tests/fixtures/simple_starts/1-5####.images.exr")
        seq2 = LoosePathSequence(
            "tests/fixtures/simple_starts/####.images.exr"
        ).with_existing_paths()
        assert seq2 == seq

    def test_simple_in(self):
        seq = LoosePathSequence("tests/fixtures/simple/images.1-5####.exr")
        seq2 = LoosePathSequence(
            "tests/fixtures/simple/images.####.exr"
        ).with_existing_paths()
        assert seq2 == seq

    def test_simple_ends(self):
        seq = LoosePathSequence("tests/fixtures/simple_ends/images.exr.1-5####")
        seq2 = LoosePathSequence(
            "tests/fixtures/simple_ends/images.exr.####"
        ).with_existing_paths()
        assert seq2 == seq

    def test_multi_starts(self):
        seq = LoosePathSequence(
            "tests/fixtures/multi_starts/1011-1012<UDIM>_1-3#.textures.tex"
        )
        seq2 = LoosePathSequence(
            "tests/fixtures/multi_starts/<UDIM>_#.textures.tex"
        ).with_existing_paths()
        assert seq2 == seq

    def test_multi_in(self):
        seq = LoosePathSequence(
            "tests/fixtures/multi/textures.1011-1012<UDIM>_1-3#.tex"
        )
        seq2 = LoosePathSequence(
            "tests/fixtures/multi/textures.<UDIM>_#.tex"
        ).with_existing_paths()
        assert seq2 == seq

    def test_multi_ends(self):
        seq = LoosePathSequence(
            "tests/fixtures/multi_ends/textures.tex.1011-1012<UDIM>_1-3#"
        )
        seq2 = LoosePathSequence(
            "tests/fixtures/multi_ends/textures.tex.<UDIM>_#"
        ).with_existing_paths()
        assert seq2 == seq

    def test_incomplete_multi_starts(self):
        with pytest.raises(IncompleteDimensionError):
            LoosePathSequence(
                "tests/fixtures/incomplete_multi_starts/<UDIM>_#.textures.tex"
            ).with_existing_paths()

    def test_incomplete_multi_in(self):
        with pytest.raises(IncompleteDimensionError):
            LoosePathSequence(
                "tests/fixtures/incomplete_multi/textures.<UDIM>_#.tex"
            ).with_existing_paths()

    def test_incomplete_multi_ends(self):
        with pytest.raises(IncompleteDimensionError):
            LoosePathSequence(
                "tests/fixtures/incomplete_multi_ends/textures.tex.<UDIM>_#"
            ).with_existing_paths()
