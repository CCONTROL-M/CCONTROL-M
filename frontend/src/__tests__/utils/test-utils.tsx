import React, { ReactElement } from 'react';
import { render, RenderOptions } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { TestProviders } from '../mocks/providers';
import { vi } from 'vitest';

// Função utilitária para renderizar componentes com todos os providers necessários
export const renderWithProviders = (
  ui: ReactElement,
  options?: Omit<RenderOptions, 'wrapper'> & { route?: string }
) => {
  const { route = '/', ...renderOptions } = options || {};
  
  return {
    user: userEvent.setup(),
    ...render(ui, {
      wrapper: ({ children }) => (
        <TestProviders initialRoute={route}>
          {children}
        </TestProviders>
      ),
      ...renderOptions,
    }),
  };
};

// Mock para fetch
// Esta função deve ser usada dentro de testes específicos
export const mockFetch = (mockData: any, status = 200) => {
  return vi.spyOn(global, 'fetch').mockImplementation(() => 
    Promise.resolve({
      status,
      json: () => Promise.resolve(mockData),
      ok: status >= 200 && status < 300,
      headers: new Headers(),
      statusText: status === 200 ? 'OK' : 'Error',
      text: () => Promise.resolve(JSON.stringify(mockData)),
    } as Response)
  );
};

// Reset de todos os mocks
export const resetMocks = () => {
  vi.resetAllMocks();
}; 