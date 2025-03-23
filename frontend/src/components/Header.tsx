import { useLocation } from 'react-router-dom';

const Header = () => {
  const location = useLocation();
  
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
    <header className="header">
      <h1 className="header-title">{getPageTitle()}</h1>
    </header>
  );
};

export default Header; 