pathseq
=======

.. image:: https://readthedocs.org/projects/pathseq/badge/?version=latest
    :target: https://pathseq.readthedocs.org
    :alt: Documentation

.. image:: https://github.com/AWhetter/pathseq/actions/workflows/main.yml/badge.svg?branch=main
    :target: https://github.com/AWhetter/pathseq/actions/workflows/main.yml?query=branch%3Amain
    :alt: Github Build Status

.. image:: https://img.shields.io/pypi/v/pathseq.svg
    :target: https://pypi.org/project/pathseq/
    :alt: PyPI Version

.. image:: https://img.shields.io/pypi/pyversions/pathseq.svg
    :target: https://pypi.org/project/pathseq/
    :alt: Supported Python Versions

A pathlib-like library for working with file sequences.


Getting Started
---------------

The following section demonstrates how to install ``pathseq`` and some basic usage.
Full documentation is available here: https://pathseq.readthedocs.io/en/latest/


Installation
~~~~~~~~~~~~

``pathseq`` can be installed through pip:

.. code-block:: bash

    pip install pathseq

Usage
~~~~~

TODO

For more detailed usage, see the documentation:
https://pathseq.readthedocs.io/en/latest/


Contributing
------------

Running the tests
~~~~~~~~~~~~~~~~~

Tests are executed through `tox <https://tox.readthedocs.io/en/latest/>`_.

.. code-block:: bash

    tox


Code Style
~~~~~~~~~~

Code is formatted using `black <https://github.com/python/black>`_.

You can check your formatting using black's check mode:

.. code-block:: bash

    tox -e format

You can also get black to format your changes for you:

.. code-block:: bash

    tox -e format -- src/ tests/


Release Notes
~~~~~~~~~~~~~

Release notes are managed through `towncrier <https://towncrier.readthedocs.io/en/stable/index.html>`_.
When making a pull request you will need to create a news fragment to document your change:

.. code-block:: bash

    tox -e release_notes -- create --help


Versioning
----------

We use `SemVer <https://semver.org/>`_ for versioning.
For the versions available, see the `tags on this repository <https://github.com/AWhetter/pathseq/tags>`_.


License
-------

This project is licensed under the MIT License.
See the `LICENSE.rst <LICENSE.rst>`_ file for details.
