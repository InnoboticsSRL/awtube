# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information
import sys
import os

project = 'awtube'
copyright = '2024, Armando Selvija'
author = 'Armando Selvija'
version = '0.1.0'
release = '0.1.0'

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

sys.path.insert(0, os.path.abspath('../../src'))

extensions = [
    'sphinx.ext.autodoc',
    'sphinx.ext.autosummary',
]
autosummary_generate = True

templates_path = ['_templates']
exclude_patterns = []


# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

html_title = 'awtube docs'
html_theme = 'furo'
html_theme_options = {
    "light_css_variables": {
        "color-brand-primary": "blue",
        "color-brand-content": "#CC3333",
        "color-admonition-background": "orange",
    },
}
# html_theme = 'sphinx_rtd_theme'
html_logo = '../media/logo_aw.png'
html_favicon = '../media/logo_aw.png'
html_static_path = ['_static']
