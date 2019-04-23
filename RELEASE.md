RELEASE_TYPE: patch

Change some of the internal storage logic so it's less likely to return a user error or server error when trying to index documents.

Specifically, change the logic for detecting filename extensions (which are mostly used for internal storage), and just don't set one if it can't be detected.