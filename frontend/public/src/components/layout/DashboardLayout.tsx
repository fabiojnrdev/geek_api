import React from 'react';
import { Outlet } from 'react-router-dom';
import { Sidebar } from './Sidebar';
 
export const DashboardLayout: React.FC = () => (
  <div className="min-h-screen bg-zinc-950 text-zinc-100">
    <Sidebar />
    <main className="ml-64 min-h-screen">
      <div className="p-8">
        <Outlet />
      </div>
    </main>
  </div>
);