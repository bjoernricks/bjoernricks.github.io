# This file is only used if you use `make publish` or
# explicitly specify it as your config file.

import sys
from pathlib import Path

sys.path.append(str(Path.cwd()))
from pelicanconf import *  # noqa: E402, F403

SITEURL = "https://bjoernricks.github.io"
RELATIVE_URLS = False

DELETE_OUTPUT_DIRECTORY = True
JINJA_FILTERS = {}
