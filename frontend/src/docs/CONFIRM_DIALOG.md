# Componente de Diálogo de Confirmação

Este documento descreve como utilizar o componente `ConfirmDialog` e o hook `useConfirmDialog` para implementar confirmações de ações destrutivas ou críticas no sistema.

## Visão Geral

O componente `ConfirmDialog` foi criado para substituir o uso de `window.confirm()` nativo, oferecendo uma experiência mais consistente e integrada com o design do sistema. Ele é especialmente útil para confirmar ações destrutivas, como exclusão de registros.

## Opções e Propriedades

O `ConfirmDialog` aceita as seguintes propriedades:

| Propriedade    | Tipo                      | Descrição                                           | Padrão       |
|----------------|---------------------------|-----------------------------------------------------|--------------|
| `isOpen`       | `boolean`                 | Controla se o diálogo está visível                  | (obrigatório)|
| `onClose`      | `() => void`              | Função chamada ao fechar/cancelar                   | (obrigatório)|
| `onConfirm`    | `() => void`              | Função chamada ao confirmar a ação                  | (obrigatório)|
| `title`        | `string`                  | Título do diálogo                                   | (obrigatório)|
| `description`  | `string`                  | Descrição da ação a ser confirmada                  | (obrigatório)|
| `confirmText`  | `string`                  | Texto do botão de confirmação                       | "Confirmar"  |
| `cancelText`   | `string`                  | Texto do botão de cancelamento                      | "Cancelar"   |
| `type`         | `'danger'/'warning'/'info'` | Tipo do diálogo (define cores e ícones)           | "danger"     |

## Hook useConfirmDialog

Para facilitar o uso do diálogo, criamos o hook `useConfirmDialog` que encapsula a lógica de estado e controle do componente. Ele retorna:

- `dialog`: objeto com o estado atual do diálogo
- `confirm`: função para abrir o diálogo com as opções desejadas
- `closeDialog`: função para fechar o diálogo

## Exemplos de Uso

### 1. Usando o hook useConfirmDialog (Recomendado)

```tsx
import { useConfirmDialog } from '../hooks/useConfirmDialog';
import ConfirmDialog from '../components/ConfirmDialog';

function MinhaComponente() {
  const { dialog, confirm, closeDialog } = useConfirmDialog();
  
  const handleExcluirClick = (item) => {
    confirm({
      title: "Confirmar Exclusão",
      description: `Tem certeza que deseja excluir "${item.nome}"?`,
      confirmText: "Excluir",
      type: "danger",
      onConfirm: () => excluirItem(item.id)
    });
  };
  
  const excluirItem = async (id) => {
    // Lógica para excluir o item
    try {
      await api.delete(`/items/${id}`);
      // Atualizar a lista de itens
    } catch (error) {
      // Tratar erro
    }
  };
  
  return (
    <div>
      {/* Seu componente aqui */}
      
      {/* Adicionar o ConfirmDialog ao final do componente */}
      <ConfirmDialog 
        isOpen={dialog.isOpen}
        onClose={closeDialog}
        onConfirm={dialog.onConfirm}
        title={dialog.title}
        description={dialog.description}
        confirmText={dialog.confirmText}
        cancelText={dialog.cancelText}
        type={dialog.type}
      />
    </div>
  );
}
```

### 2. Diretamente com o componente ConfirmDialog

```tsx
import { useState } from 'react';
import ConfirmDialog from '../components/ConfirmDialog';

function MinhaComponente() {
  const [isOpen, setIsOpen] = useState(false);
  const [itemParaExcluir, setItemParaExcluir] = useState(null);
  
  const handleExcluirClick = (item) => {
    setItemParaExcluir(item);
    setIsOpen(true);
  };
  
  const handleConfirmar = async () => {
    if (!itemParaExcluir) return;
    
    try {
      await api.delete(`/items/${itemParaExcluir.id}`);
      // Atualizar a lista de itens
    } catch (error) {
      // Tratar erro
    } finally {
      setItemParaExcluir(null);
      setIsOpen(false);
    }
  };
  
  const handleCancelar = () => {
    setItemParaExcluir(null);
    setIsOpen(false);
  };
  
  return (
    <div>
      {/* Seu componente aqui */}
      
      <ConfirmDialog 
        isOpen={isOpen}
        onClose={handleCancelar}
        onConfirm={handleConfirmar}
        title="Confirmar Exclusão"
        description={`Tem certeza que deseja excluir "${itemParaExcluir?.nome}"?`}
        confirmText="Excluir"
        type="danger"
      />
    </div>
  );
}
```

## Tipos de Diálogo

O componente suporta três tipos de diálogo, cada um com cores diferentes:

1. **danger** (padrão): Para ações destrutivas como exclusão
2. **warning**: Para ações que podem ter consequências importantes
3. **info**: Para confirmações informativas

## Boas Práticas

1. Use o diálogo para todas as ações destrutivas ou irreversíveis
2. Seja claro e específico na descrição da ação
3. Prefira o hook `useConfirmDialog` para simplificar o gerenciamento de estado
4. Sempre mencione o nome do item que será afetado na descrição
 