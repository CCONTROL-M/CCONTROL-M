import { describe, it, expect, vi } from 'vitest';
import { render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import Table, { TableColumn } from '../Table';

describe('Table', () => {
  // Dados de teste
  const dadosTeste = [
    { id: '1', nome: 'Item 1', descricao: 'Descrição do item 1' },
    { id: '2', nome: 'Item 2', descricao: 'Descrição do item 2' },
    { id: '3', nome: 'Item 3', descricao: 'Descrição do item 3' }
  ];
  
  // Colunas para teste
  const colunasTeste: TableColumn[] = [
    { header: 'ID', accessor: 'id' },
    { header: 'Nome', accessor: 'nome' },
    { header: 'Descrição', accessor: 'descricao' }
  ];
  
  // Função mock para onClick
  const mockOnRowClick = vi.fn();
  
  it('deve renderizar uma tabela com cabeçalho e dados', () => {
    render(
      <Table 
        columns={colunasTeste} 
        data={dadosTeste} 
      />
    );
    
    // Verificar cabeçalhos
    expect(screen.getByText('ID')).toBeInTheDocument();
    expect(screen.getByText('Nome')).toBeInTheDocument();
    expect(screen.getByText('Descrição')).toBeInTheDocument();
    
    // Verificar dados
    expect(screen.getByText('Item 1')).toBeInTheDocument();
    expect(screen.getByText('Item 2')).toBeInTheDocument();
    expect(screen.getByText('Item 3')).toBeInTheDocument();
    expect(screen.getByText('Descrição do item 1')).toBeInTheDocument();
    expect(screen.getByText('Descrição do item 2')).toBeInTheDocument();
    expect(screen.getByText('Descrição do item 3')).toBeInTheDocument();
  });
  
  it('deve mostrar mensagem quando não há dados', () => {
    render(
      <Table 
        columns={colunasTeste} 
        data={[]} 
        emptyMessage="Sem dados para exibir"
      />
    );
    
    expect(screen.getByText('Sem dados para exibir')).toBeInTheDocument();
  });
  
  it('deve renderizar um loader quando loading=true', () => {
    render(
      <Table 
        columns={colunasTeste} 
        data={dadosTeste} 
        loading={true}
      />
    );
    
    // Verificar se o overlay de carregamento está visível
    const loadingOverlay = document.querySelector('.loading-overlay');
    expect(loadingOverlay).toBeInTheDocument();
    expect(loadingOverlay).toHaveClass('visible');
  });
  
  it('deve chamar onRowClick quando uma linha é clicada', async () => {
    render(
      <Table 
        columns={colunasTeste} 
        data={dadosTeste} 
        onRowClick={mockOnRowClick}
      />
    );
    
    // Encontrar todas as linhas da tabela (exceto o cabeçalho)
    const rows = screen.getAllByRole('row').slice(1);
    
    // Clicar na primeira linha
    await userEvent.click(rows[0]);
    
    // Verificar se o callback foi chamado com o item correto
    expect(mockOnRowClick).toHaveBeenCalledWith(dadosTeste[0]);
  });
  
  it('deve renderizar conteúdo personalizado usando a função render', () => {
    // Colunas com função render personalizada
    const colunasComRender: TableColumn[] = [
      ...colunasTeste,
      {
        header: 'Ações',
        accessor: 'id',
        render: (item) => (
          <button data-testid={`btn-${item.id}`}>Editar</button>
        )
      }
    ];
    
    render(
      <Table 
        columns={colunasComRender} 
        data={dadosTeste}
      />
    );
    
    // Verificar se os botões personalizados foram renderizados
    expect(screen.getByTestId('btn-1')).toBeInTheDocument();
    expect(screen.getByTestId('btn-2')).toBeInTheDocument();
    expect(screen.getByTestId('btn-3')).toBeInTheDocument();
  });
  
  it('deve lidar com accessors aninhados corretamente', () => {
    // Dados com propriedades aninhadas
    const dadosAninhados = [
      { id: '1', usuario: { nome: 'João', email: 'joao@example.com' } },
      { id: '2', usuario: { nome: 'Maria', email: 'maria@example.com' } }
    ];
    
    // Colunas para acessar dados aninhados
    const colunasAninhadas: TableColumn[] = [
      { header: 'ID', accessor: 'id' },
      { header: 'Nome', accessor: 'usuario.nome' },
      { header: 'Email', accessor: 'usuario.email' }
    ];
    
    render(
      <Table 
        columns={colunasAninhadas} 
        data={dadosAninhados}
      />
    );
    
    // Verificar se os dados aninhados foram acessados corretamente
    expect(screen.getByText('João')).toBeInTheDocument();
    expect(screen.getByText('Maria')).toBeInTheDocument();
    expect(screen.getByText('joao@example.com')).toBeInTheDocument();
    expect(screen.getByText('maria@example.com')).toBeInTheDocument();
  });
}); 