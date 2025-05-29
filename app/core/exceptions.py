class EntityNotFound(Exception):
    """Raised when an entity (Library/Document/Chunk) is not found."""

class ValidationError(Exception):
    """Raised when business rules are violated (e.g. duplicate IDs)."""
