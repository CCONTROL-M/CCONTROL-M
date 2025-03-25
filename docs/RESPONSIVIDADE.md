# Guia de Responsividade - CCONTROL-M

Este documento fornece instruções sobre como utilizar os componentes responsivos do CCONTROL-M para garantir que a aplicação funcione bem em dispositivos móveis e tablets.

## Breakpoints

Os seguintes breakpoints são definidos no sistema:

- `--breakpoint-xs: 480px` - Dispositivos móveis pequenos
- `--breakpoint-sm: 576px` - Dispositivos móveis
- `--breakpoint-md: 768px` - Tablets
- `--breakpoint-lg: 992px` - Desktops pequenos
- `--breakpoint-xl: 1200px` - Desktops grandes

## Componentes Responsivos

### Form

O componente `Form` permite criar formulários responsivos com diferentes layouts.

```tsx
import Form from '../components/Form';
import ButtonGroup from '../components/ButtonGroup';
import Button from '../components/Button';

const actions = (
  <ButtonGroup orientation="responsive" alignment="end">
    <Button variant="secondary" onClick={handleCancel}>Cancelar</Button>
    <Button variant="primary" type="submit">Salvar</Button>
  </ButtonGroup>
);

return (
  <Form 
    onSubmit={handleSubmit} 
    layout="column" 
    gap="md" 
    actions={actions}
    actionPosition="end"
  >
    {/* Campos do formulário */}
  </Form>
);
```

#### Propriedades do Form:

- `layout`: 'column' | 'row' | 'grid' - Define o layout do formulário
- `gap`: 'sm' | 'md' | 'lg' - Define o espaçamento entre os campos
- `actions`: ReactNode - Botões de ação do formulário
- `actionPosition`: 'start' | 'end' | 'center' | 'stretch' - Alinhamento dos botões

### FormField

O componente `FormField` cria campos de formulário que se adaptam aos diferentes tamanhos de tela.

```tsx
import FormField from '../components/FormField';

<FormField
  label="Nome"
  name="nome"
  value={nome}
  onChange={handleChange}
  error={errors.nome}
  required
  width="half"
/>
```

#### Propriedades do FormField:

- `width`: 'full' | 'half' | 'third' | 'auto' - Define a largura do campo
- Em telas menores que 768px, todos os campos ocupam 100% da largura

### ButtonGroup

O componente `ButtonGroup` agrupa botões e os organiza verticalmente em dispositivos móveis.

```tsx
import ButtonGroup from '../components/ButtonGroup';

<ButtonGroup orientation="responsive" alignment="end" spacing="md">
  <Button variant="secondary" onClick={handleCancel}>Cancelar</Button>
  <Button variant="primary" onClick={handleSave}>Salvar</Button>
</ButtonGroup>
```

#### Propriedades do ButtonGroup:

- `orientation`: 'horizontal' | 'vertical' | 'responsive' - Orientação dos botões
- `spacing`: 'sm' | 'md' | 'lg' - Espaçamento entre os botões
- `alignment`: 'start' | 'center' | 'end' | 'stretch' - Alinhamento dos botões

### Button

O componente `Button` fornece botões padronizados e responsivos.

```tsx
import Button from '../components/Button';

<Button 
  variant="primary" 
  size="md" 
  loading={isLoading}
  onClick={handleClick}
>
  Confirmar
</Button>
```

#### Propriedades do Button:

- `variant`: 'primary' | 'secondary' | 'danger' | 'warning' | 'success'
- `size`: 'sm' | 'md' | 'lg'
- `fullWidth`: boolean - Ocupa 100% da largura disponível
- `loading`: boolean - Exibe um spinner durante carregamento
- `icon`: ReactNode - Ícone do botão
- `iconPosition`: 'left' | 'right' - Posição do ícone

### Table

O componente `Table` permite criar tabelas responsivas que se adaptam a diferentes tamanhos de tela.

```tsx
import Table from '../components/Table';

const columns = [
  { 
    key: 'nome', 
    label: 'Nome', 
    responsive: true // Sempre visível
  },
  { 
    key: 'email', 
    label: 'E-mail', 
    responsive: 'md' // Visível em tablets e acima
  },
  { 
    key: 'telefone', 
    label: 'Telefone', 
    responsive: 'lg' // Visível apenas em desktops
  }
];

<Table 
  columns={columns} 
  data={data} 
  responsive={true}
  maxWidth="100%"
/>
```

#### Responsividade de Colunas:

- `responsive: true` - Sempre visível
- `responsive: 'sm'` - Visível em telas >= 576px
- `responsive: 'md'` - Visível em telas >= 768px
- `responsive: 'lg'` - Visível em telas >= 992px
- `responsive: 'xl'` - Visível em telas >= 1200px

### Modal

O componente `Modal` possui modos especiais para dispositivos móveis.

```tsx
import Modal from '../components/Modal';

<Modal 
  isOpen={isOpen} 
  onClose={onClose} 
  title="Detalhes"
  size="md"
  fullScreenOnMobile={true}
  position="bottom"
>
  {/* Conteúdo do modal */}
</Modal>
```

#### Propriedades Responsivas do Modal:

- `fullScreenOnMobile`: boolean - Quando true, ocupa toda a tela em dispositivos móveis
- `position`: 'center' | 'bottom' - Posicionamento do modal

## Classes CSS Utilitárias

### Visibilidade Responsiva

- `.hide-on-mobile` - Oculta em telas menores que 576px
- `.hide-on-sm` - Oculta em telas menores que 768px
- `.hide-on-md` - Oculta em telas menores que 992px
- `.hide-on-lg` - Oculta em telas menores que 1200px
- `.hide-on-xl` - Oculta em telas maiores que 1200px

## Boas Práticas

1. **Mobile First**: Sempre projete pensando primeiro em dispositivos móveis
2. **Teste em Múltiplos Dispositivos**: Verifique o comportamento em diferentes tamanhos de tela
3. **Use Tamanhos Relativos**: Prefira unidades relativas (%, rem, em) em vez de pixels fixos
4. **Simplifique para Mobile**: Em telas pequenas, mostre apenas as informações essenciais
5. **Botões Maiores para Touch**: Em interfaces móveis, botões devem ter pelo menos 44px de altura para boa usabilidade
6. **Evite Hover**: Interações baseadas em hover não funcionam bem em dispositivos touch 