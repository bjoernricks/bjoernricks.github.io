---
title: xml.etree.ElementTree vs. lxml.etree
date: 2024-02-08 10:00:00 UTC
slug: 'stdlib-etree-vs-lxml-etree'
tags: python,xml,lxml,etree,elementtree
type: text
---

When working with XML and Python I often start with just using [xml.etree.ElementTree][stdlib]
from Python's standard library. It comes with Python and is sufficient for most
projects. But with quite big XML documents (> 1 GiB) parsing becomes slow
and [lxml.etree][lxml] shines.

While exchanging some code using [xml.etree.ElementTree][stdlib] to [lxml] I've
found some slightly differences in their implementation despite sharing the same
API.

# Namespaces

XML Namespaces can be used with a special syntax [`{namespace-uri}tag-name`](https://docs.python.org/3/library/xml.etree.elementtree.html#parsing-xml-with-namespaces) as tags.
To map a namespace to a specific prefix with [stdlib etree][stdlib], it requires
to [register the prefix/uri combination globally][register namespace]

[lxml] supports the same `{namespace-uri}tag-name` syntax but allows to register
a namespace map (a dict of namespace prefix to uri mapping) on every [Element](https://lxml.de/tutorial.html#namespaces)
during creation via a `nsmap` keyword argument.

# Default Namespace

[Registering][register namespace] the default namespace requires to pass an empty string `""` as
prefix with [stdlib etree][stdlib].

With [lxml] registering the default namespace requires to use `None` as key for
the prefix in the namespace mapping dict. Using an empty string `""` instead
will raise an exception.

With lxml it is not possible to [register a default namespace globally][register namespace]

At the end the namespace handling of lxml is superior because namespaces are not
defined globally. For example this allow to test them independently without
interference.

# Serialization

When [writing a XML document][ElementTree.write] with [stdlib etree][stdlib]
only the used namespaces will be serialized. Unused but registered namespaces
will be skipped and not included in the output.

With [lxml] all namespaces passed as a namespace map will be included in the
output wether they are used or not.

Setting `xml_declaration` to `True` and using `utf-8` as `encoding` will write
the encoding in upper cases as `<?xml version='1.0' encoding='UTF-8'?>`

[stdlib etree][stdlib] supports a `unicode` "encoding". When using this "encoding" it is
possible to pass a [TextIOBase](https://docs.python.org/3/library/io.html#io.TextIOBase) stream to the [`write`][ElementTree.write] function and `utf-8` is used as the real
encoding.

[lxml etree][lxml] only supports binary [RawIOBase](https://docs.python.org/3/library/io.html#io.RawIOBase)
streams for the [`write`][ElementTree.write] function.

[stdlib]: https://lxml.de/tutorial.html
[lxml]: https://lxml.de/api.html#lxml-etree
[ElementTree.write]: https://docs.python.org/3/library/xml.etree.elementtree.html#xml.etree.ElementTree.ElementTree.write
[register namespace]: https://docs.python.org/3/library/xml.etree.elementtree.html#xml.etree.ElementTree.register_namespace
