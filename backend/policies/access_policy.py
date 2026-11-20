"""
Política centralizada de acceso basado en roles y aislamiento territorial (Anti-IDOR).
Unifica las reglas de autorización para admin, supervisor y lider_cdp entre API REST y SSR.
"""
from dataclasses import dataclass
from typing import Optional
from domain.exceptions import ForbiddenError, ValidationError


@dataclass(frozen=True)
class UserContext:
    """Contexto inmutable del usuario autenticado para evaluación de políticas."""
    usuario_id: str
    rol: str
    supervisor_red_id: Optional[int] = None
    cdp_id: Optional[int] = None

    @property
    def is_admin(self) -> bool:
        return self.rol == 'admin'

    @property
    def is_supervisor(self) -> bool:
        return self.rol == 'supervisor'

    @property
    def is_lider_cdp(self) -> bool:
        return self.rol in ('lider_cdp', 'cdp')


class AccessPolicy:
    """Evaluador puro de permisos y alcances territoriales ministeriales."""

    @staticmethod
    def can_manage_usuarios(user: UserContext) -> bool:
        return user.is_admin

    @staticmethod
    def can_access_red(user: UserContext, target_red_id: Optional[int | str]) -> bool:
        if user.is_admin:
            return True
        if user.is_supervisor:
            if user.supervisor_red_id is None:
                return False
            if target_red_id is None or str(target_red_id).strip() == '':
                return True
            return str(target_red_id).strip() == str(user.supervisor_red_id)
        return False

    @staticmethod
    def can_access_cdp(
        user: UserContext,
        target_cdp_id: Optional[int | str],
        cdp_red_id: Optional[int | str] = None,
    ) -> bool:
        if user.is_admin:
            return True
        if user.is_supervisor:
            if user.supervisor_red_id is None or cdp_red_id is None:
                return False
            return str(cdp_red_id).strip() == str(user.supervisor_red_id)
        if user.is_lider_cdp:
            if user.cdp_id is None or target_cdp_id is None:
                return False
            return str(target_cdp_id).strip() == str(user.cdp_id)
        return False

    @staticmethod
    def resolve_reportes_scope(
        user: UserContext,
        requested_red_id: str = '',
        requested_cdp_id: str = '',
    ) -> dict:
        """
        Resuelve el alcance efectivo de consulta de reportes según rol y valida Anti-IDOR.
        Retorna dict con keys: empty (bool), supervisor_red_id, target_red_id, target_cdp_id.
        Lanza ForbiddenError si se intenta acceder fuera del ámbito asignado.
        """
        red_arg = str(requested_red_id or '').strip()
        cdp_arg = str(requested_cdp_id or '').strip()

        if user.is_admin:
            return {
                'empty': False,
                'supervisor_red_id': None,
                'target_red_id': red_arg,
                'target_cdp_id': cdp_arg,
            }

        if user.is_supervisor:
            if not user.supervisor_red_id:
                return {
                    'empty': True,
                    'supervisor_red_id': None,
                    'target_red_id': '',
                    'target_cdp_id': '',
                }
            if red_arg and red_arg != str(user.supervisor_red_id):
                raise ForbiddenError("No autorizado para consultar reportes fuera de su red asignada")
            return {
                'empty': False,
                'supervisor_red_id': user.supervisor_red_id,
                'target_red_id': str(user.supervisor_red_id),
                'target_cdp_id': cdp_arg,
            }

        if user.is_lider_cdp:
            if not user.cdp_id:
                return {
                    'empty': True,
                    'supervisor_red_id': None,
                    'target_red_id': '',
                    'target_cdp_id': '',
                }
            if cdp_arg and cdp_arg != str(user.cdp_id):
                raise ForbiddenError("No autorizado para consultar reportes de otra Casa de Paz")
            return {
                'empty': False,
                'supervisor_red_id': None,
                'target_red_id': red_arg,
                'target_cdp_id': str(user.cdp_id),
            }

        raise ForbiddenError("Rol no autorizado para consultar reportes")

    @staticmethod
    def resolve_reporte_mutation_cdp_id(
        user: UserContext,
        requested_cdp_id=None,
        *,
        allow_supervisor: bool = False,
        default_admin_cdp_id: Optional[int] = None,
        target_cdp_red_id: Optional[int | str] = None,
    ) -> int:
        """
        Resuelve y valida el cdp_id objetivo para crear, editar o eliminar reportes.
        Lanza ForbiddenError o ValidationError cuando corresponde.
        """
        if user.is_lider_cdp:
            if not user.cdp_id:
                raise ForbiddenError("No tienes una Casa de Paz asignada")
            if requested_cdp_id is not None and str(requested_cdp_id).strip() != '':
                if str(requested_cdp_id).strip() != str(user.cdp_id):
                    raise ForbiddenError("No autorizado para operar reportes de otra Casa de Paz")
            return int(user.cdp_id)

        if user.is_admin:
            if requested_cdp_id is None or str(requested_cdp_id).strip() == '':
                if default_admin_cdp_id is not None:
                    return int(default_admin_cdp_id)
                raise ValidationError("cdp_id es obligatorio para administradores")
            try:
                return int(requested_cdp_id)
            except (ValueError, TypeError):
                raise ValidationError("cdp_id no válido")

        if user.is_supervisor and allow_supervisor:
            if requested_cdp_id is None or str(requested_cdp_id).strip() == '':
                raise ValidationError("cdp_id requerido para supervisores")
            try:
                cdp_id_int = int(requested_cdp_id)
            except (ValueError, TypeError):
                raise ValidationError("cdp_id no válido")
            if not AccessPolicy.can_access_cdp(user, cdp_id_int, cdp_red_id=target_cdp_red_id):
                raise ForbiddenError("No autorizado para operar reportes de una Casa de Paz fuera de su red asignada")
            return cdp_id_int

        raise ForbiddenError("Rol no autorizado para esta operación de reporte")
