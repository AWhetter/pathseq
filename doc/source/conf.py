# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information

import pathseq

project = "pathseq"
copyright = "2024, Ashley Whetter"
author = "Ashley Whetter"
release = pathseq.__version__

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

extensions = [
    "sphinx_design",
    "sphinx.ext.intersphinx",
    "sphinx.ext.napoleon",
    "sphinx.ext.todo",
]

templates_path = ["_templates"]
exclude_patterns = ["decisions/000-decision-record-template.rst"]


# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

html_theme = "furo"
html_static_path = ["_static"]
html_css_files = [
    "solid_image_background.css",
]


# -- Options for intersphinx -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/extensions/intersphinx.html#configuration

intersphinx_mapping = {
    "python": ("https://docs.python.org/3/", None),
}


# -- Options for autodoc -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/extensions/autodoc.html#configuration

extensions.append("sphinx.ext.autodoc")
autodoc_default_options = {
    "member-order": "bysource",
}
autodoc_type_aliases = {
    "ParsedLooseSequence": "ParsedLooseSequence",
}



# -- Patch section numbering -------------------------------------------------

from docutils import nodes
from docutils.parsers.rst.directives.parts import Sectnum as SectnumDirective
from docutils.transforms.parts import SectNum as SectnumTransform


class Sectnum(SectnumDirective):
    """
    Override the Sectnum directive to call my own Sectnum transform
    """
    def run(self):
        pending = nodes.pending(SectNumTrans)
        pending.details.update(self.options)
        self.state_machine.document.note_pending(pending)
        return [pending]


class SectNumTrans(SectnumTransform):
    """
    Override `Sectnum` from docutils

    I do not want the big title of the page to be numbered:

        Document Name

        1. Section
           1.1. Subsection

    And not

        1. Document Name

        1.1 Section
           1.1.1. Subsection

    """
    start_depth = 1

    def update_section_numbers(self, node, prefix=(), depth=0, level=0):
        self.suffix = '.'
        depth += 1
        if prefix:
            sectnum = 1
        else:
            sectnum = self.startvalue
        level += 1
        index_rule = 1
        index_directive = 1
        for child in node:
            if isinstance(child, nodes.section):
                title = child[0]

                if level > self.start_depth:
                    numbers = prefix + (str(sectnum),)
                    text = (self.prefix + '.'.join(numbers) + self.suffix + u'\u00a0' * 2)
                else:
                    numbers = prefix
                    text = ''

                generated = nodes.generated('', text, classes=['sectnum'])
                title.insert(0, generated)
                title['auto'] = 1
                if depth < self.maxdepth:
                    self.update_section_numbers(child, numbers, depth, level)
                sectnum += 1


def setup(app):
    app.add_directive('sectnum', Sectnum)
