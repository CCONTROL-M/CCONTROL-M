import { useState, useEffect } from 'react';
import { ResumoDashboard } from '../types';
import api from '../services/api';
import { listarEmpresas } from '../services/empresaService';
import { getToken } from '../utils/auth';

// Estado inicial para o resumo
const resumoInicial: ResumoDashboard = {
  caixa_atual: 0,
  total_receber: 0,
  total_pagar: 0,
  recebimentos_hoje: 0,
  pagamentos_hoje: 0
};

interface DashboardDataHookResult {
  resumo: ResumoDashboard;
  loading: boolean;
  error: string | null;
  fetchData: () => Promise<void>;
  empresaId: string | null;
}

/**
 * Hook personalizado para buscar dados do dashboard
 * 
 * @param id_empresa ID da empresa para buscar dados (opcional)
 * @returns Objeto com dados do dashboard e funções de controle
 */
export function useDashboardData(id_empresa?: string): DashboardDataHookResult {
  const [resumo, setResumo] = useState<ResumoDashboard>(resumoInicial);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);
  const [empresaId, setEmpresaId] = useState<string | null>(id_empresa || null);
  
  // Função para buscar o ID da primeira empresa quando não for fornecido
  const buscarPrimeiraEmpresa = async (): Promise<string | null> => {
    try {
      const empresas = await listarEmpresas();
      if (empresas.length > 0) {
        const primeiraEmpresa = empresas[0];
        console.log(`Nenhum ID de empresa fornecido. Usando a primeira empresa encontrada: ${primeiraEmpresa.nome} (${primeiraEmpresa.id_empresa})`);
        return primeiraEmpresa.id_empresa;
      }
      return null;
    } catch (err) {
      console.error('Erro ao buscar empresas:', err);
      return null;
    }
  };
  
  // Função para buscar dados do dashboard
  const fetchData = async (): Promise<void> => {
    try {
      setLoading(true);
      setError(null);
      
      // Se não tiver empresa definida, buscar a primeira
      let idEmpresaAtual = empresaId;
      if (!idEmpresaAtual) {
        idEmpresaAtual = await buscarPrimeiraEmpresa();
        if (idEmpresaAtual) {
          setEmpresaId(idEmpresaAtual);
        } else {
          throw new Error('Não foi possível determinar uma empresa. Cadastre uma empresa primeiro.');
        }
      }
      
      // Obter o token JWT para enviar no header Authorization
      const token = getToken();
      
      // Verificar se o token existe
      if (!token) {
        throw new Error('Token de autenticação não encontrado.');
      }
      
      // Fazer a requisição à API com o ID da empresa e o token
      const response = await api.get(`/dashboard/resumo`, {
        params: { id_empresa: idEmpresaAtual },
        headers: {
          Authorization: `Bearer ${token}`
        },
        timeout: 8000 // Timeout específico para esta rota
      });
      
      // Verificar se os dados recebidos são válidos
      if (response.data) {
        setResumo({
          caixa_atual: response.data.caixa_atual || 0,
          total_receber: response.data.total_receber || 0,
          total_pagar: response.data.total_pagar || 0,
          recebimentos_hoje: response.data.recebimentos_hoje || 0,
          pagamentos_hoje: response.data.pagamentos_hoje || 0
        });
      } else {
        throw new Error('Dados inválidos recebidos do servidor');
      }
    } catch (err: any) {
      console.error('Erro ao carregar os indicadores financeiros:', err);
      
      // Tratamento específico de erros HTTP
      if (err.response) {
        const { status } = err.response;
        if (status === 404 || status === 500) {
          setError('Ocorreu um erro ao buscar os indicadores financeiros.');
        } else {
          setError(`Erro ao carregar os indicadores financeiros: ${err.response.data?.detail || err.message}`);
        }
      } else {
        setError('Não foi possível carregar os indicadores financeiros. Verifique sua conexão e tente novamente.');
      }
    } finally {
      setLoading(false);
    }
  };
  
  // Efeito para buscar dados quando o componente montar ou o ID da empresa mudar
  useEffect(() => {
    fetchData();
  }, [id_empresa]);
  
  return { resumo, loading, error, fetchData, empresaId };
} 