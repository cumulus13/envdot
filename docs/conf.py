# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

import os
import sys
from datetime import datetime

# -- Path setup --------------------------------------------------------------
# Add the project root directory to the path so that autodoc can find modules
sys.path.insert(0, os.path.abspath('..'))
sys.path.insert(0, os.path.abspath('../envdot'))

# -- Project information -----------------------------------------------------
project = 'envdot'
copyright = f'{datetime.now().year}, Hadi Cahyadi'
author = 'Hadi Cahyadi'

# The full version, including alpha/beta/rc tags
release = '1.0.14'
version = '1.0.14'

# -- General configuration ---------------------------------------------------
extensions = [
    'sphinx.ext.autodoc',
    'sphinx.ext.autosummary',
    'sphinx.ext.viewcode',
    'sphinx.ext.napoleon',
    'sphinx.ext.intersphinx',
    'sphinx.ext.todo',
    'sphinx.ext.coverage',
    'sphinx.ext.githubpages',
    'sphinx_copybutton',
    'myst_parser',
]

# Napoleon settings for Google/NumPy style docstrings
napoleon_google_docstring = True
napoleon_numpy_docstring = True
napoleon_include_init_with_doc = True
napoleon_include_private_with_doc = False
napoleon_include_special_with_doc = True
napoleon_use_admonition_for_examples = True
napoleon_use_admonition_for_notes = True
napoleon_use_admonition_for_references = True
napoleon_use_ivar = False
napoleon_use_param = True
napoleon_use_rtype = True
napoleon_type_aliases = None

# Autodoc settings
autodoc_default_options = {
    'members': True,
    'member-order': 'bysource',
    'special-members': '__init__',
    'undoc-members': True,
    'exclude-members': '__weakref__'
}
autodoc_typehints = 'description'
autosummary_generate = True

# Intersphinx mapping
intersphinx_mapping = {
    'python': ('https://docs.python.org/3', None),
}

# Add any paths that contain templates here, relative to this directory.
templates_path = ['_templates']

# List of patterns, relative to source directory, that match files and
# directories to ignore when looking for source files.
exclude_patterns = ['_build', 'Thumbs.db', '.DS_Store']

# The suffix(es) of source filenames.
source_suffix = {
    '.rst': 'restructuredtext',
    '.md': 'markdown',
}

# The master toctree document.
master_doc = 'index'

# -- Options for HTML output -------------------------------------------------
html_theme = 'sphinx_rtd_theme'
html_theme_options = {
    'logo_only': False,
    # 'display_version': True,
    'prev_next_buttons_location': 'bottom',
    'style_external_links': True,
    'collapse_navigation': False,
    'sticky_navigation': True,
    'navigation_depth': 4,
    'includehidden': True,
    'titles_only': False,
}

# Add any paths that contain custom static files (such as style sheets) here,
# relative to this directory. They are copied after the builtin static files,
# so a file named "default.css" will overwrite the builtin "default.css".
html_static_path = ['_static']

# Custom CSS
html_css_files = [
    'css/custom.css',
]

# HTML favicon and logo
# html_favicon = '_static/favicon.ico'
# html_logo = '_static/logo.png'

# -- Options for LaTeX output ------------------------------------------------
latex_elements = {
    'papersize': 'a4paper',
    'pointsize': '11pt',
}

latex_documents = [
    (master_doc, 'envdot.tex', 'envdot Documentation',
     'Hadi Cahyadi', 'manual'),
]

# -- Options for manual page output ------------------------------------------
man_pages = [
    (master_doc, 'envdot', 'envdot Documentation',
     [author], 1)
]

# -- Options for Texinfo output ----------------------------------------------
texinfo_documents = [
    (master_doc, 'envdot', 'envdot Documentation',
     author, 'envdot', 'Enhanced environment variable management for Python.',
     'Miscellaneous'),
]

# -- Extension configuration -------------------------------------------------
# Todo extension
todo_include_todos = True

# Copy button settings
copybutton_prompt_text = r">>> |\.\.\. |\$ |In \[\d*\]: | {2,5}\.\.\.: | {5,8}: "
copybutton_prompt_is_regexp = True

# MyST parser settings
myst_enable_extensions = [
    "colon_fence",
    "deflist",
    "fieldlist",
    "html_admonition",
    "html_image",
    "replacements",
    "smartquotes",
    "strikethrough",
    "substitution",
    "tasklist",
]