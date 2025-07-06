import pathlib

import pytest

import pathseq


@pytest.fixture(autouse=True)
def add_pathseq(doctest_namespace):
    doctest_namespace["pathseq"] = pathseq
    doctest_namespace["PathSequence"] = pathseq.PathSequence

    doctest_namespace["PosixPath"] = pathlib.PosixPath
