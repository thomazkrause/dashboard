import plotly.express as px
import plotly.graph_objects as go
from utils import get_cores_faixas, get_cores_situacao

class Visualizations:
    def __init__(self):
        self.cores_faixas = get_cores_faixas()
        self.cores_situacao = get_cores_situacao()
    
    def create_faixa_pizza_chart(self, faixa_stats):
        """Cria gráfico de pizza para faturamento por faixa."""
        fig = px.pie(
            values=faixa_stats['Faturamento_Total'],
            names=faixa_stats.index,
            title='💰 Distribuição do Faturamento por Faixa',
            color_discrete_map=self.cores_faixas
        )
        fig.update_traces(textposition='inside', textinfo='percent+label')
        return fig
    
    def create_faixa_bar_chart(self, faixa_stats):
        """Cria gráfico de barras para quantidade de clientes por faixa."""
        fig = px.bar(
            x=faixa_stats.index,
            y=faixa_stats['Qtd_Clientes'],
            title='👥 Quantidade de Clientes por Faixa',
            color=faixa_stats['Qtd_Clientes'],
            color_continuous_scale='Blues'
        )
        fig.update_layout(xaxis_title='Faixa de Cliente', yaxis_title='Quantidade de Clientes')
        return fig
    
    def create_evolucao_mensal_chart(self, evolucao_mensal):
        """Cria gráfico de evolução mensal por faixa."""
        fig = px.line(
            evolucao_mensal,
            x='Mes_Ano_Str',
            y='Total',
            color='Faixa_Cliente',
            title='📊 Evolução Mensal do Faturamento por Faixa',
            labels={'Total': 'Faturamento (R$)', 'Mes_Ano_Str': 'Período'},
            color_discrete_map=self.cores_faixas
        )
        fig.update_traces(mode='lines+markers')
        fig.update_layout(height=400)
        return fig
    
    def create_pareto_chart(self, pareto_data):
        """Cria gráfico de Pareto."""
        fig = go.Figure()
        
        # Barras - Valor individual
        fig.add_trace(go.Bar(
            x=list(range(len(pareto_data))),
            y=pareto_data['Valor_Total'],
            name='Valor Individual',
            marker_color='skyblue',
            yaxis='y1'
        ))
        
        # Linha - Percentual acumulado
        fig.add_trace(go.Scatter(
            x=list(range(len(pareto_data))),
            y=pareto_data['Percentual_Acumulado'],
            mode='lines+markers',
            name='% Acumulado',
            line=dict(color='red', width=2),
            yaxis='y2'
        ))
        
        fig.update_layout(
            title='📊 Análise de Pareto - Top 30 Clientes',
            xaxis_title='Ranking de Clientes',
            yaxis=dict(title='Valor (R$)', side='left'),
            yaxis2=dict(title='Percentual Acumulado (%)', side='right', overlaying='y'),
            hovermode='x unified',
            height=500
        )
        
        return fig
    
    def create_evolucao_status_chart(self, df_mensal_status, df_clientes_unicos=None, df_churn=None):
        """Cria gráfico de evolução mensal por status com linhas de clientes únicos e churn."""
        fig = px.bar(
            df_mensal_status,
            x='Mes_Ano_Str',
            y='Total',
            color='Situação',
            title='📈 Evolução Mensal - Distribuição por Status de Pagamento',
            labels={'Total': 'Valor (R$)', 'Mes_Ano_Str': 'Mês/Ano'},
            color_discrete_map=self.cores_situacao
        )
        
        # Adicionar linha de clientes únicos pagantes se os dados foram fornecidos
        if df_clientes_unicos is not None and not df_clientes_unicos.empty:
            fig.add_trace(
                go.Scatter(
                    x=df_clientes_unicos['Mes_Ano_Str'],
                    y=df_clientes_unicos['Clientes_Unicos'],
                    mode='lines+markers',
                    name='Clientes Únicos Pagantes',
                    line=dict(color='#FF6B6B', width=3),
                    marker=dict(size=8, color='#FF6B6B'),
                    yaxis='y2',
                    hovertemplate='<b>Clientes Únicos</b><br>Período: %{x}<br>Quantidade: %{y}<extra></extra>'
                )
            )
        
        # Adicionar linha de churn se os dados foram fornecidos
        if df_churn is not None and not df_churn.empty:
            fig.add_trace(
                go.Scatter(
                    x=df_churn['Mes_Ano_Str'],
                    y=df_churn['Clientes_Churn'],
                    mode='lines+markers',
                    name='Clientes em Churn',
                    line=dict(color='#FFA500', width=3, dash='dash'),
                    marker=dict(size=8, color='#FFA500'),
                    yaxis='y2',
                    hovertemplate='<b>Clientes em Churn</b><br>Período: %{x}<br>Quantidade: %{y}<br><i>Sem pagamentos há 60+ dias</i><extra></extra>'
                )
            )
            
        # Configurar segundo eixo Y se há dados de clientes únicos ou churn
        if (df_clientes_unicos is not None and not df_clientes_unicos.empty) or (df_churn is not None and not df_churn.empty):
            fig.update_layout(
                yaxis2=dict(
                    title='Quantidade de Clientes',
                    side='right',
                    overlaying='y',
                    showgrid=False,
                    color='#666666'
                )
            )
        
        fig.update_layout(
            height=500,
            xaxis_title='Período',
            yaxis_title='Valor (R$)',
            hovermode='x unified',
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=1.02,
                xanchor="right",
                x=1
            )
        )
        return fig
    
    def create_situacao_pie_chart(self, situacao_counts):
        """Cria gráfico de pizza para status de pagamento."""
        fig = px.pie(
            values=situacao_counts.values,
            names=situacao_counts.index,
            title='📊 Status de Pagamento',
            color_discrete_sequence=px.colors.qualitative.Set3
        )
        fig.update_traces(textposition='inside', textinfo='percent+label')
        return fig
    
    def create_pagamento_pie_chart(self, metodos_pagamento):
        """Cria gráfico de pizza para métodos de pagamento."""
        fig = px.pie(
            values=metodos_pagamento.values,
            names=metodos_pagamento.index,
            title='💳 Métodos de Pagamento',
            color_discrete_sequence=px.colors.qualitative.Pastel
        )
        fig.update_traces(textposition='inside', textinfo='percent+label')
        return fig