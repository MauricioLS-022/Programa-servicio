"""DTOs Pydantic v2 para gestión de usuarios y perfil."""
from typing import Any, Optional, Union
from pydantic import Field, field_validator, model_validator
from .common import BaseDTO


class UsuarioCreateDTO(BaseDTO):
    nombre: str = Field(..., min_length=1, max_length=60)
    apellido: str = Field(..., min_length=1, max_length=60)
    username: str = Field(..., min_length=1, max_length=40)
    password: str = Field(..., min_length=1, max_length=128)
    tipo_usuario: Optional[str] = Field(default=None, max_length=30)
    rol: Optional[str] = Field(default=None, max_length=30)
    red_id: Optional[Union[int, str]] = None
    cdp_id: Optional[Union[int, str]] = None
    is_active: Optional[Union[bool, int, str]] = None

    @model_validator(mode='after')
    def sync_rol_and_tipo(self):
        if not self.tipo_usuario and self.rol:
            self.tipo_usuario = self.rol
        return self


class UsuarioUpdateDTO(BaseDTO):
    nombre: Optional[str] = Field(default=None, min_length=1, max_length=60)
    apellido: Optional[str] = Field(default=None, min_length=1, max_length=60)
    username: Optional[str] = Field(default=None, min_length=1, max_length=40)
    password: Optional[str] = Field(default=None, max_length=128)
    tipo_usuario: Optional[str] = Field(default=None, max_length=30)
    rol: Optional[str] = Field(default=None, max_length=30)
    red_id: Optional[Union[int, str]] = None
    cdp_id: Optional[Union[int, str]] = None
    is_active: Optional[Union[bool, int, str]] = None

    @model_validator(mode='after')
    def sync_rol_and_tipo(self):
        if not self.tipo_usuario and self.rol:
            self.tipo_usuario = self.rol
        return self


class PerfilUsernameDTO(BaseDTO):
    nuevo_username: Optional[str] = Field(default=None, max_length=40)
    username: Optional[str] = Field(default=None, max_length=40)

    @model_validator(mode='after')
    def ensure_username_present(self):
        resolved = (self.nuevo_username or self.username or '').strip()
        if not resolved:
            raise ValueError("Debe ingresar un nombre de usuario válido.")
        self.nuevo_username = resolved
        return self


class PerfilPasswordDTO(BaseDTO):
    password_actual: str = Field(default='')
    password_nueva: str = Field(default='')
    password_confirmar: str = Field(default='')

    @field_validator('password_actual', 'password_nueva', 'password_confirmar', mode='before')
    @classmethod
    def ensure_string(cls, v: Any) -> str:
        return '' if v is None else str(v)

    @model_validator(mode='after')
    def check_passwords(self):
        if not self.password_actual:
            raise ValueError("Debe ingresar su contraseña actual")
        if not self.password_nueva:
            raise ValueError("Debe ingresar una nueva contraseña")
        if self.password_confirmar and self.password_nueva != self.password_confirmar:
            raise ValueError("Las contraseñas nuevas no coinciden")
        return self
