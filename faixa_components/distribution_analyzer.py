import streamlit as st
import plotly.express as px
from utils import formatar_moeda

class DistributionAnalyzer:
    def __init__(self, df, processor, calculator, viz, ui):
        self.df = df
        self.processor = processor
        self.calculator = calculator
        self.viz = viz
        self.ui = ui
    
    def render(self, faixa_stats, ltv_por_cliente):
        """Renderiza análise de distribuição"""
        st.subheader("📊 Análise de Distribuição por Faixa")
        
        tab1, tab2, tab3 = st.tabs(["💰 Faturamento", "👥 Clientes", "🎫 Performance"])
        
        with tab1:
            self._render_revenue_distribution(faixa_stats)
        
        with tab2:
            self._render_customer_distribution(faixa_stats, ltv_por_cliente)
        
        with tab3:
            self._render_performance_distribution(faixa_stats)
        
        st.markdown("---")
    
    def _render_revenue_distribution(self, faixa_stats):
        """Distribuição de faturamento"""
        col1, col2 = st.columns(2)
        
        with col1:
            # Gráfico de pizza
            fig_pizza = self.viz.create_faixa_pizza_chart(faixa_stats)
            st.plotly_chart(fig_pizza, use_container_width=True)
        
        with col2:
            # Gráfico de barras com valores
            fig_barras = px.bar(
                x=faixa_stats.index,
                y=faixa_stats['Faturamento_Total'],
                title="Faturamento Total por Faixa",
                color=faixa_stats['Faturamento_Total'],
                color_continuous_scale='Blues',
                text=faixa_stats['Faturamento_Total'].apply(lambda x: formatar_moeda(x))
            )
            fig_barras.update_traces(texttemplate='%{text}', textposition='outside')
            fig_barras.update_layout(height=400)
            st.plotly_chart(fig_barras, use_container_width=True)
        
        # Análise de concentração
        self._render_concentration_analysis(faixa_stats)
    
    def _render_concentration_analysis(self, faixa_stats):
        """Análise de concentração de faturamento"""
        st.write("📈 **Análise de Concentração de Faturamento**")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            # Concentração Grupo A
            if 'Grupo A (R$ 1.500+)' in faixa_stats.index:
                conc_a = faixa_stats.loc['Grupo A (R$ 1.500+)', 'Percentual_Faturamento']
                if conc_a > 60:
                    st.error(f"🚨 **Alta Dependência Grupo A**\n\n{conc_a:.1f}% do faturamento")
                elif conc_a > 40:
                    st.warning(f"⚠️ **Concentração Moderada**\n\n{conc_a:.1f}% do faturamento")
                else:
                    st.success(f"✅ **Distribuição Equilibrada**\n\n{conc_a:.1f}% do faturamento")
        
        with col2:
            # Participação dos dois grupos principais
            if len(faixa_stats) >= 2:
                top_2 = faixa_stats['Percentual_Faturamento'].nlargest(2).sum()
                st.metric("🔝 Top 2 Faixas", f"{top_2:.1f}%", "do faturamento total")
        
        with col3:
            # Índice de diversificação
            herfindahl = (faixa_stats['Percentual_Faturamento'] ** 2).sum()
            if herfindahl > 5000:
                st.error(f"📊 **Alta Concentração**\n\nÍndice: {herfindahl:.0f}")
            elif herfindahl > 3333:
                st.warning(f"📊 **Concentração Moderada**\n\nÍndice: {herfindahl:.0f}")
            else:
                st.success(f"📊 **Boa Diversificação**\n\nÍndice: {herfindahl:.0f}")
    
    def _render_customer_distribution(self, faixa_stats, ltv_por_cliente):
        """Distribuição de clientes"""
        col1, col2 = st.columns(2)
        
        with col1:
            # Gráfico de barras de quantidade de clientes
            fig_clientes = self.viz.create_faixa_bar_chart(faixa_stats)
            st.plotly_chart(fig_clientes, use_container_width=True)
        
        with col2:
            # Distribuição de LTV individual
            st.write("💎 **Distribuição de LTV Individual**")
            
            fig_ltv_dist = px.box(
                ltv_por_cliente,
                x='Faixa_Cliente',
                y='LTV_Total',
                title="Distribuição de LTV por Faixa",
                color='Faixa_Cliente',
                color_discrete_map=self.viz.cores_faixas
            )
            fig_ltv_dist.update_layout(height=400)
            st.plotly_chart(fig_ltv_dist, use_container_width=True)
    
    def _render_performance_distribution(self, faixa_stats):
        """Distribuição de performance"""
        col1, col2 = st.columns(2)
        
        with col1:
            # Gráfico de ticket médio por faixa
            fig_ticket = px.bar(
                x=faixa_stats.index,
                y=faixa_stats['Ticket_Medio'],
                title="Ticket Médio por Faixa",
                color=faixa_stats['Ticket_Medio'],
                color_continuous_scale='Greens',
                text=faixa_stats['Ticket_Medio'].apply(lambda x: formatar_moeda(x))
            )
            fig_ticket.update_traces(texttemplate='%{text}', textposition='outside')
            fig_ticket.update_layout(height=400)
            st.plotly_chart(fig_ticket, use_container_width=True)
        
        with col2:
            # Tabela de performance detalhada
            st.write("📋 **Performance Detalhada**")
            
            performance_display = faixa_stats.copy()
            performance_display['Faturamento_Total'] = performance_display['Faturamento_Total'].apply(formatar_moeda)
            performance_display['Ticket_Medio'] = performance_display['Ticket_Medio'].apply(formatar_moeda)
            
            # Adicionar eficiência (faturamento por cliente)
            performance_display['Eficiencia_Cliente'] = (faixa_stats['Faturamento_Total'] / faixa_stats['Qtd_Clientes']).apply(formatar_moeda)
            
            st.dataframe(performance_display, use_container_width=True)