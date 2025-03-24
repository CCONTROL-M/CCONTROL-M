import { describe, it, expect, vi } from 'vitest';
import { render, screen } from '@testing-library/react';
import Toast from '../Toast';

describe('Toast', () => {
  it('deve renderizar o toast com a mensagem correta', () => {
    // Arrange
    const mockOnClose = vi.fn();
    const testMessage = 'Mensagem de teste';
    
    // Act
    render(
      <Toast 
        mensagem={testMessage} 
        tipo="info" 
        duracao={3000} 
        onClose={mockOnClose} 
      />
    );
    
    // Assert
    expect(screen.getByText(testMessage)).toBeInTheDocument();
  });
  
  it('deve ter a classe correta baseada no tipo', () => {
    // Arrange
    const mockOnClose = vi.fn();
    
    // Act
    render(
      <Toast 
        mensagem="Mensagem de sucesso" 
        tipo="sucesso" 
        duracao={3000} 
        onClose={mockOnClose} 
      />
    );
    
    // Assert
    // O Toast não tem role="alert", então vamos selecioná-lo pela classe diretamente
    const toastElement = document.querySelector('.toast.toast-sucesso');
    expect(toastElement).toHaveClass('toast-sucesso');
  });
  
  it('deve chamar onClose após o tempo de duração', () => {
    // Arrange
    vi.useFakeTimers();
    const mockOnClose = vi.fn();
    
    // Act
    render(
      <Toast 
        mensagem="Mensagem temporária" 
        tipo="info" 
        duracao={1000} 
        onClose={mockOnClose} 
      />
    );
    
    // Assert - Antes do timeout, não deve ter sido chamado
    expect(mockOnClose).not.toHaveBeenCalled();
    
    // Avança o tempo
    vi.advanceTimersByTime(1000);
    
    // Depois do timeout, deve ter sido chamado
    expect(mockOnClose).toHaveBeenCalledTimes(1);
    
    // Limpa os temporizadores falsos
    vi.useRealTimers();
  });
}); 