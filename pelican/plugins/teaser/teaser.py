from typing import Any, Iterable

from pelican import signals
from pelican.contents import Article
from pelican.generators import ArticlesGenerator, Generator

Settings = dict[str, Any]


def apply_teaser(article: Article) -> None:
    if article.metadata.get("summary"):
        # article has already a summary
        return

    lines = []
    has_teaser = False
    for line in article.content.splitlines():
        if line.startswith("<!-- TEASER_END -->"):
            has_teaser = True
            break

        lines.append(line)

    if not has_teaser:
        return

    settings: Settings = article.settings
    css_class = settings.get("TEASER_CSS_CLASS", "read-more")
    content = settings.get("TEASER_CONTENT", "Read more")

    lines.append(f'<a class="{css_class}" href="{article.url}">{content}</a>')
    article.metadata["summary"] = "\n".join(lines)


def teaser_plugin(generators: Iterable[Generator]) -> None:
    for generator in generators:
        if isinstance(generator, ArticlesGenerator):
            for article in generator.articles:
                apply_teaser(article)


def register() -> None:
    signals.all_generators_finalized.connect(teaser_plugin)
