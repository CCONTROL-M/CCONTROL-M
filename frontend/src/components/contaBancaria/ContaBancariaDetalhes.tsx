import React from 'react';
import { ContaBancaria } from '../../types';

interface ContaBancariaDetalhesProps {
  conta: ContaBancaria;
}

/**
 * Componente para exibir detalhes de uma conta bancária
 */
export default function ContaBancariaDetalhes({ conta }: ContaBancariaDetalhesProps) {
  // Formatação de valores monetários
  const formatarMoeda = (valor: number) => {
    return valor.toLocaleString('pt-BR', { 
      style: 'currency', 
      currency: 'BRL' 
    });
  };

  // Formatação de data
  const formatarData = (dataString: string) => {
    if (!dataString) return 'Data não disponível';
    
    const data = new Date(dataString);
    return data.toLocaleDateString('pt-BR', {
      day: '2-digit',
      month: '2-digit',
      year: 'numeric'
    });
  };

  return (
    <div className="conta-bancaria-detalhes">
      <div className="mb-6">
        <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center mb-4">
          <h2 className="text-xl font-semibold">{conta.nome}</h2>
          <div className={`status-badge ${conta.ativa ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'} px-3 py-1 rounded-full text-sm font-medium`}>
            {conta.ativa ? 'Ativa' : 'Inativa'}
          </div>
        </div>
        
        <div className="saldo-info bg-gray-50 p-4 rounded-lg mb-6">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <p className="text-sm text-gray-500">Saldo Inicial</p>
              <p className="text-lg font-medium">{formatarMoeda(conta.saldo_inicial)}</p>
            </div>
            <div>
              <p className="text-sm text-gray-500">Saldo Atual</p>
              <p className={`text-lg font-medium ${conta.saldo_atual < 0 ? 'text-red-600' : 'text-green-600'}`}>
                {formatarMoeda(conta.saldo_atual)}
              </p>
            </div>
          </div>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <div className="info-section">
          <h3 className="text-md font-medium mb-3">Informações Bancárias</h3>
          <div className="space-y-3">
            <div className="info-item">
              <p className="text-sm text-gray-500">Banco</p>
              <p className="font-medium">{conta.banco}</p>
            </div>
            <div className="info-item">
              <p className="text-sm text-gray-500">Agência</p>
              <p className="font-medium">{conta.agencia}</p>
            </div>
            <div className="info-item">
              <p className="text-sm text-gray-500">Conta</p>
              <p className="font-medium">{conta.conta}</p>
            </div>
            <div className="info-item">
              <p className="text-sm text-gray-500">Tipo</p>
              <p className="font-medium">{conta.tipo === 'corrente' ? 'Conta Corrente' : 'Conta Poupança'}</p>
            </div>
          </div>
        </div>

        <div className="info-section">
          <h3 className="text-md font-medium mb-3">Configurações</h3>
          <div className="space-y-3">
            <div className="info-item">
              <p className="text-sm text-gray-500">Exibir no Dashboard</p>
              <p className="font-medium">{conta.mostrar_dashboard ? 'Sim' : 'Não'}</p>
            </div>
            <div className="info-item">
              <p className="text-sm text-gray-500">Data de Cadastro</p>
              <p className="font-medium">{formatarData(conta.created_at)}</p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
} 