#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys, os
import sphinx_rtd_theme


AUTHOR = 'Michel Mooij'
YEAR = '2016'
VERSION = '0.4.12'
RELEASE = VERSION


sys.path.insert(0, os.path.abspath('..'))
extensions = ['sphinx.ext.autodoc', 'sphinx.ext.viewcode']
templates_path = ['_templates']
source_suffix = '.rst'
master_doc = 'index'
project = u'waftools'
copyright = u'%s, %s' % (YEAR, AUTHOR)
version = '%s' % (VERSION)
release = '%s' % (RELEASE)
exclude_patterns = ['_build']
pygments_style = 'sphinx'

rst_epilog = '.. |pkg_version| replace:: %s' % (VERSION)


#----------------------------------------------------------------
html_title = "Waftools %s" % (VERSION)
html_short_title = "Waftools"
html_theme = "sphinx_rtd_theme"
html_theme_path = [sphinx_rtd_theme.get_html_theme_path()]
html_static_path = ['_static']
html_last_updated_fmt = '%b %d, %Y'
htmlhelp_basename = 'waftoolsdoc'


#----------------------------------------------------------------
latex_elements = {
    'papersize': 'a4paper',
    'pointsize': '10pt',
}

latex_documents = [
  ('index', 'waftools.tex', u'waftools Documentation',
   u'%s' % (AUTHOR), 'manual'),
]


#----------------------------------------------------------------
man_pages = [
    ('index', 'waftools', u'waftools Documentation',
     [u'%s' % (AUTHOR)], 1)
]


#----------------------------------------------------------------
texinfo_documents = [
  ('index', 'waftools', u'waftools Documentation',
   u'%s' % (AUTHOR), 'waftools', 'One line description of project.',
   'Miscellaneous'),
]


#----------------------------------------------------------------
epub_title = u'waftools'
epub_author = u'%s' % (AUTHOR)
epub_publisher = u'%s' % (AUTHOR)
epub_copyright = u'%s, %s' % (YEAR, AUTHOR)


