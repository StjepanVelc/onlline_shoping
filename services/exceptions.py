class ServiceError(Exception):
    """Base service exception."""


class NotFoundError(ServiceError):
    """Raised when an entity does not exist."""


class ConflictError(ServiceError):
    """Raised when a unique/consistency conflict occurs."""


class ValidationError(ServiceError):
    """Raised when payload is semantically invalid."""


class AuthError(ServiceError):
    """Raised when authentication/authorization fails."""
