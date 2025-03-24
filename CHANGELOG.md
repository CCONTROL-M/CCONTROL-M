# Changelog

## [1.3.1] - 2023-06-15

### Correções
- Corrigido problema de tela de carregamento travada no Dashboard
- Aprimorado sistema de gestão de estado de carregamento para evitar overlays persistentes
- Adicionado mecanismo de escape para permitir que usuários cancelem carregamento prolongado

### Melhorias
- Reduzido timeout de segurança do sistema de carregamento de 30s para 15s
- Adicionada documentação detalhada sobre sistema de carregamento e solução de problemas
- Implementado tratamento mais robusto de timers no componente LoadingOverlay

## [1.3.0] - 2023-05-28

### Novos Recursos
- Implementação do endpoint `/dashboard/resumo` no backend
- Adicionado suporte para visualização de resumo financeiro no Dashboard
- Nova API para cálculo de recebimentos e pagamentos diários

### Melhorias
- Otimização nas consultas de parcelas e contas a pagar
- Melhor tratamento de erros em requisições ao backend
- Implementação de fallback para dados mockados quando API está offline 