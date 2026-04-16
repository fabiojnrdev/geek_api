import React from 'react';
import { Navigate } from 'react-router-dom';
import { LoginPage } from './src/pages/LoginPage';
import { RegisterPage } from './src/pages/RegisterPage';
import { DashboardLayout } from './src/components/layout/DashboardLayout';
import { ProtectedRoute } from './src/components/auth/ProtectedRoute';
import { DashboardPage } from './src/pages/DashboardPage';
import { ProductsPage } from './src/pages/ProductsPage';
import { CategoriesPage } from './src/pages/CategoriesPage';
import { ProfilePage } from './src/pages/ProfilePage';

export const routes = [
  { path: '/login', element: <LoginPage /> },
  { path: '/register', element: <RegisterPage /> },
  {
    element: <ProtectedRoute />,
    children: [
      {
        element: <DashboardLayout />,
        children: [
          { path: '/dashboard', element: <DashboardPage /> },
          { path: '/dashboard/products', element: <ProductsPage /> },
          { path: '/dashboard/categories', element: <CategoriesPage /> },
          { path: '/dashboard/profile', element: <ProfilePage /> },
        ],
      },
    ],
  },
  { path: '/', element: <Navigate to="/dashboard" replace /> },
  { path: '*', element: <Navigate to="/" replace /> },
];
