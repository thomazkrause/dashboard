import streamlit as st
import pandas as pd  # Add this import
from utils import formatar_moeda, get_ordem_faixas

class UIComponents:
    @staticmethod
    def display_basic_kpis(kpis):
        """Exibe KPIs básicos."""
        st.header("📈 KPIs Principais")
        
        col1, col2, col3, col4, col5 = st.columns(5)
        
        with col1:
            st.metric("👥 Total Clientes", kpis['total_clientes'])
        with col2:
            st.metric("💰 Valor Total", formatar_moeda(kpis['valor_total']))
        with col3:
            st.metric("📊 Total Taxas", formatar_moeda(kpis['total_taxas']))
        with col4:
            st.metric("✅ Clientes Pagos", kpis['clientes_pagos'])
        with col5:
            st.metric("📈 Taxa Conversão", f"{kpis['taxa_conversao']:.1f}%")
    
    @staticmethod
    def display_valores_situacao(valores):
        """Exibe valores por situação."""
        st.subheader("💵 Valores por Situação")
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("✅ Valor Pago", formatar_moeda(valores['valor_pago']))
        with col2:
            st.metric("⏳ Valor Pendente", formatar_moeda(valores['valor_pendente']))
        with col3:
            st.metric("❌ Valor Expirado", formatar_moeda(valores['valor_expirado']))
        with col4:
            st.metric("⚠️ Valor em Risco", formatar_moeda(valores['valor_risco']))
    
    @staticmethod
    def display_advanced_metrics(metrics):
        """Exibe métricas avançadas."""
        st.subheader("🎯 Métricas Avançadas")
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("💎 LTV Médio", formatar_moeda(metrics['ltv_medio']))
        with col2:
            st.metric("📉 Taxa de Churn", f"{metrics['churn_rate']:.1f}%")
        with col3:
            st.metric("🎫 Ticket Médio", formatar_moeda(metrics['ticket_medio']))
        with col4:
            st.metric("🔄 Clientes Recorrentes", metrics['clientes_recorrentes'])
    
    @staticmethod
    def _safe_int(value):
        """Converte valor para int de forma segura, retornando 0 se NaN."""
        try:
            if pd.isna(value):
                return 0
            return int(value)
        except (ValueError, TypeError):
            return 0
    
    @staticmethod
    def _safe_float(value):
        """Converte valor para float de forma segura, retornando 0.0 se NaN."""
        try:
            if pd.isna(value):
                return 0.0
            return float(value)
        except (ValueError, TypeError):
            return 0.0
    
    @staticmethod
    def display_faixa_summary(faixa_stats):
        """Exibe resumo por faixa de cliente."""
        import pandas as pd  # Import necessário para pd.isna()
        
        st.subheader("📊 Resumo por Faixa de Cliente")
        col1, col2, col3 = st.columns(3)
        
        ordem_faixas = get_ordem_faixas()
        
        with col1:
            if 'Grupo A (R$ 1.500+)' in faixa_stats.index:
                grupo_a = faixa_stats.loc['Grupo A (R$ 1.500+)']
                st.metric(
                    "🥇 Grupo A (Premium)",
                    formatar_moeda(UIComponents._safe_float(grupo_a['Faturamento_Total'])),
                    f"{UIComponents._safe_float(grupo_a['Percentual_Faturamento']):.1f}% do total"
                )
                st.write(f"👥 {UIComponents._safe_int(grupo_a['Qtd_Clientes'])} clientes")
                st.write(f"🎫 Ticket médio: {formatar_moeda(UIComponents._safe_float(grupo_a['Ticket_Medio']))}")
            else:
                st.metric("🥇 Grupo A (Premium)", "R$ 0,00", "0.0% do total")
                st.write("👥 0 clientes")
                st.write("🎫 Ticket médio: R$ 0,00")
        
        with col2:
            if 'Grupo B (R$ 500-1.499)' in faixa_stats.index:
                grupo_b = faixa_stats.loc['Grupo B (R$ 500-1.499)']
                st.metric(
                    "🥈 Grupo B (Médio)",
                    formatar_moeda(UIComponents._safe_float(grupo_b['Faturamento_Total'])),
                    f"{UIComponents._safe_float(grupo_b['Percentual_Faturamento']):.1f}% do total"
                )
                st.write(f"👥 {UIComponents._safe_int(grupo_b['Qtd_Clientes'])} clientes")
                st.write(f"🎫 Ticket médio: {formatar_moeda(UIComponents._safe_float(grupo_b['Ticket_Medio']))}")
            else:
                st.metric("🥈 Grupo B (Médio)", "R$ 0,00", "0.0% do total")
                st.write("👥 0 clientes")
                st.write("🎫 Ticket médio: R$ 0,00")
        
        with col3:
            if 'Grupo C (R$ 0-499)' in faixa_stats.index:
                grupo_c = faixa_stats.loc['Grupo C (R$ 0-499)']
                st.metric(
                    "🥉 Grupo C (Básico)",
                    formatar_moeda(UIComponents._safe_float(grupo_c['Faturamento_Total'])),
                    f"{UIComponents._safe_float(grupo_c['Percentual_Faturamento']):.1f}% do total"
                )
                st.write(f"👥 {UIComponents._safe_int(grupo_c['Qtd_Clientes'])} clientes")
                st.write(f"🎫 Ticket médio: {formatar_moeda(UIComponents._safe_float(grupo_c['Ticket_Medio']))}")
            else:
                st.metric("🥉 Grupo C (Básico)", "R$ 0,00", "0.0% do total")
                st.write("👥 0 clientes")
                st.write("🎫 Ticket médio: R$ 0,00")
    
    @staticmethod
    def display_ranking_analysis(ranking_clientes, total_geral):
        """Exibe análise de concentração de clientes."""
        st.subheader("📊 Análise de Concentração")
        
        # Análise 80/20
        top_20_percent = int(len(ranking_clientes) * 0.2)
        valor_top_20 = ranking_clientes.head(top_20_percent)['Valor_Total'].sum()
        percentual_80_20 = (valor_top_20 / total_geral * 100) if total_geral > 0 else 0
        
        st.metric("📈 Regra 80/20", f"{percentual_80_20:.1f}%", "Top 20% dos clientes")
        
        # Top 10 clientes
        top_10_valor = ranking_clientes.head(10)['Valor_Total'].sum()
        percentual_top_10 = (top_10_valor / total_geral * 100) if total_geral > 0 else 0
        
        st.metric("🔝 Top 10 Clientes", f"{percentual_top_10:.1f}%", "do faturamento total")
        
        # Concentração de risco
        if percentual_top_10 > 50:
            st.error("⚠️ Alto risco de concentração!")
        elif percentual_top_10 > 30:
            st.warning("⚡ Concentração moderada")
        else:
            st.success("✅ Diversificação saudável")
    
    @staticmethod
    def display_instructions():
        """Exibe instruções de uso."""
        st.info("👆 Faça upload do seu arquivo CSV para começar!")
        
        st.header("📖 Como usar:")
        st.markdown("""
        1. **Upload**: Faça upload do seu arquivo CSV na barra lateral
        2. **KPIs**: Visualize indicadores principais, LTV e Churn
        3. **Faixas de Cliente**: Analise grupos A, B e C por valor
        4. **Ranking**: Veja top clientes e concentração de faturamento
        5. **Evolução**: Acompanhe tendências mensais por faixa
        6. **Pareto**: Entenda a distribuição 80/20 dos clientes
        """)