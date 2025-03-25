import React from 'react';
import { Outlet, useLocation } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';

/**
 * Componente para proteção de rotas - modificado para não redirecionar
 * Sempre permite acesso às rotas, independente do estado de autenticação
 */
const ProtectedRoute: React.FC = () => {
  const { isAuthenticated } = useAuth();
  const location = useLocation();

  // Sempre permitir acesso, sem redirecionamento
  return <Outlet />;
};

export default ProtectedRoute; 