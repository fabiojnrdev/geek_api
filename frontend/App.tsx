import React, { useEffect } from 'react';
import { useRoutes } from 'react-router-dom';
import { useAuthStore } from './src/store/authStore';
import { routes } from './routes';

const App: React.FC = () => {
  const { isAuthenticated, fetchMe } = useAuthStore();

  useEffect(() => {
    if (isAuthenticated) fetchMe();
  }, []);

  return useRoutes(routes); 
};

export default App;
