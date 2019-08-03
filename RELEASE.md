RELEASE_TYPE: minor

docstore no longer checks the `"sha256_checksum"` value in a POST request to `/upload`.

As far as I know, nobody is routinely uploading documents with this field, so it's simpler to take it out.

If you do send a value for `"sha256_checksum"`, it will be stored in the database separate to the one that gets computed by docstore, like so:

```json
{
  ...
  "sha256_checksum": "<computed by docstore>",
  "user_data": {
    "sha256_checksum": "<sent in the POST request>"
  }
}
```

If you want to check it, you'll need to check the database with your own code.
