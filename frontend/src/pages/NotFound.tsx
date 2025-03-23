import React from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import { runDiagnostics } from '../utils/diagnostics';

const NotFound: React.FC = () => {
  const navigate = useNavigate();
  const location = useLocation();
  const path = location.pathname;

  // Executar diagnóstico ao carregar a página
  React.useEffect(() => {
    const runDiagnosticsAndLog = async () => {
      const diagnosticResults = await runDiagnostics();
      console.log('Diagnóstico para página não encontrada:', diagnosticResults);
      
      // Salvar o erro no localStorage para depuração
      const notFoundErrors = JSON.parse(localStorage.getItem('notFoundErrors') || '[]');
      notFoundErrors.push({
        path,
        timestamp: new Date().toISOString(),
        ...diagnosticResults
      });
      localStorage.setItem('notFoundErrors', JSON.stringify(notFoundErrors));
    };
    
    runDiagnosticsAndLog();
  }, [path]);

  return (
    <div className="not-found-container">
      <div className="not-found-content">
        <h1>404</h1>
        <h2>Página Não Encontrada</h2>
        <p>
          A página <code>{path}</code> não existe no sistema.
        </p>
        <p>
          Verifique se a URL está correta ou navegue para uma seção do sistema 
          utilizando o menu lateral.
        </p>
        
        <div className="not-found-actions">
          <button 
            className="btn-primary" 
            onClick={() => navigate('/')}
          >
            Ir para o Dashboard
          </button>
          
          <button 
            className="btn-secondary" 
            onClick={() => navigate(-1)}
          >
            Voltar
          </button>
        </div>
      </div>
    </div>
  );
};

export default NotFound; 