import React, { useState } from 'react';
import { Inadimplente } from '../../types';
import Modal from '../Modal';
import FormField from '../FormField';
import useFormHandler from '../../hooks/useFormHandler';
import { formatarData, formatarMoeda } from '../../utils/formatters';

interface AcaoInadimplenciaModalProps {
  parcela: Inadimplente | null;
  onClose: () => void;
  onSalvar: (dados: AcaoInadimplenciaForm, tipoAcao: 'cobranca' | 'renegociacao') => void;
  isLoading?: boolean;
}

interface AcaoInadimplenciaForm {
  observacao: string;
  dataNovoVencimento?: string;
  valorNovo?: number;
  dataContato: string;
  meioComunicacao: string;
  responsavel: string;
}

/**
 * Modal para gerenciar ações de cobrança ou renegociação de parcelas inadimplentes
 */
const AcaoInadimplenciaModal: React.FC<AcaoInadimplenciaModalProps> = ({
  parcela,
  onClose,
  onSalvar,
  isLoading = false
}) => {
  // Estado para controlar o tipo de ação selecionada
  const [tipoAcao, setTipoAcao] = useState<'cobranca' | 'renegociacao'>('cobranca');
  
  // Data atual formatada para os campos de data
  const dataAtual = new Date().toISOString().split('T')[0];
  
  // Valores iniciais do formulário
  const valoresIniciais: AcaoInadimplenciaForm = {
    observacao: '',
    dataNovoVencimento: parcela ? new Date(new Date().getTime() + 30 * 24 * 60 * 60 * 1000).toISOString().split('T')[0] : '',
    valorNovo: parcela?.valor || 0,
    dataContato: dataAtual,
    meioComunicacao: 'telefone',
    responsavel: ''
  };
  
  // Custom hook para gerenciar o formulário
  const { formData, handleInputChange, formErrors, setFormErrors, resetForm } = useFormHandler<AcaoInadimplenciaForm>(valoresIniciais);

  // Manipular mudança no tipo de ação
  const handleTipoAcaoChange = (tipo: 'cobranca' | 'renegociacao') => {
    setTipoAcao(tipo);
    setFormErrors({});
  };
  
  // Validar o formulário com base no tipo de ação
  const validarFormulario = () => {
    const erros: Record<string, string> = {};
    
    // Validações comuns para ambos os tipos
    if (!formData.observacao.trim()) {
      erros.observacao = 'Observação é obrigatória';
    }
    
    if (!formData.dataContato) {
      erros.dataContato = 'Data de contato é obrigatória';
    }
    
    if (!formData.meioComunicacao.trim()) {
      erros.meioComunicacao = 'Meio de comunicação é obrigatório';
    }
    
    if (!formData.responsavel.trim()) {
      erros.responsavel = 'Responsável é obrigatório';
    }
    
    // Validações específicas para renegociação
    if (tipoAcao === 'renegociacao') {
      if (!formData.dataNovoVencimento) {
        erros.dataNovoVencimento = 'Nova data de vencimento é obrigatória';
      }
      
      if (!formData.valorNovo || formData.valorNovo <= 0) {
        erros.valorNovo = 'Novo valor deve ser maior que zero';
      }
    }
    
    setFormErrors(erros);
    return Object.keys(erros).length === 0;
  };
  
  // Manipular envio do formulário
  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    
    if (validarFormulario()) {
      onSalvar(formData, tipoAcao);
    }
  };
  
  if (!parcela) return null;
  
  return (
    <Modal
      isOpen={!!parcela}
      onClose={onClose}
      title={tipoAcao === 'cobranca' ? 'Registrar Cobrança' : 'Renegociar Parcela'}
      size="large"
    >
      <div className="p-1">
        {/* Informações da parcela */}
        <div className="bg-gray-50 p-4 rounded-md mb-6">
          <h3 className="text-md font-semibold mb-3">Detalhes da Parcela</h3>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div>
              <p className="text-sm text-gray-500">Cliente</p>
              <p className="font-medium">{parcela.cliente}</p>
            </div>
            <div>
              <p className="text-sm text-gray-500">Valor Devido</p>
              <p className="font-medium text-red-600">
                {parcela.valor.toLocaleString('pt-BR', {
                  style: 'currency',
                  currency: 'BRL'
                })}
              </p>
            </div>
            <div>
              <p className="text-sm text-gray-500">Vencimento</p>
              <p className="font-medium">{new Date(parcela.vencimento).toLocaleDateString('pt-BR')}</p>
            </div>
            <div>
              <p className="text-sm text-gray-500">Dias em Atraso</p>
              <p className="font-medium text-red-600">{parcela.dias_em_atraso} dias</p>
            </div>
          </div>
        </div>
        
        {/* Botões de escolha do tipo de ação */}
        <div className="mb-6">
          <div className="flex space-x-2 mb-2">
            <button
              type="button"
              className={`flex-1 py-2 rounded-md ${
                tipoAcao === 'cobranca'
                  ? 'bg-blue-600 text-white'
                  : 'bg-gray-100 text-gray-700'
              }`}
              onClick={() => handleTipoAcaoChange('cobranca')}
            >
              Registrar Cobrança
            </button>
            <button
              type="button"
              className={`flex-1 py-2 rounded-md ${
                tipoAcao === 'renegociacao'
                  ? 'bg-blue-600 text-white'
                  : 'bg-gray-100 text-gray-700'
              }`}
              onClick={() => handleTipoAcaoChange('renegociacao')}
            >
              Renegociar Parcela
            </button>
          </div>
          <p className="text-sm text-gray-500">
            {tipoAcao === 'cobranca'
              ? 'Registre uma tentativa de cobrança para esta parcela em atraso.'
              : 'Defina novas condições de pagamento para esta parcela em atraso.'}
          </p>
        </div>
        
        {/* Formulário */}
        <form onSubmit={handleSubmit}>
          <div className="space-y-4">
            {/* Campos específicos para renegociação */}
            {tipoAcao === 'renegociacao' && (
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <FormField
                  label="Nova Data de Vencimento"
                  name="dataNovoVencimento"
                  type="date"
                  value={formData.dataNovoVencimento || ''}
                  onChange={handleInputChange}
                  error={formErrors.dataNovoVencimento}
                  required
                />
                
                <FormField
                  label="Novo Valor"
                  name="valorNovo"
                  type="number"
                  value={formData.valorNovo?.toString() || ''}
                  onChange={handleInputChange}
                  error={formErrors.valorNovo}
                  required
                  min={0}
                  step="0.01"
                />
              </div>
            )}
            
            {/* Campos comuns para ambos os tipos */}
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              <FormField
                label="Data do Contato"
                name="dataContato"
                type="date"
                value={formData.dataContato}
                onChange={handleInputChange}
                error={formErrors.dataContato}
                required
              />
              
              <div className="form-group">
                <label htmlFor="meioComunicacao" className="block text-sm font-medium text-gray-700 mb-1">
                  Meio de Comunicação
                </label>
                <select
                  id="meioComunicacao"
                  name="meioComunicacao"
                  value={formData.meioComunicacao}
                  onChange={handleInputChange}
                  className="form-select w-full rounded-md border-gray-300 shadow-sm focus:border-primary focus:ring focus:ring-primary focus:ring-opacity-50"
                >
                  <option value="telefone">Telefone</option>
                  <option value="email">E-mail</option>
                  <option value="whatsapp">WhatsApp</option>
                  <option value="presencial">Presencial</option>
                  <option value="carta">Carta</option>
                  <option value="outro">Outro</option>
                </select>
                {formErrors.meioComunicacao && (
                  <p className="mt-1 text-sm text-red-600">{formErrors.meioComunicacao}</p>
                )}
              </div>
              
              <FormField
                label="Responsável"
                name="responsavel"
                type="text"
                value={formData.responsavel}
                onChange={handleInputChange}
                error={formErrors.responsavel}
                required
                placeholder="Nome do responsável pelo contato"
              />
            </div>
            
            <FormField
              label="Observações"
              name="observacao"
              type="textarea"
              value={formData.observacao}
              onChange={handleInputChange}
              error={formErrors.observacao}
              required
              placeholder={
                tipoAcao === 'cobranca'
                  ? 'Descreva o resultado da tentativa de cobrança...'
                  : 'Descreva os detalhes da renegociação...'
              }
            />
          </div>
          
          <div className="flex justify-end space-x-2 mt-6">
            <button
              type="button"
              onClick={onClose}
              className="btn-secondary px-4 py-2 rounded-md border border-gray-300 text-sm font-medium"
              disabled={isLoading}
            >
              Cancelar
            </button>
            <button
              type="submit"
              className="btn-primary px-4 py-2 rounded-md bg-primary text-white text-sm font-medium"
              disabled={isLoading}
            >
              {isLoading ? 'Salvando...' : tipoAcao === 'cobranca' ? 'Registrar Cobrança' : 'Confirmar Renegociação'}
            </button>
          </div>
        </form>
      </div>
    </Modal>
  );
};

export default AcaoInadimplenciaModal; 