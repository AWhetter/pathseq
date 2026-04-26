from pathseq import Completeness, LoosePathSequence


class TestFromDisk:
    def test_simple_starts(self):
        seq = LoosePathSequence("tests/fixtures/simple_starts/1-5####.images.exr")
        seq2 = LoosePathSequence("tests/fixtures/simple_starts/####.images.exr")
        new, completeness = seq2.resize_from_existing_paths()
        assert new == seq
        assert completeness == Completeness.FULL

    def test_simple_in(self):
        seq = LoosePathSequence("tests/fixtures/simple/images.1-5####.exr")
        seq2 = LoosePathSequence("tests/fixtures/simple/images.####.exr")
        new, completeness = seq2.resize_from_existing_paths()
        assert new == seq
        assert completeness == Completeness.FULL

    def test_simple_ends(self):
        seq = LoosePathSequence("tests/fixtures/simple_ends/images.exr.1-5####")
        seq2 = LoosePathSequence("tests/fixtures/simple_ends/images.exr.####")
        new, completeness = seq2.resize_from_existing_paths()
        assert new == seq
        assert completeness == Completeness.FULL

    def test_multi_starts(self):
        seq = LoosePathSequence(
            "tests/fixtures/multi_starts/1011-1012<UDIM>_1-3#.textures.tex"
        )
        seq2 = LoosePathSequence("tests/fixtures/multi_starts/<UDIM>_#.textures.tex")
        new, completeness = seq2.resize_from_existing_paths()
        assert new == seq
        assert completeness == Completeness.FULL

    def test_multi_in(self):
        seq = LoosePathSequence(
            "tests/fixtures/multi/textures.1011-1012<UDIM>_1-3#.tex"
        )
        seq2 = LoosePathSequence("tests/fixtures/multi/textures.<UDIM>_#.tex")
        new, completeness = seq2.resize_from_existing_paths()
        assert new == seq
        assert completeness == Completeness.FULL

    def test_multi_ends(self):
        seq = LoosePathSequence(
            "tests/fixtures/multi_ends/textures.tex.1011-1012<UDIM>_1-3#"
        )
        seq2 = LoosePathSequence("tests/fixtures/multi_ends/textures.tex.<UDIM>_#")
        new, completeness = seq2.resize_from_existing_paths()
        assert new == seq
        assert completeness == Completeness.FULL

    def test_incomplete_multi_starts(self):
        seq = LoosePathSequence(
            "tests/fixtures/incomplete_multi_starts/<UDIM>_#.textures.tex"
        )
        new, completeness = seq.resize_from_existing_paths()
        assert completeness == Completeness.PARTIAL

    def test_incomplete_multi_in(self):
        seq = LoosePathSequence("tests/fixtures/incomplete_multi/textures.<UDIM>_#.tex")
        new, completeness = seq.resize_from_existing_paths()
        assert completeness == Completeness.PARTIAL

    def test_incomplete_multi_ends(self):
        seq = LoosePathSequence(
            "tests/fixtures/incomplete_multi_ends/textures.tex.<UDIM>_#"
        )
        new, completeness = seq.resize_from_existing_paths()
        assert completeness == Completeness.PARTIAL
