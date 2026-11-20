"""DTOs Pydantic v2 para estructura ministerial: Redes, Casas de Paz y Líderes."""
from typing import Any, Optional, Union
from pydantic import Field, field_validator
from utils.validators import normalize_phone_e164
from .common import BaseDTO


def _empty_to_none(v: Any) -> Any:
    if isinstance(v, str) and v.strip() == '':
        return None
    return v


def _normalize_optional_phone(v: Any) -> Any:
    v = _empty_to_none(v)
    if v is None:
        return None
    ok, normalized, err = normalize_phone_e164(str(v))
    if not ok:
        raise ValueError(err)
    return normalized


class RedCreateDTO(BaseDTO):
    nombre: str = Field(..., min_length=1, max_length=80)
    supervisor_id: Optional[str] = Field(default=None, max_length=64)

    @field_validator('supervisor_id', mode='before')
    @classmethod
    def clean_supervisor(cls, v: Any) -> Any:
        return _empty_to_none(v)


class RedUpdateDTO(RedCreateDTO):
    is_active: Optional[Union[bool, int, str]] = None


class CdpCreateDTO(BaseDTO):
    codigo: str = Field(..., min_length=1, max_length=40)
    anfitrion: str = Field(..., min_length=1, max_length=60)
    direccion: str = Field(..., min_length=1, max_length=150)
    telefono: Optional[str] = Field(default=None, max_length=25)
    red_id: int = Field(..., ge=1)
    usuario_id: Optional[str] = Field(default=None, max_length=64)
    is_active: Optional[Union[bool, int, str]] = None

    @field_validator('red_id', 'usuario_id', mode='before')
    @classmethod
    def clean_optional(cls, v: Any) -> Any:
        return _empty_to_none(v)

    @field_validator('telefono', mode='before')
    @classmethod
    def normalize_telefono(cls, v: Any) -> Any:
        return _normalize_optional_phone(v)


class CdpUpdateDTO(BaseDTO):
    codigo: Optional[str] = Field(default=None, min_length=1, max_length=40)
    anfitrion: Optional[str] = Field(default=None, min_length=1, max_length=60)
    direccion: Optional[str] = Field(default=None, min_length=1, max_length=150)
    telefono: Optional[str] = Field(default=None, max_length=25)
    red_id: Optional[int] = Field(default=None, ge=1)
    usuario_id: Optional[str] = Field(default=None, max_length=64)
    is_active: Optional[Union[bool, int, str]] = None

    @field_validator('red_id', 'usuario_id', mode='before')
    @classmethod
    def clean_optional(cls, v: Any) -> Any:
        return _empty_to_none(v)

    @field_validator('telefono', mode='before')
    @classmethod
    def normalize_telefono(cls, v: Any) -> Any:
        return _normalize_optional_phone(v)


class LiderCreateDTO(BaseDTO):
    nombre: str = Field(..., min_length=1, max_length=50)
    apellido: str = Field(..., min_length=1, max_length=50)
    rol: str = Field(..., min_length=1, max_length=30)
    telefono: Optional[str] = Field(default=None, max_length=25)
    cdp_id: int = Field(..., ge=1)
    is_active: Optional[Union[bool, int, str]] = None

    @field_validator('cdp_id', mode='before')
    @classmethod
    def clean_optional(cls, v: Any) -> Any:
        return _empty_to_none(v)

    @field_validator('telefono', mode='before')
    @classmethod
    def normalize_telefono(cls, v: Any) -> Any:
        return _normalize_optional_phone(v)


class LiderUpdateDTO(BaseDTO):
    nombre: Optional[str] = Field(default=None, min_length=1, max_length=50)
    apellido: Optional[str] = Field(default=None, min_length=1, max_length=50)
    rol: Optional[str] = Field(default=None, min_length=1, max_length=30)
    telefono: Optional[str] = Field(default=None, max_length=25)
    cdp_id: Optional[int] = Field(default=None, ge=1)
    is_active: Optional[Union[bool, int, str]] = None

    @field_validator('cdp_id', mode='before')
    @classmethod
    def clean_optional(cls, v: Any) -> Any:
        return _empty_to_none(v)

    @field_validator('telefono', mode='before')
    @classmethod
    def normalize_telefono(cls, v: Any) -> Any:
        return _normalize_optional_phone(v)
