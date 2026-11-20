"""Contratos tipados de entrada/salida (DTOs Pydantic v2) para la API REST."""
from .common import parse_payload
from .reporte_schema import ReporteCreateDTO, ReporteUpdateDTO
from .usuario_schema import (
    UsuarioCreateDTO,
    UsuarioUpdateDTO,
    PerfilUsernameDTO,
    PerfilPasswordDTO,
)
from .estructura_schema import (
    RedCreateDTO,
    RedUpdateDTO,
    CdpCreateDTO,
    CdpUpdateDTO,
    LiderCreateDTO,
    LiderUpdateDTO,
)

__all__ = [
    'parse_payload',
    'ReporteCreateDTO',
    'ReporteUpdateDTO',
    'UsuarioCreateDTO',
    'UsuarioUpdateDTO',
    'PerfilUsernameDTO',
    'PerfilPasswordDTO',
    'RedCreateDTO',
    'RedUpdateDTO',
    'CdpCreateDTO',
    'CdpUpdateDTO',
    'LiderCreateDTO',
    'LiderUpdateDTO',
]
