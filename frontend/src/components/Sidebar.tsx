import { NavLink } from 'react-router-dom';
import { FiHome, FiDollarSign, FiBarChart2, FiFolder, FiUser, FiShield, FiSettings, FiActivity, FiBookmark } from 'react-icons/fi';

const Sidebar = () => {
  return (
    <aside className="sidebar">
      <div className="sidebar-header">
        <h1 className="sidebar-title">CCONTROL-M</h1>
      </div>

      {/* Seção 1: Visão Geral */}
      <div className="sidebar-section">
        <h2 className="sidebar-section-title">Visão Geral</h2>
        <ul className="sidebar-menu">
          <li className="sidebar-menu-item">
            <NavLink to="/" className="sidebar-menu-link">
              <span className="sidebar-menu-icon"><FiHome /></span>
              Dashboard
            </NavLink>
          </li>
        </ul>
      </div>

      {/* Seção 2: Fluxo Financeiro */}
      <div className="sidebar-section">
        <h2 className="sidebar-section-title">Fluxo Financeiro</h2>
        <ul className="sidebar-menu">
          <li className="sidebar-menu-item">
            <NavLink to="/lancamentos" className="sidebar-menu-link">
              <span className="sidebar-menu-icon"><FiDollarSign /></span>
              Lançamentos
            </NavLink>
          </li>
          <li className="sidebar-menu-item">
            <NavLink to="/vendas-parcelas" className="sidebar-menu-link">
              <span className="sidebar-menu-icon"><FiDollarSign /></span>
              Vendas & Parcelas
            </NavLink>
          </li>
          <li className="sidebar-menu-item">
            <NavLink to="/parcelas" className="sidebar-menu-link">
              <span className="sidebar-menu-icon"><FiDollarSign /></span>
              Parcelas
            </NavLink>
          </li>
          <li className="sidebar-menu-item">
            <NavLink to="/transferencias-contas" className="sidebar-menu-link">
              <span className="sidebar-menu-icon"><FiDollarSign /></span>
              Transferências
            </NavLink>
          </li>
        </ul>
      </div>

      {/* Seção 3: Relatórios & Indicadores */}
      <div className="sidebar-section">
        <h2 className="sidebar-section-title">Relatórios & Indicadores</h2>
        <ul className="sidebar-menu">
          <li className="sidebar-menu-item">
            <NavLink to="/dre" className="sidebar-menu-link">
              <span className="sidebar-menu-icon"><FiBarChart2 /></span>
              DRE
            </NavLink>
          </li>
          <li className="sidebar-menu-item">
            <NavLink to="/fluxo-caixa" className="sidebar-menu-link">
              <span className="sidebar-menu-icon"><FiBarChart2 /></span>
              Fluxo de Caixa
            </NavLink>
          </li>
          <li className="sidebar-menu-item">
            <NavLink to="/inadimplencia" className="sidebar-menu-link">
              <span className="sidebar-menu-icon"><FiBarChart2 /></span>
              Inadimplência
            </NavLink>
          </li>
          <li className="sidebar-menu-item">
            <NavLink to="/ciclo-operacional" className="sidebar-menu-link">
              <span className="sidebar-menu-icon"><FiBarChart2 /></span>
              Ciclo Operacional
            </NavLink>
          </li>
        </ul>
      </div>

      {/* Seção 4: Cadastros Base */}
      <div className="sidebar-section">
        <h2 className="sidebar-section-title">Cadastros Base</h2>
        <ul className="sidebar-menu">
          <li className="sidebar-menu-item">
            <NavLink to="/empresas" className="sidebar-menu-link">
              <span className="sidebar-menu-icon"><FiBookmark /></span>
              Empresas
            </NavLink>
          </li>
          <li className="sidebar-menu-item">
            <NavLink to="/clientes" className="sidebar-menu-link">
              <span className="sidebar-menu-icon"><FiFolder /></span>
              Clientes
            </NavLink>
          </li>
          <li className="sidebar-menu-item">
            <NavLink to="/fornecedores" className="sidebar-menu-link">
              <span className="sidebar-menu-icon"><FiFolder /></span>
              Fornecedores
            </NavLink>
          </li>
          <li className="sidebar-menu-item">
            <NavLink to="/contas-bancarias" className="sidebar-menu-link">
              <span className="sidebar-menu-icon"><FiFolder /></span>
              Contas Bancárias
            </NavLink>
          </li>
          <li className="sidebar-menu-item">
            <NavLink to="/categorias" className="sidebar-menu-link">
              <span className="sidebar-menu-icon"><FiFolder /></span>
              Categorias
            </NavLink>
          </li>
          <li className="sidebar-menu-item">
            <NavLink to="/centro-custos" className="sidebar-menu-link">
              <span className="sidebar-menu-icon"><FiFolder /></span>
              Centro de Custos
            </NavLink>
          </li>
          <li className="sidebar-menu-item">
            <NavLink to="/formas-pagamento" className="sidebar-menu-link">
              <span className="sidebar-menu-icon"><FiFolder /></span>
              Formas de Pagamento
            </NavLink>
          </li>
        </ul>
      </div>

      {/* Seção 5: Perfil do Usuário */}
      <div className="sidebar-section">
        <h2 className="sidebar-section-title">Perfil do Usuário</h2>
        <ul className="sidebar-menu">
          <li className="sidebar-menu-item">
            <NavLink to="/meus-dados" className="sidebar-menu-link">
              <span className="sidebar-menu-icon"><FiUser /></span>
              Meus Dados
            </NavLink>
          </li>
        </ul>
      </div>

      {/* Seção 6: Administração */}
      <div className="sidebar-section">
        <h2 className="sidebar-section-title">Administração</h2>
        <ul className="sidebar-menu">
          <li className="sidebar-menu-item">
            <NavLink to="/gestao-usuarios" className="sidebar-menu-link">
              <span className="sidebar-menu-icon"><FiShield /></span>
              Gestão de Usuários
            </NavLink>
          </li>
          <li className="sidebar-menu-item">
            <NavLink to="/permissoes" className="sidebar-menu-link">
              <span className="sidebar-menu-icon"><FiShield /></span>
              Permissões
            </NavLink>
          </li>
          <li className="sidebar-menu-item">
            <NavLink to="/logs-auditoria" className="sidebar-menu-link">
              <span className="sidebar-menu-icon"><FiActivity /></span>
              Logs de Auditoria
            </NavLink>
          </li>
        </ul>
      </div>

      {/* Seção 7: Configurações (Somente SuperAdmin) */}
      <div className="sidebar-section">
        <h2 className="sidebar-section-title">Configurações</h2>
        <ul className="sidebar-menu">
          <li className="sidebar-menu-item">
            <NavLink to="/conexoes-externas" className="sidebar-menu-link">
              <span className="sidebar-menu-icon"><FiSettings /></span>
              Conexões Externas
            </NavLink>
          </li>
          <li className="sidebar-menu-item">
            <NavLink to="/parametros-sistema" className="sidebar-menu-link">
              <span className="sidebar-menu-icon"><FiSettings /></span>
              Parâmetros do Sistema
            </NavLink>
          </li>
        </ul>
      </div>
    </aside>
  );
};

export default Sidebar; 