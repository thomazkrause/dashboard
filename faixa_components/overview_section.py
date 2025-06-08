import streamlit as st
from utils import formatar_moeda

class OverviewSection:
    def __init__(self, df, processor, calculator, viz, ui):
        self.df = df
        self.processor = processor
        self.calculator = calculator
        self.viz = viz
        self.ui = ui
    
    def render(self, faixa_stats, ltv_por_cliente):
        """Renderiza seção de visão geral"""
        st.subheader("📊 Visão Geral por Faixa de Cliente")
        
        # KPIs gerais
        self._render_general_kpis(faixa_stats, ltv_por_cliente)
        
        # Resumo executivo por faixa
        st.markdown("---")
        self.ui.display_faixa_summary(faixa_stats)
        st.markdown("---")
    
    def _render_general_kpis(self, faixa_stats, ltv_por_cliente):
        """Renderiza KPIs gerais"""
        col1, col2, col3, col4, col5 = st.columns(5)
        
        total_clientes = len(ltv_por_cliente)
        valor_total = ltv_por_cliente['LTV_Total'].sum()
        ltv_medio_geral = ltv_por_cliente['LTV_Total'].mean()
        
        with col1:
            st.metric("👥 Total de Clientes", f"{total_clientes:,}")
        
        with col2:
            st.metric("💰 LTV Total", formatar_moeda(valor_total))
        
        with col3:
            st.metric("💎 LTV Médio", formatar_moeda(ltv_medio_geral))
        
        with col4:
            # Faixa dominante
            faixa_dominante = faixa_stats['Percentual_Faturamento'].idxmax()
            percentual_dominante = faixa_stats.loc[faixa_dominante, 'Percentual_Faturamento']
            st.metric("🏆 Faixa Dominante", faixa_dominante.split('(')[0].strip(), f"{percentual_dominante:.1f}%")
        
        with col5:
            # Diversificação (inverso do índice de concentração)
            concentracao = (faixa_stats['Percentual_Faturamento'] ** 2).sum() / 100
            diversificacao = 100 - concentracao
            st.metric("🎯 Diversificação", f"{diversificacao:.1f}%")