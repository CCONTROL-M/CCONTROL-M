import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { Toaster } from 'react-hot-toast';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { ReactQueryDevtools } from '@tanstack/react-query-devtools';

// Componentes principais
import Layout from './components/Layout';
import Dashboard from './pages/Dashboard';
import Lancamentos from './pages/Lancamentos';
import VendasParcelas from './pages/VendasParcelas';
import Parcelas from './pages/Parcelas';
import TransferenciasContas from './pages/TransferenciasContas';
import DRE from './pages/DRE';
import FluxoCaixa from './pages/FluxoCaixa';
import Inadimplencia from './pages/Inadimplencia';
import CicloOperacional from './pages/CicloOperacional';
import Clientes from './pages/Clientes';
import Fornecedores from './pages/Fornecedores';
import ContasBancarias from './pages/ContasBancarias';
import ContaBancariaDetalhes from './pages/ContaBancariaDetalhes';
import Categorias from './pages/Categorias';
import CentroCustos from './pages/CentroCustos';
import FormasPagamento from './pages/FormasPagamento';
import MeusDados from './pages/MeusDados';
import GestaoUsuarios from './pages/GestaoUsuarios';
import Permissoes from './pages/Permissoes';
import ConexoesExternas from './pages/ConexoesExternas';
import ParametrosSistema from './pages/ParametrosSistema';
import AuditoriaLogs from './pages/AuditoriaLogs';
import Empresas from './pages/Empresas';
import TesteCors from './pages/TesteCors';
import NotFound from './pages/NotFound';

// Providers e contextos
import { AuthProvider } from './contexts/AuthContext';
import { ApiStatusProvider } from './contexts/ApiStatusContext';
import { LayoutProvider } from './contexts/LayoutContext';
import { LoadingProvider } from './contexts/LoadingContext';

// Cliente React Query
const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      retry: 1,
      refetchOnWindowFocus: false,
    },
  },
});

/**
 * Componente principal da aplicação
 */
function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <LoadingProvider>
        <ApiStatusProvider>
          <AuthProvider>
            <LayoutProvider>
              <BrowserRouter>
                <Toaster position="top-right" />
                <Routes>
                  <Route path="/" element={<Layout />}>
                    <Route index element={<Dashboard />} />
                    <Route path="lancamentos" element={<Lancamentos />} />
                    <Route path="vendas-parcelas" element={<VendasParcelas />} />
                    <Route path="parcelas" element={<Parcelas />} />
                    <Route path="transferencias-contas" element={<TransferenciasContas />} />
                    <Route path="dre" element={<DRE />} />
                    <Route path="fluxo-caixa" element={<FluxoCaixa />} />
                    <Route path="inadimplencia" element={<Inadimplencia />} />
                    <Route path="ciclo-operacional" element={<CicloOperacional />} />
                    <Route path="clientes" element={<Clientes />} />
                    <Route path="fornecedores" element={<Fornecedores />} />
                    <Route path="contas-bancarias" element={<ContasBancarias />} />
                    <Route path="contas-bancarias/:id" element={<ContaBancariaDetalhes />} />
                    <Route path="categorias" element={<Categorias />} />
                    <Route path="centro-custos" element={<CentroCustos />} />
                    <Route path="formas-pagamento" element={<FormasPagamento />} />
                    <Route path="meus-dados" element={<MeusDados />} />
                    <Route path="gestao-usuarios" element={<GestaoUsuarios />} />
                    <Route path="permissoes" element={<Permissoes />} />
                    <Route path="conexoes-externas" element={<ConexoesExternas />} />
                    <Route path="parametros-sistema" element={<ParametrosSistema />} />
                    <Route path="logs-auditoria" element={<AuditoriaLogs />} />
                    <Route path="empresas" element={<Empresas />} />
                    <Route path="teste-cors" element={<TesteCors />} />
                    
                    {/* Rota 404 dentro do layout */}
                    <Route path="*" element={<NotFound />} />
                  </Route>

                  {/* Redirecionamentos */}
                  <Route path="/vendas" element={<Navigate to="/vendas-parcelas" replace />} />
                  <Route path="/dashboard" element={<Navigate to="/" replace />} />
                  <Route path="/home" element={<Navigate to="/" replace />} />
                  <Route path="/login" element={<Navigate to="/" replace />} />
                  
                  {/* Rota 404 global */}
                  <Route path="*" element={<NotFound />} />
                </Routes>
              </BrowserRouter>
            </LayoutProvider>
          </AuthProvider>
        </ApiStatusProvider>
      </LoadingProvider>
      <ReactQueryDevtools />
    </QueryClientProvider>
  );
}

export default App; 