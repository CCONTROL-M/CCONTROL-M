import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useToastUtils } from '../hooks/useToast';
import { useAuth } from '../contexts/AuthContext';

/**
 * Página de Login
 */
export default function Login() {
  const [email, setEmail] = useState('');
  const [senha, setSenha] = useState('');
  const [loading, setLoading] = useState(false);
  const navigate = useNavigate();
  const { showSuccessToast, showErrorToast } = useToastUtils();
  const { login } = useAuth();

  // Função para lidar com o login
  const handleLogin = async (e: React.FormEvent) => {
    e.preventDefault();
    
    // Validações básicas
    if (!email.trim()) {
      showErrorToast('Por favor, informe o e-mail');
      return;
    }
    
    if (!senha.trim()) {
      showErrorToast('Por favor, informe a senha');
      return;
    }
    
    setLoading(true);
    
    try {
      // Simulando autenticação com atraso
      await new Promise(resolve => setTimeout(resolve, 800));
      
      // Em um cenário real, aqui seria feita uma chamada à API de autenticação
      // Para este exemplo, aceitamos qualquer e-mail e senha
      const userData = { 
        nome: 'Usuário de Teste',
        email: email,
        id_empresa: '1'
      };
      
      // Usar o método de login do contexto em vez de localStorage direto
      login('fake-jwt-token', userData);
      
      showSuccessToast('Login realizado com sucesso!');
      navigate('/');
    } catch (error) {
      console.error('Erro ao fazer login:', error);
      showErrorToast('Erro ao fazer login. Verifique suas credenciais.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-100">
      <div className="bg-white p-8 rounded-lg shadow-md w-full max-w-md">
        <div className="text-center mb-8">
          <h1 className="text-2xl font-bold text-gray-800">CCONTROL-M</h1>
          <p className="text-gray-600 mt-2">Faça login para acessar o sistema</p>
        </div>
        
        <form onSubmit={handleLogin}>
          <div className="mb-6">
            <label htmlFor="email" className="block text-gray-700 font-medium mb-2">
              E-mail
            </label>
            <input
              type="email"
              id="email"
              className="w-full px-4 py-3 border rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
              placeholder="seu@email.com"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              required
            />
          </div>
          
          <div className="mb-6">
            <label htmlFor="senha" className="block text-gray-700 font-medium mb-2">
              Senha
            </label>
            <input
              type="password"
              id="senha"
              className="w-full px-4 py-3 border rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
              placeholder="••••••••"
              value={senha}
              onChange={(e) => setSenha(e.target.value)}
              required
            />
          </div>
          
          <div className="flex items-center justify-between mb-6">
            <div className="flex items-center">
              <input
                type="checkbox"
                id="lembrar"
                className="h-4 w-4 text-blue-600 border-gray-300 rounded"
              />
              <label htmlFor="lembrar" className="ml-2 block text-gray-700">
                Lembrar-me
              </label>
            </div>
            
            <a href="#" className="text-blue-600 hover:text-blue-800 text-sm">
              Esqueceu a senha?
            </a>
          </div>
          
          <button
            type="submit"
            className="w-full bg-blue-600 text-white py-3 rounded-lg hover:bg-blue-700 transition duration-200"
            disabled={loading}
          >
            {loading ? 'Entrando...' : 'Entrar'}
          </button>
        </form>
        
        <p className="text-center text-gray-600 mt-6">
          Não tem uma conta?{' '}
          <a href="#" className="text-blue-600 hover:text-blue-800">
            Entre em contato
          </a>
        </p>
      </div>
    </div>
  );
} 