# Implementation notes

I wrote this app for personal use.
There's only a single user (me), and I'm only using it to store a few thousand documents at most.
That lets me ignore lots of hard problems around scaling, trusted input, concurrent reads and writes -- and the code is simpler for it.

There are a few interesting design choices, which work well in the context of a personal tool, but you shouldn't use in larger software.



## Storing the individual PDF files

When I save a file to disk, I normalise the filename into something computer-friendly.
This means stripping out all the special characters, lowercasing the whole name, and replacing spaces with hyphens.
The files get sorted into directories based on their first letter.
(( ASCIIFYING ))
Something like:

```
files
 ├─ a
 │   ├─ advice-for-renters.pdf
 │   └─ alex-chan-contract.pdf
 └─ b
     ├─ breakdown-cover-ipid-document.pdf
     └─ british-gas-terms-and-conditions.pdf
```

If you download a file, I use the Content-Disposition HTTP header to send the original filename -- so this normalisation is completely hidden from the user.

Initially I was using UUIDs for filenames, but they're quite opaque.
This way keeps the filenames computer-friendly, but still close to the original, so they'll stay usable if you stop using docstore but lose the database.

If you upload a file with the same name twice, I append a random string to the filename to avoid clashes.
Something like:

```
files
 └─ a
     ├─ advice-for-renters.pdf
     └─ advice-for-renters_a187b.pdf
```

The thumbnails are kept in a separate folder -- they're less important than the original files, and I don't want to mix them up.



## Storing the metadata

All the metadata is kept in a single JSON file.
JSON means it's human-readable and human-editable, and not tied to any particular software or language.
Here's what it looks like:

```json
{
  "000914e9-be70-4d11-bba5-6c902e9bcb44": {
    "filename": "Advice for renters.pdf",
    "file_identifier": "a/advice-for-renters.pdf",
    "checksum": "sha256:8b9...b40",
    "date_created": "2019-11-25 00:05:52 +0000",
    "tags": [
	  "home:renting",
	  "home:123-sesame-street"
    ],
    "thumbnail_identifier": "0/000914e9-be70-4d11-bba5-6c902e9bcb44.jpg",
    "title": "2019-11: Advice for renters"
  },
  ...
}
```

I use UUIDs as IDs, which is a holdover from an early version -- right now they're only used to identify the thumbnail images.
I could probably get away with storing a list of documents, but it's not worth changing.

When I upload a file, the app records a SHA256 checksum.
These documents should all be immutable, so this is a way to spot file corruption.

When the app starts, it loads the entire JSON file into memory.
It also polls the file periodically, and if it detects a change, it reloads the file.
This would cause issues if I was running at large scale, but for a few thousand documents this isn't a problem.



## Finding documents with a given set of tags

I query documents with a Python list comprehension:

```python
query = [
    "utilities",
    "home:123-sesame-street",
]

matching_documents = [
    doc
    for doc in documents
    if all(query_tag in doc.get("tags", []) for query_tag in query)
]
```

You could use a fancier data structure, or a database join, or something else, but this is fast enough for a small number of documents that it's not an issue.
Because all the documents are already in memory, it takes fractions of a millisecond to query thousands of documents.
