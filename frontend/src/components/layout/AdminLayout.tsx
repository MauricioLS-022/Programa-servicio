import React from 'react';
import { AppLayout } from './AppLayout';

/**
 * @deprecated Utilizar `AppLayout` en su lugar. Mantenido por compatibilidad regresiva.
 */
export const AdminLayout: React.FC = () => {
  return <AppLayout />;
};

export default AdminLayout;
