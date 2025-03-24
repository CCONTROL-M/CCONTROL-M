import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen, fireEvent } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import ConfirmDialog from '../ConfirmDialog';

describe('ConfirmDialog', () => {
  // Mocks para as funções do componente
  const mockOnClose = vi.fn();
  const mockOnConfirm = vi.fn();

  beforeEach(() => {
    // Reset dos mocks antes de cada teste
    vi.resetAllMocks();
    
    // Limpar eventuais eventos adicionados ao document
    vi.restoreAllMocks();

    // Simular o body para verificar o overflow
    Object.defineProperty(document.body.style, 'overflow', {
      get: () => document.body.getAttribute('data-overflow') || '',
      set: (value) => document.body.setAttribute('data-overflow', value),
      configurable: true
    });
  });

  it('não deve renderizar nada quando isOpen=false', () => {
    render(
      <ConfirmDialog
        isOpen={false}
        onClose={mockOnClose}
        onConfirm={mockOnConfirm}
        title="Confirmação de teste"
        description="Descrição de teste"
      />
    );

    // Verificar se o diálogo não foi renderizado
    expect(screen.queryByText('Confirmação de teste')).not.toBeInTheDocument();
  });

  it('deve renderizar o diálogo corretamente quando isOpen=true', () => {
    render(
      <ConfirmDialog
        isOpen={true}
        onClose={mockOnClose}
        onConfirm={mockOnConfirm}
        title="Confirmação de teste"
        description="Descrição de teste"
      />
    );

    // Verificar se o diálogo foi renderizado
    expect(screen.getByText('Confirmação de teste')).toBeInTheDocument();
    expect(screen.getByText('Descrição de teste')).toBeInTheDocument();
    
    // Verificar os botões padrão
    expect(screen.getByText('Confirmar')).toBeInTheDocument();
    expect(screen.getByText('Cancelar')).toBeInTheDocument();
  });

  it('deve usar textos personalizados para os botões quando fornecidos', () => {
    render(
      <ConfirmDialog
        isOpen={true}
        onClose={mockOnClose}
        onConfirm={mockOnConfirm}
        title="Confirmação de teste"
        description="Descrição de teste"
        confirmText="Sim, tenho certeza"
        cancelText="Não, voltar"
      />
    );

    // Verificar os textos personalizados dos botões
    expect(screen.getByText('Sim, tenho certeza')).toBeInTheDocument();
    expect(screen.getByText('Não, voltar')).toBeInTheDocument();
  });

  it('deve chamar onConfirm e onClose quando o botão de confirmação é clicado', async () => {
    render(
      <ConfirmDialog
        isOpen={true}
        onClose={mockOnClose}
        onConfirm={mockOnConfirm}
        title="Confirmação de teste"
        description="Descrição de teste"
      />
    );

    // Clicar no botão de confirmação
    await userEvent.click(screen.getByText('Confirmar'));

    // Verificar se as funções foram chamadas
    expect(mockOnConfirm).toHaveBeenCalledTimes(1);
    expect(mockOnClose).toHaveBeenCalledTimes(1);
  });

  it('deve chamar onClose quando o botão de cancelamento é clicado', async () => {
    render(
      <ConfirmDialog
        isOpen={true}
        onClose={mockOnClose}
        onConfirm={mockOnConfirm}
        title="Confirmação de teste"
        description="Descrição de teste"
      />
    );

    // Clicar no botão de cancelamento
    await userEvent.click(screen.getByText('Cancelar'));

    // Verificar se apenas onClose foi chamado
    expect(mockOnClose).toHaveBeenCalledTimes(1);
    expect(mockOnConfirm).not.toHaveBeenCalled();
  });

  it('deve chamar onClose quando o fundo do overlay é clicado', async () => {
    render(
      <ConfirmDialog
        isOpen={true}
        onClose={mockOnClose}
        onConfirm={mockOnConfirm}
        title="Confirmação de teste"
        description="Descrição de teste"
      />
    );

    // Encontrar o overlay e clicar nele
    const overlay = screen.getByText('Confirmação de teste').parentElement?.parentElement;
    expect(overlay).toHaveClass('dialog-overlay');
    
    if (overlay) {
      await userEvent.click(overlay);
    }

    // Verificar se onClose foi chamado
    expect(mockOnClose).toHaveBeenCalledTimes(1);
  });

  it('deve chamar onClose quando a tecla ESC é pressionada', () => {
    render(
      <ConfirmDialog
        isOpen={true}
        onClose={mockOnClose}
        onConfirm={mockOnConfirm}
        title="Confirmação de teste"
        description="Descrição de teste"
      />
    );

    // Simular pressionamento da tecla ESC
    fireEvent.keyDown(document, { key: 'Escape' });

    // Verificar se onClose foi chamado
    expect(mockOnClose).toHaveBeenCalledTimes(1);
  });

  it('deve aplicar a classe correta baseada no tipo', () => {
    // Renderizar com tipo 'warning'
    const { rerender } = render(
      <ConfirmDialog
        isOpen={true}
        onClose={mockOnClose}
        onConfirm={mockOnConfirm}
        title="Confirmação de teste"
        description="Descrição de teste"
        type="warning"
      />
    );

    // Verificar se a classe de warning foi aplicada
    const dialog = screen.getByText('Confirmação de teste').parentElement?.parentElement;
    expect(dialog).toHaveClass('confirm-dialog-warning');

    // Re-renderizar com tipo 'info'
    rerender(
      <ConfirmDialog
        isOpen={true}
        onClose={mockOnClose}
        onConfirm={mockOnConfirm}
        title="Confirmação de teste"
        description="Descrição de teste"
        type="info"
      />
    );

    // Verificar se a classe de info foi aplicada
    expect(dialog).toHaveClass('confirm-dialog-info');
  });

  it('deve definir overflow como "hidden" no body quando o diálogo está aberto', () => {
    const { unmount } = render(
      <ConfirmDialog
        isOpen={true}
        onClose={mockOnClose}
        onConfirm={mockOnConfirm}
        title="Confirmação de teste"
        description="Descrição de teste"
      />
    );

    // Verificar se o overflow do body foi definido como hidden
    expect(document.body.getAttribute('data-overflow')).toBe('hidden');

    // Desmontar o componente e verificar se o overflow volta ao normal
    unmount();
    expect(document.body.getAttribute('data-overflow')).toBe('auto');
  });
}); 