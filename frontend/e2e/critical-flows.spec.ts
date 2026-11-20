import { test, expect, type Page } from '@playwright/test';

async function loginViaSpa(page: Page, usuario: string, contrasena: string) {
  await page.goto('/app/login');
  await expect(page.getByRole('heading', { name: /Iniciar Sesión|Vino Nuevo/i })).toBeVisible();
  await page.locator('input[name="usuario"], input#usuario').first().fill(usuario);
  await page.locator('input[name="contrasena"], input#contrasena').first().fill(contrasena);
  await Promise.all([
    page.waitForResponse((res) => res.url().includes('/api/auth/login') && res.status() === 200),
    page.getByRole('button', { name: /Ingresar|Iniciar Sesión/i }).click(),
  ]);
  await expect(page).toHaveURL(/\/app\/dashboard/);
}

test.describe('Smoke E2E: Flask + React SPA (/app)', () => {
  test('1. Admin: Login real con cookie HttpOnly, Estructura, Ficha Técnica CDP y Logout', async ({ page }) => {
    await loginViaSpa(page, 'admin', 'admin');

    // Verificar dashboard administrativo cargado desde API real
    await expect(page.getByText('Panel Administrativo')).toBeVisible();

    // Navegar a Estructura y abrir Ficha Técnica de la primera CDP
    await page.goto('/app/estructura');
    await expect(page.getByText('Estructura Organizacional')).toBeVisible();
    await expect(page.getByText('Casa "HEB-001"')).toBeVisible();

    await page.getByRole('link', { name: /Gestionar/i }).first().click();
    await expect(page).toHaveURL(/\/app\/casa-de-paz\/\d+/);
    await expect(page.getByText(/Ficha Informativa · Casa de Paz/i)).toBeVisible();

    // Verificar que las mutaciones sin cabecera X-CSRFToken son bloqueadas con 400 (csrf_error)
    const noCsrfRes = await page.request.post('/api/redes', {
      data: { nombre: 'Red Sin CSRF' },
    });
    expect(noCsrfRes.status()).toBe(400);
    const noCsrfJson = await noCsrfRes.json();
    expect(noCsrfJson.code).toBe('csrf_error');

    // Cerrar sesión y validar limpieza de sesión en backend (/api/auth/me)
    const logoutBtn = page.getByRole('button', { name: /Cerrar Sesión/i }).first();
    await Promise.all([
      page.waitForResponse((res) => res.url().includes('/api/auth/logout') && res.status() === 200),
      logoutBtn.click(),
    ]);
    await expect(page).toHaveURL(/\/app\/login/);

    const meRes = await page.request.get('/api/auth/me');
    const meJson = await meRes.json();
    expect(meJson.authenticated).toBe(false);
  });

  test('2. Líder CDP: Inicio de sesión, vista de dashboard y envío de nuevo reporte', async ({ page }) => {
    await loginViaSpa(page, 'lider', 'lider');

    await expect(page.getByText(/Mis Reportes/i)).toBeVisible();

    // Ir a Generar Reporte (fecha es readonly prellenada automáticamente con el día actual)
    await page.goto('/app/generar-reporte');
    await expect(page.getByRole('heading', { name: /Generar Reporte/i })).toBeVisible();

    await expect(page.locator('input[name="fecha"]')).toHaveValue(/^\d{4}-\d{2}-\d{2}$/);
    await page.locator('input[name="hr_inicio"]').fill('19:00');
    await page.locator('input[name="hr_fin"]').fill('20:30');
    await page.locator('input[name="tema"]').fill('E2E Fe y Unidad');
    await page.locator('input[name="nro_regulares"]').fill('8');
    await page.locator('input[name="nro_ninos"]').fill('2');
    await page.locator('input[name="nro_visitas"]').fill('1');
    await page.locator('input[name="nro_comprometidos"]').fill('3');

    await Promise.all([
      page.waitForResponse((res) => res.url().includes('/api/reportes') && res.request().method() === 'POST' && res.status() === 201),
      page.getByRole('button', { name: /Enviar Reporte|Guardar Reporte/i }).click(),
    ]);

    await expect(page).toHaveURL(/\/app\/dashboard/);
  });

  test('3. Supervisor: Aislamiento territorial en UI (403 en /usuarios) y API Anti-IDOR (403 red ajena)', async ({ page }) => {
    await loginViaSpa(page, 'supervisor', 'supervisor');

    // En Estructura solo ve su red asignada y sin botones de creación admin
    await page.goto('/app/estructura');
    await expect(page.getByText('Estructura de mi Red')).toBeVisible();
    await expect(page.getByRole('button', { name: /Nueva Red/i })).toHaveCount(0);

    // Intento directo de acceso a /app/usuarios -> pantalla institucional 403
    await page.goto('/app/usuarios');
    await expect(page.getByText('403')).toBeVisible();
    await expect(page.getByText('Acceso denegado')).toBeVisible();

    // Verificación directa contra API con la misma cookie HttpOnly de sesión: red ajena (id=2) -> 403
    const redAjenaRes = await page.request.get('/api/redes/2');
    expect(redAjenaRes.status()).toBe(403);

    const casasAjenaRes = await page.request.get('/api/casas_de_paz?red_id=2');
    expect(casasAjenaRes.status()).toBe(403);

    const usuariosRes = await page.request.get('/api/usuarios');
    expect(usuariosRes.status()).toBe(403);
  });
});
