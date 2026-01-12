*****************
Contributor Guide
*****************

Making a Change
===============

Tests are executed through `tox <https://tox.readthedocs.io/en/latest/>`_.

.. code-block:: bash

    tox


Code is formatted using `ruff <https://github.com/python/black>`_.

.. code-block:: bash

    tox -e autoformat


When making a pull request you will need to create a news fragment to document your change.
Release notes are managed through `towncrier <https://towncrier.readthedocs.io/en/stable/index.html>`_.

.. code-block:: bash

    tox -e release_notes -- create --help


Release Process
===============

This page documents the steps to be taken to release a new version of Sphinx AutoAPI.

Pre-Checks
----------

1. Check that the dependencies of the package are correct.
2. Clean the ``.tox`` directory and run the tests.
3. Commit and push any changes needed to make the tests pass.
4. Check that the tests passed on github.

Preparation
-----------

1. Update the version numbers in ``autoapi/__init__.py``.
2. Run ``tox -e release_notes -- build``
3. Commit and push the changes.
4. Check that the tests passed on github.

Release
-------

1. Create a new release in github that tags the commit
   and uses the built release notes as the description.

The tag created by the release will trigger the github actions to
build and upload the package to PyPI.
