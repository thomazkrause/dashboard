import streamlit as st
import pandas as pd
from utils import formatar_moeda

class EvolutionTracker:
    def __init__(self, df, processor, calculator, viz, ui):
        self.df = df
        self.processor = processor
        self.calculator = calculator
        self.viz = viz
        self.ui = ui
    
    def render(self, ltv_por_cliente):
        """Renderiza evolução mensal por faixa"""
        st.subheader("📈 Evolução Mensal por Faixa de Cliente")
        
        if 'Mes_Ano' not in self.df.columns:
            st.warning("⚠️ Coluna 'Mes_Ano' não encontrada. Verifique o processamento de datas.")
            return
        
        df_com_faixa = self.processor.get_df_com_faixa(ltv_por_cliente)
        
        if df_com_faixa.empty:
            st.warning("⚠️ Não foi possível processar dados com faixa para evolução temporal.")
            return
        
        # Agrupar por mês e faixa
        evolucao_mensal = df_com_faixa.groupby(['Mes_Ano', 'Faixa_Cliente']).agg({
            'Total': ['sum', 'count'],
            'CPF/CNPJ': 'nunique'
        }).round(2)
        
        evolucao_mensal.columns = ['Valor_Total', 'Qtd_Transacoes', 'Clientes_Unicos']
        evolucao_mensal = evolucao_mensal.reset_index()
        evolucao_mensal['Mes_Ano_Str'] = evolucao_mensal['Mes_Ano'].astype(str)
        
        # Controles de visualização
        self._render_evolution_controls(evolucao_mensal)
        
        # Análise de crescimento por faixa
        self._analyze_monthly_growth(evolucao_mensal)
        
        # Tabela de evolução
        self._render_evolution_table(evolucao_mensal)
        
        st.markdown("---")
    
    def _render_evolution_controls(self, evolucao_mensal):
        """Renderiza controles de evolução"""
        col1, col2 = st.columns(2)
        
        with col1:
            metrica_evolucao = st.selectbox(
                "📊 Métrica para evolução:",
                ['Valor_Total', 'Qtd_Transacoes', 'Clientes_Unicos'],
                format_func=lambda x: {
                    'Valor_Total': 'Valor Total',
                    'Qtd_Transacoes': 'Quantidade de Transações',
                    'Clientes_Unicos': 'Clientes Únicos'
                }[x]
            )
        
        with col2:
            tipo_grafico = st.selectbox(
                "📈 Tipo de gráfico:",
                ['Linha', 'Área', 'Barras']
            )
        
        # Gráfico principal de evolução
        fig_evolucao = self.viz.create_evolucao_mensal_chart(evolucao_mensal)
        fig_evolucao.update_layout(height=400)
        st.plotly_chart(fig_evolucao, use_container_width=True)
    
    def _analyze_monthly_growth(self, evolucao_mensal):
        """Analisa crescimento mensal por faixa"""
        st.write("📊 **Análise de Crescimento Mensal**")
        
        if len(evolucao_mensal) < 2:
            st.info("📊 Necessários pelo menos 2 períodos para análise de crescimento.")
            return
        
        # Calcular crescimento para cada faixa
        crescimento_data = []
        
        for faixa in evolucao_mensal['Faixa_Cliente'].unique():
            df_faixa = evolucao_mensal[evolucao_mensal['Faixa_Cliente'] == faixa].sort_values('Mes_Ano')
            
            if len(df_faixa) >= 2:
                ultimo_valor = df_faixa['Valor_Total'].iloc[-1]
                penultimo_valor = df_faixa['Valor_Total'].iloc[-2]
                
                if penultimo_valor > 0:
                    crescimento_ultimo = ((ultimo_valor - penultimo_valor) / penultimo_valor) * 100
                else:
                    crescimento_ultimo = 0
                
                crescimento_data.append({
                    'Faixa': faixa,
                    'Crescimento_Ultimo': crescimento_ultimo,
                    'Valor_Atual': ultimo_valor
                })
        
        # Exibir crescimentos
        if crescimento_data:
            cols = st.columns(len(crescimento_data))
            
            for i, dados in enumerate(crescimento_data):
                with cols[i]:
                    emoji = {'Grupo A': '🥇', 'Grupo B': '🥈', 'Grupo C': '🥉'}.get(dados['Faixa'].split('(')[0].strip(), '📊')
                    
                    st.metric(
                        f"{emoji} {dados['Faixa'].split('(')[0].strip()}",
                        formatar_moeda(dados['Valor_Atual']),
                        f"{dados['Crescimento_Ultimo']:+.1f}%"
                    )
    
    def _render_evolution_table(self, evolucao_mensal):
        """Renderiza tabela de evolução"""
        st.write("📋 **Tabela de Evolução Mensal**")
        
        # Pivot para melhor visualização
        pivot_evolucao = evolucao_mensal.pivot(
            index='Mes_Ano_Str', 
            columns='Faixa_Cliente', 
            values='Valor_Total'
        ).fillna(0)
        
        # Formatar valores
        pivot_display = pivot_evolucao.applymap(lambda x: formatar_moeda(x) if x > 0 else '-')
        
        st.dataframe(pivot_display, use_container_width=True)