import React, { useEffect, useState } from "react";
import { Venda, Cliente, NovaVenda, Parcela } from "../types";
import { formatarData, formatarMoeda } from "../utils/formatters";
import { listarVendas, cadastrarVenda, buscarVenda, listarParcelasPorVenda } from "../services/vendaService";
import { listarClientes } from "../services/clienteService";
import Modal from "../components/Modal";
import { useMock, setUseMock } from '../utils/mock';
import Table, { TableColumn } from "../components/Table";
import DataStateHandler from "../components/DataStateHandler";
import { useToastUtils } from "../hooks/useToast";
import VendasParcelasForm from "../components/VendasParcelasForm";

export default function VendasParcelas() {
  // Estados para a listagem de vendas
  const [vendas, setVendas] = useState<Venda[]>([]);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);
  
  // Estados para detalhes de venda e parcelas
  const [vendaSelecionada, setVendaSelecionada] = useState<Venda | null>(null);
  const [parcelas, setParcelas] = useState<Parcela[]>([]);
  const [loadingParcelas, setLoadingParcelas] = useState<boolean>(false);
  
  // Estados para modais
  const [modalNovaVenda, setModalNovaVenda] = useState<boolean>(false);
  const [modalDetalhes, setModalDetalhes] = useState<boolean>(false);
  const [modalConfirmacao, setModalConfirmacao] = useState<boolean>(false);
  const [vendaParaExcluir, setVendaParaExcluir] = useState<string | null>(null);
  
  // Estados auxiliares
  const [clientes, setClientes] = useState<Cliente[]>([]);
  const [enviandoFormulario, setEnviandoFormulario] = useState<boolean>(false);
  
  // Toast para notificações
  const { showSuccessToast, showErrorToast } = useToastUtils();

  // Efeito inicial para carregar vendas e clientes
  useEffect(() => {
    // Não ativamos mais o modo mock automaticamente
    // O usuário precisa ativar manualmente se quiser
    console.log("Iniciando componente VendasParcelas com modo atual");
    
    // Carregar as vendas
    buscarVendas();
    
    // Carregar os clientes para o formulário
    buscarClientes();
  }, []);

  // Colunas da tabela de vendas
  const colunasVendas: TableColumn[] = [
    {
      header: "Cliente",
      accessor: "nome_cliente",
      render: (venda: Venda) => venda.nome_cliente || venda.cliente?.nome || "Cliente não informado"
    },
    {
      header: "Valor",
      accessor: "valor_total",
      render: (venda: Venda) => formatarMoeda(venda.valor_total)
    },
    {
      header: "Data",
      accessor: "data_venda",
      render: (venda: Venda) => formatarData(venda.data_venda || '')
    },
    {
      header: "Parcelas",
      accessor: "numero_parcelas"
    },
    {
      header: "Status",
      accessor: "status",
      render: (venda: Venda) => (
        <span className={`status-badge ${venda.status === 'paga' ? 'success' : venda.status === 'parcial' ? 'warning' : 'danger'}`}>
          {venda.status === 'paga' ? 'Paga' : venda.status === 'parcial' ? 'Parcial' : 'Pendente'}
        </span>
      )
    },
    {
      header: "Ações",
      accessor: "id_venda",
      render: (venda: Venda) => (
        <div className="table-actions">
          <button 
            className="btn-icon btn-view" 
            onClick={() => abrirDetalhesVenda(venda.id_venda)}
            aria-label="Ver detalhes"
          >
            👁️
          </button>
          <button 
            className="btn-icon btn-delete" 
            onClick={() => confirmarExclusao(venda.id_venda)}
            aria-label="Excluir venda"
          >
            🗑️
          </button>
        </div>
      )
    }
  ];

  // Colunas da tabela de parcelas
  const colunasParcelas: TableColumn[] = [
    {
      header: "Nº",
      accessor: "numero",
      render: (parcela: Parcela, index?: number) => parcela.numero || (index !== undefined ? index + 1 : 1)
    },
    {
      header: "Valor",
      accessor: "valor",
      render: (parcela: Parcela) => formatarMoeda(parcela.valor)
    },
    {
      header: "Vencimento",
      accessor: "data_vencimento",
      render: (parcela: Parcela) => formatarData(parcela.data_vencimento)
    },
    {
      header: "Status",
      accessor: "status",
      render: (parcela: Parcela) => (
        <span className={`status-badge ${parcela.status === 'paga' ? 'success' : parcela.status === 'atrasada' ? 'danger' : 'warning'}`}>
          {parcela.status === 'paga' ? 'Paga' : parcela.status === 'atrasada' ? 'Atrasada' : 'Pendente'}
        </span>
      )
    },
    {
      header: "Data Pagamento",
      accessor: "data_pagamento",
      render: (parcela: Parcela) => parcela.data_pagamento ? formatarData(parcela.data_pagamento) : '-'
    }
  ];

  /**
   * Busca a lista de vendas da API
   */
  async function buscarVendas() {
    setLoading(true);
    setError(null);
    
    try {
      const data = await listarVendas();
      setVendas(data);
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : "Erro desconhecido";
      setError(errorMessage);
      showErrorToast("Erro ao carregar as vendas");
      console.error(err);
    } finally {
      setLoading(false);
    }
  }

  /**
   * Abre o modal com detalhes da venda e suas parcelas
   */
  async function abrirDetalhesVenda(id: string) {
    setLoadingParcelas(true);
    
    try {
      // Buscar detalhes da venda
      const venda = await buscarVenda(id);
      setVendaSelecionada(venda);
      
      // Buscar parcelas da venda
      const parcelasVenda = await listarParcelasPorVenda(id);
      setParcelas(parcelasVenda);
      
      // Abrir o modal
      setModalDetalhes(true);
    } catch (err) {
      console.error(err);
      showErrorToast("Erro ao carregar os detalhes da venda");
    } finally {
      setLoadingParcelas(false);
    }
  }

  /**
   * Busca a lista de clientes para o formulário
   */
  async function buscarClientes() {
    try {
      const data = await listarClientes();
      setClientes(data);
    } catch (err) {
      console.error(err);
      showErrorToast("Erro ao carregar a lista de clientes");
    }
  }

  /**
   * Abre o modal para cadastrar nova venda
   */
  const abrirModalNovaVenda = () => {
    setModalNovaVenda(true);
  };

  /**
   * Confirma exclusão de venda
   */
  const confirmarExclusao = (id: string) => {
    setVendaParaExcluir(id);
    setModalConfirmacao(true);
  };

  /**
   * Exclui uma venda
   */
  const excluirVenda = async () => {
    if (!vendaParaExcluir) return;
    
    try {
      // Aqui você deve implementar a chamada real para excluir a venda
      // await excluirVenda(vendaParaExcluir);
      
      // Como não temos a função implementada, vamos apenas simular
      setVendas(prevVendas => prevVendas.filter(venda => venda.id_venda !== vendaParaExcluir));
      
      showSuccessToast("Venda excluída com sucesso!");
    } catch (err) {
      console.error(err);
      showErrorToast("Erro ao excluir a venda");
    } finally {
      setModalConfirmacao(false);
      setVendaParaExcluir(null);
    }
  };

  /**
   * Processa o formulário de nova venda
   */
  const handleCadastrarVenda = async (formData: NovaVenda) => {
    setEnviandoFormulario(true);
    
    try {
      // Cadastrar a venda
      const vendaCriada = await cadastrarVenda(formData);
      
      // Adicionar a venda à lista
      setVendas(prev => [...prev, vendaCriada]);
      
      // Fechar o modal
      setModalNovaVenda(false);
      
      // Mostrar mensagem de sucesso
      showSuccessToast("Venda cadastrada com sucesso!");
    } catch (err) {
      console.error("Erro ao cadastrar venda:", err);
      showErrorToast("Erro ao cadastrar venda. Tente novamente.");
    } finally {
      setEnviandoFormulario(false);
    }
  };

  return (
    <div className="vendas-page">
      <div className="page-header">
        <h1 className="page-title">Vendas e Parcelas</h1>
        <div className="page-actions">
          <button
            className="btn-primary"
            onClick={abrirModalNovaVenda}
          >
            Nova Venda
          </button>
        </div>
      </div>

      <div className="card mb-6">
        <div className="card-body">
          <h2 className="card-title">Vendas Registradas</h2>
          <DataStateHandler
            loading={loading}
            error={error}
            dataLength={vendas.length}
            onRetry={buscarVendas}
            emptyMessage="Nenhuma venda encontrada."
          >
            <Table
              columns={colunasVendas}
              data={vendas}
              emptyMessage="Nenhuma venda encontrada."
            />
          </DataStateHandler>
        </div>
      </div>

      {/* Modal de Detalhes da Venda */}
      <Modal
        isOpen={modalDetalhes}
        onClose={() => setModalDetalhes(false)}
        title="Detalhes da Venda"
        size="large"
      >
        {vendaSelecionada && (
          <div className="venda-detalhes">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-4">
              <div>
                <h3 className="text-lg font-semibold mb-2">Informações da Venda</h3>
                <p><strong>Cliente:</strong> {vendaSelecionada.nome_cliente || vendaSelecionada.cliente?.nome || "Cliente não informado"}</p>
                <p><strong>Data:</strong> {formatarData(vendaSelecionada.data_venda || vendaSelecionada.data_inicio || '')}</p>
                <p><strong>Valor Total:</strong> {formatarMoeda(vendaSelecionada.valor_total)}</p>
                <p><strong>Parcelas:</strong> {vendaSelecionada.numero_parcelas}</p>
              </div>
              <div>
                <h3 className="text-lg font-semibold mb-2">Status de Pagamento</h3>
                <p>
                  <strong>Status Atual:</strong> 
                  <span className={`status-badge ml-2 ${vendaSelecionada.status === 'paga' ? 'success' : vendaSelecionada.status === 'parcial' ? 'warning' : 'danger'}`}>
                    {vendaSelecionada.status === 'paga' ? 'Paga' : vendaSelecionada.status === 'parcial' ? 'Parcial' : 'Pendente'}
                  </span>
                </p>
                <p><strong>Valor Pago:</strong> {formatarMoeda(vendaSelecionada.valor_pago || 0)}</p>
                <p><strong>Valor Pendente:</strong> {formatarMoeda(vendaSelecionada.valor_total - (vendaSelecionada.valor_pago || 0))}</p>
              </div>
            </div>
            
            <h3 className="text-lg font-semibold mb-3">Parcelas</h3>
            <DataStateHandler
              loading={loadingParcelas}
              error={null}
              dataLength={parcelas.length}
              emptyMessage="Nenhuma parcela encontrada para esta venda."
            >
              <Table
                columns={colunasParcelas}
                data={parcelas}
                emptyMessage="Nenhuma parcela encontrada para esta venda."
              />
            </DataStateHandler>
          </div>
        )}
      </Modal>

      {/* Modal de Nova Venda */}
      <Modal
        isOpen={modalNovaVenda}
        onClose={() => setModalNovaVenda(false)}
        title="Cadastrar Nova Venda"
        size="large"
      >
        <VendasParcelasForm
          clientes={clientes}
          onSubmit={handleCadastrarVenda}
          onCancel={() => setModalNovaVenda(false)}
          isLoading={enviandoFormulario}
        />
      </Modal>

      {/* Modal de Confirmação de Exclusão */}
      <Modal
        isOpen={modalConfirmacao}
        onClose={() => setModalConfirmacao(false)}
        title="Confirmar Exclusão"
        size="small"
      >
        <div className="confirmation-modal">
          <p className="mb-4">Tem certeza que deseja excluir esta venda e todas as suas parcelas? Esta ação não pode ser desfeita.</p>
          <div className="flex justify-end gap-2">
            <button
              className="btn-outline"
              onClick={() => setModalConfirmacao(false)}
            >
              Cancelar
            </button>
            <button
              className="btn-danger"
              onClick={excluirVenda}
            >
              Excluir
            </button>
          </div>
        </div>
      </Modal>
    </div>
  );
} 