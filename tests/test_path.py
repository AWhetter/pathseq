from pathseq import Completeness, PathSequence


class TestFromDisk:
    def test_simple(self):
        seq = PathSequence("tests/fixtures/simple/images.1-5####.exr")
        seq2 = PathSequence("tests/fixtures/simple/images.####.exr")
        new, completeness = seq2.resize_from_existing_paths()
        assert new == seq
        assert completeness == Completeness.FULL

    def test_multi(self):
        seq = PathSequence("tests/fixtures/multi/textures.1011-1012<UDIM>_1-3#.tex")
        seq2 = PathSequence("tests/fixtures/multi/textures.<UDIM>_#.tex")
        new, completeness = seq2.resize_from_existing_paths()
        assert new == seq
        assert completeness == Completeness.FULL

    def test_incomplete_multi(self):
        seq = PathSequence("tests/fixtures/incomplete_multi/textures.<UDIM>_#.tex")
        new, completeness = seq.resize_from_existing_paths()
        assert completeness == Completeness.PARTIAL
