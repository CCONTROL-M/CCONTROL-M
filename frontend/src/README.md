# CCONTROL-M Frontend

Frontend da aplicação CCONTROL-M, desenvolvido com React e TypeScript.

## Índice

- [CCONTROL-M Frontend](#ccontrol-m-frontend)
  - [Índice](#índice)
  - [Visão Geral](#visão-geral)
  - [Funcionalidades](#funcionalidades)
  - [Tecnologias](#tecnologias)
  - [Inicialização](#inicialização)
  - [Estrutura do Projeto](#estrutura-do-projeto)
  - [Modo Mock](#modo-mock)
  - [Componentes Principais](#componentes-principais)
  - [Serviços](#serviços)
  - [Contribuição](#contribuição)

## Visão Geral

CCONTROL-M é um sistema de controle financeiro para pequenas e médias empresas, permitindo o gerenciamento de clientes, fornecedores, vendas, contas a pagar e receber, e transferências entre contas.

## Funcionalidades

- Dashboard com visão geral financeira
- Gestão de clientes e fornecedores
- Controle de vendas e parcelas
- Contas a pagar e receber
- Transferências entre contas
- Gestão de usuários e permissões
- Configurações do sistema

## Tecnologias

- React 18
- TypeScript
- Tailwind CSS
- React Router
- Axios para requisições HTTP
- React Query para gerenciamento de estado remoto
- Vite como bundler

## Inicialização

```bash
# Instalar dependências
npm install

# Iniciar em modo de desenvolvimento
npm run dev

# Construir para produção
npm run build

# Visualizar build de produção localmente
npm run preview
```

## Estrutura do Projeto

```
frontend/
├── public/         # Arquivos estáticos
├── src/
│   ├── components/ # Componentes reutilizáveis
│   ├── contexts/   # Contextos React
│   ├── hooks/      # Hooks personalizados
│   ├── pages/      # Componentes de página
│   ├── services/   # Serviços de API
│   ├── types/      # Definições de tipos
│   ├── utils/      # Funções utilitárias
│   ├── App.tsx     # Componente principal da aplicação
│   └── main.tsx    # Ponto de entrada da aplicação
├── index.html      # Template HTML
└── vite.config.ts  # Configuração do Vite
```

## Modo Mock

O sistema possui um modo mock para facilitar o desenvolvimento e testes quando se deseja testar cenários específicos sem modificar dados reais. **Este modo é destinado apenas para desenvolvimento e testes, não para uso em produção.**

### Como Ativar o Modo Mock

Existem duas maneiras de ativar o modo mock:

1. **Toggle na Interface (Apenas em Desenvolvimento)**: Um ícone de mock está disponível no canto inferior direito da aplicação **apenas em ambiente de desenvolvimento**, permitindo alternar entre o modo real e o mock.

2. **Variável de Ambiente**: Configure `VITE_MOCK_ENABLED=true` em seu arquivo `.env.local` para desenvolvimento local.

> **Importante**: O modo mock não é mais ativado automaticamente quando a API está offline. O sistema permanecerá no modo real mesmo em caso de erros de conectividade.

### Serviços com Suporte a Mock

Os seguintes serviços possuem implementação de mock:

- Clientes
- Fornecedores
- Vendas
- Parcelas
- Lançamentos
- Transferências entre contas
- Usuários

### Desenvolvimento com Mocks

Para criar um novo serviço mock:

1. Crie um arquivo `nomeDoServicoMock.ts` na pasta `src/services/`
2. Implemente os métodos mock necessários (listar, buscar, cadastrar, etc.)
3. Integre o mock no serviço real, verificando o estado mock através da função `useMock()`

Exemplo de implementação:

```typescript
// Em serviceMock.ts
export async function listarDadosMock(): Promise<Dado[]> {
  return new Promise((resolve) => {
    setTimeout(() => {
      resolve([...dadosMock]);
    }, 500);
  });
}

// Em service.ts
import { useMock } from '../utils/mock';
import { listarDadosMock } from './serviceMock';

export async function listarDados(): Promise<Dado[]> {
  if (useMock()) {
    return listarDadosMock();
  }
  
  const response = await api.get('/dados');
  return response.data;
}
```

## Componentes Principais

- **Table**: Componente reutilizável para exibição de dados em formato tabular
- **DataStateHandler**: Gerencia estados de carregamento, erro e dados vazios
- **Form / FormField**: Componentes para criação de formulários com validação
- **ConfirmDialog**: Modal para confirmar ações destrutivas
- **ConnectivityStatus**: Exibe informações sobre conectividade com a API

## Serviços

Os serviços da aplicação são responsáveis pela comunicação com a API e implementam os métodos necessários para cada entidade do sistema:

- `api.ts`: Configuração base do Axios com interceptors para tratamento de erros e retry
- `clienteService.ts`: Gerenciamento de clientes
- `fornecedorService.ts`: Gerenciamento de fornecedores
- `vendaService.ts`: Gerenciamento de vendas
- `parcelaService.ts`: Gerenciamento de parcelas de vendas
- `lancamentoService.ts`: Gerenciamento de contas a pagar e receber
- `transferenciaService.ts`: Gerenciamento de transferências entre contas
- `usuarioService.ts`: Gerenciamento de usuários e autenticação

## Contribuição

1. Faça um fork do projeto
2. Crie uma branch para sua feature (`git checkout -b feature/nova-funcionalidade`)
3. Commit suas mudanças (`git commit -m 'Adiciona nova funcionalidade'`)
4. Push para a branch (`git push origin feature/nova-funcionalidade`)
5. Abra um Pull Request 