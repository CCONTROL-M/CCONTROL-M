import React, { createContext, useContext, ReactNode } from 'react';

// Tipo para o usuário
interface User {
  nome: string;
  email: string;
  id_empresa: string;
}

// Tipo para o contexto de autenticação
interface AuthContextType {
  user: User;
  isAuthenticated: boolean;
}

// Usuário padrão fixo
const defaultUser: User = {
  nome: 'Usuário de Desenvolvimento',
  email: 'dev@exemplo.com',
  id_empresa: '1'
};

// Criando o contexto com um valor padrão
const AuthContext = createContext<AuthContextType>({
  user: defaultUser,
  isAuthenticated: true
});

// Hook personalizado para usar o contexto
export const useAuth = () => useContext(AuthContext);

// Props para o provedor de contexto
interface AuthProviderProps {
  children: ReactNode;
}

// Provedor de contexto simplificado
export const AuthProvider: React.FC<AuthProviderProps> = ({ children }) => {
  // Valor fixo do contexto
  const value = {
    user: defaultUser,
    isAuthenticated: true
  };

  return (
    <AuthContext.Provider value={value}>
      {children}
    </AuthContext.Provider>
  );
}; 