from datetime import date

AUTHOR = "Björn Ricks"
SITENAME = "Björn Ricks"
SITEURL = ""
SITESUBTITLE = "A personal Blog."
EMAIL = "bjoern.ricks@gmail.com"
COPYRIGHT_DATE = date.today().year

PATH = "content"

TIMEZONE = "Europe/Berlin"

DEFAULT_LANG = "en"

# Feed generation is usually not desired when developing
FEED_ALL_ATOM = None
CATEGORY_FEED_ATOM = None
TRANSLATION_FEED_ATOM = None
AUTHOR_FEED_ATOM = None
AUTHOR_FEED_RSS = None

# Blogroll
LINKS = (
    ("Pelican", "https://getpelican.com/"),
    ("Python.org", "https://www.python.org/"),
    ("Jinja2", "https://palletsprojects.com/p/jinja/"),
    ("You can modify those links in your config file", "#"),
)

# Social widget
SOCIAL = (
    ("You can add links in your config file", "#"),
    ("Another social link", "#"),
)

DEFAULT_PAGINATION = 10

ARTICLE_PATHS = ["posts"]
ARTICLE_URL = "posts/{category}/{slug}/"
ARTICLE_SAVE_AS = "posts/{category}/{slug}/index.html"

PAGE_URL = "pages/{slug}/"
PAGE_SAVE_AS = "pages/{slug}/index.html"

CATEGORIES_SAVE_AS = "categories/index.html"
CATEGORY_URL = "categories/{slug}/"
CATEGORY_SAVE_AS = "categories/{slug}/index.html"

STYLESHEET_URL = "/theme/css/style.css"

FEED_DOMAIN = SITEURL
FEED_RSS = "rss.xml"
FEED_ATOM = "feeds/atom.xml"
FEED_ALL_ATOM = "feeds/all.atom.xml"
CATEGORY_FEED_ATOM = "feeds/{slug}.atom.xml"

MENUITEMS = (
    ("/pages/about/", "About Me", "fa fa-user"),
    ("https://norden.social/@bjoernricks", "Mastodon", "fa fa-mastodon"),
    ("http://github.com/bjoernricks", "GitHub", "fa fa-github"),
    ("/feeds/atom.xml", "Atom Feed", "fa fa-rss"),
    ("/categories/", "Tags", "fa fa-tags"),
)

# Uncomment following line if you want document-relative URLs when developing
# RELATIVE_URLS = True


def debug(value: str) -> str:
    print(f"debug: {value}, {type(value)}, {dir(value)}")
    return ""


JINJA_FILTERS = {"debug": debug}
JINJA_GLOBALS = {"enumerate": enumerate}

from mdit_toc import toc_plugin
from pelican.plugins.markdown_it import DEFAULT_MARKDOWN_IT_PLUGINS

MARKDOWN_IT_PLUGINS = [
    *DEFAULT_MARKDOWN_IT_PLUGINS,
    (toc_plugin, {}),
]

TEASER_CSS_CLASS = "button is-link"
TEASER_CONTENT = 'Read more <span class="icon is-small"><i class="fa fa-angle-double-right"></i></span>'
