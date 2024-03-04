---
title: Understanding Context Manager and its Syntastic Sugar
date: 2024-03-04 10:00:00 UTC
slug: context-manager
tags: python,context-manager,with-statement
type: text
---

The Context Manager is one of my favorite features in Python. It can be used for
all kind of interesting things around blocks of code. This article gives a
background about the origins of the context manager, which problem it solves and
how to use it.

[TOC]

# Origins

When using resources like files, memory, network connections, it is
desirable to release the resources after they aren't in use anymore. Otherwise
it can cause several issues like not being able to create another connection or
various [memory leaks](https://en.wikipedia.org/wiki/Memory_leak).

Of course this could be avoided by using *opening* and *closing* methods (or
functions) on the resources, like in the following code examples:

```python
# Example 1 - A network connection

connection = create_connection()
# use the connection, for example send bytes
connection.shutdown()
```

```python
# Example 2 - A file for I/O

file = open("foo.txt")
# do something with the file, for example read and write bytes
file.close()
```

```python
# Example 3 - A lock for concurrent access

lock = acquire_lock()
# run code that requires exclusive access
lock.release()
```

```python
# Example 3 -  Database access

db = database_open()
db.transaction()
# execute SQL statements for example db.execute("INSERT INTO foo VALUES ('bar')")
db.commit()
db.close()
```

But using *opening* and *closing* methods has some drawbacks:

* The releasing method may be called conditionally at different places. As a
  result the resource may not be closed in all required cases
* The releasing method might never be called because it is just forgotten, the
  documentation wasn't read, ...
* At best the method names are standardized (for example to always
  to use `open` and `close`)
* Errors may occur and exceptions will be raised before the resources can
  released

Especially the last item would always require to write code such as:

```python
file = open("foo.txt")

try:
    # do something with the file
finally:
    file.close()
```

where *do something with the file* can be very long, contain function calls,
conditionals, additional error handling with nested try/except blocks and
therefore it becomes difficult to read.

But at the end, this approach is always error prone because it's just implicitly
required to be run within a try/except block.

To address these shortcomings, [PEP 343](https://peps.python.org/pep-0343/)
introduced the `with` statement and the *Context Manager Protocol*.

# Context Manager Protocol

As you have seen in the previous examples handling resources always consists of
two phases:

1. **acquiring** (or opening)
2. **releasing** (or closing)

Context Managers have been introduced to handle the process of acquiring and
releasing of resources automatically even under error conditions.

Let us take a look at the Context Manager:

```python
class ContextManager:
    def __enter__(self) -> Any:
        """
        Setup and acquire the resource and return it
        """

    def __exit__(self, exc_type, exc_value, traceback) -> bool:
        """
        Shutdown and release the resource even if an error was raised
        """
```

A context manager implementation consists of two [dunder](https://www.pythonmorsels.com/what-are-dunder-methods/)
methods, `__enter__` and `__exit__`.

The `__enter__` method is intended to setup and acquire a resource. The resource
object or an object handling the resource may be returned from the method
optionally.

The `__exit__` method is intended to shutdown and release the resource and gets
the current error information passed if an error was raised. Otherwise the three
arguments are `None`. Therefore the method is even able to handle raised errors
optionally. If the error should be suppressed `True` must be returned.

# The With Statement as Syntastic Sugar

To actually execute both methods Context Managers are used in conjunction with
the `with` statement. The `with` statement encircles a block of code.

It is defined as:

```python
with EXPRESSION as TARGET:
    BLOCK
```

where the *as TARGET* part is optional.

This is [Syntastic Sugar](https://snarky.ca/tag/syntactic-sugar/) and
semantically equivalent to:

```python
manager = (EXPRESSION)
try:
    TARGET = manager.__enter__(manager)
    BLOCK
except:
    if not manager.__exit__(*sys.exc_info()):
        raise
else:
    manager.__exit__(None, None, None)

```

TARGET will get the return value of the Context Manager's `__enter__` method.
The `__exit__` method will be called either with the exception and traceback
information in case of an error, or when the code of BLOCK has finished. In case
of an error, the Context Manager can suppress the fall through of the error by
returning a truthy value from the `__exit__` method. Otherwise the error will be
(re-)raised. Remember, not having a return statement in a method actually
returns `None`, which evaluates to `False`. Thus by default the error will be
(re-)raised.

The with statement also allows to combine several context managers.

> With more than one item, the context managers are processed as if multiple
> with statements were nested:

```python
with A() as a, B() as b:
    BLOCK
```

is semantically equivalent to:

```python
with A() as a:
    with B() as b:
        BLOCK
```

[Source](https://docs.python.org/3/reference/compound_stmts.html#the-with-statement)

In summary:

> The Python with statement creates a runtime context that allows you to run
> a group of statements under the control of a context manager. PEP 343 added
> the with statement to make it possible to factor out standard use cases of
> the try … finally statement.

> Compared to traditional try … finally constructs, the with statement can
> make your code clearer, safer, and reusable.

[Source](https://realpython.com/python-with-statement/#the-with-statement-approach)

# Implementing a Context Manager using contextlib

When implementing a context manager as a class it may be difficult to understand
the actual call flow. Therefore Python provides tools in the standard library
for implementing a context manager using a function.

Using [contextlib.contextmanager](https://docs.python.org/3/library/contextlib.html#contextlib.contextmanager)
decorator allows for implementing a `Context Manager` easily by using a
[generator function](https://docs.python.org/3/reference/datamodel.html#generator-functions).
Take a look at the following code:

```python
from contextlib import contextmanager

@contextmanager
def managed_resource(*args, **kwargs):
    # Code to acquire resource, e.g.:
    resource = acquire_resource(*args, **kwargs)
    try:
        yield resource
    finally:
        # Code to release resource, e.g.:
        release_resource(resource)
```

This is equivalent to the following class based context manager:


```python
class managed_resource:
    def __init__(*args, **kwargs):
        self.args = args
        self.kwargs = kwargs
        self.resource = None

    def __enter__(self):
        self.resource = acquire_resource(*self.args, *self.kwargs)
        return self.resource

    def __exit__(self, exc_type, exc_value, exc_traceback):
        release_resource(self.resource)
```

The function based context manager is easier to read and to follow.

To understand what `contextmanger` decorator does actually internally, a
(simplified) version of the decorator itself could be implemented as:

```python
class GeneratorContextManager:

    def __init__(self, generator):
        self.generator = generator

    def __enter__(self):
        return self.generator.send(None)

    def __exit__(self, exc_type, exc_value, exc_traceback):
       if exc_type is None:
           try:
               self.generator.send(None)
           except StopIteration:
               return
       else:
           try:
               self.generator.throw(exc_type, exc_value, exc_traceback)
           except StopIteration:
               return True
           except:
                raise

def contextmanager(generator_func):
   def wrapper(*args, **kwargs):
       return GeneratorContextManager(generator_func(*args, **kwargs))
   return wrapper
```

[Source](https://peps.python.org/pep-0343/#generator-decorator)

# Capture the Call Flow

To explain the code from the previous chapters and to understand its call flow
easily, two simple context managers can be implemented.

A class based Context Manager:

```python
class SimpleContextManager:
    def __enter__(self):
        print("acquire")
        return "resource"

    def __exit__(self, exc_type, exc_value, exc_traceback):
        print("release")


with SimpleContextManager() as manager:
    print(manager)
```

Output:

```python
>>> with SimpleContextManager() as manager:
...     print(manager)
...
acquire
resource
release
```

Via `contextlib.contextmanager` decorator:

```python
from contextlib import contextmanager

@contextmanager
def simple_context_manager():
    print("acquire")
    try:
        yield "resource"
    finally:
        print("release")

with simple_context_manager() as manager:
    print(manager)
```

Output

```python
>>> with simple_context_manager() as manager:
...     print(manager)
...
acquire
resource
release
```

# Example Context Managers

To express the usefulness and flexibility of Context Managers, let me show you
some additional examples for using Context Manager even beyond strict resource
acquisition and release.

## Example 1 - Redirect Stdout

A Context Manager to redirect stdout to some other IO object.

```python
import sys

class RedirectStdout:
    def __init__(self, new_target):
        self._new_stdout = new_target
        self._old_stdout = None

    def __enter__(self):
        self._old_stdout = sys.stdout
        sys.stdout = self._new_stdout
        return self._new_stdout

    def __exit__(self, exc_type, exc_value, exc_traceback):
        sys.stdout = self._old_stdout
```

Usage:

```python
with open('help.txt', 'w') as f, RedirectStdout(f):
    help(print)
```

A similar Context Manager is available in the Python standard library as
[`contextlib.redirect_stdout`](https://docs.python.org/3/library/contextlib.html#contextlib.redirect_stdout).

## Example 2 - Suppress Exceptions

A Context Manager to suppress all raised exceptions.

```python
from contextlib import contextmanager

@contextmanager
def catch_all():
    try:
        yield
    except:
        pass
```

Usage:

```python
with catch_all():
    raise RuntimeException("foo")
```

A related Context Manager is available in the Python standard library as
[`contextlib.suppress`](https://docs.python.org/3/library/contextlib.html#contextlib.suppress).

## Example 3 - Add a directory to the Python module search path temporarily

```python
import sys

@contextmanager
def add_module_path(path: str):
    sys.path.append(path)
    try:
        yield
    finally:
        try:
            sys.path.remove(path)
        except ValueError:
            # path is not in sys.path
            pass
```

Usage:

```python
with add_module_path("./packages/"):
    import rich
```

## Example 4 - Print Prefix

```python
class PrintPrefix:
    def __init__(self, prefix: str):
        self.prefix = prefix
        self.active = False

    def print(self, *args, **kwargs):
        if self.active:
            print(self.prefix, *args, **kwargs)
        else:
            print(*args, **kwargs)

    def __enter__(self):
        self.active = True
        return self

    def __exit__(self, exc_type, exc_value, exc_traceback):
        self.active = False
```

Usage:

```python
with PrintPrefix("😀") as out:
    out.print("are we happy now?")
    out.print("yes we are!")
```

Output:

```
>>> with PrintPrefix("😀") as out:
...     out.print("are we happy now?")
...     out.print("yes we are!")
...
😀 are we happy now?
😀 yes we are!
```

# Links

* [With Statement Context Managers](https://docs.python.org/3/reference/datamodel.html#with-statement-context-managers)
* [Context Manager Types](https://docs.python.org/3/library/stdtypes.html#typecontextmanager)
* [PEP 343 – The “with” Statement](https://peps.python.org/pep-0343/)
* [Real Python – Context Managers and Python's with Statement](https://realpython.com/python-with-statement/)
