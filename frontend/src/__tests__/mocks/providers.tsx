import React, { ReactNode } from 'react';
import { LoadingProvider } from '../../contexts/LoadingContext';
import { ApiStatusProvider } from '../../contexts/ApiStatusContext';
import { ToastProvider } from '../../hooks/useToast';
import { MemoryRouter } from 'react-router-dom';

// Mock do ConfirmDialog provider
export const ConfirmDialogProviderMock = ({ children }: { children: ReactNode }) => {
  // Aqui seria implementado um mock completo do ConfirmDialogProvider
  // mas como não temos acesso ao código original, deixamos apenas um wrapper vazio
  return <>{children}</>;
};

// Provider para testes que inclui todos os providers necessários
export const TestProviders = ({ children, initialRoute = '/' }: { children: ReactNode, initialRoute?: string }) => {
  return (
    <MemoryRouter initialEntries={[initialRoute]}>
      <LoadingProvider>
        <ApiStatusProvider>
          <ToastProvider>
            <ConfirmDialogProviderMock>
              {children}
            </ConfirmDialogProviderMock>
          </ToastProvider>
        </ApiStatusProvider>
      </LoadingProvider>
    </MemoryRouter>
  );
};

// Função para renderizar componentes com todos os providers necessários
export const renderWithProviders = (ui: React.ReactElement, options = {}) => {
  return (
    <TestProviders>
      {ui}
    </TestProviders>
  );
}; 