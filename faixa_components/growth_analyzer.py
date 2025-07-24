import streamlit as st
from utils import formatar_moeda

class GrowthAnalyzer:
    def __init__(self, df, processor, calculator, viz, ui):
        self.df = df
        self.processor = processor
        self.calculator = calculator
        self.viz = viz
        self.ui = ui
    
    def render(self, faixa_stats, ltv_por_cliente):
        """Renderiza análise de oportunidades de crescimento"""
        st.subheader("🚀 Oportunidades de Crescimento")
        
        tab1, tab2, tab3 = st.tabs(["📈 Potencial de Upgrade", "🎯 Expansão de Base", "💎 Otimização de Valor"])
        
        with tab1:
            self._render_upgrade_potential(faixa_stats)
        
        with tab2:
            self._render_base_expansion(faixa_stats)
        
        with tab3:
            self._render_value_optimization(faixa_stats, ltv_por_cliente)
        
        st.markdown("---")
    
    def _render_upgrade_potential(self, faixa_stats):
        """Análise de potencial de upgrade"""
        st.write("📈 **Potencial de Upgrade entre Faixas**")
        
        upgrade_scenarios = []
        
        # Cenário 1: Grupo C → Grupo B
        if 'Grupo C (R$ 0-499)' in faixa_stats.index:
            clientes_c = faixa_stats.loc['Grupo C (R$ 0-499)', 'Qtd_Clientes']
            upgrade_c_b = int(clientes_c * 0.10)
            valor_adicional_c_b = upgrade_c_b * 250
            
            upgrade_scenarios.append({
                'Cenario': 'Grupo C → B',
                'Clientes': upgrade_c_b,
                'Valor_Adicional': valor_adicional_c_b,
                'Taxa_Conversao': '10%',
                'Estrategias': ['Campanhas de upsell', 'Pacotes promocionais', 'Programa de pontos']
            })
        
        # Cenário 2: Grupo B → Grupo A
        if 'Grupo B (R$ 500-1.499)' in faixa_stats.index:
            clientes_b = faixa_stats.loc['Grupo B (R$ 500-1.499)', 'Qtd_Clientes']
            upgrade_b_a = int(clientes_b * 0.05)
            valor_adicional_b_a = upgrade_b_a * 500
            
            upgrade_scenarios.append({
                'Cenario': 'Grupo B → A',
                'Clientes': upgrade_b_a,
                'Valor_Adicional': valor_adicional_b_a,
                'Taxa_Conversao': '5%',
                'Estrategias': ['Programa VIP', 'Atendimento premium', 'Ofertas exclusivas']
            })
        
        # Exibir cenários
        for scenario in upgrade_scenarios:
            col1, col2, col3 = st.columns([2, 1, 2])
            
            with col1:
                st.markdown(f"""
                **🎯 {scenario['Cenario']}**
                - Clientes elegíveis: {scenario['Clientes']:,}
                - Taxa de conversão: {scenario['Taxa_Conversao']}
                - Valor adicional: {formatar_moeda(scenario['Valor_Adicional'])}
                """)
            
            with col2:
                # Calcular ROI estimado
                investimento = scenario['Valor_Adicional'] * 0.2  # 20% de investimento
                roi = ((scenario['Valor_Adicional'] - investimento) / investimento) * 100 if investimento > 0 else 0
                
                st.metric("💰 ROI Estimado", f"{roi:.0f}%")
                st.metric("💸 Investimento", formatar_moeda(investimento))
            
            with col3:
                st.write("**🎯 Estratégias Recomendadas:**")
                for estrategia in scenario['Estrategias']:
                    st.write(f"• {estrategia}")
            
            st.markdown("---")
    
    def _render_base_expansion(self, faixa_stats):
        """Análise de expansão de base"""
        st.write("🎯 **Estratégias de Expansão de Base por Faixa**")
        
        expansion_strategies = {
            'Grupo A (R$ 1.500+)': {
                'foco': 'Retenção e Maximização',
                'estrategias': [
                    '👑 Programa de embaixadores',
                    '🎁 Benefícios exclusivos',
                    '📞 Atendimento dedicado',
                    '🔍 Análise preditiva de churn'
                ],
                'kpis': ['Taxa de retenção', 'Frequência de compra', 'Ticket médio']
            },
            'Grupo B (R$ 500-1.499)': {
                'foco': 'Crescimento e Upgrade',
                'estrategias': [
                    '📈 Campanhas de cross-sell',
                    '🎯 Segmentação avançada',
                    '💳 Facilidades de pagamento',
                    '🔄 Programas de fidelidade'
                ],
                'kpis': ['Taxa de upgrade', 'Frequência de compra', 'Valor por transação']
            },
            'Grupo C (R$ 0-499)': {
                'foco': 'Ativação e Educação',
                'estrategias': [
                    '🚀 Campanhas de ativação',
                    '📚 Conteúdo educativo',
                    '💰 Ofertas de entrada',
                    '📱 Experiência digital otimizada'
                ],
                'kpis': ['Taxa de ativação', 'Tempo para segunda compra', 'Taxa de conversão']
            }
        }
        
        for faixa, dados in expansion_strategies.items():
            if faixa in faixa_stats.index:
                stats = faixa_stats.loc[faixa]
                
                with st.expander(f"{faixa} - {int(stats['Qtd_Clientes'])} clientes ({stats['Percentual_Faturamento']:.1f}% do faturamento)"):
                    col1, col2, col3 = st.columns(3)
                    
                    with col1:
                        st.write(f"**🎯 Foco: {dados['foco']}**")
                        st.write("**📊 Situação Atual:**")
                        st.write(f"• Clientes: {int(stats['Qtd_Clientes']):,}")
                        st.write(f"• Faturamento: {formatar_moeda(stats['Faturamento_Total'])}")
                        st.write(f"• Ticket médio: {formatar_moeda(stats['Ticket_Medio'])}")
                    
                    with col2:
                        st.write("**🚀 Estratégias:**")
                        for estrategia in dados['estrategias']:
                            st.write(f"• {estrategia}")
                    
                    with col3:
                        st.write("**📈 KPIs de Acompanhamento:**")
                        for kpi in dados['kpis']:
                            st.write(f"• {kpi}")
                        
                        # Calcular potencial de expansão
                        if faixa == 'Grupo C (R$ 0-499)':
                            potencial = stats['Qtd_Clientes'] * 0.2 * 200  # 20% aumentam R$ 200
                        elif faixa == 'Grupo B (R$ 500-1.499)':
                            potencial = stats['Qtd_Clientes'] * 0.15 * 300  # 15% aumentam R$ 300
                        else:
                            potencial = stats['Qtd_Clientes'] * 0.1 * 500   # 10% aumentam R$ 500
                        
                        st.metric("💰 Potencial Anual", formatar_moeda(potencial))
    
    def _render_value_optimization(self, faixa_stats, ltv_por_cliente):
        """Análise de otimização de valor"""
        st.write("💎 **Otimização de Valor por Faixa**")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.write("📊 **Distribuição de LTV dentro das Faixas**")
            
            for faixa in faixa_stats.index:
                clientes_faixa = ltv_por_cliente[ltv_por_cliente['Faixa_Cliente'] == faixa]
                
                if not clientes_faixa.empty:
                    q25 = clientes_faixa['LTV_Total'].quantile(0.25)
                    q50 = clientes_faixa['LTV_Total'].quantile(0.50)
                    q75 = clientes_faixa['LTV_Total'].quantile(0.75)
                    
                    st.write(f"**{faixa.split('(')[0].strip()}:**")
                    st.write(f"• Q1: {formatar_moeda(q25)}")
                    st.write(f"• Mediana: {formatar_moeda(q50)}")
                    st.write(f"• Q3: {formatar_moeda(q75)}")
                    st.write("")
        
        with col2:
            st.write("🎯 **Oportunidades de Otimização**")
            
            for faixa in faixa_stats.index:
                clientes_faixa = ltv_por_cliente[ltv_por_cliente['Faixa_Cliente'] == faixa]
                
                if not clientes_faixa.empty:
                    # Identificar outliers inferiores (potencial de crescimento)
                    q1 = clientes_faixa['LTV_Total'].quantile(0.25)
                    outliers_baixos = clientes_faixa[clientes_faixa['LTV_Total'] < q1 * 0.5]
                    
                    if len(outliers_baixos) > 0:
                        valor_potencial = len(outliers_baixos) * (q1 - outliers_baixos['LTV_Total'].mean())
                        
                        st.write(f"**{faixa.split('(')[0].strip()}:**")
                        st.write(f"• Clientes sub-performando: {len(outliers_baixos)}")
                        st.write(f"• Potencial de valor: {formatar_moeda(valor_potencial)}")
                        st.write(f"• Ação recomendada: Campanhas de reativação")
                        st.write("")