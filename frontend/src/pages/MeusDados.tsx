import { useEffect, useState } from "react";
import api from "../services/api";
import { Usuario } from "../types";
import { formatarData } from "../utils/formatters";

export default function MeusDados() {
  const [usuario, setUsuario] = useState<Usuario | null>(null);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string>("");

  useEffect(() => {
    async function fetchUsuario() {
      try {
        const response = await api.get("/usuarios/me");
        setUsuario(response.data);
      } catch (err) {
        setError("Erro ao carregar os dados do usuário.");
      } finally {
        setLoading(false);
      }
    }
    fetchUsuario();
  }, []);

  if (loading) return <p className="placeholder-text">Carregando...</p>;
  if (error) return <p className="placeholder-text">{error}</p>;

  if (!usuario) return <p className="placeholder-text">Nenhum dado encontrado.</p>;

  return (
    <div>
      <h1 className="page-title">Meus Dados</h1>
      <ul className="data-list">
        <li><strong>Nome:</strong> {usuario.nome}</li>
        <li><strong>Email:</strong> {usuario.email}</li>
        <li><strong>Tipo de Usuário:</strong> {usuario.tipo_usuario}</li>
        <li><strong>Criado em:</strong> {formatarData(usuario.created_at)}</li>
      </ul>
    </div>
  );
} 