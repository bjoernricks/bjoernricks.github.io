import functools
import re
from dataclasses import dataclass, field
from typing import Iterable, Sequence

from markdown_it import MarkdownIt
from markdown_it.common.utils import escapeHtml
from markdown_it.renderer import RendererProtocol
from markdown_it.rules_block import StateBlock
from markdown_it.rules_core import StateCore
from markdown_it.token import Token
from markdown_it.utils import EnvType, OptionsDict


@dataclass
class Node:
    level: int = 0
    title: str = ""
    children: list["Node"] = field(default_factory=list)

    def done(self) -> None:
        self.level = 0
        self.title = ""
        self.children = []


def get_levels(level: str | int | Iterable[int]) -> list[int]:
    if isinstance(level, str):
        return [int(level)]
    if isinstance(level, int):
        return [level]
    if isinstance(level, Iterable):
        return list(level)

    raise ValueError(f"Invalid value {level} of type {type(level)} for level")


def toc_plugin(
    md: MarkdownIt,
    pattern: str = r"^(\[TOC\])",
    level: int | Iterable[int] = (1, 2),
    list_type: str = "ul",
) -> None:
    """
    Plugin ported from https://github.com/nagaozen/markdown-it-toc-done-right
    """
    ast = Node()
    levels: list[int] = get_levels(level)
    compiled_pattern = re.compile(pattern, re.IGNORECASE)
    list_type = escapeHtml(list_type)

    md.block.ruler.before(
        "heading",
        "toc",
        functools.partial(_toc, compiled_pattern),
        {"alt": ["paragraph", "reference", "blockquote"]},
    )
    md.core.ruler.push(
        "generate_toc_ast", functools.partial(generate_toc_ast, ast)
    )

    md.add_render_rule(
        "toc_body", functools.partialmethod(render_toc_body, ast, levels, list_type)  # type: ignore
    )


def _toc(
    pattern: re.Pattern[str],
    state: StateBlock,
    startLine: int,
    endLine: int,
    silent: bool,
) -> bool:
    pos = state.bMarks[startLine] + state.tShift[startLine]
    max = state.eMarks[startLine]

    # use whitespace as a line tokenizer and extract the first token
    # to test against the placeholder anchored pattern, rejecting if false
    line_first_token = state.src[pos:max].split(" ")[0]
    matches = pattern.match(line_first_token)
    if not matches:
        return False

    if silent:
        return True

    state.line = startLine + 1

    token = state.push("toc_open", "nav", 1)
    token.markup = ""
    token.map = [startLine, state.line]

    token = state.push("toc_body", "", 0)
    token.markup = ""
    token.map = [startLine, state.line]
    token.children = []

    token = state.push("toc_close", "nav", -1)
    token.markup = ""

    return True


def is_level_selected(levels: list[int], level: int) -> bool:
    return level in levels


def render_toc_body(
    self: RendererProtocol,
    ast: Node,
    levels: list[int],
    list_type: str,
    tokens: Sequence[Token],
    idx: int,
    options: OptionsDict,
    env: EnvType,
) -> str:
    slugs: set[str] = set()

    def ast_to_html(tree: Node) -> str:
        elements = []

        if not tree.children:
            return ""

        if tree.level == 0 or is_level_selected(levels, tree.level):
            elements.append(f"<{list_type}>")

        for node in tree.children:
            if is_level_selected(levels, node.level):
                slug = unique_slug(slugify(node.title), slugs)
                elements.append(
                    f'<li><a href="#{slug}">{node.title}</a>{ast_to_html(node)}</li>'
                )
            else:
                ast_to_html(node)

        if tree.level == 0 or is_level_selected(levels, tree.level):
            elements.append(f"</{list_type}>")

        return "\n".join(elements)

    content = ast_to_html(ast)
    ast.done()
    return content


def headings_to_ast(ast: Node, tokens: Sequence[Token]):
    stack = [ast]

    for i, token in enumerate(tokens):
        if token.type == "heading_open":
            next_token = tokens[i + 1]
            text_children = (
                [
                    t.content
                    for t in next_token.children
                    if t.type == "text" or t.type == "code_inline"
                ]
                if next_token.children
                else []
            )
            anchor = "".join(text_children)
            node = Node(level=int(token.tag[1]), title=anchor)

            if node.level > stack[0].level:
                stack[0].children.append(node)
                stack.insert(0, node)
            elif node.level == stack[0].level:
                stack[1].children.append(node)
                stack[0] = node
            else:
                while node.level <= stack[0].level:
                    stack.pop(0)

                stack[0].children.append(node)
                stack.insert(0, node)
    return ast


def generate_toc_ast(ast: Node, state: StateCore) -> None:
    headings_to_ast(ast, state.tokens)


def slugify(title: str) -> str:
    return re.sub(
        r"[^\w\u4e00-\u9fff\- ]", "", title.strip().lower().replace(" ", "-")
    )


def unique_slug(slug: str, slugs: set[str]) -> str:
    uniq = slug
    i = 1
    while uniq in slugs:
        uniq = f"{slug}-{i}"
        i += 1
    slugs.add(uniq)
    return uniq
