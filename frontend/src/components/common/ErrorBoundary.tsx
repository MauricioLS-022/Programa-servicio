import { Component, type ErrorInfo, type ReactNode } from 'react';
import { Icon } from '../ui/Icon';
import '../../styles/errors.css';

interface Props {
  children: ReactNode;
  fallback?: ReactNode;
}

interface State {
  hasError: boolean;
  error: Error | null;
}

export class ErrorBoundary extends Component<Props, State> {
  public state: State = {
    hasError: false,
    error: null,
  };

  public static getDerivedStateFromError(error: Error): State {
    return { hasError: true, error };
  }

  public componentDidCatch(error: Error, errorInfo: ErrorInfo) {
    console.error('[ErrorBoundary] Error capturado en renderizado:', error, errorInfo);
  }

  private handleReset = () => {
    this.setState({ hasError: false, error: null });
  };

  private handleReload = () => {
    window.location.reload();
  };

  public render() {
    if (this.state.hasError) {
      if (this.props.fallback) {
        return this.props.fallback;
      }

      const isChunkError =
        this.state.error?.name === 'ChunkLoadError' ||
        Boolean(
          this.state.error?.message &&
            (this.state.error.message.includes('Failed to fetch dynamically imported module') ||
              this.state.error.message.includes('error loading dynamically imported module') ||
              this.state.error.message.includes('Loading chunk') ||
              this.state.error.message.includes('Failed to load module script'))
        );

      const title = isChunkError ? 'Actualización o desconexión detectada' : 'Error en el servidor';
      const description = isChunkError
        ? 'No se pudieron descargar los componentes de esta sección debido a una interrupción de red o una versión actualizada del sistema.'
        : 'Ocurrió un error inesperado al procesar la solicitud. Nuestro equipo ha registrado el incidente.';

      return (
        <main className="error-page-wrapper">
          <div className="error-card-canon">
            {/* Código 500 / Alerta Gigante con gradiente institucional */}
            <div className="error-code-canon code-500" aria-hidden="true">
              {isChunkError ? 'SYNC' : '500'}
            </div>

            <div className="error-content-canon">
              <h1 className="error-title-canon">{title}</h1>
              <p className="error-message-canon">{description}</p>

              {this.state.error?.message && (
                <div className="w-full bg-[#fff0f0] dark:bg-[#150f10] border border-border-subtle dark:border-[#382628] rounded-lg p-2.5 text-left mb-5 overflow-hidden">
                  <p className="text-xs font-mono text-text-muted dark:text-[#d4c2bf] truncate">
                    {this.state.error.message}
                  </p>
                </div>
              )}

              <div className="error-actions-canon">
                {isChunkError ? (
                  <button
                    type="button"
                    onClick={this.handleReload}
                    className="btn-error-canon btn-error-primary"
                  >
                    <Icon name="sync" size={20} aria-hidden="true" />
                    Actualizar Aplicación
                  </button>
                ) : (
                  <>
                    <button
                      type="button"
                      onClick={this.handleReset}
                      className="btn-error-canon btn-error-primary"
                    >
                      <Icon name="restart_alt" size={20} aria-hidden="true" />
                      Reintentar
                    </button>
                    <button
                      type="button"
                      onClick={this.handleReload}
                      className="btn-error-canon btn-error-secondary"
                    >
                      <Icon name="sync" size={20} aria-hidden="true" />
                      Recargar página
                    </button>
                  </>
                )}
              </div>
            </div>

            {/* Orbes circulares animados de fondo */}
            <div className="error-decorations" aria-hidden="true">
              <div className="decoration-circle" />
              <div className="decoration-circle" />
              <div className="decoration-circle" />
            </div>
          </div>

          <p className="error-footer-canon">
            Vino Nuevo — Servicio Comunitario
          </p>
        </main>
      );
    }

    return this.props.children;
  }
}
