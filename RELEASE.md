RELEASE_TYPE: patch

This fixes a bug introduced in v1.7.6, where trying to store a document while running inside a Docker container could throw an error:

```
OSError: [Errno 18] Invalid cross-device link
```
