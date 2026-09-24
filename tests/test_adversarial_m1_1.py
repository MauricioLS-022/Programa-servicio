"""
Empirical Adversarial Test Suite for Milestone 1 (Challenger M1_1):
1. Adversarial verification of state alternations and hierarchy edge cases:
   - Non-existent IDs
   - NULL usuario_id
   - Multiple toggle flips across Red, CDP, Leader, and User
   - Edge case parameter types
2. Investigation of whether code paths allow an inactive Red to have an active CDP
   or an inactive CDP to have an active Leader.
"""
import unittest
from unittest.mock import patch, MagicMock, call
from app import app
from db_queries import (
    toggle_estado_cdp,
    toggle_estado_lider,
    toggle_estado_usuario,
    toggle_estado_red,
)
from services.cdp_service import (
    toggle_cdp_servicio,
    actualizar_cdp_servicio,
    crear_cdp_servicio,
)
from services.leader_service import (
    toggle_lider_servicio,
    actualizar_lider_servicio,
    crear_lider_servicio,
    toggle_red_servicio,
)
from services.user_service import (
    toggle_usuario_servicio,
    actualizar_usuario_admin,
)


class TestStateAlternationsAndHierarchyEdgeCases(unittest.TestCase):
    """Adversarially tests state alternations and hierarchy edge cases."""

    def setUp(self):
        self.app = app
        self.app.config['TESTING'] = True

    # ------------------------------------------------------------------
    # 1. Non-existent IDs
    # ------------------------------------------------------------------
    def test_toggle_estado_cdp_nonexistent_id(self):
        """toggle_estado_cdp debe retornar (False, 'error', ...) para un ID inexistente."""
        cursor = MagicMock()
        cursor.fetchone.return_value = None

        ok, status, msg = toggle_estado_cdp(cursor, 99999)
        self.assertFalse(ok)
        self.assertEqual(status, 'error')
        self.assertIn("no existe", msg.lower())

    def test_toggle_estado_lider_nonexistent_id(self):
        """toggle_estado_lider debe retornar (False, 'error', ...) para un ID inexistente."""
        cursor = MagicMock()
        cursor.fetchone.return_value = None

        ok, status, msg = toggle_estado_lider(cursor, 99999)
        self.assertFalse(ok)
        self.assertEqual(status, 'error')
        self.assertIn("no existe", msg.lower())

    def test_toggle_estado_usuario_nonexistent_id(self):
        """toggle_estado_usuario debe retornar (False, 'error', ...) para un ID inexistente."""
        cursor = MagicMock()
        cursor.fetchone.return_value = None

        ok, status, msg = toggle_estado_usuario(cursor, "non-existent-uuid")
        self.assertFalse(ok)
        self.assertEqual(status, 'error')
        self.assertIn("no existe", msg.lower())

    # ------------------------------------------------------------------
    # 2. NULL usuario_id Handling in CDP Toggle
    # ------------------------------------------------------------------
    def test_toggle_estado_cdp_pause_with_null_usuario_id(self):
        """Pausar una CDP sin usuario vinculado (usuario_id = NULL) no debe intentar mutar usuario."""
        cursor = MagicMock()
        # CDP activa, Red activa, pero usuario_id = None
        cursor.fetchone.return_value = {
            'id': 10,
            'codigo': 'CDP-01',
            'is_active': 1,
            'red_id': 1,
            'usuario_id': None,
            'red_nombre': 'Red Alfa',
            'red_is_active': 1,
        }

        ok, status, msg = toggle_estado_cdp(cursor, 10)
        self.assertTrue(ok)
        self.assertEqual(status, 'pausada')

        # Verificar llamadas SQL: solo debe actualizar cdp, NO usuario
        sql_statements = [str(call_args[0][0]) for call_args in cursor.execute.call_args_list]
        self.assertTrue(any("UPDATE cdp SET is_active = 0" in stmt for stmt in sql_statements))
        self.assertFalse(any("UPDATE usuario" in stmt for stmt in sql_statements))

    def test_toggle_estado_cdp_reactivate_with_null_usuario_id(self):
        """Reactivar una CDP sin usuario vinculado (usuario_id = NULL) no debe intentar mutar usuario."""
        cursor = MagicMock()
        # CDP pausada, Red activa, pero usuario_id = None
        cursor.fetchone.return_value = {
            'id': 10,
            'codigo': 'CDP-01',
            'is_active': 0,
            'red_id': 1,
            'usuario_id': None,
            'red_nombre': 'Red Alfa',
            'red_is_active': 1,
        }

        ok, status, msg = toggle_estado_cdp(cursor, 10)
        self.assertTrue(ok)
        self.assertEqual(status, 'reactivada')

        # Verificar llamadas SQL: solo debe actualizar cdp, NO usuario
        sql_statements = [str(call_args[0][0]) for call_args in cursor.execute.call_args_list]
        self.assertTrue(any("UPDATE cdp SET is_active = 1" in stmt for stmt in sql_statements))
        self.assertFalse(any("UPDATE usuario" in stmt for stmt in sql_statements))

    # ------------------------------------------------------------------
    # 3. Multiple Toggle Flips (State Machine Invariants)
    # ------------------------------------------------------------------
    def test_cdp_multiple_toggle_flips(self):
        """Alternar repetidamente el estado de CDP debe alternar sincronizadamente entre activo y pausado."""
        cursor = MagicMock()

        # Secuencia: 1 -> 0 -> 1 -> 0 -> 1
        current_state = 1
        usuario_id = "user-uuid-1"

        def mock_fetchone():
            return {
                'id': 10,
                'codigo': 'CDP-01',
                'is_active': current_state,
                'red_id': 1,
                'usuario_id': usuario_id,
                'red_nombre': 'Red Alfa',
                'red_is_active': 1,
            }

        cursor.fetchone.side_effect = mock_fetchone

        expected_sequence = [
            ('pausada', 0),
            ('reactivada', 1),
            ('pausada', 0),
            ('reactivada', 1),
        ]

        for expected_status, new_state in expected_sequence:
            ok, status, msg = toggle_estado_cdp(cursor, 10)
            self.assertTrue(ok)
            self.assertEqual(status, expected_status)
            current_state = new_state

    def test_leader_multiple_toggle_flips(self):
        """Alternar repetidamente el estado de Líder debe alternar entre activo y pausado."""
        cursor = MagicMock()

        current_state = 1

        def mock_fetchone():
            return {
                'id': 20,
                'nombre': 'Juan',
                'apellido': 'Perez',
                'is_active': current_state,
                'cdp_id': 10,
                'cdp_codigo': 'CDP-01',
                'cdp_is_active': 1,
            }

        cursor.fetchone.side_effect = mock_fetchone

        expected_sequence = [
            ('pausado', 0),
            ('reactivado', 1),
            ('pausado', 0),
            ('reactivado', 1),
        ]

        for expected_status, new_state in expected_sequence:
            ok, status, msg = toggle_estado_lider(cursor, 20)
            self.assertTrue(ok)
            self.assertEqual(status, expected_status)
            current_state = new_state

    def test_usuario_multiple_toggle_flips(self):
        """Alternar repetidamente el estado de Usuario independiente debe alternar entre activo y desactivado."""
        cursor = MagicMock()

        current_state = 1

        def mock_fetchone():
            return {
                'id': 'user-1',
                'username': 'juanp',
                'nombre': 'Juan',
                'apellido': 'Perez',
                'is_active': current_state,
            }

        cursor.fetchone.side_effect = mock_fetchone

        expected_sequence = [
            ('desactivado', 0),
            ('reactivado', 1),
            ('desactivado', 0),
            ('reactivado', 1),
        ]

        for expected_status, new_state in expected_sequence:
            ok, status, msg = toggle_estado_usuario(cursor, 'user-1')
            self.assertTrue(ok)
            self.assertEqual(status, expected_status)
            current_state = new_state

    # ------------------------------------------------------------------
    # 4. Service Edge Inputs & Error Handling
    # ------------------------------------------------------------------
    def test_toggle_cdp_servicio_invalid_id_inputs(self):
        """toggle_cdp_servicio debe rechazar limpiamente identificadores no válidos sin lanzar excepciones."""
        with self.app.app_context():
            for invalid_id in [None, 'abc', '', [], {}]:
                ok, status, msg = toggle_cdp_servicio(invalid_id)
                self.assertFalse(ok)
                self.assertEqual(status, 'error')
                self.assertIn("no válido", msg.lower())

    def test_toggle_lider_servicio_invalid_id_inputs(self):
        """toggle_lider_servicio debe rechazar limpiamente identificadores no válidos sin lanzar excepciones."""
        with self.app.app_context():
            for invalid_id in [None, 'abc', '', [], {}]:
                ok, status, msg = toggle_lider_servicio(invalid_id)
                self.assertFalse(ok)
                self.assertEqual(status, 'error')
                self.assertIn("no válido", msg.lower())

    def test_toggle_usuario_servicio_invalid_id_inputs(self):
        """toggle_usuario_servicio debe rechazar identificadores vacíos o None."""
        with self.app.app_context():
            for invalid_id in [None, '']:
                ok, status, msg = toggle_usuario_servicio(invalid_id)
                self.assertFalse(ok)
                self.assertEqual(status, 'error')


class TestHierarchyInvariantsAndCodePathAnalysis(unittest.TestCase):
    """
    Investigates whether any code paths allow an inactive Red to have an active CDP
    or an inactive CDP to have an active Leader.
    """

    def setUp(self):
        self.app = app
        self.app.config['TESTING'] = True

    # ------------------------------------------------------------------
    # Code Path 1: Pausing Red does NOT cascade to CDPs
    # ------------------------------------------------------------------
    def test_code_path_pausing_red_leaves_cdps_active(self):
        """
        DEMOSTRACIÓN EMPÍRICA:
        Cuando una Red pasa a is_active = 0 mediante toggle_estado_red,
        sus Casas de Paz asignadas PERMANECEN activas (is_active = 1).
        Esto permite que una Red inactiva tenga Casas de Paz activas.
        """
        cursor = MagicMock()
        cursor.fetchone.return_value = {'is_active': 0}

        # Ejecutar toggle_estado_red
        nuevo_estado = toggle_estado_red(cursor, 1)
        self.assertFalse(nuevo_estado)

        # Analizar todas las consultas SQL emitidas por toggle_estado_red
        sql_statements = [str(call_args[0][0]) for call_args in cursor.execute.call_args_list]

        # Solo actualiza 'red'; NO actualiza la tabla 'cdp' ni verifica casas dependientes
        self.assertTrue(any("UPDATE red" in stmt for stmt in sql_statements))
        self.assertFalse(any("cdp" in stmt.lower() for stmt in sql_statements))

    # ------------------------------------------------------------------
    # Code Path 2: Pausing CDP does NOT cascade to Leaders
    # ------------------------------------------------------------------
    def test_code_path_pausing_cdp_leaves_leaders_active(self):
        """
        DEMOSTRACIÓN EMPÍRICA:
        Cuando una Casa de Paz pasa a is_active = 0 mediante toggle_estado_cdp,
        los líderes asignados a esa Casa (en la tabla lider) PERMANECEN activos (is_active = 1).
        Esto permite que una Casa de Paz inactiva tenga Líderes activos.
        """
        cursor = MagicMock()
        cursor.fetchone.return_value = {
            'id': 10,
            'codigo': 'CDP-01',
            'is_active': 1,
            'red_id': 1,
            'usuario_id': 'user-1',
            'red_nombre': 'Red Alfa',
            'red_is_active': 1,
        }

        ok, status, msg = toggle_estado_cdp(cursor, 10)
        self.assertTrue(ok)
        self.assertEqual(status, 'pausada')

        # Analizar todas las consultas SQL emitidas por toggle_estado_cdp
        sql_statements = [str(call_args[0][0]) for call_args in cursor.execute.call_args_list]

        # Actualiza cdp y usuario, pero NUNCA actualiza 'lider'
        self.assertTrue(any("UPDATE cdp SET is_active = 0" in stmt for stmt in sql_statements))
        self.assertTrue(any("UPDATE usuario SET is_active = 0" in stmt for stmt in sql_statements))
        self.assertFalse(any("lider" in stmt.lower() for stmt in sql_statements))

    # ------------------------------------------------------------------
    # Code Path 3: Creating a CDP does NOT validate Red is_active
    # ------------------------------------------------------------------
    @patch('services.cdp_service.get_db_connection')
    def test_code_path_crear_cdp_in_inactive_red_allowed(self, mock_get_conn):
        """
        DEMOSTRACIÓN EMPÍRICA:
        crear_cdp_servicio no valida si la Red ministerial especificada en red_id
        se encuentra activa o pausada.
        Permite insertar una nueva Casa de Paz activa (is_active = 1) en una Red inactiva.
        """
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_conn.cursor.return_value.__enter__.return_value = mock_cursor
        mock_get_conn.return_value = mock_conn

        # Cursor retorna: código no duplicado, username no duplicado
        mock_cursor.fetchone.side_effect = [
            None,  # SELECT id FROM cdp WHERE codigo = %s
            None,  # SELECT id FROM usuario WHERE username = %s
        ]

        form_data = {
            'codigo': 'CDP-NUEVA-01',
            'anfitrion': 'Pedro Perez',
            'telefono': '+58 412 1234567',
            'direccion': 'Calle Los Olivos 42',
            'red_id': '5',  # Supongamos que Red 5 está pausada (is_active = 0)
            'nombre': 'Pedro',
            'apellido': 'Perez',
            'username': 'pedrop_cdp',
            'password': 'Password123'
        }

        with self.app.app_context():
            ok, msg = crear_cdp_servicio(form_data)

        self.assertTrue(ok)

        # Analizar las consultas: nunca consultó 'SELECT is_active FROM red'
        sql_statements = [str(call_args[0][0]) for call_args in mock_cursor.execute.call_args_list]
        self.assertFalse(any("FROM red" in stmt for stmt in sql_statements))

    # ------------------------------------------------------------------
    # Code Path 4: Updating an already-active CDP with new inactive Red
    # ------------------------------------------------------------------
    @patch('services.cdp_service.get_db_connection')
    def test_code_path_actualizar_cdp_move_to_inactive_red_without_is_active_flag(self, mock_get_conn):
        """
        DEMOSTRACIÓN EMPÍRICA:
        En actualizar_cdp_servicio, la verificación de jerarquía de Red solo se ejecuta
        si `is_active_val == 1` (línea 946).
        Si una CDP ya estaba activa y se edita para cambiar su red_id a una Red inactiva
        SIN pasar el parámetro `is_active` (e.g. formulario estándar que no envía is_active),
        la verificación se omite y la CDP activa queda reasignada a una Red inactiva.
        """
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_cursor.rowcount = 1
        mock_conn.cursor.return_value.__enter__.return_value = mock_cursor
        mock_get_conn.return_value = mock_conn

        # Casa existe y pertenece a usuario user-1
        mock_cursor.fetchone.side_effect = [
            {'id': 10, 'usuario_id': 'user-1'},  # SELECT id, usuario_id FROM cdp WHERE id = 10
            None,  # SELECT id FROM cdp WHERE codigo = %s AND id != 10 (no duplicado)
            None,  # SELECT id FROM usuario WHERE username = %s AND id != user-1 (no duplicado)
        ]

        # form_data SIN is_active (edición normal de datos y reasignación de red)
        form_data = {
            'codigo': 'CDP-01',
            'anfitrion': 'Pedro Perez',
            'telefono': '+58 412 1234567',
            'direccion': 'Calle Los Olivos 42',
            'red_id': '99',  # Red 99 está inactiva en BD
            'nombre': 'Pedro',
            'apellido': 'Perez',
            'username': 'pedrop_cdp',
            'password': ''
        }

        with self.app.app_context():
            # Llamada sin pasar is_active
            ok, msg = actualizar_cdp_servicio(10, form_data, is_active=None)

        self.assertTrue(ok)

        # Analizar las consultas: se omitió la consulta a red porque is_active_val es None
        sql_statements = [str(call_args[0][0]) for call_args in mock_cursor.execute.call_args_list]
        self.assertFalse(any("FROM red" in stmt for stmt in sql_statements))

    # ------------------------------------------------------------------
    # Code Path 5: Contrast - Creating a Leader DOES validate CDP is_active
    # ------------------------------------------------------------------
    @patch('services.leader_service.get_db_connection')
    def test_crear_lider_blocks_when_cdp_is_inactive(self, mock_get_conn):
        """crear_lider_servicio SÍ valida que la CDP esté activa y bloquea si está inactiva."""
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_conn.cursor.return_value.__enter__.return_value = mock_cursor
        mock_get_conn.return_value = mock_conn

        # CDP existe pero está inactiva
        mock_cursor.fetchone.return_value = {
            'id': 10,
            'codigo': 'CDP-INACTIVA',
            'is_active': 0
        }

        form_data = {
            'nombre': 'Carlos',
            'apellido': 'Lopez',
            'telefono': '+58 414 1112233',
            'rol': 'Lider',
            'cdp_id': '10'
        }

        with self.app.app_context():
            ok, msg = crear_lider_servicio(form_data)

        self.assertFalse(ok)
        self.assertIn("inactiva/pausada", msg.lower())

    # ------------------------------------------------------------------
    # Code Path 6: Contrast - Updating a Leader DOES validate CDP is_active
    # ------------------------------------------------------------------
    @patch('services.leader_service.get_db_connection')
    def test_actualizar_lider_blocks_when_assigned_cdp_is_inactive(self, mock_get_conn):
        """actualizar_lider_servicio SÍ valida que la CDP esté activa cuando el líder queda activo."""
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_conn.cursor.return_value.__enter__.return_value = mock_cursor
        mock_get_conn.return_value = mock_conn

        # Líder existe y está activo; CDP destino existe pero está inactiva
        mock_cursor.fetchone.side_effect = [
            {'id': 5, 'nombre': 'Carlos', 'apellido': 'Lopez', 'is_active': 1},
            {'id': 10, 'codigo': 'CDP-INACTIVA', 'is_active': 0}
        ]

        form_data = {
            'nombre': 'Carlos',
            'apellido': 'Lopez',
            'telefono': '+58 414 1112233',
            'rol': 'Lider',
            'cdp_id': '10'
        }

        with self.app.app_context():
            # Líder activo se reasigna a CDP inactiva
            ok, msg = actualizar_lider_servicio(5, form_data, is_active=None)

        self.assertFalse(ok)
        self.assertIn("pausa o inactiva", msg.lower())


if __name__ == '__main__':
    unittest.main()
