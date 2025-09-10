# 🎯 Frontend Dashboard - Guia de Uso

## 📱 Interface Principal

Acesse: **http://localhost:8000**

O dashboard web oferece uma interface moderna e intuitiva para gerenciar toda a pipeline Pokemon.

## 🎮 Funcionalidades Principais

### 1. **Painel de Status**
- **Total de Pokémons**: Contador em tempo real
- **Stream Processor**: Status ativo/inativo
- **Alertas**: Contador de alertas recentes
- **Qualidade dos Dados**: Score de qualidade

### 2. **Gerenciamento de Pokémons**
- **Importar Individual**: Digite o nome e clique em "Importar"
- **Importar Exemplos**: Botão para importar pokémons de demonstração
- **Listar Todos**: Visualiza pokémons com sprites e informações
- **Visualização em Grid**: Cards com imagens e tipos

### 3. **Controles da Pipeline**

#### Stream Processing
- **▶️ Iniciar**: Ativa o processamento em tempo real
- **⏹️ Parar**: Para o stream processor
- **🐛 Simular Anomalia**: Testa detecção de anomalias

#### Processamento de Arquivos
- **📄 Exportar CSV**: Gera arquivo CSV com todos os pokémons
- **📋 Exportar JSON**: Gera arquivo JSON estruturado
- **🧹 Limpar Dados**: Normaliza e limpa dados existentes

#### Relatórios
- **📅 Diário**: Gera relatório do dia
- **📊 Semanal**: Relatório da semana
- **📈 Dashboard**: Abre dashboard HTML detalhado

### 4. **Monitoramento em Tempo Real**

#### Eventos Recentes
- Lista dos últimos eventos processados
- Mostra pokémons processados e anomalias detectadas
- Atualização automática a cada minuto

#### Alertas
- Histórico de alertas por severidade
- Alertas de teste e produção
- Botões para testar e limpar alertas

## 🎨 Interface e Usabilidade

### Design Responsivo
- **Bootstrap 5**: Interface moderna e responsiva
- **Font Awesome**: Ícones intuitivos
- **Cores Temáticas**: Visual Pokemon-inspired

### Feedback Visual
- **Toasts**: Notificações de sucesso/erro
- **Loading**: Indicadores de carregamento
- **Status Indicators**: Bolinhas coloridas para status
- **Hover Effects**: Animações suaves

### Atalhos de Teclado
- **Ctrl/Cmd + R**: Atualizar status
- **Ctrl/Cmd + I**: Focar no campo de importação

## 📊 Arquivos Gerados

Todos os arquivos são salvos na pasta `data/` e são visíveis no host:

```
data/
├── exports/           # CSV e JSON exportados
├── reports/           # Relatórios JSON
├── dashboards/        # Dashboards HTML
├── alerts/           # Logs de alertas
└── temp/             # Arquivos temporários
```

## 🔄 Fluxo de Trabalho Recomendado

### 1. **Primeira Execução**
1. Acesse http://localhost:8000
2. Clique em "Importar Exemplos" para popular o banco
3. Verifique o status no painel superior

### 2. **Monitoramento Contínuo**
1. Inicie o Stream Processor
2. Monitore eventos e alertas em tempo real
3. Gere relatórios periodicamente

### 3. **Análise de Dados**
1. Exporte dados em CSV/JSON
2. Gere dashboards HTML
3. Analise métricas de qualidade

### 4. **Teste de Anomalias**
1. Simule anomalias para testar alertas
2. Verifique logs de eventos
3. Confirme funcionamento dos alertas

## 🛠️ Recursos Técnicos

### Auto-Refresh
- **Status**: A cada 30 segundos
- **Eventos**: A cada 60 segundos
- **Conexão**: Indicador em tempo real

### API Integration
- **Async/Await**: Chamadas não-bloqueantes
- **Error Handling**: Tratamento robusto de erros
- **Loading States**: Feedback visual durante operações

### Responsividade
- **Mobile-First**: Funciona em dispositivos móveis
- **Grid Layout**: Adaptável a diferentes telas
- **Touch-Friendly**: Botões otimizados para touch

## 🎯 Casos de Uso

### 1. **Administrador de Sistema**
- Monitorar saúde da pipeline
- Configurar alertas
- Gerar relatórios executivos

### 2. **Analista de Dados**
- Exportar dados para análise
- Visualizar métricas de qualidade
- Acompanhar tendências

### 3. **Desenvolvedor**
- Testar funcionalidades
- Simular cenários de erro
- Debuggar problemas

### 4. **Usuário Final**
- Importar novos pokémons
- Visualizar coleção
- Acessar informações básicas

## 🚀 Próximos Passos

Após usar o dashboard, você pode:

1. **Explorar a API**: http://localhost:8000/docs
2. **Executar demos**: `python3 examples/pipeline_demo.py`
3. **Analisar dados**: Verificar arquivos em `./data/`
4. **Customizar**: Modificar `app/static/` para personalizar

## 💡 Dicas e Truques

- **Refresh Manual**: Use F5 para atualizar dados
- **Múltiplas Abas**: Abra várias instâncias para monitoramento
- **Bookmarks**: Salve links diretos para dashboards
- **Mobile**: Funciona perfeitamente em smartphones
- **Logs**: Verifique console do navegador para debug

---

**🎮 Divirta-se explorando o mundo Pokemon com nossa pipeline de dados!**
