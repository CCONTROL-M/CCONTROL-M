// Importações necessárias para configurar o ambiente de testes
import '@testing-library/jest-dom'; // Importa extensões de matchers para jest-dom (toBeInTheDocument, etc.)
import { afterEach, vi } from 'vitest';
import { cleanup } from '@testing-library/react';

// Limpa o DOM após cada teste
afterEach(() => {
  cleanup();
  vi.resetAllMocks();
});

// Mock do localStorage
const localStorageMock = (() => {
  let store: Record<string, string> = {};
  return {
    getItem: vi.fn((key: string) => store[key] || null),
    setItem: vi.fn((key: string, value: string) => {
      store[key] = value.toString();
    }),
    removeItem: vi.fn((key: string) => {
      delete store[key];
    }),
    clear: vi.fn(() => {
      store = {};
    }),
    length: Object.keys(store).length,
    key: vi.fn((index: number) => Object.keys(store)[index] || null),
  };
})();

// Mock da fetch API
global.fetch = vi.fn();

// Configuração do DOM virtual
Object.defineProperty(window, 'localStorage', { value: localStorageMock });
Object.defineProperty(window, 'sessionStorage', { value: localStorageMock });

// Mock de mensagens de console para não poluir os logs de teste
global.console = {
  ...console,
  // Manter o log original durante testes
  log: vi.fn(console.log),
  error: vi.fn(console.error),
  warn: vi.fn(console.warn),
  info: vi.fn(console.info),
};

// Mock para evitar erros com matchMedia
Object.defineProperty(window, 'matchMedia', {
  writable: true,
  value: vi.fn().mockImplementation(query => ({
    matches: false,
    media: query,
    onchange: null,
    addListener: vi.fn(),
    removeListener: vi.fn(),
    addEventListener: vi.fn(),
    removeEventListener: vi.fn(),
    dispatchEvent: vi.fn(),
  })),
});

// Configuração para testes da URL
Object.defineProperty(window, 'location', {
  writable: true,
  value: {
    href: 'http://localhost:3000/',
    pathname: '/',
    search: '',
    hash: '',
    origin: 'http://localhost:3000',
    host: 'localhost:3000',
    hostname: 'localhost',
    port: '3000',
    protocol: 'http:',
    assign: vi.fn(),
    replace: vi.fn(),
    reload: vi.fn(),
  },
}); 