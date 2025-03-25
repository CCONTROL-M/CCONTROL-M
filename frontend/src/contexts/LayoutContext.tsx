import React, { createContext, useContext, ReactNode } from 'react';

interface LayoutContextType {
  // Adicione aqui os estados e funções necessários para o layout
  // Por enquanto, deixaremos vazio
}

const LayoutContext = createContext<LayoutContextType>({});

export const useLayout = () => useContext(LayoutContext);

interface LayoutProviderProps {
  children: ReactNode;
}

export const LayoutProvider: React.FC<LayoutProviderProps> = ({ children }) => {
  const value = {};

  return (
    <LayoutContext.Provider value={value}>
      {children}
    </LayoutContext.Provider>
  );
}; 