# -*- encoding: utf-8


class DocstoreException(Exception):
    """A base class for all exceptions raised by docstore."""


class UserError(DocstoreException):
    """Raised when there's a problem with the user-supplied data."""
