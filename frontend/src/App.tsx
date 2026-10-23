import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { ThemeProvider } from './context/ThemeContext';
import { ToastProvider } from './context/ToastContext';
import { ProtectedRoute } from './components/layout/ProtectedRoute';
import { AppLayout } from './components/layout/AppLayout';

// Vistas
import { LoginPage } from './pages/LoginPage';
import { DashboardPage } from './pages/DashboardPage';
import { ReportesPage } from './pages/ReportesPage';
import { GenerarReportePage } from './pages/GenerarReportePage';
import { EstructuraPage } from './pages/EstructuraPage';

const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      refetchOnWindowFocus: false,
      retry: 1,
      staleTime: 1000 * 60 * 2, // 2 minutos
    },
  },
});

const basename = typeof window !== 'undefined' && window.location.pathname.startsWith('/app') ? '/app' : '/';

function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <ThemeProvider>
        <ToastProvider>
          <BrowserRouter basename={basename}>
            <Routes>
              {/* Ruta pública */}
              <Route path="/login" element={<LoginPage />} />

              {/* Rutas protegidas bajo el Layout Ministerial */}
              <Route
                path="/"
                element={
                  <ProtectedRoute>
                    <AppLayout />
                  </ProtectedRoute>
                }
              >
                <Route index element={<Navigate to="/dashboard" replace />} />
                <Route path="dashboard" element={<DashboardPage />} />
                <Route path="reportes" element={<ReportesPage />} />
                <Route
                  path="generar-reporte"
                  element={
                    <ProtectedRoute allowedRoles={['lider_cdp', 'admin']}>
                      <GenerarReportePage />
                    </ProtectedRoute>
                  }
                />
                <Route
                  path="estructura"
                  element={
                    <ProtectedRoute allowedRoles={['admin', 'supervisor']}>
                      <EstructuraPage />
                    </ProtectedRoute>
                  }
                />
              </Route>

              {/* Redirección por defecto */}
              <Route path="*" element={<Navigate to="/dashboard" replace />} />
            </Routes>
          </BrowserRouter>
        </ToastProvider>
      </ThemeProvider>
    </QueryClientProvider>
  );
}

export default App;
