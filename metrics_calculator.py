import pandas as pd
from datetime import datetime, timedelta
from utils import classificar_cliente_faixa

class MetricsCalculator:
    def __init__(self, df):
        self.df = df
    
    def calculate_basic_kpis(self):
        """Calcula KPIs básicos."""
        kpis = {
            'total_clientes': self.df['CPF/CNPJ'].nunique() if 'CPF/CNPJ' in self.df.columns else 0,
            'valor_total': self.df['Total'].sum() if 'Total' in self.df.columns else 0,
            'total_taxas': self.df['Taxa'].sum() if 'Taxa' in self.df.columns else 0,
            'clientes_pagos': 0,
            'taxa_conversao': 0
        }
        
        if 'Situação' in self.df.columns and 'CPF/CNPJ' in self.df.columns:
            kpis['clientes_pagos'] = self.df[self.df['Situação'].str.lower() == 'paga']['CPF/CNPJ'].nunique()
            
        if kpis['total_clientes'] > 0:
            kpis['taxa_conversao'] = (kpis['clientes_pagos'] / kpis['total_clientes']) * 100
            
        return kpis
    
    def calculate_valores_por_situacao(self):
        """Calcula valores por situação de pagamento."""
        valores = {
            'valor_pago': 0,
            'valor_pendente': 0,
            'valor_expirado': 0,
            'valor_risco': 0
        }
        
        if 'Situação' in self.df.columns and 'Total' in self.df.columns:
            valores['valor_pago'] = self.df[self.df['Situação'].str.lower() == 'paga']['Total'].sum()
            valores['valor_pendente'] = self.df[self.df['Situação'].str.lower() == 'pendente']['Total'].sum()
            valores['valor_expirado'] = self.df[self.df['Situação'].str.lower() == 'expirado']['Total'].sum()
            valores['valor_risco'] = valores['valor_pendente'] + valores['valor_expirado']
            
        return valores
    
    def calculate_advanced_metrics(self):
        """Calcula métricas avançadas (LTV, Churn, etc)."""
        metrics = {
            'ltv_medio': 0,
            'churn_rate': 0,
            'ticket_medio': 0,
            'clientes_recorrentes': 0
        }
        
        # LTV Médio
        if all(col in self.df.columns for col in ['CPF/CNPJ', 'Total', 'Situação']):
            ltv_por_cliente = self.df[self.df['Situação'].str.lower() == 'paga'].groupby('CPF/CNPJ')['Total'].sum()
            metrics['ltv_medio'] = ltv_por_cliente.mean() if len(ltv_por_cliente) > 0 else 0
        
        # Taxa de Churn
        if all(col in self.df.columns for col in ['CPF/CNPJ', 'Data de criação', 'Situação']):
            data_limite = datetime.now() - timedelta(days=60)
            clientes_pagaram = self.df[self.df['Situação'].str.lower() == 'paga']['CPF/CNPJ'].unique()
            df_recente = self.df[self.df['Data de criação'] >= data_limite]
            clientes_ativos = df_recente['CPF/CNPJ'].unique()
            clientes_churn = set(clientes_pagaram) - set(clientes_ativos)
            
            if len(clientes_pagaram) > 0:
                metrics['churn_rate'] = (len(clientes_churn) / len(clientes_pagaram)) * 100
        
        # Ticket Médio
        if 'Total' in self.df.columns and 'Situação' in self.df.columns:
            ticket_medio = self.df[self.df['Situação'].str.lower() == 'paga']['Total'].mean()
            metrics['ticket_medio'] = ticket_medio if not pd.isna(ticket_medio) else 0
        
        # Clientes Recorrentes
        if 'CPF/CNPJ' in self.df.columns:
            transacoes_por_cliente = self.df.groupby('CPF/CNPJ').size()
            metrics['clientes_recorrentes'] = (transacoes_por_cliente > 1).sum()
        
        return metrics
    
    def calculate_faixa_stats(self, ltv_por_cliente):
        """Calcula estatísticas por faixa de cliente."""
        if ltv_por_cliente.empty:
            return pd.DataFrame()
        
        faixa_stats = ltv_por_cliente.groupby('Faixa_Cliente').agg({
            'LTV_Total': ['sum', 'mean', 'count']
        }).round(2)
        
        faixa_stats.columns = ['Faturamento_Total', 'Ticket_Medio', 'Qtd_Clientes']
        
        # Calcular percentuais
        total_faturamento = faixa_stats['Faturamento_Total'].sum()
        faixa_stats['Percentual_Faturamento'] = (faixa_stats['Faturamento_Total'] / total_faturamento * 100).round(1)
        
        return faixa_stats
    
    def calculate_ranking_clientes(self):
        """Calcula ranking de clientes por valor."""
        if not all(col in self.df.columns for col in ['CPF/CNPJ', 'Total', 'Situação']):
            return pd.DataFrame()
        
        ranking = self.df[self.df['Situação'].str.lower() == 'paga'].groupby('CPF/CNPJ').agg({
            'Total': 'sum',
            'Nome': 'first',
            'Situação': 'count'
        }).reset_index()
        
        ranking.columns = ['CPF/CNPJ', 'Valor_Total', 'Nome', 'Num_Transacoes']
        ranking = ranking.sort_values('Valor_Total', ascending=False)
        
        # Calcular percentuais
        total_geral = ranking['Valor_Total'].sum()
        ranking['Percentual'] = (ranking['Valor_Total'] / total_geral * 100).round(2)
        ranking['Percentual_Acumulado'] = ranking['Percentual'].cumsum().round(2)
        ranking['Faixa'] = ranking['Valor_Total'].apply(classificar_cliente_faixa)
        
        return ranking
    
    def calculate_churn_mensal(self, df):
        """Calcula clientes em churn por mês."""
        from config import ANALISE_CONFIG
        
        if not all(col in df.columns for col in ['CPF/CNPJ', 'Data de criação', 'Situação', 'Mes_Ano']):
            return pd.DataFrame()
        
        # Filtrar apenas pagamentos
        df_pagos = df[df['Situação'].str.lower() == 'paga'].copy()
        
        if df_pagos.empty:
            return pd.DataFrame()
        
        # Obter último pagamento de cada cliente
        ultimo_pagamento = df_pagos.groupby('CPF/CNPJ')['Data de criação'].max().reset_index()
        ultimo_pagamento.columns = ['CPF/CNPJ', 'Ultimo_Pagamento']
        
        # Obter todos os períodos únicos
        periodos = sorted(df['Mes_Ano'].unique())
        
        churn_mensal = []
        
        for i, periodo in enumerate(periodos):
            if i == 0:  # Primeiro período não tem churn
                churn_mensal.append({
                    'Mes_Ano': periodo,
                    'Clientes_Churn': 0,
                    'Mes_Ano_Str': str(periodo)
                })
                continue
            
            # Data de corte do período (último dia do mês)
            try:
                data_corte = pd.to_datetime(f"{periodo}-01") + pd.offsets.MonthEnd(0)
                
                # Clientes que fizeram último pagamento antes de X dias da data de corte
                dias_churn = ANALISE_CONFIG['dias_churn']
                data_limite_churn = data_corte - timedelta(days=dias_churn)
                
                # Contar clientes em churn
                clientes_churn = ultimo_pagamento[
                    ultimo_pagamento['Ultimo_Pagamento'] <= data_limite_churn
                ].shape[0]
                
                churn_mensal.append({
                    'Mes_Ano': periodo,
                    'Clientes_Churn': clientes_churn,
                    'Mes_Ano_Str': str(periodo)
                })
                
            except Exception as e:
                # Em caso de erro, colocar 0
                churn_mensal.append({
                    'Mes_Ano': periodo,
                    'Clientes_Churn': 0,
                    'Mes_Ano_Str': str(periodo)
                })
        
        return pd.DataFrame(churn_mensal)