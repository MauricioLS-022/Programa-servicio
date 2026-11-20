"""Paquete de modelos y excepciones del dominio de negocio."""
from .exceptions import (
    DomainError,
    ValidationError,
    UnauthorizedError,
    ForbiddenError,
    NotFoundError,
    ConflictError,
    ServiceUnavailableError,
)

__all__ = [
    'DomainError',
    'ValidationError',
    'UnauthorizedError',
    'ForbiddenError',
    'NotFoundError',
    'ConflictError',
    'ServiceUnavailableError',
]
