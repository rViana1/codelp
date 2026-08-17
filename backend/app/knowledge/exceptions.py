class KnowledgeStorageError(Exception):
    """
    Base exception for knowledge storage failures.
    """
    pass


class KnowledgeCorruptedError(
    KnowledgeStorageError
):
    """
    Raised when persisted knowledge cannot
    be loaded because the stored data is invalid.
    """
    pass


class KnowledgeWriteError(
    KnowledgeStorageError
):
    """
    Raised when knowledge cannot be persisted safely.
    """
    pass
