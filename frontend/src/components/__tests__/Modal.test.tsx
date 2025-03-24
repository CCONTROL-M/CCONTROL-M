import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen, fireEvent } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import Modal from '../Modal';

describe('Modal', () => {
  // Mocks para as funções do componente
  const mockOnClose = vi.fn();
  
  beforeEach(() => {
    // Reset dos mocks antes de cada teste
    vi.resetAllMocks();
    
    // Simular o body para verificar o overflow
    Object.defineProperty(document.body.style, 'overflow', {
      get: () => document.body.getAttribute('data-overflow') || '',
      set: (value) => document.body.setAttribute('data-overflow', value),
      configurable: true
    });
  });
  
  it('não deve renderizar nada quando isOpen=false', () => {
    render(
      <Modal
        isOpen={false}
        onClose={mockOnClose}
        title="Modal de teste"
      >
        <p>Conteúdo de teste</p>
      </Modal>
    );
    
    // Verificar se o modal não foi renderizado
    expect(screen.queryByText('Modal de teste')).not.toBeInTheDocument();
    expect(screen.queryByText('Conteúdo de teste')).not.toBeInTheDocument();
  });
  
  it('deve renderizar o modal corretamente quando isOpen=true', () => {
    render(
      <Modal
        isOpen={true}
        onClose={mockOnClose}
        title="Modal de teste"
      >
        <p>Conteúdo de teste</p>
      </Modal>
    );
    
    // Verificar se o modal foi renderizado
    expect(screen.getByText('Modal de teste')).toBeInTheDocument();
    expect(screen.getByText('Conteúdo de teste')).toBeInTheDocument();
  });
  
  it('deve chamar onClose quando o botão de fechar é clicado', async () => {
    render(
      <Modal
        isOpen={true}
        onClose={mockOnClose}
        title="Modal de teste"
      >
        <p>Conteúdo de teste</p>
      </Modal>
    );
    
    // Encontrar o botão de fechar e clicar nele
    const closeButton = screen.getByLabelText('Fechar');
    await userEvent.click(closeButton);
    
    // Verificar se onClose foi chamado
    expect(mockOnClose).toHaveBeenCalledTimes(1);
  });
  
  it('deve chamar onClose quando a tecla ESC é pressionada', () => {
    render(
      <Modal
        isOpen={true}
        onClose={mockOnClose}
        title="Modal de teste"
      >
        <p>Conteúdo de teste</p>
      </Modal>
    );
    
    // Simular o pressionamento da tecla ESC
    fireEvent.keyDown(document, { key: 'Escape' });
    
    // Verificar se onClose foi chamado
    expect(mockOnClose).toHaveBeenCalledTimes(1);
  });
  
  it('deve chamar onClose quando o overlay é clicado', async () => {
    render(
      <Modal
        isOpen={true}
        onClose={mockOnClose}
        title="Modal de teste"
      >
        <p>Conteúdo de teste</p>
      </Modal>
    );
    
    // Encontrar o overlay e clicar nele
    const overlay = document.querySelector('.modal-overlay');
    expect(overlay).toBeInTheDocument();
    
    if (overlay) {
      // Usar MouseEvent para maior precisão no teste de clicar fora do modal
      fireEvent.mouseDown(overlay);
      fireEvent.mouseUp(overlay);
      fireEvent.click(overlay);
    }
    
    // Verificar se onClose foi chamado
    expect(mockOnClose).toHaveBeenCalledTimes(1);
  });
  
  it('não deve chamar onClose quando o conteúdo do modal é clicado', async () => {
    render(
      <Modal
        isOpen={true}
        onClose={mockOnClose}
        title="Modal de teste"
      >
        <button>Botão no modal</button>
      </Modal>
    );
    
    // Clicar em um elemento dentro do modal
    const button = screen.getByText('Botão no modal');
    await userEvent.click(button);
    
    // Verificar se onClose NÃO foi chamado
    expect(mockOnClose).not.toHaveBeenCalled();
  });
  
  it('deve aplicar a classe correta baseada no tamanho', () => {
    // Renderizar com tamanho pequeno
    const { rerender } = render(
      <Modal
        isOpen={true}
        onClose={mockOnClose}
        title="Modal de teste"
        size="small"
      >
        <p>Conteúdo de teste</p>
      </Modal>
    );
    
    // Verificar se a classe de tamanho pequeno foi aplicada
    let modalContainer = document.querySelector('.modal-container');
    expect(modalContainer).toHaveClass('modal-small');
    
    // Re-renderizar com tamanho grande
    rerender(
      <Modal
        isOpen={true}
        onClose={mockOnClose}
        title="Modal de teste"
        size="large"
      >
        <p>Conteúdo de teste</p>
      </Modal>
    );
    
    // Verificar se a classe de tamanho grande foi aplicada
    modalContainer = document.querySelector('.modal-container');
    expect(modalContainer).toHaveClass('modal-large');
  });
  
  it('deve definir overflow do body como "hidden" quando o modal está aberto', () => {
    const { unmount } = render(
      <Modal
        isOpen={true}
        onClose={mockOnClose}
        title="Modal de teste"
      >
        <p>Conteúdo de teste</p>
      </Modal>
    );
    
    // Verificar se o overflow do body foi definido como hidden
    expect(document.body.getAttribute('data-overflow')).toBe('hidden');
    
    // Desmontar o componente e verificar se o overflow volta ao normal
    unmount();
    expect(document.body.getAttribute('data-overflow')).toBe('auto');
  });
}); 