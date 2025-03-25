import { NavLink } from 'react-router-dom';
import { FiHome, FiDollarSign, FiBarChart2, FiFolder, FiUser, FiShield, FiSettings, FiActivity, FiBookmark } from 'react-icons/fi';

/**
 * Componente de barra lateral que utiliza tokens visuais padronizados
 * para manter consistência visual em toda a aplicação
 */
const Sidebar = () => {
  return (
    <aside className="sidebar bg-gray-800 text-white shadow-lg">
      <div className="sidebar-header p-4 border-b border-gray-700">
        <h1 className="sidebar-title text-xl font-bold text-primary-100">CCONTROL-M</h1>
      </div>

      {/* Seção 1: Visão Geral */}
      <div className="sidebar-section mt-4">
        <h2 className="sidebar-section-title px-4 py-2 text-sm font-medium text-gray-400 uppercase">Visão Geral</h2>
        <ul className="sidebar-menu">
          <li className="sidebar-menu-item">
            <NavLink to="/" className={({isActive}) => 
              `sidebar-menu-link flex items-center px-4 py-2 text-sm ${isActive ? 'bg-primary-700 text-white' : 'text-gray-200 hover:bg-gray-700'} transition-colors`
            }>
              <span className="sidebar-menu-icon mr-3 text-lg"><FiHome /></span>
              Dashboard
            </NavLink>
          </li>
        </ul>
      </div>

      {/* Seção 2: Fluxo Financeiro */}
      <div className="sidebar-section mt-4">
        <h2 className="sidebar-section-title px-4 py-2 text-sm font-medium text-gray-400 uppercase">Fluxo Financeiro</h2>
        <ul className="sidebar-menu">
          <li className="sidebar-menu-item">
            <NavLink to="/lancamentos" className={({isActive}) => 
              `sidebar-menu-link flex items-center px-4 py-2 text-sm ${isActive ? 'bg-primary-700 text-white' : 'text-gray-200 hover:bg-gray-700'} transition-colors`
            }>
              <span className="sidebar-menu-icon mr-3 text-lg"><FiDollarSign /></span>
              Lançamentos
            </NavLink>
          </li>
          <li className="sidebar-menu-item">
            <NavLink to="/vendas-parcelas" className={({isActive}) => 
              `sidebar-menu-link flex items-center px-4 py-2 text-sm ${isActive ? 'bg-primary-700 text-white' : 'text-gray-200 hover:bg-gray-700'} transition-colors`
            }>
              <span className="sidebar-menu-icon mr-3 text-lg"><FiDollarSign /></span>
              Vendas & Parcelas
            </NavLink>
          </li>
          <li className="sidebar-menu-item">
            <NavLink to="/parcelas" className={({isActive}) => 
              `sidebar-menu-link flex items-center px-4 py-2 text-sm ${isActive ? 'bg-primary-700 text-white' : 'text-gray-200 hover:bg-gray-700'} transition-colors`
            }>
              <span className="sidebar-menu-icon mr-3 text-lg"><FiDollarSign /></span>
              Parcelas
            </NavLink>
          </li>
          <li className="sidebar-menu-item">
            <NavLink to="/transferencias-contas" className={({isActive}) => 
              `sidebar-menu-link flex items-center px-4 py-2 text-sm ${isActive ? 'bg-primary-700 text-white' : 'text-gray-200 hover:bg-gray-700'} transition-colors`
            }>
              <span className="sidebar-menu-icon mr-3 text-lg"><FiDollarSign /></span>
              Transferências
            </NavLink>
          </li>
        </ul>
      </div>

      {/* Seção 3: Relatórios & Indicadores */}
      <div className="sidebar-section mt-4">
        <h2 className="sidebar-section-title px-4 py-2 text-sm font-medium text-gray-400 uppercase">Relatórios & Indicadores</h2>
        <ul className="sidebar-menu">
          <li className="sidebar-menu-item">
            <NavLink to="/dre" className={({isActive}) => 
              `sidebar-menu-link flex items-center px-4 py-2 text-sm ${isActive ? 'bg-primary-700 text-white' : 'text-gray-200 hover:bg-gray-700'} transition-colors`
            }>
              <span className="sidebar-menu-icon mr-3 text-lg"><FiBarChart2 /></span>
              DRE
            </NavLink>
          </li>
          <li className="sidebar-menu-item">
            <NavLink to="/fluxo-caixa" className={({isActive}) => 
              `sidebar-menu-link flex items-center px-4 py-2 text-sm ${isActive ? 'bg-primary-700 text-white' : 'text-gray-200 hover:bg-gray-700'} transition-colors`
            }>
              <span className="sidebar-menu-icon mr-3 text-lg"><FiBarChart2 /></span>
              Fluxo de Caixa
            </NavLink>
          </li>
          <li className="sidebar-menu-item">
            <NavLink to="/inadimplencia" className={({isActive}) => 
              `sidebar-menu-link flex items-center px-4 py-2 text-sm ${isActive ? 'bg-primary-700 text-white' : 'text-gray-200 hover:bg-gray-700'} transition-colors`
            }>
              <span className="sidebar-menu-icon mr-3 text-lg"><FiBarChart2 /></span>
              Inadimplência
            </NavLink>
          </li>
          <li className="sidebar-menu-item">
            <NavLink to="/ciclo-operacional" className={({isActive}) => 
              `sidebar-menu-link flex items-center px-4 py-2 text-sm ${isActive ? 'bg-primary-700 text-white' : 'text-gray-200 hover:bg-gray-700'} transition-colors`
            }>
              <span className="sidebar-menu-icon mr-3 text-lg"><FiBarChart2 /></span>
              Ciclo Operacional
            </NavLink>
          </li>
        </ul>
      </div>

      {/* Seção 4: Cadastros Base */}
      <div className="sidebar-section mt-4">
        <h2 className="sidebar-section-title px-4 py-2 text-sm font-medium text-gray-400 uppercase">Cadastros Base</h2>
        <ul className="sidebar-menu">
          <li className="sidebar-menu-item">
            <NavLink to="/empresas" className={({isActive}) => 
              `sidebar-menu-link flex items-center px-4 py-2 text-sm ${isActive ? 'bg-primary-700 text-white' : 'text-gray-200 hover:bg-gray-700'} transition-colors`
            }>
              <span className="sidebar-menu-icon mr-3 text-lg"><FiBookmark /></span>
              Empresas
            </NavLink>
          </li>
          <li className="sidebar-menu-item">
            <NavLink to="/clientes" className={({isActive}) => 
              `sidebar-menu-link flex items-center px-4 py-2 text-sm ${isActive ? 'bg-primary-700 text-white' : 'text-gray-200 hover:bg-gray-700'} transition-colors`
            }>
              <span className="sidebar-menu-icon mr-3 text-lg"><FiFolder /></span>
              Clientes
            </NavLink>
          </li>
          <li className="sidebar-menu-item">
            <NavLink to="/fornecedores" className={({isActive}) => 
              `sidebar-menu-link flex items-center px-4 py-2 text-sm ${isActive ? 'bg-primary-700 text-white' : 'text-gray-200 hover:bg-gray-700'} transition-colors`
            }>
              <span className="sidebar-menu-icon mr-3 text-lg"><FiFolder /></span>
              Fornecedores
            </NavLink>
          </li>
          <li className="sidebar-menu-item">
            <NavLink to="/contas-bancarias" className={({isActive}) => 
              `sidebar-menu-link flex items-center px-4 py-2 text-sm ${isActive ? 'bg-primary-700 text-white' : 'text-gray-200 hover:bg-gray-700'} transition-colors`
            }>
              <span className="sidebar-menu-icon mr-3 text-lg"><FiFolder /></span>
              Contas Bancárias
            </NavLink>
          </li>
          <li className="sidebar-menu-item">
            <NavLink to="/categorias" className={({isActive}) => 
              `sidebar-menu-link flex items-center px-4 py-2 text-sm ${isActive ? 'bg-primary-700 text-white' : 'text-gray-200 hover:bg-gray-700'} transition-colors`
            }>
              <span className="sidebar-menu-icon mr-3 text-lg"><FiFolder /></span>
              Categorias
            </NavLink>
          </li>
          <li className="sidebar-menu-item">
            <NavLink to="/centro-custos" className={({isActive}) => 
              `sidebar-menu-link flex items-center px-4 py-2 text-sm ${isActive ? 'bg-primary-700 text-white' : 'text-gray-200 hover:bg-gray-700'} transition-colors`
            }>
              <span className="sidebar-menu-icon mr-3 text-lg"><FiFolder /></span>
              Centro de Custos
            </NavLink>
          </li>
          <li className="sidebar-menu-item">
            <NavLink to="/formas-pagamento" className={({isActive}) => 
              `sidebar-menu-link flex items-center px-4 py-2 text-sm ${isActive ? 'bg-primary-700 text-white' : 'text-gray-200 hover:bg-gray-700'} transition-colors`
            }>
              <span className="sidebar-menu-icon mr-3 text-lg"><FiFolder /></span>
              Formas de Pagamento
            </NavLink>
          </li>
        </ul>
      </div>

      {/* Seção 5: Perfil do Usuário */}
      <div className="sidebar-section mt-4">
        <h2 className="sidebar-section-title px-4 py-2 text-sm font-medium text-gray-400 uppercase">Perfil do Usuário</h2>
        <ul className="sidebar-menu">
          <li className="sidebar-menu-item">
            <NavLink to="/meus-dados" className={({isActive}) => 
              `sidebar-menu-link flex items-center px-4 py-2 text-sm ${isActive ? 'bg-primary-700 text-white' : 'text-gray-200 hover:bg-gray-700'} transition-colors`
            }>
              <span className="sidebar-menu-icon mr-3 text-lg"><FiUser /></span>
              Meus Dados
            </NavLink>
          </li>
        </ul>
      </div>

      {/* Seção 6: Administração */}
      <div className="sidebar-section mt-4">
        <h2 className="sidebar-section-title px-4 py-2 text-sm font-medium text-gray-400 uppercase">Administração</h2>
        <ul className="sidebar-menu">
          <li className="sidebar-menu-item">
            <NavLink to="/gestao-usuarios" className={({isActive}) => 
              `sidebar-menu-link flex items-center px-4 py-2 text-sm ${isActive ? 'bg-primary-700 text-white' : 'text-gray-200 hover:bg-gray-700'} transition-colors`
            }>
              <span className="sidebar-menu-icon mr-3 text-lg"><FiShield /></span>
              Gestão de Usuários
            </NavLink>
          </li>
          <li className="sidebar-menu-item">
            <NavLink to="/permissoes" className={({isActive}) => 
              `sidebar-menu-link flex items-center px-4 py-2 text-sm ${isActive ? 'bg-primary-700 text-white' : 'text-gray-200 hover:bg-gray-700'} transition-colors`
            }>
              <span className="sidebar-menu-icon mr-3 text-lg"><FiShield /></span>
              Permissões
            </NavLink>
          </li>
          <li className="sidebar-menu-item">
            <NavLink to="/logs-auditoria" className={({isActive}) => 
              `sidebar-menu-link flex items-center px-4 py-2 text-sm ${isActive ? 'bg-primary-700 text-white' : 'text-gray-200 hover:bg-gray-700'} transition-colors`
            }>
              <span className="sidebar-menu-icon mr-3 text-lg"><FiActivity /></span>
              Logs de Auditoria
            </NavLink>
          </li>
        </ul>
      </div>

      {/* Seção 7: Configurações (Somente SuperAdmin) */}
      <div className="sidebar-section mt-4 mb-8">
        <h2 className="sidebar-section-title px-4 py-2 text-sm font-medium text-gray-400 uppercase">Configurações</h2>
        <ul className="sidebar-menu">
          <li className="sidebar-menu-item">
            <NavLink to="/conexoes-externas" className={({isActive}) => 
              `sidebar-menu-link flex items-center px-4 py-2 text-sm ${isActive ? 'bg-primary-700 text-white' : 'text-gray-200 hover:bg-gray-700'} transition-colors`
            }>
              <span className="sidebar-menu-icon mr-3 text-lg"><FiSettings /></span>
              Conexões Externas
            </NavLink>
          </li>
          <li className="sidebar-menu-item">
            <NavLink to="/parametros-sistema" className={({isActive}) => 
              `sidebar-menu-link flex items-center px-4 py-2 text-sm ${isActive ? 'bg-primary-700 text-white' : 'text-gray-200 hover:bg-gray-700'} transition-colors`
            }>
              <span className="sidebar-menu-icon mr-3 text-lg"><FiSettings /></span>
              Parâmetros do Sistema
            </NavLink>
          </li>
        </ul>
      </div>
    </aside>
  );
};

export default Sidebar; 