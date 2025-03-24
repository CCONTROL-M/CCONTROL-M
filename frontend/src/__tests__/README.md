# Estrutura de Testes do CCONTROL-M Frontend

Este documento descreve a configuração de testes automatizados para o frontend do CCONTROL-M.

## Tecnologias

- **Vitest**: Executor de testes rápido e moderno compatível com Vite
- **React Testing Library**: Biblioteca para testes centrados no usuário
- **jsdom**: Implementação JavaScript de DOM e HTML para simular o navegador

## Estrutura de Diretórios

Os testes seguem duas convenções:

1. **Testes centralizados**: Em `src/__tests__/`
2. **Testes junto aos componentes**: Em `src/components/__tests__/` (e outras pastas)

## Configuração

- **setupTests.ts**: Configuração global dos testes
- **utils/test-utils.tsx**: Utilitários para renderizar componentes com providers
- **mocks/providers.tsx**: Mocks dos providers globais

## Executando os Testes

### Comandos Disponíveis

- **Executar todos os testes uma vez**:
  ```
  npm run test
  ```

- **Executar testes em modo watch** (recomendado durante desenvolvimento):
  ```
  npm run test:watch
  ```

- **Executar testes com cobertura**:
  ```
  npm run test:coverage
  ```

## Boas Práticas

1. **Organização**:
   - Nomes dos arquivos de teste: `[Component].test.tsx` ou `[Feature].test.tsx`
   - Agrupar testes com `describe` para organizar logicamente
   - Usar nomes descritivos para os casos de teste (`it` ou `test`)

2. **Estrutura dos Testes**:
   - Seguir o padrão AAA (Arrange, Act, Assert)
   - Testar comportamentos, não implementação
   - Focar em testar a interação do usuário

3. **Mocks**:
   - Usar `vi.mock()` para mockar módulos externos
   - Usar `vi.fn()` para funções de mock
   - Usar `mockFetch()` do test-utils para mockar chamadas de API

4. **Assertions**:
   - Usar matchers do `@testing-library/jest-dom` para verificações relacionadas ao DOM
   - Preferir `getByRole` e outras queries semânticas ao invés de seletores por classe ou id

## Exemplo

```tsx
import { describe, it, expect } from 'vitest';
import { screen } from '@testing-library/react';
import { renderWithProviders } from '../utils/test-utils';
import MeuComponente from '../MeuComponente';

describe('MeuComponente', () => {
  it('deve renderizar corretamente', () => {
    // Arrange (preparação)
    renderWithProviders(<MeuComponente />);
    
    // Act (ação) - se necessário
    // userEvent.click(screen.getByRole('button'));
    
    // Assert (verificação)
    expect(screen.getByText('Texto esperado')).toBeInTheDocument();
  });
});
```

## Troubleshooting

- **Problemas de DOM**: Verifique se setupTests.ts está configurado corretamente
- **Erros de contexto**: Certifique-se de usar `renderWithProviders` para componentes que dependem de contextos
- **Falsos positivos**: Use `cleanup` após cada teste (já incluído em setupTests.ts) 