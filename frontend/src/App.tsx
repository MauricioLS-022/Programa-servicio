import { lazy, Suspense } from 'react';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { ThemeProvider } from './context/ThemeContext';
import { ToastProvider } from './context/ToastContext';
import { ProtectedRoute } from './components/layout/ProtectedRoute';
import { AppLayout } from './components/layout/AppLayout';
import { ErrorBoundary } from './components/common/ErrorBoundary';
import { PageLoadingFallback } from './components/common/PageLoadingFallback';

// Vistas con carga perezosa (Code Splitting por ruta)
const LoginPage = lazy(() => import('./pages/LoginPage'));
const DashboardPage = lazy(() =>
  import('./pages/DashboardPage').then((m) => ({ default: m.DashboardPage }))
);
const ReportesPage = lazy(() =>
  import('./pages/ReportesPage').then((m) => ({ default: m.ReportesPage }))
);
const GenerarReportePage = lazy(() =>
  import('./pages/GenerarReportePage').then((m) => ({ default: m.GenerarReportePage }))
);
const EstructuraPage = lazy(() =>
  import('./pages/EstructuraPage').then((m) => ({ default: m.EstructuraPage }))
);
const DetallesCdpPage = lazy(() =>
  import('./pages/DetallesCdpPage').then((m) => ({ default: m.DetallesCdpPage }))
);
const UsuariosPage = lazy(() =>
  import('./pages/UsuariosPage').then((m) => ({ default: m.UsuariosPage }))
);
const LideresPage = lazy(() =>
  import('./pages/LideresPage').then((m) => ({ default: m.LideresPage }))
);
const PerfilPage = lazy(() =>
  import('./pages/PerfilPage').then((m) => ({ default: m.PerfilPage }))
);
const NotFoundPage = lazy(() =>
  import('./pages/NotFoundPage').then((m) => ({ default: m.NotFoundPage }))
);

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
    <ErrorBoundary>
      <QueryClientProvider client={queryClient}>
        <ThemeProvider>
          <ToastProvider>
            <BrowserRouter basename={basename}>
              <Suspense fallback={<PageLoadingFallback />}>
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
                    <Route
                      path="casa-de-paz/:id"
                      element={
                        <ProtectedRoute allowedRoles={['admin', 'supervisor']}>
                          <DetallesCdpPage />
                        </ProtectedRoute>
                      }
                    />
                    <Route
                      path="usuarios"
                      element={
                        <ProtectedRoute allowedRoles={['admin']}>
                          <UsuariosPage />
                        </ProtectedRoute>
                      }
                    />
                    <Route
                      path="lideres"
                      element={
                        <ProtectedRoute allowedRoles={['admin', 'supervisor']}>
                          <LideresPage />
                        </ProtectedRoute>
                      }
                    />
                    <Route path="perfil" element={<PerfilPage />} />
                  </Route>

                  {/* Página 404 No Encontrado */}
                  <Route path="*" element={<NotFoundPage />} />
                </Routes>
              </Suspense>
            </BrowserRouter>
          </ToastProvider>
        </ThemeProvider>
      </QueryClientProvider>
    </ErrorBoundary>
  );
}

export default App;
