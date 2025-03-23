import { useEffect, useState } from "react";
import { Cliente } from "../types";
import { listarClientes } from "../services/clienteService";

export default function Clientes() {
  const [clientes, setClientes] = useState<Cliente[]>([]);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string>("");

  useEffect(() => {
    async function fetchData() {
      try {
        const data = await listarClientes();
        setClientes(data);
      } catch (err) {
        setError("Erro ao carregar os clientes.");
      } finally {
        setLoading(false);
      }
    }
    fetchData();
  }, []);

  if (loading) return <p className="placeholder-text">Carregando...</p>;
  if (error) return <p className="placeholder-text">{error}</p>;

  return (
    <div>
      <h1 className="page-title">Clientes</h1>
      
      {clientes.length === 0 ? (
        <p className="placeholder-text">Nenhum cliente encontrado.</p>
      ) : (
        <table>
          <thead>
            <tr>
              <th>Nome</th>
              <th>CPF/CNPJ</th>
              <th>Contato</th>
            </tr>
          </thead>
          <tbody>
            {clientes.map((cliente) => (
              <tr key={cliente.id_cliente}>
                <td>{cliente.nome}</td>
                <td>{cliente.cpf_cnpj}</td>
                <td>{cliente.contato}</td>
              </tr>
            ))}
          </tbody>
        </table>
      )}
    </div>
  );
} 