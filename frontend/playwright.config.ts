import path from 'node:path';
import fs from 'node:fs';
import { fileURLToPath } from 'node:url';
import { defineConfig, devices } from '@playwright/test';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);
const repoRoot = path.resolve(__dirname, '..');
const winVenvPython = path.join(repoRoot, 'venv', 'Scripts', 'python.exe');
const unixVenvPython = path.join(repoRoot, 'venv', 'bin', 'python');
const pythonBin = fs.existsSync(winVenvPython)
  ? `"${winVenvPython}"`
  : fs.existsSync(unixVenvPython)
    ? `"${unixVenvPython}"`
    : 'python';

const E2E_PORT = 5055;
const E2E_BASE_URL = `http://127.0.0.1:${E2E_PORT}`;

export default defineConfig({
  testDir: './e2e',
  fullyParallel: false,
  workers: 1,
  retries: 0,
  timeout: 45_000,
  expect: {
    timeout: 10_000,
  },
  reporter: [['list']],
  use: {
    baseURL: E2E_BASE_URL,
    headless: true,
    trace: 'retain-on-failure',
  },
  projects: [
    {
      name: 'chromium',
      use: { ...devices['Desktop Chrome'] },
    },
  ],
  webServer: {
    command: `${pythonBin} -c "import sys; sys.path.insert(0, 'backend'); from app import app; app.config['MOCK_MODE']=True; app.run(host='127.0.0.1', port=${E2E_PORT}, debug=False, use_reloader=False)"`,
    cwd: repoRoot,
    url: `${E2E_BASE_URL}/api/health`,
    reuseExistingServer: !process.env.CI,
    timeout: 30_000,
    env: {
      ...process.env,
      FLASK_ENV: 'development',
      MOCK_MODE: 'True',
      DEBUG: 'False',
      APP_HOST: '127.0.0.1',
      APP_PORT: String(E2E_PORT),
      RECAPTCHA_SITE_KEY: '',
      RECAPTCHA_SECRET_KEY: '',
    },
  },
});
