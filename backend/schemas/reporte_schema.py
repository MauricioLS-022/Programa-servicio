"""DTOs Pydantic v2 para creación y edición de reportes ministeriales."""
from typing import Any, Optional, Union
from pydantic import Field, field_validator
from .common import BaseDTO


def _empty_to_none(v: Any) -> Any:
    if isinstance(v, str) and v.strip() == '':
        return None
    return v


class ReporteCreateDTO(BaseDTO):
    cdp_id: Optional[int] = Field(default=None, ge=1)
    enviado_por_lider_id: Optional[int] = Field(default=None, ge=1)
    fecha: Optional[str] = Field(default=None, max_length=30)
    hr_inicio: Optional[str] = Field(default=None, max_length=20)
    hr_fin: Optional[str] = Field(default=None, max_length=20)
    tema: Optional[str] = Field(default=None, max_length=150)
    observaciones: Optional[str] = Field(default=None, max_length=2000)

    nro_regulares: Optional[int] = Field(default=None, ge=0, le=100000)
    nro_ninos: Optional[int] = Field(default=None, ge=0, le=100000)
    nro_visitas: Optional[int] = Field(default=None, ge=0, le=100000)
    nro_comprometidos: Optional[int] = Field(default=None, ge=0, le=100000)
    reconciliaciones: Optional[int] = Field(default=None, ge=0, le=100000)
    confesiones: Optional[int] = Field(default=None, ge=0, le=100000)
    asistencia: Optional[int] = Field(default=None, ge=0, le=400000)

    ofrendas_usd: Optional[float] = Field(default=None, ge=0)
    ofrendas_bs: Optional[float] = Field(default=None, ge=0)
    ofrenda_usd: Optional[float] = Field(default=None, ge=0)
    ofrenda_bs: Optional[float] = Field(default=None, ge=0)
    cesta_amor: Optional[Union[bool, int, str]] = None

    @field_validator(
        'cdp_id', 'enviado_por_lider_id', 'nro_regulares', 'nro_ninos',
        'nro_visitas', 'nro_comprometidos', 'reconciliaciones', 'confesiones',
        'asistencia', 'ofrendas_usd', 'ofrendas_bs', 'ofrenda_usd', 'ofrenda_bs',
        mode='before',
    )
    @classmethod
    def coerce_empty_numeric(cls, v: Any) -> Any:
        return _empty_to_none(v)


class ReporteUpdateDTO(ReporteCreateDTO):
    """Contrato para actualización parcial o total de un reporte existente."""
    pass
