import pathlib

import pytest

import pathseq


@pytest.fixture(autouse=True)
def add_pathseq(doctest_namespace):
    doctest_namespace["pathseq"] = pathseq
    for attr in pathseq.__all__:
        doctest_namespace[attr] = getattr(pathseq, attr)

    doctest_namespace["Path"] = pathlib.Path
    doctest_namespace["PosixPath"] = pathlib.PosixPath
    doctest_namespace["PurePosixPath"] = pathlib.PurePosixPath
    doctest_namespace["PureWindowsPath"] = pathlib.PureWindowsPath
