import pytest

from pathseq import IncompleteDimensionError, PathSequence


class TestFromDisk:
    def test_simple(self):
        seq = PathSequence("tests/fixtures/simple/images.1-5####.exr")
        seq2 = PathSequence.from_disk("tests/fixtures/simple/images.####.exr")
        assert seq2 == seq

    def test_multi(self):
        seq = PathSequence("tests/fixtures/multi/textures.1011-1012<UDIM>_1-3#.tex")
        seq2 = PathSequence.from_disk("tests/fixtures/multi/textures.<UDIM>_#.tex")
        assert seq2 == seq

    def test_incomplete_multi(self):
        with pytest.raises(IncompleteDimensionError):
            PathSequence.from_disk("tests/fixtures/incomplete_multi/textures.<UDIM>_#.tex")
