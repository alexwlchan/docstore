RELEASE_TYPE: minor

docstore now stores checksums in a different format.  Previously it wrote a field like:

```json
{
  ...
  "sha256_checksum": "abc...def"
}
```

It now writes a field `"checksum"` with the algorithm prepended, for example:

```json
{
  ...
  "checksum": "sha256:abc...def"
}
```

which is more future-proof if I ever decide to change the checksum algorithm.

Old databases will be migrated to the new format when you first run a release with the new code.
