import React, { useState } from 'react';
import { Outlet } from 'react-router-dom';
import { DesktopHeader } from './DesktopHeader';
import { MobileHeader } from './MobileHeader';
import { MobileSidebar } from './MobileSidebar';
import { MobileBottomNav } from './MobileBottomNav';
import '../../styles/layout.css';

export const AppLayout: React.FC = () => {
  const [sidebarOpen, setSidebarOpen] = useState(false);

  return (
    <div className="app-layout-wrapper">
      {/* 1. Barra de navegación horizontal de escritorio (> 1024px) */}
      <DesktopHeader />

      {/* 2. Cabecera fija superior móvil (<= 1024px) */}
      <MobileHeader onToggleMenu={() => setSidebarOpen(true)} />

      {/* 3. Menú lateral desplegable off-canvas móvil con overlay (<= 1024px) */}
      <MobileSidebar isOpen={sidebarOpen} onClose={() => setSidebarOpen(false)} />

      {/* 4. Área de contenido principal */}
      <main className="app-main-content" id="main-content">
        <Outlet />
      </main>

      {/* 5. Barra fija inferior táctil móvil (<= 1024px) */}
      <MobileBottomNav />
    </div>
  );
};

export default AppLayout;

