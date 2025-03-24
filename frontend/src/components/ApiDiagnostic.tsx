import React, { useState, useEffect } from 'react';
import { useApiStatus } from '../contexts/ApiStatusContext';
import { getApiErrorReport, useMock, toggleMock } from '../utils/mock';
import { verificarStatusAPI } from '../services/api';

/**
 * Componente de diagnóstico da API
 * 
 * Exibe informações detalhadas sobre o estado da API e
 * fornece ferramentas para diagnosticar e resolver problemas
 */
const ApiDiagnostic: React.FC = () => {
  const { apiOnline, mensagemErro, ultimaVerificacao, forcarVerificacao } = useApiStatus();
  const [showDetails, setShowDetails] = useState(false);
  const [apiErrors, setApiErrors] = useState<Record<string, any>>({});
  const [diagnosticRunning, setDiagnosticRunning] = useState(false);
  const [diagnosticResults, setDiagnosticResults] = useState<string[]>([]);
  
  // Atualizar erros de API quando exibir detalhes
  useEffect(() => {
    if (showDetails) {
      setApiErrors(getApiErrorReport());
      
      // Agendar atualizações periódicas
      const interval = setInterval(() => {
        setApiErrors(getApiErrorReport());
      }, 3000);
      
      return () => clearInterval(interval);
    }
  }, [showDetails]);
  
  // Executar diagnóstico da API
  const runDiagnostic = async () => {
    setDiagnosticRunning(true);
    setDiagnosticResults([]);
    
    try {
      // Testar conexão com a API
      addDiagnosticStep('Testando conexão com a API...');
      const apiStatus = await verificarStatusAPI();
      
      if (apiStatus.online) {
        addDiagnosticStep('✅ API está acessível');
      } else {
        addDiagnosticStep('❌ API não está acessível');
        addDiagnosticStep(`Erro: ${apiStatus.error?.message || 'Desconhecido'}`);
        
        // Sugestões de resolução
        addDiagnosticStep('');
        addDiagnosticStep('📋 Sugestões para resolver:');
        addDiagnosticStep('1. Verifique se o servidor backend está rodando');
        addDiagnosticStep('2. Verifique se a URL da API está correta');
        addDiagnosticStep('3. Verifique se não há problemas de CORS');
        addDiagnosticStep('4. Ative o modo Mock temporariamente para continuar trabalhando');
      }
    } catch (error) {
      addDiagnosticStep(`❌ Erro durante diagnóstico: ${error instanceof Error ? error.message : String(error)}`);
    } finally {
      setDiagnosticRunning(false);
    }
  };
  
  // Adicionar um passo ao diagnóstico
  const addDiagnosticStep = (message: string) => {
    setDiagnosticResults(prev => [...prev, message]);
  };
  
  // Formatar data para exibição
  const formatDate = (date: Date | null) => {
    if (!date) return 'Nunca';
    return date.toLocaleTimeString();
  };
  
  // Componente que exibe os erros de API
  const ApiErrorsDisplay = () => {
    const errorEntries = Object.entries(apiErrors);
    
    if (errorEntries.length === 0) {
      return <p className="text-green-600">Nenhum erro de API registrado até o momento.</p>;
    }
    
    return (
      <div className="api-errors-list">
        <h4 className="text-red-600 font-bold mb-2">Erros de API registrados</h4>
        <ul className="space-y-2">
          {errorEntries.map(([endpoint, data]) => (
            <li key={endpoint} className="border-l-4 border-red-400 pl-2 py-1">
              <p className="font-bold">{endpoint}</p>
              <p>Ocorrências: {data.count}</p>
              <p>Última mensagem: {data.lastMessage}</p>
              <p>Último erro: {new Date(data.timestamp).toLocaleString()}</p>
            </li>
          ))}
        </ul>
      </div>
    );
  };
  
  return (
    <div className="api-diagnostic p-4 border rounded-lg bg-gray-50 shadow-sm">
      <h2 className="text-xl font-bold mb-2">Diagnóstico de API</h2>
      
      <div className="status-summary flex flex-col sm:flex-row justify-between items-start sm:items-center mb-4">
        <div>
          <p className="mb-1">
            <span className="font-bold">Status:</span>{' '}
            <span className={apiOnline ? 'text-green-600' : 'text-red-600'}>
              {apiOnline ? 'Online' : 'Offline'}
            </span>
          </p>
          <p className="mb-1">
            <span className="font-bold">Modo Mock:</span>{' '}
            <span className={useMock() ? 'text-yellow-600' : 'text-blue-600'}>
              {useMock() ? 'Ativado' : 'Desativado'}
            </span>
          </p>
          <p className="text-sm text-gray-600">
            Última verificação: {formatDate(ultimaVerificacao)}
          </p>
        </div>
        
        <div className="action-buttons mt-3 sm:mt-0 space-x-2">
          <button 
            onClick={() => toggleMock()}
            className="px-3 py-1 bg-yellow-500 text-white rounded hover:bg-yellow-600"
          >
            {useMock() ? 'Desativar Mock' : 'Ativar Mock'}
          </button>
          <button 
            onClick={() => forcarVerificacao()}
            className="px-3 py-1 bg-blue-500 text-white rounded hover:bg-blue-600"
          >
            Verificar API
          </button>
        </div>
      </div>
      
      {mensagemErro && (
        <div className="error-message p-2 bg-red-100 text-red-800 rounded mb-4">
          <p className="font-bold">Erro:</p>
          <p>{mensagemErro}</p>
        </div>
      )}
      
      <div className="diagnostic-actions mb-4">
        <button 
          onClick={() => setShowDetails(!showDetails)}
          className="text-blue-600 underline hover:text-blue-800"
        >
          {showDetails ? 'Ocultar detalhes' : 'Mostrar detalhes'}
        </button>
        {' | '}
        <button 
          onClick={runDiagnostic}
          disabled={diagnosticRunning}
          className="text-blue-600 underline hover:text-blue-800 disabled:text-gray-400"
        >
          {diagnosticRunning ? 'Executando diagnóstico...' : 'Executar diagnóstico'}
        </button>
      </div>
      
      {showDetails && (
        <div className="details mt-4 p-3 bg-gray-100 rounded border">
          <h3 className="font-bold mb-2">Detalhes de Diagnóstico</h3>
          <ApiErrorsDisplay />
        </div>
      )}
      
      {diagnosticResults.length > 0 && (
        <div className="diagnostic-results mt-4 p-3 bg-gray-100 rounded border">
          <h3 className="font-bold mb-2">Resultados do Diagnóstico</h3>
          <pre className="whitespace-pre-wrap text-sm font-mono bg-white p-2 rounded">
            {diagnosticResults.join('\n')}
          </pre>
        </div>
      )}
    </div>
  );
};

export default ApiDiagnostic; 