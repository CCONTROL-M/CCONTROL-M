import { useLocation } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';

/**
 * Componente de cabeçalho padronizado que utiliza tokens visuais globais
 * para manter consistência visual em toda a aplicação
 */
const Header = () => {
  const location = useLocation();
  const { user } = useAuth();
  
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

  return (
    <header className="header bg-white border-b border-gray-200 shadow-sm">
      <h1 className="header-title text-2xl font-semibold text-primary">{getPageTitle()}</h1>
      
      <div className="header-actions">
        <div className="user-menu flex items-center gap-3 px-3 py-2 rounded-lg hover:bg-gray-50 transition-colors">
          <div className="user-info flex flex-col">
            <span className="user-name font-medium text-gray-800">{user.nome}</span>
            <span className="user-email text-sm text-gray-600">{user.email}</span>
          </div>
        </div>
      </div>
    </header>
  );
};

export default Header; 