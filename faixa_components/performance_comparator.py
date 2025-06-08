import streamlit as st
import plotly.graph_objects as go
from utils import formatar_moeda

class PerformanceComparator:
    def __init__(self, df, processor, calculator, viz, ui):
        self.df = df
        self.processor = processor
        self.calculator = calculator
        self.viz = viz
        self.ui = ui
    
    def render(self, faixa_stats, ltv_por_cliente):
        """Renderiza comparação de performance entre faixas"""
        st.subheader("🔍 Comparação de Performance entre Faixas")
        
        # Análise de gaps entre faixas
        self._render_performance_gaps(faixa_stats)
        
        # Análise de potencial de crescimento
        self._render_growth_potential(faixa_stats)
        
        st.markdown("---")
    
    def _render_performance_gaps(self, faixa_stats):
        """Renderiza gaps de performance"""
        col1, col2 = st.columns(2)
        
        with col1:
            st.write("📊 **Gaps de Performance**")
            
            # Calcular gaps entre faixas consecutivas
            faixas_ordenadas = ['Grupo A (R$ 1.500+)', 'Grupo B (R$ 500-1.499)', 'Grupo C (R$ 0-499)']
            
            for i in range(len(faixas_ordenadas) - 1):
                faixa_superior = faixas_ordenadas[i]
                faixa_inferior = faixas_ordenadas[i + 1]
                
                if faixa_superior in faixa_stats.index and faixa_inferior in faixa_stats.index:
                    ticket_superior = faixa_stats.loc[faixa_superior, 'Ticket_Medio']
                    ticket_inferior = faixa_stats.loc[faixa_inferior, 'Ticket_Medio']
                    
                    gap_ticket = ((ticket_superior - ticket_inferior) / ticket_inferior) * 100 if ticket_inferior > 0 else 0
                    
                    st.metric(
                        f"{faixa_superior.split('(')[0].strip()} vs {faixa_inferior.split('(')[0].strip()}",
                        f"{gap_ticket:.0f}%",
                        f"{formatar_moeda(ticket_superior)} vs {formatar_moeda(ticket_inferior)}"
                    )
        
        with col2:
            st.write("⚖️ **Índices de Eficiência**")
            
            # Calcular índices de eficiência
            for faixa in faixa_stats.index:
                stats = faixa_stats.loc[faixa]
                
                # Eficiência de receita (faturamento / número de clientes)
                eficiencia_receita = stats['Faturamento_Total'] / stats['Qtd_Clientes']
                
                # Índice de concentração (% faturamento / % clientes)
                perc_clientes = (stats['Qtd_Clientes'] / faixa_stats['Qtd_Clientes'].sum()) * 100
                indice_concentracao = stats['Percentual_Faturamento'] / perc_clientes if perc_clientes > 0 else 0
                
                emoji = {'Grupo A': '🥇', 'Grupo B': '🥈', 'Grupo C': '🥉'}.get(faixa.split('(')[0].strip(), '📊')
                
                st.metric(
                    f"{emoji} {faixa.split('(')[0].strip()}",
                    f"{indice_concentracao:.2f}",
                    f"Índice de concentração"
                )
                st.caption(f"Eficiência: {formatar_moeda(eficiencia_receita)}/cliente")
    
    def _render_growth_potential(self, faixa_stats):
        """Renderiza potencial de crescimento"""
        st.write("🚀 **Análise de Potencial de Crescimento**")
        
        potencial_data = []
        
        for faixa in faixa_stats.index:
            stats = faixa_stats.loc[faixa]
            
            # Calcular potencial baseado na faixa superior
            if faixa == 'Grupo C (R$ 0-499)':
                # Potencial de upgrade para Grupo B
                clientes_c = stats['Qtd_Clientes']
                upgrade_potential = clientes_c * 0.15  # 15% podem fazer upgrade
                valor_adicional = upgrade_potential * 250  # Assumindo upgrade para média de R$ 250
                
                potencial_data.append({
                    'Faixa': 'Grupo C → B',
                    'Clientes_Potencial': upgrade_potential,
                    'Valor_Adicional': valor_adicional,
                    'Estrategia': 'Campanhas de upsell'
                })
            
            elif faixa == 'Grupo B (R$ 500-1.499)':
                # Potencial de upgrade para Grupo A
                clientes_b = stats['Qtd_Clientes']
                upgrade_potential = clientes_b * 0.10  # 10% podem fazer upgrade
                valor_adicional = upgrade_potential * 500  # Assumindo upgrade para média de R$ 500
                
                potencial_data.append({
                    'Faixa': 'Grupo B → A',
                    'Clientes_Potencial': upgrade_potential,
                    'Valor_Adicional': valor_adicional,
                    'Estrategia': 'Programas VIP'
                })
        
        if potencial_data:
            for pot in potencial_data:
                col1, col2 = st.columns(2)
                
                with col1:
                    st.markdown(f"""
                    **🎯 {pot['Faixa']}**
                    - Clientes potenciais: {pot['Clientes_Potencial']:.0f}
                    - Valor adicional: {formatar_moeda(pot['Valor_Adicional'])}
                    - Estratégia: {pot['Estrategia']}
                    """)
                
                with col2:
                    # Calcular ROI estimado
                    investimento = pot['Valor_Adicional'] * 0.2  # 20% de investimento
                    roi = ((pot['Valor_Adicional'] - investimento) / investimento) * 100 if investimento > 0 else 0
                    
                    st.metric("💰 ROI Estimado", f"{roi:.0f}%")
                    st.metric("💸 Investimento", formatar_moeda(investimento))