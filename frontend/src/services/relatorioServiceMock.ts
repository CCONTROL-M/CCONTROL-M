/**
 * Serviço de relatórios mock para desenvolvimento
 */

import { ResumoDashboard } from '../types';

/**
 * Mock de dados para o dashboard
 */
export async function buscarResumoDashboardMock(): Promise<ResumoDashboard> {
  // Simula um delay de rede
  await new Promise(resolve => setTimeout(resolve, 800));
  
  return {
    caixa_atual: 23574.85,
    total_receber: 45678.23,
    total_pagar: 12987.67,
    recebimentos_hoje: 2350.00,
    pagamentos_hoje: 1875.45
  };
} 