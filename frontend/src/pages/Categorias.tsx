import { useEffect, useState } from "react";
import api from "../services/api";
import { Categoria } from "../types";

export default function Categorias() {
  const [categorias, setCategorias] = useState<Categoria[]>([]);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string>("");

  useEffect(() => {
    async function fetchCategorias() {
      try {
        const response = await api.get("/categorias");
        setCategorias(response.data);
      } catch (err) {
        setError("Erro ao carregar as categorias.");
      } finally {
        setLoading(false);
      }
    }
    fetchCategorias();
  }, []);

  if (loading) return <p className="placeholder-text">Carregando...</p>;
  if (error) return <p className="placeholder-text">{error}</p>;

  return (
    <div>
      <h1 className="page-title">Categorias</h1>
      
      {categorias.length === 0 ? (
        <p className="placeholder-text">Nenhuma categoria encontrada.</p>
      ) : (
        <table>
          <thead>
            <tr>
              <th>Nome</th>
            </tr>
          </thead>
          <tbody>
            {categorias.map((cat) => (
              <tr key={cat.id_categoria}>
                <td>{cat.nome}</td>
              </tr>
            ))}
          </tbody>
        </table>
      )}
    </div>
  );
} 