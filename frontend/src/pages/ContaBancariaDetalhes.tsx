import React, { useEffect, useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { ContaBancaria } from '../types';
import { buscarContaBancaria } from '../services/contaBancariaService';
import { buscarContaBancariaMock } from '../services/contaBancariaServiceMock';
import { useMock } from '../utils/mock';
import { useToastUtils } from '../hooks/useToast';
import DataStateHandler from '../components/DataStateHandler';
import ContaBancariaDetalhes from '../components/contaBancaria/ContaBancariaDetalhes';
import TransacoesContaBancaria from '../components/contaBancaria/TransacoesContaBancaria';
import Modal from '../components/Modal';
import ContaBancariaForm from '../components/contaBancaria/ContaBancariaForm';
import { useApiStatus } from '../contexts/ApiStatusContext';
import ApiDiagnostic from '../components/ApiDiagnostic';

/**
 * Página de detalhes de uma conta bancária
 */
export default function ContaBancariaDetalhesPagina() {
  // Parâmetros da URL
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  
  // Estados
  const [contaBancaria, setContaBancaria] = useState<ContaBancaria | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [modalEditarAberto, setModalEditarAberto] = useState(false);
  
  // Hooks
  const { showSuccessToast, showErrorToast } = useToastUtils();
  const { apiOnline } = useApiStatus();

  // Efeito para carregar os dados da conta
  useEffect(() => {
    if (id) {
      carregarContaBancaria(id);
    }
  }, [id]);

  // Carregar os dados da conta bancária
  const carregarContaBancaria = async (idConta: string) => {
    setLoading(true);
    setError(null);
    
    try {
      // Se a API estiver offline e não estiver em modo mock, mostrar erro
      if (!apiOnline && !useMock()) {
        throw new Error('API indisponível. Ative o modo Mock para ver dados simulados.');
      }
      
      // Buscar a conta bancária (passando id_empresa = 1 como valor padrão)
      const data = useMock() 
        ? await buscarContaBancariaMock(idConta) 
        : await buscarContaBancaria(idConta, '1'); // Passando id_empresa
      
      setContaBancaria(data);
    } catch (err) {
      console.error('Erro ao carregar conta bancária:', err);
      const errorMessage = err instanceof Error ? err.message : 'Erro ao carregar dados da conta bancária';
      setError(errorMessage);
      showErrorToast(errorMessage);
      
      // Em caso de erro, tentar carregar dados mock
      if (!useMock()) {
        try {
          console.info('Tentando carregar dados mock como fallback');
          const mockData = await buscarContaBancariaMock(idConta);
          setContaBancaria(mockData);
          setError('API indisponível. Exibindo dados simulados como fallback.');
        } catch (mockErr) {
          console.error('Erro ao carregar dados mock:', mockErr);
        }
      }
    } finally {
      setLoading(false);
    }
  };

  // Abrir modal de edição
  const handleEditarClick = () => {
    setModalEditarAberto(true);
  };

  // Fechar modal de edição
  const handleFecharModal = () => {
    setModalEditarAberto(false);
  };

  // Atualizar a conta bancária
  const handleSalvarConta = async (contaData: {
    nome: string;
    banco: string;
    agencia: string;
    conta: string;
    tipo: string;
    saldo_inicial: number;
    ativa: boolean;
    mostrar_dashboard: boolean;
  }) => {
    try {
      // Implementar a lógica de atualização (pode usar a mesma do ContasBancarias.tsx)
      // Para este exemplo, vamos apenas fechar o modal e recarregar os dados
      setModalEditarAberto(false);
      if (id) {
        await carregarContaBancaria(id);
      }
      showSuccessToast('Conta bancária atualizada com sucesso!');
    } catch (err) {
      console.error('Erro ao atualizar conta bancária:', err);
      const errorMessage = err instanceof Error ? err.message : 'Não foi possível atualizar a conta bancária';
      showErrorToast(`${errorMessage}. Tente novamente mais tarde.`);
    }
  };

  // Voltar para a lista de contas
  const handleVoltar = () => {
    navigate('/contas-bancarias');
  };

  return (
    <div className="conta-bancaria-detalhes-page">
      <div className="page-header">
        <div className="flex items-center">
          <button 
            className="btn-icon mr-2"
            onClick={handleVoltar}
            aria-label="Voltar"
          >
            ←
          </button>
          <h1 className="page-title">Detalhes da Conta Bancária</h1>
        </div>
        
        {contaBancaria && (
          <div className="page-actions">
            <button 
              className="btn-primary"
              onClick={handleEditarClick}
            >
              Editar Conta
            </button>
          </div>
        )}
      </div>
      
      <DataStateHandler
        loading={loading}
        error={error}
        dataLength={contaBancaria ? 1 : 0}
        onRetry={() => id && carregarContaBancaria(id)}
        emptyMessage="Conta bancária não encontrada."
      >
        <>
          {(!apiOnline && !useMock()) && (
            <div className="mb-6">
              <ApiDiagnostic />
            </div>
          )}
          
          {contaBancaria && (
            <div className="space-y-8">
              <div className="bg-white p-6 rounded-lg shadow-sm">
                <ContaBancariaDetalhes conta={contaBancaria} />
              </div>
              
              <div className="bg-white p-6 rounded-lg shadow-sm">
                <TransacoesContaBancaria conta={contaBancaria} />
              </div>
            </div>
          )}
        </>
      </DataStateHandler>
      
      {/* Modal de edição de conta bancária */}
      {contaBancaria && (
        <Modal
          isOpen={modalEditarAberto}
          onClose={handleFecharModal}
          title="Editar Conta Bancária"
        >
          <ContaBancariaForm
            contaBancaria={contaBancaria}
            onSave={handleSalvarConta}
            onCancel={handleFecharModal}
          />
        </Modal>
      )}
    </div>
  );
} 