"""
Tests unitarios y de integración para el modo Mock y el Circuit Breaker:
- Aislamiento absoluto de BD cuando MOCK_MODE está activado (zero connection attempts)
- Circuit Breaker: estados CLOSED, OPEN, HALF_OPEN y recuperación
- Coherencia relacional estricta de mock_data.py
- Coerción de tipos de ID (int vs str) en selectores y consultas
- Navegación end-to-end sin BD para Admin, Supervisor y Líder de CDP
"""
import unittest
from unittest.mock import patch, MagicMock
from app import app
import database
from mock_data import (
    get_redes_demo,
    get_casas_demo,
    get_mock_usuarios,
    get_mock_lideres,
    get_mock_reportes,
    get_mock_generales,
    get_mock_red,
    get_mock_cdp,
    get_mock_cdp_detalle
)


class TestMockModeIsolation(unittest.TestCase):
    """Verifica que el modo mock aísle por completo las llamadas a base de datos."""

    def setUp(self):
        self._orig_mock = app.config.get('MOCK_MODE', False)
        database.reset_circuit_breaker()
        app.config['TESTING'] = True

    def tearDown(self):
        app.config['MOCK_MODE'] = self._orig_mock
        database.reset_circuit_breaker()

    @patch('pymysql.connect')
    def test_get_db_connection_zero_attempts_when_mock_mode_true(self, mock_pymysql):
        """Con MOCK_MODE=True, get_db_connection DEBE retornar None y NO llamar a pymysql.connect."""
        with app.app_context():
            app.config['MOCK_MODE'] = True
            conn = database.get_db_connection()
            self.assertIsNone(conn)
            mock_pymysql.assert_not_called()
            self.assertFalse(database.is_db_available())

    def test_is_mock_mode_detection(self):
        """is_mock_mode detecta correctamente la configuración de la app."""
        with app.app_context():
            app.config['MOCK_MODE'] = True
            self.assertTrue(database.is_mock_mode())
            app.config['MOCK_MODE'] = False
            self.assertFalse(database.is_mock_mode())


class TestCircuitBreaker(unittest.TestCase):
    """Verifica la máquina de estados y la resiliencia del Circuit Breaker."""

    def setUp(self):
        self._orig_mock = app.config.get('MOCK_MODE', False)
        database.reset_circuit_breaker()
        app.config['TESTING'] = True
        app.config['MOCK_MODE'] = False

    def tearDown(self):
        app.config['MOCK_MODE'] = self._orig_mock
        database.reset_circuit_breaker()

    @patch('database._create_raw_connection')
    def test_circuit_opens_on_failure(self, mock_create_conn):
        """Cuando la conexión falla, el circuit breaker pasa a estado OPEN."""
        mock_create_conn.side_effect = Exception("MySQL connection refused")

        with app.app_context():
            conn1 = database.get_db_connection()
            self.assertIsNone(conn1)
            status = database.get_circuit_breaker_status()
            self.assertEqual(status['state'], database.STATE_OPEN)
            self.assertFalse(status['db_available'])
            self.assertEqual(status['fail_count'], 1)

            # Siguiente llamada dentro del intervalo: fast-fail sin intentar conectar de nuevo
            conn2 = database.get_db_connection()
            self.assertIsNone(conn2)
            # Solo se debió haber llamado a _create_raw_connection 1 vez
            self.assertEqual(mock_create_conn.call_count, 1)

    @patch('database._create_raw_connection')
    @patch('time.time')
    def test_circuit_half_open_and_recovery(self, mock_time, mock_create_conn):
        """Tras expirar el intervalo, el circuito pasa a HALF_OPEN y se recupera con éxito."""
        mock_time.return_value = 1000.0
        mock_create_conn.side_effect = Exception("Fallo inicial")

        with app.app_context():
            # 1. Fallo inicial
            database.get_db_connection()
            self.assertEqual(database._circuit_state, database.STATE_OPEN)

            # 2. Avance en el tiempo más allá de _DB_RETRY_INTERVAL (15s)
            mock_time.return_value = 1020.0
            fake_conn = MagicMock()
            fake_conn.open = True
            mock_create_conn.side_effect = None
            mock_create_conn.return_value = fake_conn

            # 3. Intento de reconexión
            conn = database.get_db_connection()
            self.assertIsNotNone(conn)
            status = database.get_circuit_breaker_status()
            self.assertEqual(status['state'], database.STATE_CLOSED)
            self.assertTrue(status['db_available'])
            self.assertEqual(status['fail_count'], 0)


class TestMockDataIntegrity(unittest.TestCase):
    """Verifica que los datos mock sean 100% coherentes y relacionales."""

    def test_casas_belong_to_valid_redes(self):
        """Cada Casa de Paz en get_casas_demo debe pertenecer a una Red existente."""
        redes = get_redes_demo()
        red_ids = {r['id'] for r in redes}
        casas = get_casas_demo()

        for c in casas:
            self.assertIn(c['red_id'], red_ids, f"Casa {c['nombre']} tiene red_id {c['red_id']} inexistente")
            matching_red = next(r for r in redes if r['id'] == c['red_id'])
            self.assertEqual(c['red_nombre'], matching_red['nombre'])

    def test_lideres_belong_to_valid_casas_and_redes(self):
        """Cada Líder debe tener coherencia estricta entre su cdp_id y red_id."""
        casas = get_casas_demo()
        casa_map = {c['id']: c for c in casas}
        lideres = get_mock_lideres()

        for l in lideres:
            self.assertIn(l['cdp_id'], casa_map, f"Líder {l['nombre']} tiene cdp_id {l['cdp_id']} inexistente")
            casa = casa_map[l['cdp_id']]
            self.assertEqual(l['red_id'], casa['red_id'], f"Líder {l['nombre']} red_id no coincide con su Casa")
            self.assertEqual(l['cdp_nombre'], casa['nombre'])

    def test_reportes_consistency(self):
        """Todos los reportes mock deben apuntar a Casas y Redes existentes y congruentes."""
        casas = get_casas_demo()
        casa_map = {c['id']: c for c in casas}
        reportes = get_mock_reportes()

        self.assertGreater(len(reportes), 0)
        for r in reportes:
            self.assertIn(r['cdp_id'], casa_map, f"Reporte {r['id']} tiene cdp_id {r['cdp_id']} inexistente")
            casa = casa_map[r['cdp_id']]
            self.assertEqual(r['red_id'], casa['red_id'], f"Reporte {r['id']} red_id no coincide con su Casa")
            self.assertEqual(r['cdp_nombre'], casa['nombre'])
            asistencia_calculada = r['nro_regulares'] + r['nro_niños'] + r['nro_visitas'] + r['nro_comprometidos']
            self.assertEqual(r['asistencia'], asistencia_calculada, f"Reporte {r['id']} asistencia no coincide")

    def test_type_coercion_red_and_cdp_selectors(self):
        """get_mock_red y get_mock_cdp deben soportar IDs tanto int como str sin fallback erróneo."""
        red_int = get_mock_red(2)
        red_str = get_mock_red('2')
        self.assertEqual(red_int['red_id'], 2)
        self.assertEqual(red_str['red_id'], 2)
        self.assertEqual(red_int['nombre_red'], 'Red Sur')
        self.assertEqual(red_str['nombre_red'], 'Red Sur')

        cdp_int = get_mock_cdp(3)
        cdp_str = get_mock_cdp('3')
        self.assertEqual(cdp_int['id'], 3)
        self.assertEqual(cdp_str['id'], 3)
        self.assertEqual(cdp_int['nombre_cdp'], 'Casa Nueva Vida')
        self.assertEqual(cdp_str['nombre_cdp'], 'Casa Nueva Vida')

    def test_cdp_detalle_completeness(self):
        """get_mock_cdp_detalle debe retornar todas las llaves requeridas por detalles_cdp.html."""
        detalle = get_mock_cdp_detalle('1')
        self.assertEqual(detalle['id'], 1)
        self.assertEqual(detalle['codigo'], 'HEB-001')
        self.assertEqual(detalle['nombre'], 'Casa Bethel')
        self.assertEqual(detalle['red_nombre'], 'Red Hebrón')
        self.assertEqual(detalle['supervisor_nombre'], 'Pedro González')
        self.assertIn('asistencia_promedio', detalle)
        self.assertIn('ofrendas_usd_totales', detalle)
        self.assertIn('lideres', detalle)
        self.assertIn('reportes', detalle)
        self.assertGreater(len(detalle['lideres']), 0)
        self.assertGreater(len(detalle['reportes']), 0)


class TestNavigationWithoutDatabase(unittest.TestCase):
    """Pruebas end-to-end usando el test_client de Flask en modo Mock."""

    def setUp(self):
        self._orig_mock = app.config.get('MOCK_MODE', False)
        app.config['TESTING'] = True
        app.config['MOCK_MODE'] = True
        self.client = app.test_client()

    def tearDown(self):
        app.config['MOCK_MODE'] = self._orig_mock
        database.reset_circuit_breaker()

    def test_admin_flow_without_db(self):
        """Admin puede iniciar sesión y acceder a todas las vistas sin base de datos."""
        res_login = self.client.post('/iniciar_sesion', data={'usuario': 'admin', 'contrasena': 'admin'}, follow_redirects=False)
        self.assertEqual(res_login.status_code, 302)
        self.assertIn('/admin/dashboard', res_login.headers['Location'])

        for url in [
            '/admin/dashboard',
            '/admin/reportes',
            '/admin/lider',
            '/admin/estructura',
            '/admin/usuario',
            '/admin/casa_de_paz/1',
            '/admin/perfil'
        ]:
            res = self.client.get(url)
            self.assertEqual(res.status_code, 200, f"Fallo al cargar vista admin: {url}")

    def test_supervisor_flow_without_db(self):
        """Supervisor puede iniciar sesión y acceder a sus vistas sin base de datos."""
        res_login = self.client.post('/iniciar_sesion', data={'usuario': 'supervisor', 'contrasena': 'supervisor'}, follow_redirects=False)
        self.assertEqual(res_login.status_code, 302)
        self.assertIn('/supervisor/dashboard', res_login.headers['Location'])

        for url in [
            '/supervisor/dashboard',
            '/supervisor/reportes',
            '/supervisor/lider',
            '/supervisor/estructura',
            '/supervisor/casa_de_paz/1',
            '/supervisor/perfil'
        ]:
            res = self.client.get(url)
            self.assertEqual(res.status_code, 200, f"Fallo al cargar vista supervisor: {url}")

    def test_lider_cdp_flow_without_db(self):
        """Líder CDP puede iniciar sesión, ver dashboard y usar formularios sin base de datos."""
        res_login = self.client.post('/iniciar_sesion', data={'usuario': 'lider', 'contrasena': 'lider'}, follow_redirects=False)
        self.assertEqual(res_login.status_code, 302)
        self.assertIn('/lider_cdp/dashboard', res_login.headers['Location'])

        res_dash = self.client.get('/lider_cdp/dashboard')
        self.assertEqual(res_dash.status_code, 200)

        res_form = self.client.get('/lider_cdp/generar_reporte')
        self.assertEqual(res_form.status_code, 200)
        self.assertIn('Generar Reporte', res_form.get_data(as_text=True))
        self.assertIn('Juan Carlos', res_form.get_data(as_text=True))

        post_data = {
            'fecha': '2026-08-25',
            'hr_inicio': '19:00',
            'hr_fin': '20:30',
            'tema': 'Nuevo Test en Mock',
            'nro_regulares': 10,
            'nro_ninos': 2,
            'nro_visitas': 2,
            'nro_comprometidos': 1,
            'ofrendas_usd': 20.0,
            'ofrendas_bs': 360.0,
            'cesta_amor': 1,
            'observaciones': 'Prueba sin BD'
        }
        res_post = self.client.post('/lider_cdp/generar_reporte', data=post_data, follow_redirects=True)
        self.assertEqual(res_post.status_code, 200)
        self.assertIn('guardado exitosamente', res_post.get_data(as_text=True).lower())

        res_edit = self.client.post('/lider_cdp/reporte/mock-rep-1/editar', data=post_data, follow_redirects=True)
        self.assertEqual(res_edit.status_code, 200)

        res_del = self.client.post('/lider_cdp/reporte/mock-rep-1/eliminar', follow_redirects=True)
        self.assertEqual(res_del.status_code, 200)

        res_perfil = self.client.get('/lider_cdp/perfil')
        self.assertEqual(res_perfil.status_code, 200)
        self.assertIn(b'Juan Carlos', res_perfil.data)

    def test_reportes_filters_mock_data(self):
        """Filtros de reportes por red_id y cdp_id funcionan adecuadamente en modo mock."""
        self.client.post('/iniciar_sesion', data={'usuario': 'admin', 'contrasena': 'admin'})
        
        res_red1 = self.client.get('/admin/reportes?red_id=1')
        self.assertEqual(res_red1.status_code, 200)
        html_red1 = res_red1.get_data(as_text=True)
        self.assertIn('Casa Bethel', html_red1)

        res_red2 = self.client.get('/admin/reportes?red_id=2')
        self.assertEqual(res_red2.status_code, 200)
        html_red2 = res_red2.get_data(as_text=True)
        self.assertIn('Casa de Oración Sur', html_red2)


class TestProductionFallbacksAndDataIntegrity(unittest.TestCase):
    """Verifica que los fallbacks corregidos protejan la consistencia y seguridad en producción."""

    def setUp(self):
        self.app = app
        self.client = app.test_client()
        self.app.config['TESTING'] = True
        self.app.config['WTF_CSRF_ENABLED'] = False

    def test_get_cdp_detalle_nonexistent_returns_none_in_db_mode(self):
        """Con BD activa, si una CDP no existe en la BD, no debe hacer fallback a mock data."""
        mock_conn = MagicMock()
        mock_cur = MagicMock()
        mock_conn.cursor.return_value.__enter__.return_value = mock_cur
        mock_cur.fetchone.return_value = None  # No existe en MySQL

        with patch('services.cdp_service.get_db_connection', return_value=mock_conn):
            from services.cdp_service import get_cdp_detalle
            detalle = get_cdp_detalle(99999)
            self.assertIsNone(detalle, "Debe retornar None cuando no existe en la base de datos")

    def test_get_cdp_detalle_nonexistent_returns_none_in_demo_mode(self):
        """Sin conexión, si el ID no existe en el catálogo demo, debe retornar None."""
        with patch('services.cdp_service.get_db_connection', return_value=None):
            from services.cdp_service import get_cdp_detalle
            detalle = get_cdp_detalle(99999)
            self.assertIsNone(detalle, "Debe retornar None para ID inexistente en demo")

    def test_mock_red_and_cdp_nonexistent_return_empty_objects(self):
        """get_mock_red y get_mock_cdp con ID inexistente deben retornar estructuras vacías y no la entidad 1."""
        from mock_data import get_mock_red, get_mock_cdp
        red_vacia = get_mock_red(99999)
        self.assertEqual(red_vacia['nombre_red'], 'Red sin datos')
        self.assertEqual(red_vacia['asistencia_total'], 0)

        cdp_vacia = get_mock_cdp(99999)
        self.assertEqual(cdp_vacia['codigo'], '')
        self.assertEqual(cdp_vacia['total_asistencia'], 0)

    def test_actualizar_reporte_rejects_missing_cdp_id(self):
        """actualizar_reporte debe rechazar peticiones con cdp_id nulo o cero (prevención bypass IDOR)."""
        from services.cdp_service import actualizar_reporte
        ok, msg = actualizar_reporte('rep-1', None, {})
        self.assertFalse(ok)
        self.assertIn("Identificador de Casa de Paz no válido", msg)

        ok2, msg2 = actualizar_reporte('rep-1', 0, {})
        self.assertFalse(ok2)
        self.assertIn("Identificador de Casa de Paz no válido", msg2)

    def test_get_casas_sin_reporte_7d_returns_empty_when_mock_disabled(self):
        """Si la conexión a BD falla y MOCK_MODE=False, debe retornar lista vacía (no datos demo)."""
        from services.dashboard_service import get_casas_sin_reporte_7d
        with patch('services.dashboard_service.get_db_connection', return_value=None), \
             patch('services.dashboard_service.mock_mode_enabled', return_value=False):
            casas = get_casas_sin_reporte_7d()
            self.assertEqual(casas, [], "Debe retornar lista vacía cuando mock_mode está deshabilitado")

    def test_get_metricas_exception_returns_level_appropriate_empty_data(self):
        """Ante excepción SQL, get_metricas debe retornar el empty del nivel correspondiente."""
        from services.dashboard_service import get_metricas
        mock_conn = MagicMock()
        mock_conn.cursor.side_effect = Exception("Crash simulado en BD")

        with patch('services.dashboard_service.get_db_connection', return_value=mock_conn):
            metricas_red = get_metricas('red', red_id=2)
            self.assertEqual(metricas_red.get('nombre_red'), 'Red sin datos')

            metricas_cdp = get_metricas('cdp', cdp_id=3)
            self.assertEqual(metricas_cdp.get('codigo'), '')
            self.assertIn('promedio_historico', metricas_cdp)

    def test_api_supervisor_allows_cdp_level_in_own_red(self):
        """Supervisor puede consultar nivel 'cdp' para una casa de su propia red vía API."""
        with self.client.session_transaction() as sess:
            sess['usuario_id'] = 'sup-user-id'
            sess['usuario'] = 'supervisor1'
            sess['rol'] = 'supervisor'

        mock_casas = [{'id': 1, 'codigo': 'HEB-001', 'red_id': 1}, {'id': 2, 'codigo': 'SUR-001', 'red_id': 2}]
        with patch('routes.api_routes.get_supervisor_red_id', return_value=1), \
             patch('services.dashboard_service.get_selectores', return_value=([], mock_casas)), \
             patch('routes.api_routes.get_metricas', return_value={'codigo': 'HEB-001', 'asistencia': 20}) as mock_m:
            
            resp = self.client.get('/api/dashboard/datos?nivel=cdp&cdp_id=1')
            self.assertEqual(resp.status_code, 200)
            mock_m.assert_called_once_with('cdp', 1, 1)

    def test_api_supervisor_blocks_cdp_level_in_other_red(self):
        """Supervisor recibe 403 si intenta consultar una casa de otra red vía API."""
        with self.client.session_transaction() as sess:
            sess['usuario_id'] = 'sup-user-id'
            sess['usuario'] = 'supervisor1'
            sess['rol'] = 'supervisor'

        mock_casas = [{'id': 1, 'codigo': 'HEB-001', 'red_id': 1}, {'id': 2, 'codigo': 'SUR-001', 'red_id': 2}]
        with patch('routes.api_routes.get_supervisor_red_id', return_value=1), \
             patch('services.dashboard_service.get_selectores', return_value=([], mock_casas)):
            
            resp = self.client.get('/api/dashboard/datos?nivel=cdp&cdp_id=2')
            self.assertEqual(resp.status_code, 403)


if __name__ == '__main__':
    unittest.main()
