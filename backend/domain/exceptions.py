"""
Excepciones semánticas del dominio de negocio.
Permiten traducir errores de negocio a respuestas HTTP/JSON consistentes
sin acoplar los servicios a códigos HTTP ni duplicar lógica en cada ruta.
"""
from typing import Any, Optional


class DomainError(Exception):
    """Excepción base para errores controlados del dominio."""

    status_code: int = 400
    code: str = "domain_error"

    def __init__(
        self,
        message: str,
        *,
        status_code: Optional[int] = None,
        code: Optional[str] = None,
        details: Optional[Any] = None,
    ):
        super().__init__(message)
        self.message = message
        if status_code is not None:
            self.status_code = status_code
        if code is not None:
            self.code = code
        self.details = details

    def to_dict(self) -> dict[str, Any]:
        payload: dict[str, Any] = {
            "success": False,
            "error": self.message,
            "code": self.code,
        }
        if self.details is not None:
            payload["details"] = self.details
        return payload


class ValidationError(DomainError):
    """Error de validación de datos de entrada o contrato."""

    status_code = 400
    code = "validation_error"


class UnauthorizedError(DomainError):
    """Error de autenticación ausente o expirada."""

    status_code = 401
    code = "unauthorized"


class ForbiddenError(DomainError):
    """Error de autorización por rol o aislamiento territorial (anti-IDOR)."""

    status_code = 403
    code = "forbidden"


class NotFoundError(DomainError):
    """Recurso o entidad solicitada no encontrada."""

    status_code = 404
    code = "not_found"


class ConflictError(DomainError):
    """Conflicto de integridad, unicidad o dependencia activa."""

    status_code = 409
    code = "conflict"


class ServiceUnavailableError(DomainError):
    """Servicio o base de datos temporalmente no disponible."""

    status_code = 503
    code = "service_unavailable"
