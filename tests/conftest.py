import sys

import pytest


def pytest_collection_modifyitems(items):
    if sys.platform.startswith("win"):
        to_skip = {
            # We want to be able to demonstrate that Path is returned,
            # but this is PosixPath or WindowsPath depending on the OS.
            # Making this test work on all platforms would require making
            # the examples more complex, which we don't want to do in these
            # docs that are targeted at new users. So skip the tests on Windows.
            "doc/source/index.rst::index.rst",
            "doc/source/quickstart.rst::quickstart.rst",
        }
        for item in items:
            if item.nodeid in to_skip:
                item.add_marker(pytest.mark.xfail)
