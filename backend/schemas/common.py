"""
Utilidades comunes para validación declarativa con Pydantic v2 en las fronteras de la API REST.
Traduce errores de validación de Pydantic a domain.exceptions.ValidationError con mensajes
en español y estructura homogénea compatible con ApiError del frontend.
"""
from typing import Any, Type, TypeVar
from pydantic import BaseModel, ConfigDict, ValidationError as PydanticValidationError
from domain.exceptions import ValidationError as DomainValidationError

T = TypeVar('T', bound=BaseModel)


class BaseDTO(BaseModel):
    """Clase base para DTOs de entrada REST."""

    model_config = ConfigDict(
        extra='allow',
        str_strip_whitespace=True,
        populate_by_name=True,
    )

    def to_service_dict(self) -> dict[str, Any]:
        """Convierte el DTO validado a diccionario limpio para la capa de servicios."""
        return self.model_dump(exclude_none=True)


def _translate_pydantic_error(err: dict[str, Any]) -> str:
    err_type = err.get('type', '')
    msg = err.get('msg', 'Valor no válido')

    if err_type == 'missing':
        return 'Este campo es obligatorio.'
    if err_type in ('int_parsing', 'int_type'):
        return 'Debe ser un número entero válido.'
    if err_type in ('float_parsing', 'float_type', 'decimal_parsing'):
        return 'Debe ser un valor numérico válido.'
    if err_type == 'greater_than_equal':
        ge = err.get('ctx', {}).get('ge')
        return f'Debe ser mayor o igual a {ge}.'
    if err_type == 'less_than_equal':
        le = err.get('ctx', {}).get('le')
        return f'Debe ser menor o igual a {le}.'
    if err_type == 'string_too_short':
        min_len = err.get('ctx', {}).get('min_length')
        return f'Debe tener al menos {min_len} caracteres.'
    if err_type == 'string_too_long':
        max_len = err.get('ctx', {}).get('max_length')
        return f'No puede superar {max_len} caracteres.'
    if err_type == 'value_error':
        # Pydantic prefija ValueError custom con "Value error, "
        if msg.startswith('Value error, '):
            return msg[len('Value error, '):]
        return msg
    return msg


def parse_payload(schema_cls: Type[T], raw_data: Any) -> T:
    """
    Valida y coerciona `raw_data` usando `schema_cls`.
    Si falla, lanza `domain.exceptions.ValidationError` (HTTP 400 JSON) con `details`.
    """
    if raw_data is None:
        raw_data = {}
    if not isinstance(raw_data, dict):
        raise DomainValidationError(
            "El cuerpo de la solicitud debe ser un objeto JSON válido.",
            details=[{"field": "body", "message": "Se esperaba un objeto JSON."}],
        )

    try:
        return schema_cls.model_validate(raw_data)
    except PydanticValidationError as exc:
        details = []
        for err in exc.errors():
            loc = '.'.join(str(part) for part in err.get('loc', ())) or 'body'
            details.append({
                "field": loc,
                "message": _translate_pydantic_error(err),
            })
        first = details[0] if details else {"field": "body", "message": "Datos de entrada inválidos."}
        summary = (
            first['message']
            if first['field'] == 'body'
            else f"Campo '{first['field']}': {first['message']}"
        )
        raise DomainValidationError(summary, details=details)
