import React, { useEffect, useState } from 'react';
import { Cliente } from '../../types';
import { listarClientes } from '../../services/clienteService';
import useFormHandler from '../../hooks/useFormHandler';
import FormField from '../FormField';

// Interface para o formulário de filtro
interface InadimplenciaFiltroForm {
  dataInicio: string;
  dataFim: string;
  id_cliente?: string;
}

interface InadimplenciaFiltroProps {
  onFiltrar: (filtros: InadimplenciaFiltroForm) => void;
}

/**
 * Componente de filtro para a página de inadimplência
 */
const InadimplenciaFiltro: React.FC<InadimplenciaFiltroProps> = ({ onFiltrar }) => {
  // Estado para armazenar a lista de clientes
  const [clientes, setClientes] = useState<Cliente[]>([]);
  const [carregandoClientes, setCarregandoClientes] = useState(false);

  // Obter o primeiro e último dia do mês atual para os filtros padrão
  const dataAtual = new Date();
  const primeiroDiaDoMes = new Date(dataAtual.getFullYear(), dataAtual.getMonth(), 1)
    .toISOString().split('T')[0];
  const ultimoDiaDoMes = new Date(dataAtual.getFullYear(), dataAtual.getMonth() + 1, 0)
    .toISOString().split('T')[0];

  // Valores iniciais do formulário
  const valoresIniciais: InadimplenciaFiltroForm = {
    dataInicio: primeiroDiaDoMes,
    dataFim: ultimoDiaDoMes,
    id_cliente: undefined
  };

  // Usar o hook de formulário para gerenciar os valores
  const { formData, handleInputChange, resetForm } = useFormHandler<InadimplenciaFiltroForm>(valoresIniciais);

  // Buscar a lista de clientes ao montar o componente
  useEffect(() => {
    const buscarClientes = async () => {
      setCarregandoClientes(true);
      try {
        const clientesData = await listarClientes();
        setClientes(clientesData);
      } catch (error) {
        console.error('Erro ao buscar clientes:', error);
      } finally {
        setCarregandoClientes(false);
      }
    };

    buscarClientes();
  }, []);

  // Função para limpar os filtros
  const handleLimpar = () => {
    resetForm();
    onFiltrar(valoresIniciais);
  };

  // Função para lidar com o envio do formulário
  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    onFiltrar(formData);
  };

  return (
    <div className="filtro-container p-4 bg-white rounded-lg shadow-sm mb-6">
      <h2 className="text-lg font-semibold mb-4">Filtrar Inadimplência</h2>
      
      <form onSubmit={handleSubmit} className="space-y-4">
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          {/* Filtro de período - Data Início */}
          <FormField
            label="Data Início"
            name="dataInicio"
            type="date"
            value={formData.dataInicio}
            onChange={handleInputChange}
            required
          />
          
          {/* Filtro de período - Data Fim */}
          <FormField
            label="Data Fim"
            name="dataFim"
            type="date"
            value={formData.dataFim}
            onChange={handleInputChange}
            required
          />
          
          {/* Filtro de cliente */}
          <div className="form-group">
            <label htmlFor="id_cliente" className="block text-sm font-medium text-gray-700 mb-1">
              Cliente
            </label>
            <select
              id="id_cliente"
              name="id_cliente"
              value={formData.id_cliente || ''}
              onChange={handleInputChange}
              className="form-select w-full rounded-md border-gray-300 shadow-sm focus:border-primary focus:ring focus:ring-primary focus:ring-opacity-50"
            >
              <option value="">Todos os clientes</option>
              {clientes.map((cliente) => (
                <option key={cliente.id_cliente} value={cliente.id_cliente}>
                  {cliente.nome}
                </option>
              ))}
            </select>
          </div>
        </div>
        
        <div className="flex justify-end space-x-2 pt-2">
          <button
            type="button"
            onClick={handleLimpar}
            className="btn-secondary px-4 py-2 rounded-md border border-gray-300 text-sm font-medium"
          >
            Limpar Filtros
          </button>
          <button
            type="submit"
            className="btn-primary px-4 py-2 rounded-md bg-primary text-white text-sm font-medium"
          >
            Aplicar Filtros
          </button>
        </div>
      </form>
    </div>
  );
};

export default InadimplenciaFiltro; 