import logging
from collections.abc import Iterable
from pathlib import Path
from typing import Any, Callable, Sequence, Tuple

import yaml
from mdit_py_plugins.anchors import anchors_plugin
from mdit_py_plugins.footnote import footnote_plugin
from mdit_py_plugins.tasklists import tasklists_plugin
from pygments import highlight
from pygments.formatters import HtmlFormatter
from pygments.lexers import get_lexer_by_name, guess_lexer
from pygments.util import ClassNotFound

from markdown_it import MarkdownIt
from markdown_it.renderer import RendererHTML as MarkdownITRendererHTML
from markdown_it.token import Token
from markdown_it.utils import EnvType, OptionsDict
from pelican import signals
from pelican.readers import BaseReader, Readers

Settings = dict[str, Any]
MetaData = dict[str, str]
MarkdownItPlugin = Callable[..., None]

DEFAULT_MARKDOWN_IT_LOG_LEVEL = "WARNING"
DEFAULT_MARKDOWN_IT_PRESET_TYPE = "commonmark"
DEFAULT_MARKDOWN_IT_PLUGINS: list[
    MarkdownItPlugin | tuple[MarkdownItPlugin, dict[str, Any]]
] = [
    (tasklists_plugin, {"enabled": True}),
    (anchors_plugin, {"max_level": 3, "permalink": True}),
    footnote_plugin,
]


class MarkdownError(Exception):
    pass


def parse_front_matter(text: str) -> Tuple[str, MetaData]:
    text = text.lstrip()

    if not text.startswith("---"):
        return text, {}

    splitted = text.splitlines()

    front_matter = []
    other = []
    for i, line in enumerate(splitted[1:], 2):
        if line.startswith("---"):
            other = splitted[i:]
            break
        front_matter.append(line.rstrip())

    try:
        metadata = yaml.safe_load("\n".join(front_matter))
    except yaml.MarkedYAMLError as err:
        raise MarkdownError("Error while parsing meta data") from err
    if not isinstance(metadata, dict):
        raise MarkdownError(
            f"Could not parse meta data. Invalid data {metadata}"
        )
    return "\n".join(other), metadata


class RendererHTML(MarkdownITRendererHTML):
    def render(
        self, tokens: Sequence[Token], options: OptionsDict, env: EnvType
    ) -> str:
        # for i, token in enumerate(tokens, 1):
        #     print(f"{i}={token}")
        #     print()
        return super().render(tokens, options, env)

    def fence(
        self,
        tokens: Sequence[Token],
        idx: int,
        options: OptionsDict,
        env: EnvType,
    ) -> str:
        token = tokens[idx]
        info = token.info.strip() if token.info else ""
        language = ""
        lexer = None

        if info:
            arr = info.split(maxsplit=1)
            language = arr[0]

        if language:
            try:
                lexer = get_lexer_by_name(language)
            except ClassNotFound:
                pass

        if not lexer:
            try:
                lexer = guess_lexer(token.content)
            except ClassNotFound:
                return token.content

        return highlight(
            token.content,
            lexer,
            HtmlFormatter(wrapcode=True),
        )


class MarkdownItReader(BaseReader):
    enabled = True
    file_extensions = ["md", "markdown"]

    def __init__(self, settings: Settings):
        super().__init__(settings)

        preset_type = self.settings.get(
            "MARKDOWN_IT_PRESET_TYPE", DEFAULT_MARKDOWN_IT_PRESET_TYPE
        )
        log_level = self.settings.get(
            "MARKDOWN_IT_LOG_LEVEL", DEFAULT_MARKDOWN_IT_LOG_LEVEL
        ).upper()
        markdown_it_plugins = self.settings.get(
            "MARKDOWN_IT_PLUGINS", DEFAULT_MARKDOWN_IT_PLUGINS
        )

        logger = logging.getLogger("markdown_it")
        logger.setLevel(log_level)

        self._md = MarkdownIt(
            preset_type,
            {
                "typographer": True,
            },
            renderer_cls=RendererHTML,
        )
        self._md.enable(
            [
                "replacements",
                "smartquotes",
                "strikethrough",
            ]
        )
        for plugin in markdown_it_plugins:
            if isinstance(plugin, Iterable):
                plugin, kwargs = plugin  # noqa: PLW2901
                self._md.use(plugin, **kwargs)
            else:
                self._md.use(plugin)

    def _parse_metadata(self, meta: MetaData) -> MetaData:
        formatted_fields = self.settings.get("FORMATTED_FIELDS", [])
        output = {}

        for name, value in meta.items():
            name = name.lower()  # noqa: PLW2901
            if name in formatted_fields:
                value = self._md.render(value)  # noqa: PLW2901
            output[name] = self.process_metadata(name, value)

        return output

    def read_string(self, content: str) -> Tuple[str, MetaData]:
        text, meta = parse_front_matter(content)
        text = self._md.render(text, self.settings)
        meta = self._parse_metadata(meta)
        return text, meta

    def read(self, filename: str) -> Tuple[str, MetaData]:
        content = Path(filename).read_text(encoding="utf-8")
        return self.read_string(content)

    @classmethod
    def add(cls, readers: Readers):
        readers.reader_classes["markdown"] = cls


def register():
    signals.readers_init.connect(MarkdownItReader.add)
