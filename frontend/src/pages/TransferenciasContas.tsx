import React, { useState, useEffect } from 'react';
import { 
  listarTransferencias, 
  cadastrarTransferencia,
  filtrarTransferencias 
} from '../services/transferenciaService';
import { listarContasBancarias } from '../services/contaBancariaService';
import { Transferencia, ContaBancaria } from '../types';
import { formatarMoeda, formatarData } from '../utils/formatters';
import Table from '../components/Table';
import DataStateHandler from '../components/DataStateHandler';
import Modal from '../components/Modal';
import FormField from '../components/FormField';
import { useToastUtils } from '../hooks/useToast';
import useFormHandler from '../hooks/useFormHandler';
import useConfirmDialog from '../hooks/useConfirmDialog';
import ConfirmDialog from '../components/ConfirmDialog';

interface TransferenciaExibicao extends Transferencia {
  numero: number;
}

interface FormularioTransferencia {
  conta_origem: string;
  conta_destino: string;
  valor: number;
  data: string;
  observacao?: string;
}

interface FiltrosTransferencia {
  dataInicio?: string;
  dataFim?: string;
  contaOrigem?: string;
  contaDestino?: string;
  status?: string;
}

export default function TransferenciasContas() {
  // Estados para listagem de transferências
  const [transferencias, setTransferencias] = useState<TransferenciaExibicao[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  
  // Estados para o modal de nova transferência
  const [modalAberto, setModalAberto] = useState(false);
  const [enviandoFormulario, setEnviandoFormulario] = useState(false);
  
  // Estados para contas bancárias
  const [contasBancarias, setContasBancarias] = useState<ContaBancaria[]>([]);
  const [carregandoContas, setCarregandoContas] = useState(false);
  
  // Estados para filtros
  const [filtrosAbertos, setFiltrosAbertos] = useState(false);
  const [filtros, setFiltros] = useState<FiltrosTransferencia>({
    dataInicio: undefined,
    dataFim: undefined,
    contaOrigem: undefined,
    contaDestino: undefined,
    status: undefined
  });
  
  // Inicializar formulário vazio
  const formularioVazio: FormularioTransferencia = {
    conta_origem: '',
    conta_destino: '',
    valor: 0,
    data: new Date().toISOString().split('T')[0],
    observacao: ''
  };
  
  // Usar hooks personalizados
  const { showSuccessToast, showErrorToast, showInfoToast } = useToastUtils();
  const { dialog, confirm, closeDialog } = useConfirmDialog();
  
  // Usar o hook useFormHandler para gerenciar o formulário
  const { 
    formData: formulario, 
    setFormData: setFormulario, 
    formErrors: errosFormulario,
    handleInputChange,
    validate,
    resetForm
  } = useFormHandler<FormularioTransferencia>(formularioVazio);

  // Colunas da tabela de transferências
  const columns = [
    {
      header: 'Nº',
      accessor: 'numero',
      render: (item: TransferenciaExibicao) => item.numero,
    },
    {
      header: 'Data',
      accessor: 'data',
      render: (item: TransferenciaExibicao) => formatarData(item.data),
    },
    {
      header: 'Conta Origem',
      accessor: 'conta_origem',
      render: (item: TransferenciaExibicao) => item.conta_origem,
    },
    {
      header: 'Conta Destino',
      accessor: 'conta_destino',
      render: (item: TransferenciaExibicao) => item.conta_destino,
    },
    {
      header: 'Valor',
      accessor: 'valor',
      render: (item: TransferenciaExibicao) => formatarMoeda(item.valor),
    },
    {
      header: 'Status',
      accessor: 'status',
      render: (item: TransferenciaExibicao) => (
        <span className={`badge status-${item.status.toLowerCase()}`}>
          {item.status}
        </span>
      ),
    },
  ];

  // Buscar transferências ao montar o componente
  useEffect(() => {
    buscarTransferencias();
  }, []);
  
  // Buscar contas bancárias quando abrir o modal
  useEffect(() => {
    if (modalAberto) {
      buscarContasBancarias();
    }
  }, [modalAberto]);

  // Função para buscar todas as transferências
  const buscarTransferencias = async () => {
    setLoading(true);
    setError(null);
    
    try {
      const data = await listarTransferencias();
      // Adicionar número sequencial para exibição
      const transferenciasComNumero = data.map((item, index) => ({
        ...item,
        numero: index + 1
      }));
      setTransferencias(transferenciasComNumero);
    } catch (err) {
      console.error('Erro ao carregar transferências:', err);
      setError('Erro ao carregar transferências. Tente novamente mais tarde.');
      showErrorToast('Erro ao carregar transferências');
    } finally {
      setLoading(false);
    }
  };
  
  // Função para buscar transferências com filtros
  const buscarTransferenciasFiltradas = async () => {
    setLoading(true);
    setError(null);
    
    try {
      // Remover filtros vazios
      const filtrosLimpos: FiltrosTransferencia = {};
      if (filtros.dataInicio) filtrosLimpos.dataInicio = filtros.dataInicio;
      if (filtros.dataFim) filtrosLimpos.dataFim = filtros.dataFim;
      if (filtros.contaOrigem) filtrosLimpos.contaOrigem = filtros.contaOrigem;
      if (filtros.contaDestino) filtrosLimpos.contaDestino = filtros.contaDestino;
      if (filtros.status) filtrosLimpos.status = filtros.status;
      
      const data = await filtrarTransferencias(filtrosLimpos);
      
      // Adicionar número sequencial para exibição
      const transferenciasComNumero = data.map((item, index) => ({
        ...item,
        numero: index + 1
      }));
      
      setTransferencias(transferenciasComNumero);
      showInfoToast(`${data.length} transferência(s) encontrada(s)`);
    } catch (err) {
      console.error('Erro ao filtrar transferências:', err);
      setError('Erro ao filtrar transferências. Tente novamente mais tarde.');
      showErrorToast('Erro ao filtrar transferências');
    } finally {
      setLoading(false);
    }
  };
  
  // Função para buscar contas bancárias
  const buscarContasBancarias = async () => {
    setCarregandoContas(true);
    
    try {
      const contas = await listarContasBancarias();
      setContasBancarias(contas);
      
      // Definir a primeira conta como padrão se existir
      if (contas.length > 0 && !formulario.conta_origem) {
        setFormulario(prev => ({ ...prev, conta_origem: contas[0].id_conta }));
      }
    } catch (err) {
      console.error('Erro ao carregar contas bancárias:', err);
      showErrorToast('Erro ao carregar contas bancárias');
    } finally {
      setCarregandoContas(false);
    }
  };
  
  // Abrir o modal de nova transferência
  const abrirModalNovaTransferencia = () => {
    // Resetar o formulário
    resetForm();
    setModalAberto(true);
  };
  
  // Validação do formulário
  const validarFormulario = () => {
    // Regras de validação
    const validationRules: Record<keyof FormularioTransferencia, any> = {
      conta_origem: {
        required: true,
        custom: (value: string) => {
          if (value === formulario.conta_destino) {
            return 'A conta de origem não pode ser igual à conta de destino';
          }
          return undefined;
        }
      },
      conta_destino: {
        required: true,
        custom: (value: string) => {
          if (value === formulario.conta_origem) {
            return 'A conta de destino não pode ser igual à conta de origem';
          }
          return undefined;
        }
      },
      valor: {
        required: true,
        custom: (value: number) => {
          if (value <= 0) {
            return 'O valor deve ser maior que zero';
          }
          return undefined;
        }
      },
      data: {
        required: true
      },
      observacao: {} // Campo opcional, sem validações
    };
    
    return validate(validationRules);
  };

  // Função para cadastrar uma nova transferência
  const cadastrarNovaTransferencia = async (e: React.FormEvent) => {
    e.preventDefault();
    
    // Validar o formulário antes de enviar
    const formularioValido = validarFormulario();
    
    if (!formularioValido) {
      return;
    }
    
    try {
      // Buscar os nomes das contas para enviar ao backend
      const contaOrigem = contasBancarias.find(c => c.id_conta === formulario.conta_origem);
      const contaDestino = contasBancarias.find(c => c.id_conta === formulario.conta_destino);
      
      if (!contaOrigem || !contaDestino) {
        throw new Error('Conta bancária não encontrada');
      }
      
      // Confirmar a operação antes de prosseguir
      confirm({
        title: "Confirmar Transferência",
        description: `Você está transferindo ${formatarMoeda(formulario.valor)} da conta ${contaOrigem.nome} para a conta ${contaDestino.nome}. Deseja continuar?`,
        confirmText: "Transferir",
        cancelText: "Cancelar",
        type: "warning",
        onConfirm: async () => {
          try {
            setEnviandoFormulario(true);
            
            // Preparar objeto para envio
            const transferencia = {
              data: formulario.data,
              conta_origem: contaOrigem.nome,
              conta_destino: contaDestino.nome,
              valor: formulario.valor,
              status: 'Pendente',
              observacao: formulario.observacao
            };
            
            // Enviar para o servidor
            await cadastrarTransferencia(transferencia);
            
            // Fechar modal e atualizar listagem
            setModalAberto(false);
            buscarTransferencias();
            
            showSuccessToast('Transferência cadastrada com sucesso!');
          } catch (err) {
            console.error('Erro ao cadastrar transferência:', err);
            showErrorToast('Erro ao cadastrar transferência');
          } finally {
            setEnviandoFormulario(false);
          }
        }
      });
    } catch (err) {
      console.error('Erro ao preparar transferência:', err);
      showErrorToast('Erro ao preparar transferência');
    }
  };
  
  // Manipulador de mudanças nos filtros
  const handleFiltroChange = (e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement>) => {
    const { name, value } = e.target;
    setFiltros(prev => ({ ...prev, [name]: value || undefined }));
  };
  
  // Aplicar filtros
  const aplicarFiltros = (e: React.FormEvent) => {
    e.preventDefault();
    buscarTransferenciasFiltradas();
    setFiltrosAbertos(false);
  };
  
  // Limpar filtros
  const limparFiltros = () => {
    setFiltros({
      dataInicio: undefined,
      dataFim: undefined,
      contaOrigem: undefined,
      contaDestino: undefined,
      status: undefined
    });
    buscarTransferencias();
    setFiltrosAbertos(false);
  };

  return (
    <div className="page-container">
      <div className="page-header">
        <h1 className="page-title">Transferências entre Contas</h1>
        <div className="page-actions">
          <button
            className="btn-secondary mr-2"
            onClick={() => setFiltrosAbertos(!filtrosAbertos)}
          >
            <i className="fas fa-filter"></i> Filtros
          </button>
          <button
            className="btn-primary"
            onClick={abrirModalNovaTransferencia}
          >
            <i className="fas fa-plus"></i> Nova Transferência
          </button>
        </div>
      </div>
      
      {/* Painel de Filtros */}
      {filtrosAbertos && (
        <div className="card mb-4">
          <div className="card-header">
            <h2 className="card-title">Filtros</h2>
          </div>
          <div className="card-body">
            <form onSubmit={aplicarFiltros}>
              <div className="form-grid">
                <FormField
                  label="Data Início"
                  name="dataInicio"
                  type="date"
                  value={filtros.dataInicio || ''}
                  onChange={handleFiltroChange}
                />
                
                <FormField
                  label="Data Fim"
                  name="dataFim"
                  type="date"
                  value={filtros.dataFim || ''}
                  onChange={handleFiltroChange}
                />
                
                <div className="form-group">
                  <label htmlFor="contaOrigem">Conta Origem</label>
                  <select
                    id="contaOrigem"
                    name="contaOrigem"
                    value={filtros.contaOrigem || ''}
                    onChange={handleFiltroChange}
                  >
                    <option value="">Todas</option>
                    {contasBancarias.map((conta) => (
                      <option key={conta.id_conta} value={conta.nome}>
                        {conta.nome}
                      </option>
                    ))}
                  </select>
                </div>
                
                <div className="form-group">
                  <label htmlFor="contaDestino">Conta Destino</label>
                  <select
                    id="contaDestino"
                    name="contaDestino"
                    value={filtros.contaDestino || ''}
                    onChange={handleFiltroChange}
                  >
                    <option value="">Todas</option>
                    {contasBancarias.map((conta) => (
                      <option key={conta.id_conta} value={conta.nome}>
                        {conta.nome}
                      </option>
                    ))}
                  </select>
                </div>
                
                <div className="form-group">
                  <label htmlFor="status">Status</label>
                  <select
                    id="status"
                    name="status"
                    value={filtros.status || ''}
                    onChange={handleFiltroChange}
                  >
                    <option value="">Todos</option>
                    <option value="Pendente">Pendente</option>
                    <option value="Concluída">Concluída</option>
                    <option value="Agendada">Agendada</option>
                    <option value="Cancelada">Cancelada</option>
                  </select>
                </div>
              </div>
              
              <div className="form-actions">
                <button
                  type="button"
                  className="btn-secondary"
                  onClick={limparFiltros}
                >
                  Limpar
                </button>
                <button
                  type="submit"
                  className="btn-primary"
                >
                  Aplicar
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* Listagem de Transferências */}
      <div className="card">
        <div className="card-header">
          <h2 className="card-title">Lista de Transferências</h2>
          <div className="card-tools">
            <button
              className="btn-secondary btn-sm"
              onClick={buscarTransferencias}
              disabled={loading}
            >
              <i className="fas fa-sync"></i> Atualizar
            </button>
          </div>
        </div>
        <div className="card-body">
          <DataStateHandler
            loading={loading}
            error={error}
            dataLength={transferencias.length}
            emptyMessage="Nenhuma transferência encontrada."
            onRetry={buscarTransferencias}
          >
            <Table
              columns={columns}
              data={transferencias}
              emptyMessage="Nenhuma transferência encontrada."
            />
          </DataStateHandler>
        </div>
      </div>
      
      {/* Modal de Nova Transferência */}
      <Modal
        isOpen={modalAberto}
        onClose={() => setModalAberto(false)}
        title="Nova Transferência"
        size="medium"
      >
        <DataStateHandler
          loading={carregandoContas}
          dataLength={contasBancarias.length}
          emptyMessage="Nenhuma conta bancária disponível."
        >
          <form onSubmit={cadastrarNovaTransferencia}>
            <div className="form-group">
              <label htmlFor="conta_origem">Conta de Origem:</label>
              <select
                id="conta_origem"
                name="conta_origem"
                value={formulario.conta_origem}
                onChange={handleInputChange}
                className={errosFormulario.conta_origem ? 'input-error' : ''}
                disabled={enviandoFormulario}
                required
              >
                <option value="">Selecione a conta de origem</option>
                {contasBancarias.map((conta) => (
                  <option key={conta.id_conta} value={conta.id_conta}>
                    {conta.nome} - {conta.banco} - Saldo: {formatarMoeda(conta.saldo_atual)}
                  </option>
                ))}
              </select>
              {errosFormulario.conta_origem && (
                <div className="form-field-error">{errosFormulario.conta_origem}</div>
              )}
            </div>
            
            <div className="form-group">
              <label htmlFor="conta_destino">Conta de Destino:</label>
              <select
                id="conta_destino"
                name="conta_destino"
                value={formulario.conta_destino}
                onChange={handleInputChange}
                className={errosFormulario.conta_destino ? 'input-error' : ''}
                disabled={enviandoFormulario}
                required
              >
                <option value="">Selecione a conta de destino</option>
                {contasBancarias.map((conta) => (
                  <option key={conta.id_conta} value={conta.id_conta}>
                    {conta.nome} - {conta.banco}
                  </option>
                ))}
              </select>
              {errosFormulario.conta_destino && (
                <div className="form-field-error">{errosFormulario.conta_destino}</div>
              )}
            </div>
            
            <FormField
              label="Valor (R$)"
              name="valor"
              type="number"
              value={formulario.valor}
              onChange={handleInputChange}
              error={errosFormulario.valor}
              disabled={enviandoFormulario}
              step="0.01"
              min={0.01}
              required
            />
            
            <FormField
              label="Data"
              name="data"
              type="date"
              value={formulario.data}
              onChange={handleInputChange}
              error={errosFormulario.data}
              disabled={enviandoFormulario}
              required
            />
            
            <div className="form-group">
              <label htmlFor="observacao">Observação:</label>
              <textarea
                id="observacao"
                name="observacao"
                value={formulario.observacao || ''}
                onChange={handleInputChange}
                disabled={enviandoFormulario}
                rows={3}
              />
            </div>
            
            <div className="form-actions">
              <button
                type="button"
                className="btn-secondary"
                onClick={() => setModalAberto(false)}
                disabled={enviandoFormulario}
              >
                Cancelar
              </button>
              <button
                type="submit"
                className="btn-primary"
                disabled={enviandoFormulario}
              >
                {enviandoFormulario ? 'Salvando...' : 'Salvar'}
              </button>
            </div>
          </form>
        </DataStateHandler>
      </Modal>
      
      {/* Diálogo de confirmação */}
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