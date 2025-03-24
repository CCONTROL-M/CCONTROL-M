import React from 'react';
import { Navigate, Outlet, useLocation } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import LoadingOverlay from './LoadingOverlay';

/**
 * Componente para proteger rotas que exigem autenticação
 * Redireciona para a página de login se o usuário não estiver autenticado
 */
const ProtectedRoute: React.FC = () => {
  const { isAuthenticated, loading } = useAuth();
  const location = useLocation();

  // Exibir loading enquanto verifica autenticação
  if (loading) {
    return <LoadingOverlay visible={true} text="Verificando autenticação..." />;
  }

  // Redirecionar para login se não estiver autenticado
  if (!isAuthenticated) {
    return <Navigate to="/login" state={{ from: location }} replace />;
  }

  // Renderizar as rotas filhas se estiver autenticado
  return <Outlet />;
};

export default ProtectedRoute; 