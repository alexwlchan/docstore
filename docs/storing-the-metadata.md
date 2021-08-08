# Storing the metadata

I store a certain amount of metadata alongside each file, including:

*   The original filename
*   When I saved it
*   A one-line human-readable description
*   What tags I'm using

This document explains how I model the metadata and how I serialise it to disk.



## Modelling the metadata with attrs

I use the [attrs library][attrs] to define my metadata models.
The library provides a couple of decorators that let you define data classes without writing all the usual boilerplate.

For example:

```pycon
>>> import attr

>>> @attr.s
... class Document:
...     path = attr.ib()
...     tags = attr.ib()
```

This defines a class called `Document` with two attributes `path` and `tags`.
It gives me a constructor, and makes both those attributes available for reading/writing:

```pycon
>>> doc = Document(
...     path="scanned_doc.pdf",
...     tags=["home", "bills", "acme energy"]
... )

>>> doc.path
"scanned_doc.pdf"

>>> doc.tags
["home", "bills", "acme energy"]

>>> doc.tags.append("utilities:electricity")
>>> doc.tags
["home", "bills", "acme energy", "utilities:electricity"]
```

The attrs library defines commonly used methods on the class, saving you from writing that boilerplate yourself.
For example, it includes a nice repr() of objects:

```pycon
>>> repr(doc)
Document(path="scanned_doc.pdf", tags=["home", "bills", "acme energy", "utilities:electricity"])
```

That repr() can be eval()'d to get back the same value, and attrs provides methods for equality and hashing (not shown):

```pycon
>>> eval(repr(doc)) == doc
True

>>> doc == Document(path="cat.jpg", tags=["pets"])
False
```

If this looks similar to the [dataclasses module][dataclasses] in the Python standard library, it's because attrs was a direct inspiration for dataclasses.
I was using attrs before dataclasses existed and I've never been persuaded to switch.

Using attrs allows me to write short, compact models for my metadata.
The entire model definition is less than 40 lines: [see models.py](https://github.com/alexwlchan/docstore/blob/a4b7972d147b538bbf48792566d55eeaea24e32a/src/docstore/models.py#L40-L71) for my model implemtnation.

[attrs]: https://www.attrs.org/en/stable/
[dataclasses]: https://docs.python.org/3/library/dataclasses.html



## Using JSON as a database

You can serialise an attrs model to a Python dict:

```pycon
>>> attr.asdict(doc)
{"path": "scanned_doc.pdf", "tags": ["home", "bills", "acme energy", "utilities:electricity"]}
```

This looks pretty close to JSON, and I save all the metadata into a standalone JSON file that lives in the top-level directory of a docstore instance.

There are several reasons I like JSON for storing my docstore metadata:

-   It maps very closely to data structures in Python.
    I don't have to deal with any complex serialisation code.

-   JSON is a simple format with parsing libraries in lots of languages.
    Even if I lost all the code for docstore, I could still use the metadata.

-   JSON is plain text, so it's easy to edit.
    If I want to edit some metadata, I can open the metadata file in any text editor and make changes.
    This means I didn't have to put any editing-related code in docstore itself.

I only have a few thousand files, so the performance impact of reading/writing all the JSON every time is minimal.
You shouldn't use JSON for large data sets, but for small data sets it's absolutely fine.



## Serialising attrs models to JSON and back

To save attrs models as JSON, or to read JSON as attrs models, I use the [cattrs library][cattrs].
This provides a pair of functions to go in both directions:

```pycon
>>> cattr.unstructure(doc)
{"path": "scanned_doc.pdf", "tags": ["home", "bills", "acme energy"]}

>>> cattr.structure(
...     {"path": "cat.jpg", "tags": ["pets"]},
...     Document)
Document(path="cat.jpg", tags=["pets"])
```

It has all the logic for doing validation, handling errors, and converting everything to the right type – so I don't have to write any custom serialisation code in docstore.

[cattrs]: https://cattrs.readthedocs.io/en/latest/
