import { useLocation, useNavigate } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';

const Header = () => {
  const location = useLocation();
  const navigate = useNavigate();
  const { user, logout, login } = useAuth();
  
  // Função para formatar o título da página
  const getPageTitle = () => {
    const path = location.pathname;
    
    // Mapeamento de rotas para títulos
    const routes: Record<string, string> = {
      '/': 'Dashboard',
      '/lancamentos': 'Lançamentos',
      '/vendas-parcelas': 'Vendas & Parcelas',
      '/parcelas': 'Parcelas de Vendas',
      '/transferencias-contas': 'Transferências entre Contas',
      '/dre': 'DRE',
      '/fluxo-caixa': 'Fluxo de Caixa',
      '/inadimplencia': 'Relatório de Inadimplência',
      '/ciclo-operacional': 'Ciclo Operacional',
      '/clientes': 'Clientes',
      '/fornecedores': 'Fornecedores',
      '/contas-bancarias': 'Contas Bancárias',
      '/categorias': 'Categorias',
      '/centro-custos': 'Centro de Custos',
      '/formas-pagamento': 'Formas de Pagamento',
      '/meus-dados': 'Meus Dados',
      '/gestao-usuarios': 'Gestão de Usuários',
      '/permissoes': 'Permissões',
      '/conexoes-externas': 'Conexões Externas',
      '/parametros-sistema': 'Parâmetros do Sistema',
      '/logs-auditoria': 'Logs de Auditoria',
      '/empresas': 'Empresas Cadastradas'
    };
    
    return routes[path] || 'CCONTROL-M';
  };

  // Função para realizar logout
  const handleLogout = () => {
    logout();
    navigate('/login');
  };
  
  // Função para login automático (usuário de desenvolvimento)
  const handleAutoLogin = () => {
    const userData = {
      nome: 'Usuário de Desenvolvimento',
      email: 'dev@exemplo.com',
      id_empresa: '1'
    };
    
    login('fake-jwt-token', userData);
  };

  return (
    <header className="header">
      <h1 className="header-title">{getPageTitle()}</h1>
      
      <div className="header-actions">
        {user ? (
          <div className="user-menu">
            <div className="user-info">
              <span className="user-name">{user.nome}</span>
              <span className="user-email">{user.email}</span>
            </div>
            
            <button 
              className="btn-logout" 
              onClick={handleLogout}
              aria-label="Sair do sistema"
            >
              Sair
            </button>
          </div>
        ) : (
          <div className="user-menu">
            <button 
              className="btn-login" 
              onClick={handleAutoLogin}
              aria-label="Login automático"
            >
              Login de Dev
            </button>
          </div>
        )}
      </div>
    </header>
  );
};

export default Header; 