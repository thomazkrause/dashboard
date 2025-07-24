# Dashboard de Análise de Faturamento 💰

Dashboard interativo para análise de faturamento desenvolvido com Streamlit, com recursos avançados de análise de churn e métricas de clientes.

## 🚀 Funcionalidades

### **Análises Principais**
- **KPIs Principais**: Visualização de métricas fundamentais
- **Análise por Faixa**: Segmentação de clientes em grupos A, B e C
- **Ranking de Clientes**: Top clientes e análise de concentração
- **Análise de Pareto**: Visualização 80/20
- **Evolução Temporal**: Acompanhamento mensal de métricas
- **Filtros Interativos**: Análise por situação e método de pagamento

### **🆕 Recursos Avançados**
- **📊 Gráfico Triplo Combinado**: Evolução mensal com barras de faturamento e linhas de métricas de clientes
- **👥 Clientes Únicos Pagantes**: Linha vermelha mostrando clientes ativos por mês
- **📉 Análise de Churn**: Linha laranja tracejada identificando clientes em processo de churn (sem pagamentos há 60+ dias)
- **🔄 Métricas Dinâmicas**: Cálculos automáticos baseados no último pagamento de cada cliente
- **⚙️ Configuração Flexível**: Período de churn configurável (padrão: 60 dias)

### **Visualizações Interativas**
- **Eixo Duplo**: Valores financeiros (esquerda) e quantidade de clientes (direita)
- **Hover Personalizado**: Informações detalhadas sobre cada métrica
- **Cores Distintas**: Sistema de cores intuitivo para fácil identificação
- **Responsividade**: Layout adaptável para diferentes tamanhos de tela

## 📁 Estrutura do Projeto

### **Arquivos Principais**
- `main.py` - Aplicação principal do Streamlit
- `database.py` - Gerenciamento de dados (Supabase/Memória)
- `data_processor.py` - Processamento e transformação de dados
- `metrics_calculator.py` - Cálculos de métricas e análises avançadas
- `visualizations.py` - Criação de gráficos e visualizações
- `config.py` - Configurações centralizadas do sistema

### **Componentes Modulares**
- `tabs/` - Abas do dashboard (KPIs, ranking, evolução, etc.)
- `faixa_components/` - Análises de segmentação de clientes
- `ui_components.py` - Componentes de interface
- `utils.py` - Funções utilitárias e helpers

### **Integrações**
- `iugu_service.py` - Integração com API da Iugu
- `sync_service.py` - Sincronização automática de dados
- `webhook_handler.py` - Manipulação de webhooks

## 🔧 Instalação e Configuração

### **Pré-requisitos**
```bash
# Python 3.9+
# pip (gerenciador de pacotes)
```

### **Instalação**
```bash
# Instalar dependências
pip install -r requirements.txt

# Executar aplicação
streamlit run main.py
```

### **Configuração Supabase (Opcional)**
```bash
# Criar arquivo .streamlit/secrets.toml
SUPABASE_URL = "sua_url_supabase"
SUPABASE_KEY = "sua_chave_supabase"
```

## 📊 Principais Métricas

### **KPIs Financeiros**
- **Faturamento Total**: Soma de todas as transações pagas
- **Ticket Médio**: Valor médio por transação
- **Taxa de Conversão**: Percentual de clientes que pagaram
- **Valor em Risco**: Soma de pendentes + expirados

### **Métricas de Clientes**
- **Clientes Únicos**: Quantidade de clientes distintos por período
- **LTV (Lifetime Value)**: Valor total pago por cliente
- **Churn Rate**: Clientes sem pagamentos há 60+ dias
- **Clientes Recorrentes**: Clientes com múltiplas transações

### **Análise de Churn**
- **Definição**: Clientes sem pagamentos há 60+ dias
- **Cálculo**: Baseado no último pagamento de cada cliente
- **Visualização**: Linha laranja tracejada no gráfico de evolução
- **Configuração**: Período ajustável em `config.py`

## 🎨 Guia Visual

### **Gráfico de Evolução Mensal**
- **📊 Barras Coloridas**: Faturamento por status (pago, pendente, expirado)
- **🔴 Linha Vermelha**: Clientes únicos pagantes por mês
- **🟠 Linha Tracejada**: Clientes em processo de churn
- **⚖️ Eixo Duplo**: Valores (R$) à esquerda, quantidade à direita

### **Sistema de Cores**
- **🟢 Verde**: Pagamentos confirmados
- **🟡 Amarelo**: Pagamentos pendentes
- **🔴 Vermelho**: Pagamentos expirados
- **🟠 Laranja**: Métricas de churn

## 📈 Como Usar

### **1. Upload de Dados**
```
Formatos aceitos: CSV
Colunas necessárias:
- Nome: Nome do cliente
- CPF/CNPJ: Documento identificador
- Total: Valor da transação
- Taxa: Taxa cobrada
- Situação: Status (Paga, Pendente, Expirado)
- Data de criação: Data da transação
```

### **2. Navegação**
- **Dashboard Principal**: Visão geral com todos os KPIs
- **Histórico de Cliente**: Análise individual detalhada
- **Projeção de Faturamento**: Previsões baseadas em histórico

### **3. Análise de Churn**
- Observe a linha laranja tracejada no gráfico de evolução
- Identifique períodos com maior churn
- Correlacione com métricas de clientes ativos
- Use para estratégias de retenção

## 🔍 Casos de Uso

### **Gestão Financeira**
- Monitorar evolução mensal do faturamento
- Identificar padrões sazonais
- Calcular projeções de receita
- Analisar concentração de clientes

### **Análise de Clientes**
- Segmentar clientes por valor (A, B, C)
- Identificar clientes em risco de churn
- Acompanhar evolução da base ativa
- Otimizar estratégias de retenção

### **Tomada de Decisões**
- Priorizar ações comerciais
- Identificar oportunidades de crescimento
- Monitorar saúde financeira
- Planejar estratégias de marketing

## 🚀 Melhorias Recentes

### **v2.1 - Análise de Churn**
- ✅ Implementado cálculo automático de churn
- ✅ Linha de churn no gráfico de evolução
- ✅ Configuração flexível do período
- ✅ Hover com informações detalhadas

### **v2.0 - Gráfico Triplo**
- ✅ Adicionada linha de clientes únicos pagantes
- ✅ Eixo duplo para melhor visualização
- ✅ Sistema de cores aprimorado
- ✅ Interatividade melhorada

## 📋 Próximas Funcionalidades

- [ ] Alertas automáticos de churn
- [ ] Integração com WhatsApp para notificações
- [ ] Dashboard mobile otimizado
- [ ] Relatórios automatizados em PDF
- [ ] Análise preditiva com ML

## 🎯 Performance

### **Otimizações Implementadas**
- Cache de dados com `@st.cache_data`
- Processamento vectorizado com pandas
- Queries otimizadas para grandes datasets
- Componentes modulares para melhor manutenibilidade

### **Capacidade**
- Suporte a datasets com 100k+ registros
- Resposta < 2 segundos para análises
- Uso eficiente de memória
- Escalabilidade horizontal

---

*Desenvolvido para análise completa de faturamento com foco em métricas de negócio e retenção de clientes.*