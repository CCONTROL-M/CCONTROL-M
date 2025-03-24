# Sistema de Carregamento (Loading)

## Componentes Disponíveis

### 1. LoadingContext

O contexto global de carregamento do sistema, fornecendo métodos para gerenciar estados de carregamento em toda a aplicação.

```tsx
// Como importar
import { useLoading } from '../contexts/LoadingContext';

// Como usar
const { 
  isLoading,          // Estado atual (boolean)
  startLoading,       // Função para iniciar carregamento
  stopLoading,        // Função para parar carregamento
  setLoadingState,    // Método legado
  activeOperationsCount, // Contador de operações ativas
  resetLoadingState   // Função para resetar o estado (emergência)
} = useLoading();

// Exemplo de uso com ID de operação
startLoading('minhaOperacao');
// ... código assíncrono ...
stopLoading('minhaOperacao');
```

### 2. LoadingOverlay

Componente de overlay visual que exibe uma animação de carregamento sobre a interface.

```tsx
// Já utilizado internamente pelo LoadingContext
// Raramente precisa ser usado diretamente

import LoadingOverlay from '../components/LoadingOverlay';

<LoadingOverlay 
  visible={true} 
  text="Carregando dados..." 
  theme="dark"
  blur={true}
/>
```

### 3. DataStateHandler

Componente para gerenciar estados de dados (carregamento, erro, vazio) de forma padronizada.

```tsx
import DataStateHandler from '../components/DataStateHandler';

<DataStateHandler
  loading={loading}         // Estado de carregamento
  error={error}             // Mensagem de erro (ou null)
  dataLength={data.length}  // Opcional: tamanho dos dados
  onRetry={fetchData}       // Função para repetir operação
  emptyMessage="Nenhum registro encontrado." // Mensagem quando vazio
  useGlobalLoading={false}  // Se deve usar o overlay global
>
  {/* Conteúdo a ser exibido quando carregado com sucesso */}
  <div>Conteúdo carregado</div>
</DataStateHandler>
```

## Melhores Práticas

### Gestão de Estado

1. **Evite múltiplos sistemas de loading**: Escolha entre o sistema global (LoadingContext) ou o local (estado do componente), mas não misture ambos no mesmo componente.

2. **Use IDs para operações específicas**: Ao usar `startLoading` e `stopLoading`, sempre forneça um ID único para rastrear operações específicas.

   ```tsx
   // Bom
   startLoading('fetchUserData');
   try {
     await fetchUserData();
   } finally {
     stopLoading('fetchUserData');
   }
   
   // Ruim - dificulta o rastreamento
   startLoading();
   try {
     await fetchUserData();
   } finally {
     stopLoading();
   }
   ```

3. **Sempre use try/finally**: Garanta que `stopLoading` seja chamado mesmo em caso de erro.

   ```tsx
   try {
     startLoading('operacao');
     // código que pode lançar erro
   } catch (error) {
     // tratamento do erro
   } finally {
     stopLoading('operacao');
   }
   ```

### Recomendações de Uso

1. **Prefira DataStateHandler para componentes individuais**: Para carregamento de dados em componentes específicos, use o `DataStateHandler` em vez de acessar diretamente o contexto de loading.

2. **Use LoadingContext para operações globais**: Reserve o contexto global para operações que afetam toda a aplicação, como envio de formulários, autenticação ou navegação.

3. **Defina timeout razoável**: O sistema tem um timeout de segurança de 15 segundos, mas considere timeouts menores para operações específicas.

4. **Forneça feedback visual adicional**: Para operações longas, considere mostrar progresso ou mensagem informativa além do spinner.

5. **Reset como último recurso**: Use `resetLoadingState()` apenas em situações excepcionais, como recuperação de erros críticos.

## Prevenção de Problemas

1. **Vazamento de memória**: Certifique-se de limpar todos os timers e event listeners em componentes com useEffect.

2. **Loading infinito**: Sempre implemente um mecanismo de timeout ou detecção de erro para evitar loading infinito.

3. **Conflito entre componentes**: Quando múltiplos componentes usam o sistema de loading, use IDs distintos para rastrear cada operação.

4. **Má experiência do usuário**: Sempre forneça feedback adequado e mecanismos de escape para o usuário em operações demoradas.

## Exemplos Comuns

### Carregamento de Dados Simples

```tsx
function MinhaLista() {
  const [dados, setDados] = useState([]);
  const [carregando, setCarregando] = useState(false);
  const [erro, setErro] = useState(null);

  async function buscarDados() {
    try {
      setCarregando(true);
      setErro(null);
      const resultado = await api.get('/dados');
      setDados(resultado.data);
    } catch (error) {
      setErro('Falha ao carregar dados');
      console.error(error);
    } finally {
      setCarregando(false);
    }
  }

  useEffect(() => {
    buscarDados();
  }, []);

  return (
    <DataStateHandler
      loading={carregando}
      error={erro}
      dataLength={dados.length}
      onRetry={buscarDados}
      useGlobalLoading={false}
    >
      <ul>
        {dados.map(item => (
          <li key={item.id}>{item.nome}</li>
        ))}
      </ul>
    </DataStateHandler>
  );
}
```

### Operação Global (Submissão de Formulário)

```tsx
function EnviarFormulario() {
  const { startLoading, stopLoading } = useLoading();
  
  async function handleSubmit(data) {
    try {
      startLoading('enviarFormulario');
      await api.post('/formulario', data);
      toast.success('Formulário enviado com sucesso!');
    } catch (error) {
      toast.error('Erro ao enviar formulário');
      console.error(error);
    } finally {
      stopLoading('enviarFormulario');
    }
  }
  
  return (
    <form onSubmit={handleSubmit}>
      {/* campos do formulário */}
      <button type="submit">Enviar</button>
    </form>
  );
}
```

## Solução de Problemas

Se encontrar problemas com o sistema de carregamento, consulte o documento de [Solução de Problemas de Carregamento](/docs/troubleshooting/loading-issues.md) para obter orientações detalhadas. 