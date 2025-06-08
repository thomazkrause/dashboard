import streamlit as st
import pandas as pd
from utils import formatar_moeda

class StrategyRecommender:
    def __init__(self, df, processor, calculator, viz, ui):
        self.df = df
        self.processor = processor
        self.calculator = calculator
        self.viz = viz
        self.ui = ui
    
    def render(self, faixa_stats):
        """Renderiza recomendações estratégicas"""
        st.subheader("💡 Recomendações Estratégicas")
        
        # Análise da situação atual
        situacao_atual = self._analyze_current_situation(faixa_stats)
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.write("📊 **Diagnóstico Atual**")
            for insight in situacao_atual['insights']:
                st.markdown(f"• {insight}")
        
        with col2:
            st.write("🎯 **Plano de Ação Recomendado**")
            for acao in situacao_atual['acoes']:
                st.markdown(f"• {acao}")
        
        # Roadmap estratégico
        self._render_strategic_roadmap()
        
        # ROI esperado
        self._render_roi_projections(faixa_stats)
    
    def _analyze_current_situation(self, faixa_stats):
        """Analisa a situação atual e gera insights"""
        insights = []
        acoes = []
        
        # Análise de concentração
        grupo_a_perc = faixa_stats.loc['Grupo A (R$ 1.500+)', 'Percentual_Faturamento'] if 'Grupo A (R$ 1.500+)' in faixa_stats.index else 0
        
        if grupo_a_perc > 60:
            insights.append("🚨 Alta dependência do Grupo A - risco de concentração")
            acoes.append("🛡️ Diversificar base desenvolvendo Grupos B e C")
        elif grupo_a_perc < 30:
            insights.append("📊 Baixa participação do Grupo A - oportunidade de premium")
            acoes.append("⬆️ Focar em estratégias de upgrade para Grupo A")
        
        # Análise de distribuição
        grupo_c_perc = faixa_stats.loc['Grupo C (R$ 0-499)', 'Percentual_Faturamento'] if 'Grupo C (R$ 0-499)' in faixa_stats.index else 0
        grupo_c_clientes = faixa_stats.loc['Grupo C (R$ 0-499)', 'Qtd_Clientes'] if 'Grupo C (R$ 0-499)' in faixa_stats.index else 0
        total_clientes = faixa_stats['Qtd_Clientes'].sum()
        
        if grupo_c_clientes / total_clientes > 0.6:  # Mais de 60% dos clientes no Grupo C
            insights.append("📈 Grande base de clientes Grupo C - potencial de crescimento")
            acoes.append("🚀 Implementar programas de ativação e upgrade para Grupo C")
        
        # Análise de eficiência
        grupo_b_ticket = faixa_stats.loc['Grupo B (R$ 500-1.499)', 'Ticket_Medio'] if 'Grupo B (R$ 500-1.499)' in faixa_stats.index else 0
        
        if grupo_b_ticket > 800:  # Grupo B com ticket alto
            insights.append("💎 Grupo B com bom ticket médio - candidatos a upgrade")
            acoes.append("🎯 Criar jornada de upgrade do Grupo B para A")
        
        # Análise de equilíbrio
        distribuicao_equilibrada = all(
            20 <= faixa_stats.loc[faixa, 'Percentual_Faturamento'] <= 50 
            for faixa in faixa_stats.index
        )
        
        if distribuicao_equilibrada:
            insights.append("✅ Distribuição equilibrada entre faixas")
            acoes.append("🔄 Manter estratégias atuais e otimizar performance")
        else:
            insights.append("⚖️ Distribuição desbalanceada entre faixas")
            acoes.append("📊 Rebalancear estratégias por faixa")
        
        return {
            'insights': insights,
            'acoes': acoes
        }
    
    def _render_strategic_roadmap(self):
        """Renderiza roadmap estratégico"""
        st.write("🗓️ **Roadmap Estratégico**")
        
        roadmap_tabs = st.tabs(["📅 30 dias", "📅 90 dias", "📅 6 meses"])
        
        with roadmap_tabs[0]:
            st.write("**🚀 Ações Imediatas (30 dias):**")
            st.write("• Implementar segmentação de campanhas por faixa")
            st.write("• Criar programa de retenção para Grupo A")
            st.write("• Lançar campanha de ativação para Grupo C")
            st.write("• Definir KPIs específicos por faixa")
        
        with roadmap_tabs[1]:
            st.write("**📈 Desenvolvimento (90 dias):**")
            st.write("• Implementar programa de fidelidade diferenciado")
            st.write("• Otimizar jornada de upgrade entre faixas")
            st.write("• Desenvolver análise preditiva de churn")
            st.write("• Criar ofertas personalizadas por comportamento")
        
        with roadmap_tabs[2]:
            st.write("**🎯 Consolidação (6 meses):**")
            st.write("• Avaliar efetividade das estratégias por faixa")
            st.write("• Ajustar critérios de segmentação se necessário")
            st.write("• Expandir programa de embaixadores")
            st.write("• Implementar automação de marketing por faixa")
    
    def _render_roi_projections(self, faixa_stats):
        """Renderiza projeções de ROI"""
        st.write("💰 **Projeção de ROI das Estratégias**")
        
        # Estimativas conservadoras de crescimento
        crescimento_estimado = {
            'Grupo A (R$ 1.500+)': 0.05,  # 5% de crescimento
            'Grupo B (R$ 500-1.499)': 0.10,  # 10% de crescimento
            'Grupo C (R$ 0-499)': 0.15   # 15% de crescimento
        }
        
        projecoes = []
        for faixa, taxa in crescimento_estimado.items():
            if faixa in faixa_stats.index:
                valor_atual = faixa_stats.loc[faixa, 'Faturamento_Total']
                valor_projetado = valor_atual * (1 + taxa)
                incremento = valor_projetado - valor_atual
                
                projecoes.append({
                    'Faixa': faixa.split('(')[0].strip(),
                    'Valor_Atual': valor_atual,
                    'Crescimento_Esperado': f"{taxa*100:.0f}%",
                    'Valor_Adicional': incremento
                })
        
        if projecoes:
            col1, col2, col3 = st.columns(3)
            
            valor_adicional_total = sum(p['Valor_Adicional'] for p in projecoes)
            investimento_estimado = valor_adicional_total * 0.3  # 30% de investimento
            roi_projetado = ((valor_adicional_total - investimento_estimado) / investimento_estimado) * 100
            
            with col1:
                st.metric("💰 Valor Adicional Projetado", formatar_moeda(valor_adicional_total))
            
            with col2:
                st.metric("💸 Investimento Estimado", formatar_moeda(investimento_estimado))
            
            with col3:
                st.metric("📈 ROI Projetado", f"{roi_projetado:.0f}%")
            
            # Tabela de projeções
            st.write("📋 **Detalhamento das Projeções por Faixa**")
            
            projecoes_df = pd.DataFrame(projecoes)
            projecoes_df['Valor_Atual'] = projecoes_df['Valor_Atual'].apply(formatar_moeda)
            projecoes_df['Valor_Adicional'] = projecoes_df['Valor_Adicional'].apply(formatar_moeda)
            
            st.dataframe(projecoes_df, use_container_width=True, hide_index=True)