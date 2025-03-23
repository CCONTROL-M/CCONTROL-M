import { useEffect, useState } from "react";
import api from "../services/api";
import { Usuario } from "../types";
import { formatarData } from "../utils/formatters";

export default function GestaoUsuarios() {
  const [usuarios, setUsuarios] = useState<Usuario[]>([]);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string>("");

  useEffect(() => {
    async function fetchUsuarios() {
      try {
        const response = await api.get("/usuarios");
        setUsuarios(response.data);
      } catch (err) {
        setError("Erro ao carregar os usuários.");
      } finally {
        setLoading(false);
      }
    }
    fetchUsuarios();
  }, []);

  if (loading) return <p className="placeholder-text">Carregando...</p>;
  if (error) return <p className="placeholder-text">{error}</p>;

  if (usuarios.length === 0) return <p className="placeholder-text">Nenhum usuário encontrado.</p>;

  return (
    <div>
      <h1 className="page-title">Gestão de Usuários</h1>
      <table>
        <thead>
          <tr>
            <th>Nome</th>
            <th>Email</th>
            <th>Tipo</th>
            <th>Criado em</th>
          </tr>
        </thead>
        <tbody>
          {usuarios.map((u) => (
            <tr key={u.id_usuario}>
              <td>{u.nome}</td>
              <td>{u.email}</td>
              <td>{u.tipo_usuario}</td>
              <td>{formatarData(u.created_at)}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
} 