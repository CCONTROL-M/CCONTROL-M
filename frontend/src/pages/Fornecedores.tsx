import { useEffect, useState } from "react";
import api from "../services/api";
import { Fornecedor } from "../types";

export default function Fornecedores() {
  const [fornecedores, setFornecedores] = useState<Fornecedor[]>([]);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string>("");

  useEffect(() => {
    async function fetchFornecedores() {
      try {
        const response = await api.get("/fornecedores");
        setFornecedores(response.data);
      } catch (err) {
        setError("Erro ao carregar os fornecedores.");
      } finally {
        setLoading(false);
      }
    }
    fetchFornecedores();
  }, []);

  if (loading) return <p className="placeholder-text">Carregando...</p>;
  if (error) return <p className="placeholder-text">{error}</p>;

  return (
    <div>
      <h1 className="page-title">Fornecedores</h1>
      
      {fornecedores.length === 0 ? (
        <p className="placeholder-text">Nenhum fornecedor encontrado.</p>
      ) : (
        <table>
          <thead>
            <tr>
              <th>Nome</th>
              <th>CNPJ</th>
              <th>Contato</th>
              <th>Avaliação</th>
            </tr>
          </thead>
          <tbody>
            {fornecedores.map((f) => (
              <tr key={f.id_fornecedor}>
                <td>{f.nome}</td>
                <td>{f.cnpj}</td>
                <td>{f.contato}</td>
                <td>{f.avaliacao}</td>
              </tr>
            ))}
          </tbody>
        </table>
      )}
    </div>
  );
} 