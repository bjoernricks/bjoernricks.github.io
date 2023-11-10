---
category: 'python'
date: 2023-11-10 09:58:50 UTC
description: 'Quick overview about the most important additions in a Python release'
link: ''
slug: what-s-new-in-python
tags: python,news,features
title: What's new in Python 3
type: text
---
Quick overview about the most important additions in a Python release

[TOC]

<!-- TEASER_END -->

# Python 3.12

[https://docs.python.org/3/whatsnew/3.12.html](https://docs.python.org/3/whatsnew/3.12.html)

## Typing

* Type Parameter Syntax [PEP 695](https://peps.python.org/pep-0695/)
```python
class ClassA[T: str]:
    def method1(self) -> T:
```
instead of
```python
from typing import Generic, TypeVar

_T_co = TypeVar("_T_co", covariant=True, bound=str)

class ClassA(Generic[_T_co]):
    def method1(self) -> _T_co:
```

# Python 3.11

[https://docs.python.org/3/whatsnew/3.11.html](https://docs.python.org/3/whatsnew/3.11.html)

## Features
* [Faster CPython](https://docs.python.org/3/whatsnew/3.11.html#faster-cpython)
* tomllib — Support for parsing TOML in the Standard Library [PEP 680](https://peps.python.org/pep-0680/)
* Exception Groups and except* [PEP 654](https://peps.python.org/pep-0654/)
* [`with contextlib.chdir(directory):` ](https://docs.python.org/3/library/contextlib.html#contextlib.chdir)

## Typing
*  Self Type [PEP 673](https://peps.python.org/pep-0673/)
*  [LiteralString](https://docs.python.org/3/library/typing.html#typing.LiteralString) [PEP 675](https://peps.python.org/pep-0675/)

## Enum
* [StrEnum](https://docs.python.org/3/library/enum.html#enum.StrEnum)

## AsyncIO
* [TaskGroup](https://docs.python.org/3/library/asyncio-task.html#asyncio.TaskGroup)
* Implementation of trio’s cancel scope feature with [timeout](https://docs.python.org/3.11/library/asyncio-task.html#asyncio.timeout) and [timeout_at](https://docs.python.org/3.11/library/asyncio-task.html#asyncio.timeout_at)

# Python 3.10

[https://docs.python.org/3/whatsnew/3.10.html](https://docs.python.org/3/whatsnew/3.10.html)

## Features
* Structural Pattern Matching [PEP 634]()

## Typing
* Allow writing union types as `X | Y` [PEP 604](https://peps.python.org/pep-0604/)

## Dataclasses
* Added slots parameter
* Keyword-only fields

## AsyncIO
* async versions of iter and next called [aiter and anext](https://github.com/python/cpython/issues/76042)

# Python 3.9

[https://docs.python.org/3/whatsnew/3.9.html](https://docs.python.org/3/whatsnew/3.9.html)

## Features
* PEG language parser [PEP 617](https://peps.python.org/pep-0617/)
* Zoneinfo module [PEP 615](https://peps.python.org/pep-0615/)

## Typing
* Type Hinting Generics In Standard Collections [PEP 585](https://peps.python.org/pep-0585/)
	Examples: `list[str]`

## AsyncIO
* [asyncio.to_thread](https://docs.python.org/3/library/asyncio-task.html#asyncio.to_thread) -> for running IO-bound functions in a separate thread to avoid blocking the event loop