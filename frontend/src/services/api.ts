import axios from "axios";

// Função para obter o token de autenticação do localStorage
const getAuthToken = () => {
  return localStorage.getItem('token');
};

const api = axios.create({
  baseURL: "http://localhost:8000",
  headers: {
    'Content-Type': 'application/json',
  }
});

// Interceptor para adicionar token de autenticação a todas as requisições
api.interceptors.request.use(
  (config) => {
    const token = getAuthToken();
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Interceptor para tratar erros de resposta
api.interceptors.response.use(
  (response) => {
    return response;
  },
  (error) => {
    if (error.response) {
      // O servidor respondeu com um status code fora do intervalo 2xx
      console.error("Erro da API:", error.response.status, error.response.data);
      
      // Se o erro for 401 (não autorizado), redirecionar para login
      if (error.response.status === 401) {
        localStorage.removeItem('token');
        window.location.href = '/login';
      }
    } else if (error.request) {
      // A requisição foi feita mas não houve resposta
      console.error("Erro de conexão:", error.request);
    } else {
      // Erro ao configurar a requisição
      console.error("Erro:", error.message);
    }
    return Promise.reject(error);
  }
);

export default api; 