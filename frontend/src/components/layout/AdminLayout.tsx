import React from 'react';
import { Outlet } from 'react-router-dom';
import { Sidebar } from './Sidebar';
import { Header } from './Header';
import { MobileHeader, MobileBottomNav } from './MobileHeader';

export const AdminLayout: React.FC = () => {
  return (
    <div className="min-h-screen flex bg-surface dark:bg-neutral-900 text-text-main dark:text-neutral-100 transition-colors duration-200">
      {/* Desktop Sidebar */}
      <Sidebar />

      {/* Main Content Area */}
      <div className="flex-1 flex flex-col min-w-0 pb-16 md:pb-0">
        <MobileHeader />
        <Header />

        <main className="flex-1 p-4 sm:p-6 md:p-8 max-w-7xl w-full mx-auto">
          <Outlet />
        </main>

        <MobileBottomNav />
      </div>
    </div>
  );
};

