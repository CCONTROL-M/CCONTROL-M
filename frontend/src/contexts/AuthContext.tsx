import React, { createContext, useContext, useState, useEffect, ReactNode } from 'react';

// Tipo para o usuário
interface User {
  nome: string;
  email: string;
  id_empresa: string;
}

// Tipo para o contexto de autenticação
interface AuthContextType {
  user: User | null;
  isAuthenticated: boolean;
  loading: boolean;
  login: (token: string, userData: User) => void;
  logout: () => void;
}

// Usuário padrão para desenvolvimento
const defaultDevUser: User = {
  nome: 'Usuário de Desenvolvimento',
  email: 'dev@exemplo.com',
  id_empresa: '1'
};

// Criando o contexto com um valor padrão
const AuthContext = createContext<AuthContextType>({
  user: null,
  isAuthenticated: false,
  loading: true,
  login: () => {},
  logout: () => {}
});

// Hook personalizado para usar o contexto
export const useAuth = () => useContext(AuthContext);

// Props para o provedor de contexto
interface AuthProviderProps {
  children: ReactNode;
}

// Provedor de contexto
export const AuthProvider: React.FC<AuthProviderProps> = ({ children }) => {
  const [user, setUser] = useState<User | null>(null);
  const [loading, setLoading] = useState(true);

  // Verificar se o usuário está autenticado ao carregar a página
  useEffect(() => {
    const checkAuth = async () => {
      const token = localStorage.getItem('token');
      const storedUser = localStorage.getItem('user');
      
      try {
        if (token && storedUser) {
          // Em um sistema real, você deve validar o token com o backend
          const userData = JSON.parse(storedUser);
          setUser(userData);
        } else {
          // Para desenvolvimento, definir um usuário padrão automaticamente
          // Comentar esta linha se quiser que o login seja obrigatório
          setUser(defaultDevUser);
        }
      } catch (error) {
        console.error('Erro ao restaurar sessão:', error);
        localStorage.removeItem('token');
        localStorage.removeItem('user');
        // Em caso de erro, usar o usuário padrão de desenvolvimento
        setUser(defaultDevUser);
      } finally {
        setLoading(false);
      }
    };
    
    checkAuth();
  }, []);

  // Função para fazer login
  const login = (token: string, userData: User) => {
    localStorage.setItem('token', token);
    localStorage.setItem('user', JSON.stringify(userData));
    setUser(userData);
  };

  // Função para fazer logout
  const logout = () => {
    localStorage.removeItem('token');
    localStorage.removeItem('user');
    // Após logout, definir o usuário padrão de desenvolvimento
    setUser(defaultDevUser);
  };

  // Valor do contexto
  const value = {
    user,
    isAuthenticated: !!user,
    loading,
    login,
    logout
  };

  return (
    <AuthContext.Provider value={value}>
      {children}
    </AuthContext.Provider>
  );
}; 