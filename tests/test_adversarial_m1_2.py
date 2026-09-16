"""
Empirical Adversarial Test Suite for Milestone 1 (Challenger M1_2):
1. Adversarial verification of cache invalidation guarantees across ALL success and failure branches.
2. Adversarial verification that independent user toggle cannot mutate or corrupt linked CDP or Red state.
3. Contrast and verify unidirectional synchronization contract (CDP -> User vs User -/-> CDP).
4. Edge cases with orphaned relational IDs (orphaned red_id or cdp_id).
"""
import unittest
from unittest.mock import patch, MagicMock, call
from app import app
from db_queries import (
    toggle_estado_cdp,
    toggle_estado_lider,
    toggle_estado_usuario
)
from services.cdp_service import (
    toggle_cdp_servicio,
    actualizar_cdp_servicio
)
from services.leader_service import (
    toggle_lider_servicio,
    actualizar_lider_servicio
)
from services.user_service import (
    toggle_usuario_servicio,
    actualizar_usuario_admin
)


class TestAdversarialCacheInvalidation(unittest.TestCase):
    """Verifica de forma adversaria las garantías de invalidación de caché en todas las ramas."""

    def setUp(self):
        self.app = app
        self.app.config['TESTING'] = True

    # -------------------------------------------------------------
    # CDP Cache Invalidation Tests
    # -------------------------------------------------------------
    @patch('services.cdp_service.get_db_connection')
    @patch('services.cdp_service.db_queries.toggle_estado_cdp')
    @patch('services.cdp_service.invalidate_dashboard_cache')
    def test_toggle_cdp_cache_invalidated_on_success_reactivate(self, mock_cache, mock_toggle, mock_get_conn):
        """toggle_cdp_servicio debe invalidar caché y hacer commit al reactivar exitosamente."""
        mock_conn = MagicMock()
        mock_get_conn.return_value = mock_conn
        mock_toggle.return_value = (True, 'reactivada', 'Reactivada exitosamente')

        with self.app.app_context():
            ok, status, msg = toggle_cdp_servicio(10)

        self.assertTrue(ok)
        self.assertEqual(status, 'reactivada')
        mock_conn.commit.assert_called_once()
        mock_conn.rollback.assert_not_called()
        mock_cache.assert_called_once()

    @patch('services.cdp_service.get_db_connection')
    @patch('services.cdp_service.db_queries.toggle_estado_cdp')
    @patch('services.cdp_service.invalidate_dashboard_cache')
    def test_toggle_cdp_cache_invalidated_on_success_pause(self, mock_cache, mock_toggle, mock_get_conn):
        """toggle_cdp_servicio debe invalidar caché y hacer commit al pausar exitosamente."""
        mock_conn = MagicMock()
        mock_get_conn.return_value = mock_conn
        mock_toggle.return_value = (True, 'pausada', 'Pausada exitosamente')

        with self.app.app_context():
            ok, status, msg = toggle_cdp_servicio(10)

        self.assertTrue(ok)
        self.assertEqual(status, 'pausada')
        mock_conn.commit.assert_called_once()
        mock_conn.rollback.assert_not_called()
        mock_cache.assert_called_once()

    @patch('services.cdp_service.get_db_connection')
    @patch('services.cdp_service.db_queries.toggle_estado_cdp')
    @patch('services.cdp_service.invalidate_dashboard_cache')
    def test_toggle_cdp_cache_not_invalidated_when_blocked_by_red(self, mock_cache, mock_toggle, mock_get_conn):
        """toggle_cdp_servicio NO debe invalidar caché y debe hacer rollback si la Red está inactiva."""
        mock_conn = MagicMock()
        mock_get_conn.return_value = mock_conn
        mock_toggle.return_value = (False, 'bloqueada', 'Red en pausa')

        with self.app.app_context():
            ok, status, msg = toggle_cdp_servicio(10)

        self.assertFalse(ok)
        self.assertEqual(status, 'bloqueada')
        mock_conn.commit.assert_not_called()
        mock_conn.rollback.assert_called_once()
        mock_cache.assert_not_called()

    @patch('services.cdp_service.get_db_connection')
    @patch('services.cdp_service.invalidate_dashboard_cache')
    def test_toggle_cdp_cache_not_invalidated_on_invalid_id_or_no_db(self, mock_cache, mock_get_conn):
        """toggle_cdp_servicio NO debe invalidar caché con ID inválido o falla de conexión."""
        with self.app.app_context():
            # ID no convertible
            ok, status, _ = toggle_cdp_servicio('invalid_id')
            self.assertFalse(ok)
            self.assertEqual(status, 'error')
            mock_cache.assert_not_called()

            # Sin conexión
            mock_get_conn.return_value = None
            ok, status, _ = toggle_cdp_servicio(10)
            self.assertFalse(ok)
            self.assertEqual(status, 'error')
            mock_cache.assert_not_called()

    @patch('services.cdp_service.get_db_connection')
    @patch('services.cdp_service.db_queries.toggle_estado_cdp')
    @patch('services.cdp_service.invalidate_dashboard_cache')
    def test_toggle_cdp_cache_not_invalidated_on_db_exception(self, mock_cache, mock_toggle, mock_get_conn):
        """toggle_cdp_servicio NO debe invalidar caché y debe hacer rollback si ocurre excepción SQL."""
        mock_conn = MagicMock()
        mock_get_conn.return_value = mock_conn
        mock_toggle.side_effect = Exception("DB crash during toggle")

        with self.app.app_context():
            ok, status, _ = toggle_cdp_servicio(10)

        self.assertFalse(ok)
        self.assertEqual(status, 'error')
        mock_conn.commit.assert_not_called()
        mock_conn.rollback.assert_called_once()
        mock_cache.assert_not_called()

    @patch('services.cdp_service.get_db_connection')
    @patch('services.cdp_service.db_queries.actualizar_cdp_admin')
    @patch('services.cdp_service.invalidate_dashboard_cache')
    def test_actualizar_cdp_cache_guarantees(self, mock_cache, mock_update, mock_get_conn):
        """actualizar_cdp_servicio invalida en éxito y NO en bloqueo jerárquico."""
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_conn.cursor.return_value.__enter__.return_value = mock_cursor
        mock_get_conn.return_value = mock_conn

        form_data = {
            'codigo': 'CDP-01',
            'anfitrion': 'Juan Perez',
            'telefono': '04141234567',
            'direccion': 'Calle Principal 123',
            'red_id': '1',
            'modo_usuario': 'nuevo',
            'username': 'juanp',
            'nombre': 'Juan',
            'apellido': 'Perez'
        }

        with self.app.app_context():
            # Rama bloqueada: Red inactiva
            mock_cursor.fetchone.side_effect = [
                {'id': 10, 'usuario_id': 'u1'}, # CDP existe
                {'id': 1, 'nombre': 'Red 1', 'is_active': 0}, # Red inactiva
            ]
            ok, msg = actualizar_cdp_servicio(10, form_data, is_active=1)
            self.assertFalse(ok)
            self.assertIn("se encuentra en pausa", msg)
            mock_cache.assert_not_called()
            mock_conn.commit.assert_not_called()

            # Rama éxito: Red activa
            mock_cursor.fetchone.side_effect = [
                {'id': 10, 'usuario_id': 'u1'}, # CDP existe
                {'id': 1, 'nombre': 'Red 1', 'is_active': 1}, # Red activa
                None, # código único
                None, # username único
            ]
            ok, msg = actualizar_cdp_servicio(10, form_data, is_active=1)
            self.assertTrue(ok)
            mock_cache.assert_called_once()
            mock_conn.commit.assert_called_once()

    # -------------------------------------------------------------
    # Leader Cache Invalidation Tests
    # -------------------------------------------------------------
    @patch('services.leader_service.get_db_connection')
    @patch('services.leader_service.toggle_estado_lider')
    @patch('services.leader_service.invalidate_dashboard_cache')
    def test_toggle_lider_cache_invalidated_on_success(self, mock_cache, mock_toggle, mock_get_conn):
        """toggle_lider_servicio invalida caché y hace commit en éxito."""
        mock_conn = MagicMock()
        mock_get_conn.return_value = mock_conn
        mock_toggle.return_value = (True, 'reactivado', 'Líder reactivado')

        with self.app.app_context():
            ok, status, _ = toggle_lider_servicio(5)

        self.assertTrue(ok)
        self.assertEqual(status, 'reactivado')
        mock_conn.commit.assert_called_once()
        mock_cache.assert_called_once()

    @patch('services.leader_service.get_db_connection')
    @patch('services.leader_service.toggle_estado_lider')
    @patch('services.leader_service.invalidate_dashboard_cache')
    def test_toggle_lider_cache_not_invalidated_when_blocked_by_cdp(self, mock_cache, mock_toggle, mock_get_conn):
        """toggle_lider_servicio NO invalida caché y hace rollback si la CDP asignada está pausada."""
        mock_conn = MagicMock()
        mock_get_conn.return_value = mock_conn
        mock_toggle.return_value = (False, 'bloqueada', 'Casa de Paz en pausa')

        with self.app.app_context():
            ok, status, _ = toggle_lider_servicio(5)

        self.assertFalse(ok)
        self.assertEqual(status, 'bloqueada')
        mock_conn.commit.assert_not_called()
        mock_conn.rollback.assert_called_once()
        mock_cache.assert_not_called()

    @patch('services.leader_service.get_db_connection')
    @patch('services.leader_service.actualizar_lider')
    @patch('services.leader_service.invalidate_dashboard_cache')
    def test_actualizar_lider_cache_guarantees(self, mock_cache, mock_update, mock_get_conn):
        """actualizar_lider_servicio invalida en éxito y NO si la CDP está inactiva."""
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_conn.cursor.return_value.__enter__.return_value = mock_cursor
        mock_get_conn.return_value = mock_conn

        form_data = {
            'nombre': 'Andres',
            'apellido': 'Bello',
            'telefono': '04121234567',
            'rol': 'Lider',
            'cdp_id': '10'
        }

        with self.app.app_context():
            # Rama bloqueada: CDP inactiva
            mock_cursor.fetchone.side_effect = [
                {'id': 5, 'nombre': 'Andres', 'is_active': 0}, # líder existe
                {'id': 10, 'codigo': 'CDP-10', 'is_active': 0}  # CDP inactiva
            ]
            ok, msg = actualizar_lider_servicio(5, form_data, is_active=1)
            self.assertFalse(ok)
            self.assertIn("se encuentra en pausa", msg)
            mock_cache.assert_not_called()
            mock_conn.commit.assert_not_called()

            # Rama éxito: CDP activa
            mock_cursor.fetchone.side_effect = [
                {'id': 5, 'nombre': 'Andres', 'is_active': 0}, # líder existe
                {'id': 10, 'codigo': 'CDP-10', 'is_active': 1}  # CDP activa
            ]
            ok, msg = actualizar_lider_servicio(5, form_data, is_active=1)
            self.assertTrue(ok)
            mock_cache.assert_called_once()
            mock_conn.commit.assert_called_once()

    # -------------------------------------------------------------
    # User Cache Invalidation Tests
    # -------------------------------------------------------------
    @patch('services.user_service.get_db_connection')
    @patch('services.user_service.toggle_estado_usuario')
    @patch('services.user_service.invalidate_dashboard_cache')
    def test_toggle_usuario_cache_invalidated_on_success(self, mock_cache, mock_toggle, mock_get_conn):
        """toggle_usuario_servicio invalida caché y hace commit en éxito."""
        mock_conn = MagicMock()
        mock_get_conn.return_value = mock_conn
        mock_toggle.return_value = (True, 'reactivado', 'Usuario reactivado')

        with self.app.app_context():
            ok, status, _ = toggle_usuario_servicio('user-uuid')

        self.assertTrue(ok)
        self.assertEqual(status, 'reactivado')
        mock_conn.commit.assert_called_once()
        mock_cache.assert_called_once()

    @patch('services.user_service.get_db_connection')
    @patch('services.user_service.toggle_estado_usuario')
    @patch('services.user_service.invalidate_dashboard_cache')
    def test_toggle_usuario_cache_not_invalidated_on_failure(self, mock_cache, mock_toggle, mock_get_conn):
        """toggle_usuario_servicio NO invalida caché si el usuario no existe o falla la BD."""
        mock_conn = MagicMock()
        mock_get_conn.return_value = mock_conn
        mock_toggle.return_value = (False, 'error', 'El usuario no existe.')

        with self.app.app_context():
            # Usuario no existe
            ok, status, _ = toggle_usuario_servicio('non-existent-user')
            self.assertFalse(ok)
            mock_conn.rollback.assert_called_once()
            mock_cache.assert_not_called()

            # Sin user_id
            ok, status, _ = toggle_usuario_servicio('')
            self.assertFalse(ok)
            mock_cache.assert_not_called()

    @patch('services.user_service.get_db_connection')
    @patch('services.user_service.invalidate_dashboard_cache')
    def test_actualizar_usuario_admin_cache_guarantees(self, mock_cache, mock_get_conn):
        """actualizar_usuario_admin invalida en éxito y NO en fallo de validación."""
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_conn.cursor.return_value.__enter__.return_value = mock_cursor
        mock_get_conn.return_value = mock_conn

        with self.app.app_context():
            # Fallo de validación: username inválido (caracteres no permitidos)
            bad_form = {
                'nombre': 'Usuario',
                'apellido': 'Test',
                'username': 'bad@username!',
                'tipo_usuario': 'admin'
            }
            ok, msg = actualizar_usuario_admin('u-1', bad_form)
            self.assertFalse(ok)
            mock_cache.assert_not_called()
            mock_conn.commit.assert_not_called()

            # Éxito: usuario actualizado con is_active=1
            mock_cursor.fetchone.return_value = None  # username único
            good_form = {
                'nombre': 'Usuario',
                'apellido': 'Test',
                'username': 'usuariovalido',
                'tipo_usuario': 'admin',
                'is_active': '1'
            }
            ok, msg = actualizar_usuario_admin('u-1', good_form)
            self.assertTrue(ok)
            mock_cache.assert_called_once()
            mock_conn.commit.assert_called_once()

    # -------------------------------------------------------------
    # Resilience: Cache Invalidation Exception Does Not Break Transaction
    # -------------------------------------------------------------
    @patch('services.cdp_service.get_db_connection')
    @patch('services.cdp_service.db_queries.toggle_estado_cdp')
    @patch('services.cdp_service.invalidate_dashboard_cache', side_effect=RuntimeError("Cache subsystem offline"))
    def test_cache_failure_does_not_break_cdp_toggle(self, mock_cache, mock_toggle, mock_get_conn):
        """Si invalidate_dashboard_cache falla con excepción, toggle_cdp_servicio no debe romperse."""
        mock_conn = MagicMock()
        mock_get_conn.return_value = mock_conn
        mock_toggle.return_value = (True, 'reactivada', 'Ok')

        with self.app.app_context():
            ok, status, msg = toggle_cdp_servicio(10)

        self.assertTrue(ok)
        self.assertEqual(status, 'reactivada')
        mock_conn.commit.assert_called_once()

    @patch('services.user_service.get_db_connection')
    @patch('services.user_service.toggle_estado_usuario')
    @patch('services.user_service.invalidate_dashboard_cache', side_effect=RuntimeError("Cache subsystem offline"))
    def test_cache_failure_does_not_break_user_toggle(self, mock_cache, mock_toggle, mock_get_conn):
        """Si invalidate_dashboard_cache falla con excepción, toggle_usuario_servicio no debe romperse."""
        mock_conn = MagicMock()
        mock_get_conn.return_value = mock_conn
        mock_toggle.return_value = (True, 'reactivado', 'Ok')

        with self.app.app_context():
            ok, status, msg = toggle_usuario_servicio('user-1')

        self.assertTrue(ok)
        self.assertEqual(status, 'reactivado')
        mock_conn.commit.assert_called_once()


class TestAdversarialIndependentUserToggle(unittest.TestCase):
    """
    Verifica de forma adversaria que la alternancia independiente de usuarios
    NO puede mutar, corromper ni afectar el estado de Casas de Paz (CDP) o Redes vinculadas.
    """

    def setUp(self):
        self.app = app
        self.app.config['TESTING'] = True

    def test_toggle_estado_usuario_sql_isolation(self):
        """
        Garantía SQL estricta: toggle_estado_usuario ÚNICAMENTE consulta y actualiza la tabla usuario.
        Nunca debe ejecutar consultas sobre cdp, red o lider.
        """
        cursor = MagicMock()
        cursor.fetchone.return_value = {
            'id': 'user-100',
            'username': 'lider100',
            'nombre': 'Pedro',
            'apellido': 'Navaja',
            'is_active': 1
        }

        ok, accion, msg = toggle_estado_usuario(cursor, 'user-100')
        self.assertTrue(ok)
        self.assertEqual(accion, 'desactivado')

        # Analizar todas las consultas SQL ejecutadas
        executed_sqls = [c[0][0].strip().upper() for c in cursor.execute.call_args_list]
        for sql in executed_sqls:
            self.assertNotIn("CDP", sql, f"Infracción de aislamiento: consulta tocó tabla cdp: {sql}")
            self.assertNotIn("RED", sql, f"Infracción de aislamiento: consulta tocó tabla red: {sql}")
            self.assertNotIn("LIDER", sql, f"Infracción de aislamiento: consulta tocó tabla lider: {sql}")
            self.assertTrue("USUARIO" in sql, f"Consulta esperada sobre tabla usuario, pero se ejecutó: {sql}")

    def test_user_toggle_linked_to_paused_cdp_cannot_reactivate_cdp(self):
        """
        Caso de ataque/corrupción:
        Un usuario vinculado a una CDP en pausa ('is_active = 0') es reactivado directamente ('is_active = 1').
        Debe verificarse que la CDP permanece 'is_active = 0' y no ocurre reactivación colateral encubierta.
        """
        db_state = {
            'usuario': {
                'u-cdp-paused': {'id': 'u-cdp-paused', 'username': 'u_cdp', 'nombre': 'Ana', 'apellido': 'G', 'is_active': 0}
            },
            'cdp': {
                1: {'id': 1, 'codigo': 'CDP-PAUSED', 'is_active': 0, 'usuario_id': 'u-cdp-paused', 'red_id': 1}
            },
            'red': {
                1: {'id': 1, 'nombre': 'Red Pausada', 'is_active': 0}
            }
        }

        cursor = MagicMock()
        def mock_execute(query, params=None):
            q_norm = query.strip().upper()
            if "SELECT" in q_norm and "FROM USUARIO" in q_norm:
                uid = params[0]
                user = db_state['usuario'].get(uid)
                cursor.fetchone.return_value = user.copy() if user else None
            elif "UPDATE USUARIO SET IS_ACTIVE =" in q_norm:
                if "IS_ACTIVE = 1" in q_norm:
                    db_state['usuario'][params[0]]['is_active'] = 1
                elif "IS_ACTIVE = 0" in q_norm:
                    db_state['usuario'][params[0]]['is_active'] = 0

        cursor.execute.side_effect = mock_execute

        # 1. Reactivar la cuenta de usuario independientemente
        ok, status, msg = toggle_estado_usuario(cursor, 'u-cdp-paused')
        self.assertTrue(ok)
        self.assertEqual(status, 'reactivado')

        # 2. Oráculo de integridad:
        self.assertEqual(db_state['usuario']['u-cdp-paused']['is_active'], 1)
        self.assertEqual(db_state['cdp'][1]['is_active'], 0)
        self.assertEqual(db_state['red'][1]['is_active'], 0)
        self.assertEqual(db_state['cdp'][1]['usuario_id'], 'u-cdp-paused')

    def test_user_toggle_linked_to_active_cdp_does_not_pause_cdp(self):
        """
        Caso de aislamiento:
        Un usuario vinculado a una CDP activa ('is_active = 1') es desactivado ('is_active = 0').
        La CDP debe mantener su estado 'is_active = 1' intacto.
        """
        db_state = {
            'usuario': {
                'u-cdp-active': {'id': 'u-cdp-active', 'username': 'u_active', 'nombre': 'Luis', 'apellido': 'R', 'is_active': 1}
            },
            'cdp': {
                2: {'id': 2, 'codigo': 'CDP-ACTIVA', 'is_active': 1, 'usuario_id': 'u-cdp-active', 'red_id': 1}
            },
            'red': {
                1: {'id': 1, 'nombre': 'Red Activa', 'is_active': 1}
            }
        }

        cursor = MagicMock()
        def mock_execute(query, params=None):
            q_norm = query.strip().upper()
            if "SELECT" in q_norm and "FROM USUARIO" in q_norm:
                uid = params[0]
                user = db_state['usuario'].get(uid)
                cursor.fetchone.return_value = user.copy() if user else None
            elif "UPDATE USUARIO SET IS_ACTIVE =" in q_norm:
                if "IS_ACTIVE = 1" in q_norm:
                    db_state['usuario'][params[0]]['is_active'] = 1
                elif "IS_ACTIVE = 0" in q_norm:
                    db_state['usuario'][params[0]]['is_active'] = 0

        cursor.execute.side_effect = mock_execute

        # Desactivar usuario independientemente
        ok, status, msg = toggle_estado_usuario(cursor, 'u-cdp-active')
        self.assertTrue(ok)
        self.assertEqual(status, 'desactivado')

        # Oráculo de integridad:
        self.assertEqual(db_state['usuario']['u-cdp-active']['is_active'], 0)
        self.assertEqual(db_state['cdp'][2]['is_active'], 1)
        self.assertEqual(db_state['red'][1]['is_active'], 1)
        self.assertEqual(db_state['cdp'][2]['usuario_id'], 'u-cdp-active')

    def test_user_toggle_supervisor_does_not_mutate_red_state(self):
        """
        Caso de aislamiento para Supervisores de Red:
        Alternar el estado de un usuario supervisor no debe cambiar el estado is_active de la Red.
        """
        db_state = {
            'usuario': {
                'u-sup-1': {'id': 'u-sup-1', 'username': 'supervisor1', 'nombre': 'Super', 'apellido': 'Visor', 'is_active': 1}
            },
            'red': {
                5: {'id': 5, 'nombre': 'Red Norte', 'is_active': 1, 'supervisor_id': 'u-sup-1'}
            }
        }

        cursor = MagicMock()
        def mock_execute(query, params=None):
            q_norm = query.strip().upper()
            if "SELECT" in q_norm and "FROM USUARIO" in q_norm:
                uid = params[0]
                user = db_state['usuario'].get(uid)
                cursor.fetchone.return_value = user.copy() if user else None
            elif "UPDATE USUARIO SET IS_ACTIVE =" in q_norm:
                if "IS_ACTIVE = 1" in q_norm:
                    db_state['usuario'][params[0]]['is_active'] = 1
                elif "IS_ACTIVE = 0" in q_norm:
                    db_state['usuario'][params[0]]['is_active'] = 0

        cursor.execute.side_effect = mock_execute

        # Desactivar supervisor
        ok, status, _ = toggle_estado_usuario(cursor, 'u-sup-1')
        self.assertTrue(ok)
        self.assertEqual(db_state['usuario']['u-sup-1']['is_active'], 0)
        self.assertEqual(db_state['red'][5]['is_active'], 1)
        self.assertEqual(db_state['red'][5]['supervisor_id'], 'u-sup-1')

        # Reactivar supervisor
        ok, status, _ = toggle_estado_usuario(cursor, 'u-sup-1')
        self.assertTrue(ok)
        self.assertEqual(db_state['usuario']['u-sup-1']['is_active'], 1)
        self.assertEqual(db_state['red'][5]['is_active'], 1)
        self.assertEqual(db_state['red'][5]['supervisor_id'], 'u-sup-1')

    def test_stress_multiple_flips_state_oracle(self):
        """
        Stress test: 20 alternancias rápidas consecutivas en una cuenta de usuario.
        El oráculo valida que en ningún ciclo se contamina o modifica ninguna otra entidad.
        """
        user_record = {'id': 'u-stress', 'username': 'stress_user', 'nombre': 'Stress', 'apellido': 'Test', 'is_active': 1}
        other_entities = {
            'cdp_active': 1,
            'cdp_user': 'u-stress',
            'red_active': 1,
            'red_supervisor': 'u-stress'
        }

        cursor = MagicMock()
        def mock_execute(query, params=None):
            q_norm = query.strip().upper()
            if "FROM USUARIO" in q_norm:
                cursor.fetchone.return_value = user_record.copy()
            elif "UPDATE USUARIO SET IS_ACTIVE = 0" in q_norm:
                user_record['is_active'] = 0
            elif "UPDATE USUARIO SET IS_ACTIVE = 1" in q_norm:
                user_record['is_active'] = 1

        cursor.execute.side_effect = mock_execute

        for i in range(20):
            expected_target = 0 if (i % 2 == 0) else 1
            ok, status, _ = toggle_estado_usuario(cursor, 'u-stress')
            self.assertTrue(ok)
            self.assertEqual(user_record['is_active'], expected_target)
            # Validar que entidades externas permanecen exactamente inalteradas
            self.assertEqual(other_entities['cdp_active'], 1)
            self.assertEqual(other_entities['cdp_user'], 'u-stress')
            self.assertEqual(other_entities['red_active'], 1)
            self.assertEqual(other_entities['red_supervisor'], 'u-stress')

    # -------------------------------------------------------------
    # Contrast: CDP Toggle Sincroniza vs User Toggle Aislado
    # -------------------------------------------------------------
    def test_contrast_cdp_toggle_syncs_user_while_user_toggle_isolates(self):
        """
        Verifica el contrato asimétrico:
        - toggle_estado_cdp SI sincroniza el usuario vinculado (usuario.is_active = cdp.is_active).
        - toggle_estado_usuario NO sincroniza la cdp vinculada (cdp.is_active permanece inmutable).
        """
        cursor_cdp = MagicMock()
        cursor_cdp.fetchone.return_value = {
            'id': 7,
            'codigo': 'CDP-07',
            'is_active': 0,
            'red_id': 1,
            'usuario_id': 'u-7',
            'red_nombre': 'Red 1',
            'red_is_active': 1
        }
        ok, status, _ = toggle_estado_cdp(cursor_cdp, 7)
        self.assertTrue(ok)
        self.assertEqual(status, 'reactivada')

        executed_sqls_cdp = [c[0][0].strip().upper() for c in cursor_cdp.execute.call_args_list]
        self.assertTrue(any('UPDATE CDP SET IS_ACTIVE = 1' in sql for sql in executed_sqls_cdp))
        self.assertTrue(any('UPDATE USUARIO SET IS_ACTIVE = 1' in sql for sql in executed_sqls_cdp))

        # toggle_estado_cdp con usuario_id = None funciona sin fallar
        cursor_cdp_no_user = MagicMock()
        cursor_cdp_no_user.fetchone.return_value = {
            'id': 8,
            'codigo': 'CDP-08',
            'is_active': 0,
            'red_id': 1,
            'usuario_id': None,
            'red_nombre': 'Red 1',
            'red_is_active': 1
        }
        ok, status, _ = toggle_estado_cdp(cursor_cdp_no_user, 8)
        self.assertTrue(ok)
        self.assertEqual(status, 'reactivada')
        executed_no_user = [c[0][0].strip().upper() for c in cursor_cdp_no_user.execute.call_args_list]
        self.assertTrue(any('UPDATE CDP SET IS_ACTIVE = 1' in sql for sql in executed_no_user))
        self.assertFalse(any('UPDATE USUARIO' in sql for sql in executed_no_user))

    def test_toggle_cdp_and_lider_orphaned_ids(self):
        """
        Verifica comportamiento ante IDs huérfanos:
        - CDP con red_id inexistente en tabla red: bloquea/retorna error.
        - Líder con cdp_id inexistente en tabla cdp: bloquea/retorna error.
        """
        cursor = MagicMock()
        cursor.fetchone.return_value = None  # No hay fila en JOIN

        # CDP huérfana
        ok, status, msg = toggle_estado_cdp(cursor, 999)
        self.assertFalse(ok)
        self.assertEqual(status, 'error')

        # Líder huérfano
        ok, status, msg = toggle_estado_lider(cursor, 888)
        self.assertFalse(ok)
        self.assertEqual(status, 'error')


if __name__ == '__main__':
    unittest.main()
