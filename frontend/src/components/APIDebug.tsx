import { useState } from 'react';
import api from '../services/api';
import { APIResponse } from '../types';

export default function APIDebug() {
  const [endpoint, setEndpoint] = useState<string>('/api/v1/centros-custo');
  const [response, setResponse] = useState<APIResponse | null>(null);
  const [loading, setLoading] = useState<boolean>(false);

  const testConnection = async () => {
    setLoading(true);
    setResponse(null);
    
    try {
      const res = await api.get(endpoint);
      setResponse({
        status: res.status,
        data: res.data
      });
    } catch (error: any) {
      console.error('Erro na requisição:', error);
      setResponse({
        status: error.response?.status || 0,
        data: error.response?.data || {},
        error: error.message || 'Erro desconhecido'
      });
    } finally {
      setLoading(false);
    }
  };

  return (
    <div style={{ 
      border: '1px solid #ccc', 
      padding: '15px', 
      margin: '15px 0', 
      borderRadius: '4px',
      backgroundColor: '#f8f9fa' 
    }}>
      <h3>Diagnóstico de API</h3>
      <div style={{ display: 'flex', marginBottom: '10px' }}>
        <input
          type="text"
          value={endpoint}
          onChange={(e) => setEndpoint(e.target.value)}
          style={{ flex: 1, marginRight: '10px', padding: '5px' }}
          placeholder="Endpoint da API (ex: /api/v1/centros-custo)"
        />
        <button 
          onClick={testConnection}
          disabled={loading}
          style={{ 
            padding: '5px 10px',
            backgroundColor: '#007bff',
            color: 'white',
            border: 'none',
            borderRadius: '4px',
            cursor: 'pointer'
          }}
        >
          {loading ? 'Testando...' : 'Testar Conexão'}
        </button>
      </div>

      {response && (
        <div style={{ 
          marginTop: '10px', 
          padding: '10px', 
          backgroundColor: response.status >= 200 && response.status < 300 ? '#d4edda' : '#f8d7da',
          borderRadius: '4px'
        }}>
          <p><strong>Status:</strong> {response.status}</p>
          {response.error && <p><strong>Erro:</strong> {response.error}</p>}
          <div>
            <strong>Dados:</strong>
            <pre style={{ 
              backgroundColor: '#f1f1f1', 
              padding: '10px', 
              overflow: 'auto', 
              maxHeight: '200px' 
            }}>
              {JSON.stringify(response.data, null, 2)}
            </pre>
          </div>
        </div>
      )}

      <div style={{ marginTop: '15px' }}>
        <h4>Informações de Ambiente</h4>
        <ul style={{ paddingLeft: '20px' }}>
          <li><strong>Base URL:</strong> {api.defaults.baseURL}</li>
          <li><strong>Token:</strong> {localStorage.getItem('token') ? '✅ Presente' : '❌ Ausente'}</li>
          <li><strong>Navegador:</strong> {navigator.userAgent}</li>
        </ul>
      </div>
    </div>
  );
} 