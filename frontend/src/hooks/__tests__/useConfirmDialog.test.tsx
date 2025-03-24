import { describe, it, expect, vi, beforeEach } from 'vitest';
import { renderHook, act } from '@testing-library/react';
import useConfirmDialog, { CONFIRM_DIALOG_EVENTS } from '../useConfirmDialog';

describe('useConfirmDialog', () => {
  // Setup e cleanup
  beforeEach(() => {
    vi.resetAllMocks();
    vi.spyOn(document, 'dispatchEvent');
  });

  it('deve inicializar com o estado correto', () => {
    // Renderizar o hook
    const { result } = renderHook(() => useConfirmDialog());

    // Verificar o estado inicial
    expect(result.current.dialog).toEqual({
      isOpen: false,
      title: '',
      description: '',
      onConfirm: expect.any(Function),
      confirmText: 'Confirmar',
      cancelText: 'Cancelar',
      type: 'danger'
    });
  });

  it('deve abrir o diálogo com as opções corretas quando confirm é chamado', () => {
    // Renderizar o hook
    const { result } = renderHook(() => useConfirmDialog());

    // Opções para o diálogo
    const mockOnConfirm = vi.fn();
    const options = {
      title: 'Título de teste',
      description: 'Descrição de teste',
      onConfirm: mockOnConfirm,
      confirmText: 'OK',
      cancelText: 'Cancelar',
      type: 'warning' as const
    };

    // Chamar o método confirm
    act(() => {
      result.current.confirm(options);
    });

    // Verificar se o estado foi atualizado corretamente
    expect(result.current.dialog).toEqual({
      ...options,
      isOpen: true
    });

    // Verificar se o evento OPENED foi disparado
    expect(document.dispatchEvent).toHaveBeenCalledWith(
      expect.objectContaining({
        type: CONFIRM_DIALOG_EVENTS.OPENED
      })
    );
  });

  it('deve fechar o diálogo quando closeDialog é chamado', () => {
    // Renderizar o hook
    const { result } = renderHook(() => useConfirmDialog());

    // Primeiro abrir o diálogo
    act(() => {
      result.current.confirm({
        title: 'Título de teste',
        description: 'Descrição de teste',
        onConfirm: vi.fn()
      });
    });

    // Verificar que o diálogo está aberto
    expect(result.current.dialog.isOpen).toBe(true);

    // Chamar o método closeDialog
    act(() => {
      result.current.closeDialog();
    });

    // Verificar se o diálogo foi fechado
    expect(result.current.dialog.isOpen).toBe(false);

    // Verificar se o evento CLOSED foi disparado
    expect(document.dispatchEvent).toHaveBeenCalledWith(
      expect.objectContaining({
        type: CONFIRM_DIALOG_EVENTS.CLOSED
      })
    );
  });

  it('deve resolver a promessa e chamar onConfirm quando a ação é confirmada', async () => {
    // Renderizar o hook
    const { result } = renderHook(() => useConfirmDialog());

    // Opções para o diálogo
    const mockOnConfirm = vi.fn();
    let promiseResolved = false;

    // Chamar o método confirm e guardar a promessa
    let confirmPromise: Promise<void>;
    act(() => {
      confirmPromise = result.current.confirm({
        title: 'Título de teste',
        description: 'Descrição de teste',
        onConfirm: mockOnConfirm
      });
      
      // Adicionar then para verificar se a promessa foi resolvida
      confirmPromise.then(() => {
        promiseResolved = true;
      });
    });

    // Simular a confirmação chamando onConfirm do estado atual
    act(() => {
      result.current.dialog.onConfirm();
    });

    // Aguardar a próxima iteração para promessas serem processadas
    await Promise.resolve();

    // Verificar se onConfirm foi chamado
    expect(mockOnConfirm).toHaveBeenCalledTimes(1);
    
    // Verificar se a promessa foi resolvida
    expect(promiseResolved).toBe(true);
    
    // Verificar se o diálogo foi fechado
    expect(result.current.dialog.isOpen).toBe(false);
  });

  it('deve emitir eventos quando o diálogo é aberto e fechado', () => {
    // Renderizar o hook
    const { result } = renderHook(() => useConfirmDialog());

    // Resetar o spy para limpar chamadas anteriores
    vi.mocked(document.dispatchEvent).mockClear();

    // Abrir o diálogo
    act(() => {
      result.current.confirm({
        title: 'Título de teste',
        description: 'Descrição de teste',
        onConfirm: vi.fn()
      });
    });

    // Verificar se o evento OPENED foi disparado
    expect(document.dispatchEvent).toHaveBeenCalledWith(
      expect.objectContaining({
        type: CONFIRM_DIALOG_EVENTS.OPENED,
        detail: expect.objectContaining({
          title: 'Título de teste',
          description: 'Descrição de teste'
        })
      })
    );

    // Resetar o spy para limpar chamadas anteriores
    vi.mocked(document.dispatchEvent).mockClear();

    // Fechar o diálogo
    act(() => {
      result.current.closeDialog();
    });

    // Verificar se o evento CLOSED foi disparado
    expect(document.dispatchEvent).toHaveBeenCalledWith(
      expect.objectContaining({
        type: CONFIRM_DIALOG_EVENTS.CLOSED
      })
    );
  });
}); 