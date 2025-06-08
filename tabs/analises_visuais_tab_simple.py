import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

class AnalisesVisuaisTab:
    def __init__(self, df, viz):
        self.df = df
        self.viz = viz
    
    def render(self):
        """Renderiza a aba de análises visuais"""
        if self.df.empty:
            st.warning("⚠️ Nenhum dado disponível para análise visual.")
            return
        
        # Análise de status de pagamento
        self._render_payment_status_analysis()
        
        # Análise de métodos de pagamento
        self._render_payment_method_analysis()
        
        # Análise temporal
        self._render_temporal_analysis()
        
        # Análise de valores
        self._render_value_analysis()
    
    def _render_payment_status_analysis(self):
        """Renderiza análise de status de pagamento"""
        st.subheader("💳 Análise de Status de Pagamento")
        
        if 'Situação' not in self.df.columns:
            st.warning("⚠️ Coluna 'Situação' não encontrada.")
            return
        
        col1, col2 = st.columns([2, 1])
        
        with col1:
            situacao_counts = self.df['Situação'].value_counts()
            fig_situacao = self.viz.create_situacao_pie_chart(situacao_counts)
            st.plotly_chart(fig_situacao, use_container_width=True)
        
        with col2:
            st.write("📊 **Estatísticas por Status**")
            total_transacoes = len(self.df)
            
            for situacao, count in situacao_counts.items():
                percentual = (count / total_transacoes) * 100
                st.metric(f"📊 {situacao}", f"{count:,}", f"{percentual:.1f}%")
        
        st.markdown("---")
    
    def _render_payment_method_analysis(self):
        """Renderiza análise de métodos de pagamento"""
        st.subheader("💳 Análise de Métodos de Pagamento")
        
        if 'Paga com' not in self.df.columns:
            st.warning("⚠️ Coluna 'Paga com' não encontrada.")
            return
        
        # Filtrar apenas registros pagos
        df_pagos = self.df.copy()
        if 'Situação' in self.df.columns:
            df_pagos = self.df[self.df['Situação'].str.lower() == 'paga']
        
        if df_pagos.empty:
            st.info("📊 Nenhum registro pago encontrado para análise de métodos.")
            return
        
        col1, col2 = st.columns([2, 1])
        
        with col1:
            metodos_pagamento = df_pagos['Paga com'].value_counts()
            fig_pagamento = self.viz.create_pagamento_pie_chart(metodos_pagamento)
            st.plotly_chart(fig_pagamento, use_container_width=True)
        
        with col2:
            st.write("📈 **Top 5 Métodos**")
            
            if 'Total' in df_pagos.columns:
                metodo_stats = df_pagos.groupby('Paga com')['Total'].agg(['sum', 'count']).round(2)
                metodo_stats.columns = ['Valor_Total', 'Quantidade']
                metodo_stats = metodo_stats.sort_values('Valor_Total', ascending=False)
                
                for i, (metodo, stats) in enumerate(metodo_stats.head(5).iterrows()):
                    if pd.notna(metodo):
                        st.metric(
                            f"💳 {metodo}",
                            f"R$ {stats['Valor_Total']:,.2f}",
                            f"{int(stats['Quantidade'])} transações"
                        )
        
        st.markdown("---")
    
    def _render_temporal_analysis(self):
        """Renderiza análise temporal"""
        st.subheader("📅 Análise Temporal")
        
        if 'Data de criação' not in self.df.columns:
            st.warning("⚠️ Coluna 'Data de criação' não encontrada.")
            return
        
        # Preparar dados temporais
        df_temporal = self.df.copy()
        df_temporal['Data de criação'] = pd.to_datetime(df_temporal['Data de criação'], errors='coerce')
        df_temporal = df_temporal.dropna(subset=['Data de criação'])
        
        if df_temporal.empty:
            st.warning("⚠️ Nenhuma data válida encontrada.")
            return
        
        df_temporal['Dia_Semana'] = df_temporal['Data de criação'].dt.day_name()
        df_temporal['Mes'] = df_temporal['Data de criação'].dt.month
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.write("📊 **Transações por Dia da Semana**")
            dias_semana = df_temporal['Dia_Semana'].value_counts()
            st.bar_chart(dias_semana)
        
        with col2:
            st.write("📊 **Transações por Mês**")
            meses = df_temporal['Mes'].value_counts().sort_index()
            st.bar_chart(meses)
        
        st.markdown("---")
    
    def _render_value_analysis(self):
        """Renderiza análise de valores"""
        st.subheader("💰 Análise de Distribuição de Valores")
        
        if 'Total' not in self.df.columns:
            st.warning("⚠️ Coluna 'Total' não encontrada.")
            return
        
        valores = self.df['Total'].dropna()
        
        if valores.empty:
            st.warning("⚠️ Nenhum valor válido encontrado.")
            return
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.write("📊 **Estatísticas Básicas**")
            st.metric("💰 Valor Médio", f"R$ {valores.mean():,.2f}")
            st.metric("📊 Mediana", f"R$ {valores.median():,.2f}")
            st.metric("📈 Desvio Padrão", f"R$ {valores.std():,.2f}")
        
        with col2:
            st.write("🎯 **Extremos**")
            st.metric("🔝 Valor Máximo", f"R$ {valores.max():,.2f}")
            st.metric("🔻 Valor Mínimo", f"R$ {valores.min():,.2f}")
            st.metric("📏 Amplitude", f"R$ {valores.max() - valores.min():,.2f}")
        
        with col3:
            st.write("📊 **Quartis**")
            q1, q2, q3 = valores.quantile([0.25, 0.5, 0.75])
            st.metric("Q1 (25%)", f"R$ {q1:,.2f}")
            st.metric("Q2 (50%)", f"R$ {q2:,.2f}")
            st.metric("Q3 (75%)", f"R$ {q3:,.2f}")
        
        # Histograma
        st.write("📊 **Distribuição de Valores**")
        fig_hist = px.histogram(
            valores,
            nbins=30,
            title="Distribuição de Valores",
            labels={'value': 'Valor (R$)', 'count': 'Frequência'}
        )
        st.plotly_chart(fig_hist, use_container_width=True)