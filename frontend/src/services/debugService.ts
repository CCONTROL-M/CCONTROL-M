import api from './api';
import axios from 'axios';

/**
 * Função para verificar a saúde do backend
 * @returns Informações sobre o status do backend
 */
export async function verificarSaudeBackend() {
  try {
    // Usa o endpoint criado especificamente para testar a conexão
    const response = await axios.get('http://localhost:8000/api/v1/health');
    
    return {
      status: 'ok',
      statusCode: response.status,
      message: 'Backend conectado com sucesso',
      data: response.data
    };
  } catch (error: any) {
    console.error('Erro ao verificar a saúde do backend:', error);
    
    return {
      status: 'error',
      statusCode: error.response?.status || 0,
      message: error.message || 'Erro desconhecido',
      detalhes: {
        nomeDaErro: error.name,
        mensagem: error.message,
        temResposta: !!error.response,
        temRequest: !!error.request,
        ehCORS: error.message.includes('CORS') || false
      }
    };
  }
}

/**
 * Função para testar uma chamada específica da API
 * @param endpoint Endpoint a ser testado
 * @returns Resultado do teste
 */
export async function testarChamadaAPI(endpoint: string) {
  try {
    // Usa a instância configurada da API
    const response = await api.get(endpoint);
    
    return {
      status: 'ok',
      statusCode: response.status,
      message: `Chamada para ${endpoint} bem-sucedida`,
      data: response.data
    };
  } catch (error: any) {
    console.error(`Erro ao chamar endpoint ${endpoint}:`, error);
    
    return {
      status: 'error',
      statusCode: error.response?.status || 0,
      message: `Erro ao chamar ${endpoint}: ${error.message || 'Erro desconhecido'}`,
      detalhes: {
        endpoint,
        nomeDaErro: error.name,
        mensagem: error.message,
        temResposta: !!error.response,
        statusResposta: error.response?.status,
        dadosResposta: error.response?.data,
        temRequest: !!error.request
      }
    };
  }
}

/**
 * Função para verificar a conexão com vários endpoints importantes
 */
export async function diagnosticarProblemas() {
  const resultados = {
    saude: await verificarSaudeBackend(),
    vendas: await testarChamadaAPI('/vendas'),
    clientes: await testarChamadaAPI('/clientes'),
    categorias: await testarChamadaAPI('/categorias'),
    formasPagamento: await testarChamadaAPI('/formas-pagamento')
  };
  
  return {
    todosOK: Object.values(resultados).every(r => r.status === 'ok'),
    resultados
  };
} 