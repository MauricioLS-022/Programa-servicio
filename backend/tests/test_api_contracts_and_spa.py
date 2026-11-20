"""
tests/test_api_contracts_and_spa.py - Validación de contratos JSON Backend <-> Frontend SPA,
endpoint de salud (/api/health) y servicio híbrido SPA (/app, /assets/<path>) en Flask.
"""
import os
import tempfile
import unittest
from unittest.mock import patch
import app as app_module
from app import app
from utils.cache import invalidate_dashboard_cache


class TestApiContractsAndSpa(unittest.TestCase):

    def setUp(self):
        self._orig_mock = app.config.get('MOCK_MODE', False)
        app.config['TESTING'] = True
        app.config['MOCK_MODE'] = True
        app.config['WTF_CSRF_ENABLED'] = False
        invalidate_dashboard_cache()
        self.client = app.test_client()

    def tearDown(self):
        app.config['MOCK_MODE'] = self._orig_mock
        invalidate_dashboard_cache()

    def _set_session(self, rol: str, usuario_id: str = 'admin-1'):
        with self.client.session_transaction() as sess:
            sess.clear()
            sess['usuario_id'] = usuario_id
            sess['usuario'] = rol
            sess['rol'] = rol

    # ------------------------------------------------------------------
    # 1. Endpoint de salud /api/health
    # ------------------------------------------------------------------
    def test_api_health_get_and_head_public(self):
        res_get = self.client.get('/api/health')
        self.assertEqual(res_get.status_code, 200)
        data = res_get.get_json()
        self.assertEqual(data, {'status': 'ok', 'app': 'vino-nuevo', 'service': 'api'})

        res_head = self.client.head('/api/health')
        self.assertEqual(res_head.status_code, 200)

    # ------------------------------------------------------------------
    # 2. Contratos JSON esperados por TypeScript en frontend/src/types/
    # ------------------------------------------------------------------
    def test_contract_dashboard_datos_general_red_cdp(self):
        self._set_session('admin')

        res_gen = self.client.get('/api/dashboard/datos?nivel=general', headers={'Accept': 'application/json'})
        self.assertEqual(res_gen.status_code, 200)
        gen = res_gen.get_json()
        for key in ('total_asistencia', 'total_casas', 'cumplimiento', 'ofrendas_usd', 'ofrendas_bs', 'distribucion', 'ranking_redes', 'alertas', 'tendencia_semanas'):
            self.assertIn(key, gen, f"Falta clave '{key}' en /api/dashboard/datos?nivel=general")

        res_red = self.client.get('/api/dashboard/datos?nivel=red&red_id=1', headers={'Accept': 'application/json'})
        self.assertEqual(res_red.status_code, 200)
        red = res_red.get_json()
        for key in ('nombre_red', 'asistencia_total', 'casas_activas'):
            self.assertIn(key, red, f"Falta clave '{key}' en /api/dashboard/datos?nivel=red")

        res_cdp = self.client.get('/api/dashboard/datos?nivel=cdp&cdp_id=1', headers={'Accept': 'application/json'})
        self.assertEqual(res_cdp.status_code, 200)
        cdp = res_cdp.get_json()
        for key in ('codigo', 'nombre_cdp', 'total_asistencia'):
            self.assertIn(key, cdp, f"Falta clave '{key}' en /api/dashboard/datos?nivel=cdp")

    def test_contract_lider_dashboard(self):
        self._set_session('lider_cdp', 'mock-lider-id')
        res = self.client.get('/api/lider/dashboard?page=1&per_page=5')
        self.assertEqual(res.status_code, 200)
        data = res.get_json()
        for key in ('cdp', 'lideres', 'metricas', 'reportes', 'total_reportes', 'page', 'pages', 'tiene_cdp'):
            self.assertIn(key, data, f"Falta clave '{key}' en /api/lider/dashboard")
        for m_key in ('total_reportes', 'asistencia_promedio', 'ofrendas_usd_totales', 'ofrendas_bs_totales'):
            self.assertIn(m_key, data['metricas'])

    def test_contract_reportes_estructura_lideres_usuarios(self):
        self._set_session('admin')

        # /api/reportes -> ReportesResponse
        res_rep = self.client.get('/api/reportes?page=1&per_page=5')
        self.assertEqual(res_rep.status_code, 200)
        rep = res_rep.get_json()
        for key in ('reportes', 'total', 'page', 'pages', 'per_page'):
            self.assertIn(key, rep)
        if rep['reportes']:
            for item_key in ('id', 'cdp_id', 'fecha', 'tema', 'asistencia', 'ofrendas_usd', 'ofrendas_bs'):
                self.assertIn(item_key, rep['reportes'][0])

        # /api/redes
        res_redes = self.client.get('/api/redes')
        self.assertEqual(res_redes.status_code, 200)
        redes = res_redes.get_json()
        self.assertIn('redes', redes)
        self.assertGreater(len(redes['redes']), 0)
        for key in ('id', 'nombre', 'is_active'):
            self.assertIn(key, redes['redes'][0])

        # /api/casas_de_paz
        res_casas = self.client.get('/api/casas_de_paz')
        self.assertEqual(res_casas.status_code, 200)
        casas = res_casas.get_json()
        for key in ('casas', 'total', 'sin_reporte_7d_ids'):
            self.assertIn(key, casas)
        self.assertGreater(len(casas['casas']), 0)
        for item_key in ('id', 'codigo', 'red_id', 'is_active', 'sin_reporte_7d'):
            self.assertIn(item_key, casas['casas'][0])

        # /api/lideres
        res_lid = self.client.get('/api/lideres?page=1&per_page=5')
        self.assertEqual(res_lid.status_code, 200)
        lid = res_lid.get_json()
        for key in ('lideres', 'total', 'page', 'pages', 'per_page'):
            self.assertIn(key, lid)

        # /api/usuarios -> UsuariosResponse
        res_usr = self.client.get('/api/usuarios?page=1&per_page=5')
        self.assertEqual(res_usr.status_code, 200)
        usr = res_usr.get_json()
        for key in ('usuarios', 'total', 'total_activos', 'page', 'pages', 'per_page'):
            self.assertIn(key, usr)
        self.assertGreater(len(usr['usuarios']), 0)
        for item_key in ('id', 'username', 'nombre', 'apellido', 'is_active'):
            self.assertIn(item_key, usr['usuarios'][0])

    # ------------------------------------------------------------------
    # 3. Servicio híbrido SPA (/app, /app/<route>, /assets/<path>)
    # ------------------------------------------------------------------
    def test_serve_spa_and_assets_with_compiled_dist(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            assets_dir = os.path.join(tmpdir, 'assets')
            os.makedirs(assets_dir, exist_ok=True)
            with open(os.path.join(tmpdir, 'index.html'), 'w', encoding='utf-8') as f:
                f.write('<!doctype html><html><body><div id="root">SPA_OK</div></body></html>')
            with open(os.path.join(assets_dir, 'bundle.js'), 'w', encoding='utf-8') as f:
                f.write('console.log("spa");')
            with open(os.path.join(assets_dir, 'bundle.js.br'), 'wb') as f:
                f.write(b'MOCK_BROTLI_BYTES')
            with open(os.path.join(assets_dir, 'bundle.js.gz'), 'wb') as f:
                f.write(b'MOCK_GZIP_BYTES')

            with patch.object(app_module, 'frontend_dist_dir', tmpdir):
                with self.client.get('/app') as res_root:
                    self.assertEqual(res_root.status_code, 200)
                    self.assertIn(b'SPA_OK', res_root.data)

                with self.client.get('/app/dashboard') as res_deep:
                    self.assertEqual(res_deep.status_code, 200)
                    self.assertIn(b'SPA_OK', res_deep.data)

                with self.client.get('/assets/bundle.js', headers={'Accept-Encoding': 'identity'}) as res_asset:
                    self.assertEqual(res_asset.status_code, 200)
                    self.assertIn(b'console.log("spa")', res_asset.data)
                    self.assertEqual(res_asset.headers.get('Vary'), 'Accept-Encoding')
                    self.assertIn('immutable', res_asset.headers.get('Cache-Control', ''))

                with self.client.get('/assets/bundle.js', headers={'Accept-Encoding': 'gzip, deflate, br'}) as res_br:
                    self.assertEqual(res_br.status_code, 200)
                    self.assertEqual(res_br.headers.get('Content-Encoding'), 'br')
                    self.assertEqual(res_br.headers.get('Vary'), 'Accept-Encoding')
                    self.assertIn('javascript', res_br.content_type)
                    self.assertEqual(res_br.data, b'MOCK_BROTLI_BYTES')

                with self.client.get('/assets/bundle.js', headers={'Accept-Encoding': 'gzip'}) as res_gz:
                    self.assertEqual(res_gz.status_code, 200)
                    self.assertEqual(res_gz.headers.get('Content-Encoding'), 'gzip')
                    self.assertIn('javascript', res_gz.content_type)
                    self.assertEqual(res_gz.data, b'MOCK_GZIP_BYTES')

                with self.client.get('/assets/no-existe.js') as res_missing_asset:
                    self.assertEqual(res_missing_asset.status_code, 404)

    def test_serve_spa_returns_404_when_dist_missing(self):
        with patch.object(app_module, 'frontend_dist_dir', os.path.join(tempfile.gettempdir(), 'nonexistent_dist_vn_999')):
            res = self.client.get('/app')
            self.assertEqual(res.status_code, 404)


if __name__ == '__main__':
    unittest.main()
