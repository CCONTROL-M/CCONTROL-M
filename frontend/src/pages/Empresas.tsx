import { useEffect, useState } from "react";
import api from "../services/api";
import APIDebug from "../components/APIDebug";
import { Empresa as EmpresaBase } from "../types";

// Estende a interface base para incluir campos específicos desta página
interface Empresa extends EmpresaBase {
  razao_social: string;
  nome_fantasia?: string;
  ativo: boolean;
  cidade?: string;
  estado?: string;
}

export default function Empresas() {
  const [empresas, setEmpresas] = useState<Empresa[]>([]);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string>("");
  const [showDebug, setShowDebug] = useState<boolean>(false);

  useEffect(() => {
    async function fetchEmpresas() {
      try {
        setLoading(true);
        const response = await api.get("/api/v1/empresas");
        setEmpresas(response.data.items || response.data);
        setError("");
      } catch (err) {
        console.error("Erro ao carregar empresas:", err);
        setError("Erro ao carregar empresas. Verifique a conexão com o servidor.");
      } finally {
        setLoading(false);
      }
    }
    fetchEmpresas();
  }, []);

  return (
    <div>
      <h1 className="page-title">Empresas</h1>
      
      <button 
        onClick={() => setShowDebug(!showDebug)}
        style={{ 
          padding: '5px 10px', 
          marginBottom: '10px',
          backgroundColor: '#6c757d',
          color: 'white',
          border: 'none',
          borderRadius: '4px',
          cursor: 'pointer'
        }}
      >
        {showDebug ? 'Ocultar Diagnóstico' : 'Mostrar Diagnóstico'}
      </button>
      
      {showDebug && <APIDebug />}
      
      {loading && <p className="placeholder-text">Carregando...</p>}
      
      {error && <p className="placeholder-text error-message">{error}</p>}
      
      {!loading && !error && empresas.length === 0 ? (
        <p className="placeholder-text">Nenhuma empresa encontrada.</p>
      ) : (
        <table className="data-table">
          <thead>
            <tr>
              <th>Razão Social</th>
              <th>Nome Fantasia</th>
              <th>CNPJ</th>
              <th>Cidade/UF</th>
              <th>Status</th>
            </tr>
          </thead>
          <tbody>
            {empresas.map((empresa) => (
              <tr key={empresa.id_empresa}>
                <td>{empresa.razao_social}</td>
                <td>{empresa.nome_fantasia || '-'}</td>
                <td>{empresa.cnpj}</td>
                <td>
                  {empresa.cidade && empresa.estado 
                    ? `${empresa.cidade}/${empresa.estado}`
                    : empresa.cidade || empresa.estado || '-'
                  }
                </td>
                <td>{empresa.ativo ? "Ativa" : "Inativa"}</td>
              </tr>
            ))}
          </tbody>
        </table>
      )}
    </div>
  );
} 