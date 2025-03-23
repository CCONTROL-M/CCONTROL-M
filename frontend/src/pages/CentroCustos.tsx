import { useEffect, useState } from "react";
import api from "../services/api";
import APIDebug from "../components/APIDebug";
import { CentroCusto } from "../types";

export default function CentroCustos() {
  const [centros, setCentros] = useState<CentroCusto[]>([]);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string>("");
  const [showDebug, setShowDebug] = useState<boolean>(false);

  useEffect(() => {
    async function fetchCentros() {
      try {
        const response = await api.get("/api/v1/centros-custo");
        setCentros(response.data.items || response.data);
      } catch (err) {
        console.error("Erro ao carregar centros de custo:", err);
        setError("Erro ao carregar os centros de custo.");
      } finally {
        setLoading(false);
      }
    }
    fetchCentros();
  }, []);

  if (loading) return <p className="placeholder-text">Carregando...</p>;

  return (
    <div>
      <h1 className="page-title">Centro de Custos</h1>
      
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
      
      {error && <p className="placeholder-text error-message">{error}</p>}
      
      {!error && centros.length === 0 ? (
        <p className="placeholder-text">Nenhum centro de custo encontrado.</p>
      ) : (
        <table>
          <thead>
            <tr>
              <th>Nome</th>
            </tr>
          </thead>
          <tbody>
            {centros.map((c) => (
              <tr key={c.id_centro}>
                <td>{c.nome}</td>
              </tr>
            ))}
          </tbody>
        </table>
      )}
    </div>
  );
} 