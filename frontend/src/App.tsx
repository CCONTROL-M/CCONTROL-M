import { BrowserRouter, Routes, Route } from 'react-router-dom';
import Layout from './components/Layout';

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

function App() {
  return (
    <BrowserRouter>
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
        </Route>
      </Routes>
    </BrowserRouter>
  );
}

export default App; 