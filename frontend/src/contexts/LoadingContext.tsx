import React, { createContext, useState, useContext, ReactNode } from 'react';
import LoadingOverlay from '../components/LoadingOverlay';

// Interface para o contexto de carregamento
interface LoadingContextType {
  isLoading: boolean;
  setLoading: (loading: boolean) => void;
}

// Criação do contexto
const LoadingContext = createContext<LoadingContextType | undefined>(undefined);

// Hook personalizado para usar o contexto
export const useLoading = (): LoadingContextType => {
  const context = useContext(LoadingContext);
  
  if (!context) {
    throw new Error('useLoading deve ser usado dentro de um LoadingProvider');
  }
  
  return context;
};

// Interface para as props do provider
interface LoadingProviderProps {
  children: ReactNode;
}

// Componente Provider
export const LoadingProvider: React.FC<LoadingProviderProps> = ({ children }) => {
  const [isLoading, setIsLoading] = useState<boolean>(false);
  
  // Função para controlar o estado de carregamento
  const setLoading = (loading: boolean) => {
    setIsLoading(loading);
  };
  
  // Valor do contexto
  const value: LoadingContextType = {
    isLoading,
    setLoading
  };
  
  return (
    <LoadingContext.Provider value={value}>
      {children}
      <LoadingOverlay visible={isLoading} />
    </LoadingContext.Provider>
  );
}; 