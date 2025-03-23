import { useState, useEffect } from 'react';
import axios from 'axios';
import { diagnosticarProblemas } from '../services/debugService';

export default function TesteCors() {
  const [status, setStatus] = useState<string>('');
  const [error, setError] = useState<string>('');
  const [diagnostico, setDiagnostico] = useState<any>(null);
  const [mostrarDiagnostico, setMostrarDiagnostico] = useState<boolean>(false);

  useEffect(() => {
    // Testar conexão direta com o backend
    const testBackendConnection = async () => {
      try {
        setStatus('Testando conexão...');
        
        // Testar chamada direta (sem instância api configurada)
        const response = await axios.get('http://localhost:8000/api/v1/health', {
          headers: {
            'Content-Type': 'application/json'
          }
        });
        
        setStatus(`Conexão OK! Status: ${response.status}`);
        console.log('Resposta do servidor:', response.data);
      } catch (err: any) {
        console.error('Erro ao conectar com o backend:', err);
        
        if (err.message && err.message.includes('CORS')) {
          setError(`Erro de CORS: ${err.message}`);
        } else if (err.response) {
          setError(`Erro ${err.response.status}: ${err.response.statusText}`);
        } else if (err.request) {
          setError('Sem resposta do servidor. O servidor está rodando?');
        } else {
          setError(`Erro: ${err.message || 'Erro desconhecido'}`);
        }
      }
    };

    testBackendConnection();
  }, []);

  const executarDiagnostico = async () => {
    setMostrarDiagnostico(true);
    const resultado = await diagnosticarProblemas();
    setDiagnostico(resultado);
  };

  return (
    <div style={{ padding: '20px' }}>
      <h1>Teste de Conexão com Backend</h1>
      
      {status && (
        <p style={{ color: 'green' }}><strong>Status:</strong> {status}</p>
      )}
      
      {error && (
        <div style={{ color: 'red', marginTop: '20px' }}>
          <h3>Erro detectado:</h3>
          <p>{error}</p>
          
          <div style={{ marginTop: '20px', padding: '15px', backgroundColor: '#f8f8f8', borderRadius: '5px' }}>
            <h4>Soluções comuns para problemas de CORS:</h4>
            <ol>
              <li>Verifique se o backend está rodando na porta 8000</li>
              <li>Confirme que a configuração CORS no backend permite requisições de http://localhost:3003</li>
              <li>Teste com uma extensão do navegador que desabilita CORS (apenas para desenvolvimento)</li>
              <li>Reinicie ambos os servidores (frontend e backend)</li>
            </ol>
          </div>
        </div>
      )}

      <div style={{ marginTop: '30px' }}>
        <button 
          onClick={executarDiagnostico} 
          style={{ 
            padding: '8px 16px', 
            backgroundColor: '#4CAF50', 
            color: 'white', 
            border: 'none', 
            borderRadius: '4px',
            cursor: 'pointer' 
          }}
        >
          Executar Diagnóstico Detalhado
        </button>
        
        {mostrarDiagnostico && diagnostico && (
          <div style={{ marginTop: '20px' }}>
            <h3>Resultado do Diagnóstico</h3>
            <p>Status Geral: {diagnostico.todosOK ? 'Todos endpoints OK' : 'Há problemas em pelo menos um endpoint'}</p>
            
            <div style={{ marginTop: '15px' }}>
              <h4>Endpoint de Saúde (Health Check)</h4>
              <div style={{ 
                padding: '10px', 
                backgroundColor: diagnostico.resultados.saude.status === 'ok' ? '#E8F5E9' : '#FFEBEE',
                borderRadius: '4px'
              }}>
                <p><strong>Status:</strong> {diagnostico.resultados.saude.status}</p>
                <p><strong>Mensagem:</strong> {diagnostico.resultados.saude.message}</p>
                {diagnostico.resultados.saude.data && (
                  <pre style={{ background: '#f0f0f0', padding: '10px', borderRadius: '4px' }}>
                    {JSON.stringify(diagnostico.resultados.saude.data, null, 2)}
                  </pre>
                )}
              </div>
            </div>
            
            <div style={{ marginTop: '15px' }}>
              <h4>Endpoint de Vendas</h4>
              <div style={{ 
                padding: '10px', 
                backgroundColor: diagnostico.resultados.vendas.status === 'ok' ? '#E8F5E9' : '#FFEBEE',
                borderRadius: '4px'
              }}>
                <p><strong>Status:</strong> {diagnostico.resultados.vendas.status}</p>
                <p><strong>Mensagem:</strong> {diagnostico.resultados.vendas.message}</p>
                {diagnostico.resultados.vendas.status === 'error' && diagnostico.resultados.vendas.detalhes && (
                  <details>
                    <summary>Detalhes do erro</summary>
                    <pre style={{ background: '#f0f0f0', padding: '10px', borderRadius: '4px' }}>
                      {JSON.stringify(diagnostico.resultados.vendas.detalhes, null, 2)}
                    </pre>
                  </details>
                )}
              </div>
            </div>
            
            <div style={{ marginTop: '15px' }}>
              <h4>Outros Endpoints</h4>
              <table style={{ width: '100%', borderCollapse: 'collapse' }}>
                <thead>
                  <tr style={{ backgroundColor: '#f0f0f0' }}>
                    <th style={{ padding: '8px', textAlign: 'left', border: '1px solid #ddd' }}>Endpoint</th>
                    <th style={{ padding: '8px', textAlign: 'left', border: '1px solid #ddd' }}>Status</th>
                    <th style={{ padding: '8px', textAlign: 'left', border: '1px solid #ddd' }}>Código</th>
                  </tr>
                </thead>
                <tbody>
                  <tr>
                    <td style={{ padding: '8px', border: '1px solid #ddd' }}>Clientes</td>
                    <td style={{ 
                      padding: '8px', 
                      border: '1px solid #ddd', 
                      backgroundColor: diagnostico.resultados.clientes.status === 'ok' ? '#E8F5E9' : '#FFEBEE' 
                    }}>
                      {diagnostico.resultados.clientes.status}
                    </td>
                    <td style={{ padding: '8px', border: '1px solid #ddd' }}>
                      {diagnostico.resultados.clientes.statusCode || 'N/A'}
                    </td>
                  </tr>
                  <tr>
                    <td style={{ padding: '8px', border: '1px solid #ddd' }}>Categorias</td>
                    <td style={{ 
                      padding: '8px', 
                      border: '1px solid #ddd', 
                      backgroundColor: diagnostico.resultados.categorias.status === 'ok' ? '#E8F5E9' : '#FFEBEE' 
                    }}>
                      {diagnostico.resultados.categorias.status}
                    </td>
                    <td style={{ padding: '8px', border: '1px solid #ddd' }}>
                      {diagnostico.resultados.categorias.statusCode || 'N/A'}
                    </td>
                  </tr>
                  <tr>
                    <td style={{ padding: '8px', border: '1px solid #ddd' }}>Formas de Pagamento</td>
                    <td style={{ 
                      padding: '8px', 
                      border: '1px solid #ddd', 
                      backgroundColor: diagnostico.resultados.formasPagamento.status === 'ok' ? '#E8F5E9' : '#FFEBEE' 
                    }}>
                      {diagnostico.resultados.formasPagamento.status}
                    </td>
                    <td style={{ padding: '8px', border: '1px solid #ddd' }}>
                      {diagnostico.resultados.formasPagamento.statusCode || 'N/A'}
                    </td>
                  </tr>
                </tbody>
              </table>
            </div>
          </div>
        )}
      </div>
    </div>
  );
} 