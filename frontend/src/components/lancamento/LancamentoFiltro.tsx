import React from 'react';
import { ContaBancaria } from '../../types';
import useFormHandler from '../../hooks/useFormHandler';

export interface LancamentoFiltroForm {
  dataInicio: string;
  dataFim: string;
  tipo: string;
  status: string;
  id_conta_bancaria: string;
}

interface LancamentoFiltroProps {
  contasBancarias: ContaBancaria[];
  onFiltrar: (filtros: LancamentoFiltroForm) => void;
}

/**
 * Componente para filtrar lançamentos financeiros
 */
const LancamentoFiltro: React.FC<LancamentoFiltroProps> = ({ contasBancarias, onFiltrar }) => {
  // Obter o primeiro e último dia do mês atual para filtro padrão
  const primeiroDiaMes = new Date(
    new Date().getFullYear(),
    new Date().getMonth(),
    1
  ).toISOString().split('T')[0];
  
  const ultimoDiaMes = new Date(
    new Date().getFullYear(),
    new Date().getMonth() + 1,
    0
  ).toISOString().split('T')[0];

  // Estado inicial do filtro
  const filtroInicial: LancamentoFiltroForm = {
    dataInicio: primeiroDiaMes,
    dataFim: ultimoDiaMes,
    tipo: '',
    status: '',
    id_conta_bancaria: ''
  };

  // Usar o hook de formulário para gerenciar o estado do filtro
  const { formData, handleInputChange } = useFormHandler<LancamentoFiltroForm>(filtroInicial);

  // Manipular o envio do formulário de filtro
  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    onFiltrar(formData);
  };

  // Limpar todos os filtros
  const handleLimpar = () => {
    // Resetar para os valores iniciais (mês atual)
    onFiltrar(filtroInicial);
  };

  return (
    <div className="filtro-container bg-white p-4 rounded-md shadow-sm mb-4">
      <h3 className="text-lg font-semibold mb-3">Filtros</h3>
      
      <form onSubmit={handleSubmit} className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <div className="form-field">
          <label htmlFor="dataInicio">Data Inicial</label>
          <input
            type="date"
            id="dataInicio"
            name="dataInicio"
            value={formData.dataInicio}
            onChange={handleInputChange}
            className="form-input"
          />
        </div>
        
        <div className="form-field">
          <label htmlFor="dataFim">Data Final</label>
          <input
            type="date"
            id="dataFim"
            name="dataFim"
            value={formData.dataFim}
            onChange={handleInputChange}
            className="form-input"
          />
        </div>
        
        <div className="form-field">
          <label htmlFor="tipo">Tipo</label>
          <select
            id="tipo"
            name="tipo"
            value={formData.tipo}
            onChange={handleInputChange}
            className="form-select"
          >
            <option value="">Todos</option>
            <option value="receita">Receita</option>
            <option value="despesa">Despesa</option>
          </select>
        </div>
        
        <div className="form-field">
          <label htmlFor="status">Status</label>
          <select
            id="status"
            name="status"
            value={formData.status}
            onChange={handleInputChange}
            className="form-select"
          >
            <option value="">Todos</option>
            <option value="Pendente">Pendente</option>
            <option value="Pago">Pago</option>
            <option value="Recebido">Recebido</option>
            <option value="Agendado">Agendado</option>
            <option value="Cancelado">Cancelado</option>
          </select>
        </div>
        
        <div className="form-field">
          <label htmlFor="id_conta_bancaria">Conta Bancária</label>
          <select
            id="id_conta_bancaria"
            name="id_conta_bancaria"
            value={formData.id_conta_bancaria}
            onChange={handleInputChange}
            className="form-select"
          >
            <option value="">Todas</option>
            {contasBancarias.map(conta => (
              <option key={conta.id_conta} value={conta.id_conta}>
                {conta.nome} - {conta.banco}
              </option>
            ))}
          </select>
        </div>
        
        <div className="flex items-end space-x-2">
          <button 
            type="submit" 
            className="btn-primary"
          >
            Filtrar
          </button>
          <button 
            type="button" 
            className="btn-secondary"
            onClick={handleLimpar}
          >
            Limpar
          </button>
        </div>
      </form>
    </div>
  );
};

export default LancamentoFiltro; 