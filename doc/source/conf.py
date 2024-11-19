# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information

import pathseq
project = 'pathseq'
copyright = '2024, Ashley Whetter'
author = 'Ashley Whetter'
release = pathseq.__version__

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

extensions = [
    'sphinx_design',
    'sphinx.ext.intersphinx',
    'sphinx.ext.todo',
    'sphinxcontrib.kroki',
]

templates_path = ['_templates']
exclude_patterns = [
    'decisions/000-decision-record-template.rst'
]


# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

html_theme = 'furo'
html_static_path = ['_static']
html_css_files = [
    'kroki_lists.css',
    'solid_image_background.css',
]


# -- Options for intersphinx -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/extensions/intersphinx.html#configuration

intersphinx_mapping = {
    'python': ('https://docs.python.org/3/', None),
}
