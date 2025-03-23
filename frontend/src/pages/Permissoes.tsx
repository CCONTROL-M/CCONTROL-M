import { useEffect, useState } from "react";
import api from "../services/api";
import { Permissao } from "../types";

// Estendendo a interface para incluir o nome do usuário
interface PermissaoUsuario extends Permissao {
  nome: string;
}

export default function Permissoes() {
  const [permissoes, setPermissoes] = useState<PermissaoUsuario[]>([]);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string>("");

  useEffect(() => {
    async function fetchPermissoes() {
      try {
        const response = await api.get("/usuarios/permissoes");
        setPermissoes(response.data);
      } catch (err) {
        setError("Erro ao carregar permissões.");
      } finally {
        setLoading(false);
      }
    }
    fetchPermissoes();
  }, []);

  if (loading) return <p className="placeholder-text">Carregando...</p>;
  if (error) return <p className="placeholder-text">{error}</p>;

  if (permissoes.length === 0) return <p className="placeholder-text">Nenhuma permissão registrada.</p>;

  return (
    <div>
      <h1 className="page-title">Permissões de Usuários</h1>
      <table>
        <thead>
          <tr>
            <th>Usuário</th>
            <th>Telas Permitidas</th>
          </tr>
        </thead>
        <tbody>
          {permissoes.map((p) => (
            <tr key={p.id_usuario}>
              <td>{p.nome}</td>
              <td>{p.telas_permitidas.join(", ")}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
} 