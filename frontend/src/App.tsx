import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import Layout from './components/Layout';
import MockToggle from './components/MockToggle';

// Páginas
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
import Categorias from './pages/Categorias';
import CentroCustos from './pages/CentroCustos';
import FormasPagamento from './pages/FormasPagamento';
import MeusDados from './pages/MeusDados';
import GestaoUsuarios from './pages/GestaoUsuarios';
import Permissoes from './pages/Permissoes';
import ConexoesExternas from './pages/ConexoesExternas';
import ParametrosSistema from './pages/ParametrosSistema';
import LogsAuditoria from './pages/LogsAuditoria';
import Empresas from './pages/Empresas';
import TesteCors from './pages/TesteCors';
import NotFound from './pages/NotFound';

function App() {
  return (
    <BrowserRouter>
      <Routes>
        {/* Rotas dentro do layout principal com sidebar */}
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
          <Route path="categorias" element={<Categorias />} />
          <Route path="centro-custos" element={<CentroCustos />} />
          <Route path="formas-pagamento" element={<FormasPagamento />} />
          <Route path="meus-dados" element={<MeusDados />} />
          <Route path="gestao-usuarios" element={<GestaoUsuarios />} />
          <Route path="permissoes" element={<Permissoes />} />
          <Route path="conexoes-externas" element={<ConexoesExternas />} />
          <Route path="parametros-sistema" element={<ParametrosSistema />} />
          <Route path="logs-auditoria" element={<LogsAuditoria />} />
          <Route path="empresas" element={<Empresas />} />
          <Route path="teste-cors" element={<TesteCors />} />
          
          {/* Rota para páginas não encontradas dentro do Layout */}
          <Route path="*" element={<NotFound />} />
        </Route>
        
        {/* Redirecionamentos e aliases para URLs alternativas */}
        <Route path="/vendas" element={<Navigate to="/vendas-parcelas" replace />} />
        <Route path="/dashboard" element={<Navigate to="/" replace />} />
        <Route path="/home" element={<Navigate to="/" replace />} />
        
        {/* Rota 404 fora do layout (caso de erro grave) */}
        <Route path="*" element={<NotFound />} />
      </Routes>
      <MockToggle />
    </BrowserRouter>
  );
}

export default App; 