# Documentação Técnica - Testes Automatizados

Este documento descreve a estrutura, implementação e boas práticas dos testes automatizados do sistema CCONTROL-M.

## 🧪 1. Ferramentas de Teste Utilizadas

Para garantir a qualidade e robustez do código, utilizamos as seguintes ferramentas:

- **Vitest**: Framework de testes rápido e moderno, compatível com o ecossistema Vite
- **React Testing Library**: Biblioteca para testar componentes React de forma mais próxima à experiência do usuário
- **@testing-library/jest-dom**: Extensões de matchers customizados para Jest/Vitest
- **@testing-library/user-event**: Simulação de interações do usuário (cliques, digitação, etc.)
- **jsdom**: Ambiente de DOM virtual para execução de testes sem navegador
- **Mock Service Worker (MSW)**: Interceptação de requisições para testes de integração (para testes futuros)

## 📂 2. Estrutura de Pastas de Testes

A organização dos testes segue uma estrutura clara e intuitiva:

- Testes centralizados em:
  - `src/__tests__/` para testes de páginas
  - `src/components/__tests__/` para testes de componentes
  - `src/hooks/__tests__/` para testes de hooks customizados
  
- Arquivos nomeados no formato:
  - `.test.tsx` para componentes React
  - `.test.ts` para funções e utilitários

- Mocks e utilitários auxiliares:
  - `src/__tests__/mocks/` para mocks de serviços e componentes
  - `src/__tests__/utils/` para funções utilitárias de teste

## ⚙️ 3. Como Executar os Testes

Para executar os testes, utilize os seguintes comandos:

- **Testes unitários**:
  ```bash
  npm run test
  ```

- **Modo watch** (executa automaticamente quando os arquivos mudam):
  ```bash
  npm run test:watch
  ```

- **Cobertura** (gera relatório de cobertura de código):
  ```bash
  npm run test:coverage
  ```

## ✅ 4. Telas Cobertas por Testes Automatizados

| Tela / Página            | Status     | Tipos de Testes Cobertos                        |
|--------------------------|------------|--------------------------------------------------|
| Clientes                 | ✅ Completo | CRUD, validação, toasts, modais, confirmação     |
| DRE                      | ✅ Completo | API, filtros, loading, erros, exibição total     |
| Parcelas                 | ✅ Completo | Filtros, alteração de status, toasts, erros      |
| Transferências           | ✅ Completo | Validação entre contas, filtros, toast, erros    |
| Vendas e Parcelas        | ✅ Completo | Geração de parcelas, formulário, CRUD            |
| Modal                    | ✅ Completo | Abertura/fechamento, eventos de teclado, variações|
| useConfirmDialog         | ✅ Completo | Hook de confirmação, eventos, promises           |

## 🧠 5. Boas Práticas Documentadas

Nos testes implementados, seguimos estas boas práticas:

- **Testes isolados e específicos**: Cada teste verifica apenas uma funcionalidade
- **Mocks para serviços**: Simulamos chamadas de API com mocks
- **Reset de estado**: Utilizamos `beforeEach` e `afterEach` para garantir isolamento
- **Seletores semânticos**: Priorizamos o uso de `getByRole`, `getByLabelText` e outros seletores semânticos
- **Teste de feedback visual**: Verificamos se toasts de sucesso/erro são exibidos adequadamente
- **Tratamento de erros**: Cobrimos cenários de falha (API offline, validações, etc.)
- **Dados dinâmicos**: Testamos componentes com dados variados para garantir robustez
- **Testes assíncronos**: Utilizamos `waitFor` e `async/await` para tratar operações assíncronas
- **Prevenção de falhas**: Utilizamos `screen.debug()` para depurar quando necessário

Exemplo de teste seguindo boas práticas:

```typescript
it('deve validar campos obrigatórios no formulário', async () => {
  renderWithProviders(<VendasParcelas />);
  
  // Abrir o modal
  const botaoNovaVenda = screen.getByText('Nova Venda');
  await userEvent.click(botaoNovaVenda);
  
  // Tentar cadastrar sem preencher
  await waitFor(() => {
    const cadastrarButton = screen.getByText('Cadastrar Venda');
    userEvent.click(cadastrarButton);
  });
  
  // Verificar mensagens de erro
  await waitFor(() => {
    expect(screen.getByText('Selecione um cliente')).toBeInTheDocument();
    expect(screen.getByText('Informe um valor válido')).toBeInTheDocument();
    expect(screen.getByText('Descrição deve ter pelo menos 3 caracteres')).toBeInTheDocument();
  });
  
  // Verificar que o serviço não foi chamado
  expect(vendaService.cadastrarVenda).not.toHaveBeenCalled();
});
```

## 📌 6. Setup Global

O ambiente de testes é configurado globalmente através de:

- **`setupTests.ts`**: Define o ambiente de teste com:
  - Configuração do jsdom
  - Extensões do jest-dom
  - Configurações globais do Vitest

- **Providers de teste**: Implementados em `src/__tests__/mocks/providers.tsx`:
  - `TestProviders`: Encapsula todos os providers necessários
  - `ConfirmDialogProviderMock`: Mock do provider de diálogos de confirmação
  - `renderWithProviders`: Função helper para renderizar componentes com todos os providers

- **Utilitários de teste**: Implementados em `src/__tests__/utils/test-utils.tsx`:
  - `renderWithProviders`: Helper para renderizar com providers
  - `mockFetch`: Helper para simular chamadas fetch
  - `resetMocks`: Helper para reiniciar mocks

## 📈 7. Evolução futura recomendada

Para aprimorar a cobertura e qualidade dos testes, recomendamos:

- **Incluir testes para páginas pendentes**:
  - `Dashboard`
  - `Fluxo de Caixa`
  - `Inadimplência`
  - `Configurações`

- **Expandir tipos de testes**:
  - Implementar testes de integração (multi-componentes)
  - Adicionar testes de snapshot para componentes visuais
  - Adotar Cypress para testes end-to-end em produção

- **Melhorias de infraestrutura**:
  - Integrar testes em pipeline CI/CD
  - Implementar análise de cobertura automática
  - Configurar limites mínimos de cobertura

- **Documentação adicional**:
  - Adicionar exemplos de testes para novos contribuidores
  - Documentar padrões específicos para testes de componentes complexos 