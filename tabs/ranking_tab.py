import streamlit as st
from utils import formatar_moeda

class RankingTab:
    def __init__(self, df, calculator, viz, ui):
        self.df = df
        self.calculator = calculator
        self.viz = viz
        self.ui = ui
    
    def render(self):
        """Renderiza a aba de ranking de clientes"""
        st.header("🥇 Ranking de Clientes por Valor")
        
        ranking_clientes = self.calculator.calculate_ranking_clientes()
        
        if ranking_clientes.empty:
            st.warning("⚠️ Não foi possível calcular ranking de clientes.")
            return
        
        total_geral = ranking_clientes['Valor_Total'].sum()
        
        # Seções da aba
        self._render_concentration_analysis(ranking_clientes, total_geral)
        self._render_top_clients_table(ranking_clientes)
        self._render_pareto_analysis(ranking_clientes)
        self._render_client_segments(ranking_clientes)
    
    def _render_concentration_analysis(self, ranking_clientes, total_geral):
        """Renderiza análise de concentração"""
        st.subheader("📊 Análise de Concentração")
        
        col1, col2 = st.columns([2, 1])
        
        with col1:
            # Métricas de concentração
            top_5_valor = ranking_clientes.head(5)['Valor_Total'].sum()
            top_10_valor = ranking_clientes.head(10)['Valor_Total'].sum()
            top_20_percent = int(len(ranking_clientes) * 0.2)
            valor_top_20 = ranking_clientes.head(top_20_percent)['Valor_Total'].sum()
            
            col_a, col_b, col_c = st.columns(3)
            
            with col_a:
                percentual_top_5 = (top_5_valor / total_geral * 100)
                st.metric("🔝 Top 5 Clientes", f"{percentual_top_5:.1f}%", "do faturamento")
            
            with col_b:
                percentual_top_10 = (top_10_valor / total_geral * 100)
                st.metric("🏆 Top 10 Clientes", f"{percentual_top_10:.1f}%", "do faturamento")
            
            with col_c:
                percentual_80_20 = (valor_top_20 / total_geral * 100)
                st.metric("📈 Regra 80/20", f"{percentual_80_20:.1f}%", "Top 20% dos clientes")
        
        with col2:
            self.ui.display_ranking_analysis(ranking_clientes, total_geral)
        
        st.markdown("---")
    
    def _render_top_clients_table(self, ranking_clientes):
        """Renderiza tabela dos top clientes"""
        st.subheader("🥇 Top 20 Clientes")
        
        # Filtros
        col1, col2 = st.columns(2)
        
        with col1:
            quantidade = st.selectbox(
                "📊 Quantidade de clientes:", 
                [10, 20, 30, 50], 
                index=1
            )
        
        with col2:
            faixa_filtro = st.selectbox(
                "🎯 Filtrar por faixa:",
                ['Todas'] + list(ranking_clientes['Faixa'].unique())
            )
        
        # Aplicar filtros
        ranking_filtrado = ranking_clientes.copy()
        if faixa_filtro != 'Todas':
            ranking_filtrado = ranking_filtrado[ranking_filtrado['Faixa'] == faixa_filtro]
        
        ranking_display = ranking_filtrado.head(quantidade).copy()
        
        # Formatação para exibição
        ranking_display['Valor_Total_Fmt'] = ranking_display['Valor_Total'].apply(formatar_moeda)
        ranking_display['Percentual_Fmt'] = ranking_display['Percentual'].apply(lambda x: f"{x:.2f}%")
        ranking_display['Percentual_Acumulado_Fmt'] = ranking_display['Percentual_Acumulado'].apply(lambda x: f"{x:.2f}%")
        
        # Selecionar colunas para exibição
        display_columns = ['Nome', 'Valor_Total_Fmt', 'Percentual_Fmt', 'Percentual_Acumulado_Fmt', 'Num_Transacoes', 'Faixa']
        ranking_final = ranking_display[display_columns]
        ranking_final.columns = ['Cliente', 'Valor Total', '% Individual', '% Acumulado', 'Transações', 'Faixa']
        
        st.dataframe(ranking_final, use_container_width=True, hide_index=True)
        
        # Estatísticas do filtro aplicado
        if faixa_filtro != 'Todas':
            st.info(f"📊 Mostrando {len(ranking_display)} clientes da faixa {faixa_filtro}")
        
        st.markdown("---")
    
    def _render_pareto_analysis(self, ranking_clientes):
        """Renderiza análise de Pareto"""
        st.subheader("📈 Análise de Pareto - Concentração de Clientes")
        
        # Controles
        col1, col2 = st.columns(2)
        
        with col1:
            top_n = st.slider("🔢 Número de clientes no Pareto:", 10, 100, 30, 5)
        
        with col2:
            st.metric("🎯 Princípio 80/20", "Identificar os clientes mais valiosos")
        
        # Gráfico de Pareto
        pareto_data = ranking_clientes.head(top_n)
        fig_pareto = self.viz.create_pareto_chart(pareto_data)
        st.plotly_chart(fig_pareto, use_container_width=True)
        
        # Insights do Pareto
        self._display_pareto_insights(pareto_data, ranking_clientes)
        
        st.markdown("---")
    
    def _display_pareto_insights(self, pareto_data, ranking_completo):
        """Exibe insights da análise de Pareto"""
        st.subheader("💡 Insights da Análise de Pareto")
        
        total_clientes = len(ranking_completo)
        total_valor = ranking_completo['Valor_Total'].sum()
        
        # Encontrar onde se atinge 80% do valor
        ponto_80 = ranking_completo[ranking_completo['Percentual_Acumulado'] <= 80]
        
        if not ponto_80.empty:
            clientes_80 = len(ponto_80)
            percentual_clientes_80 = (clientes_80 / total_clientes) * 100
            
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.metric(
                    "🎯 Clientes que geram 80%", 
                    clientes_80,
                    f"{percentual_clientes_80:.1f}% do total"
                )
            
            with col2:
                if percentual_clientes_80 <= 20:
                    st.success("✅ Pareto Clássico Confirmado!")
                elif percentual_clientes_80 <= 30:
                    st.info("📊 Concentração Forte")
                else:
                    st.warning("⚠️ Concentração Moderada")
            
            with col3:
                valor_restante = total_valor * 0.2
                st.metric("💰 20% Restante do Valor", formatar_moeda(valor_restante))
        
        # Recomendações estratégicas
        st.write("🎯 **Recomendações Estratégicas:**")
        
        recomendacoes = []
        
        if len(ponto_80) <= total_clientes * 0.2:
            recomendacoes.append("💎 **Foque nos clientes premium**: Desenvolva programas VIP para os top clientes")
            recomendacoes.append("🛡️ **Retenção crítica**: Implemente estratégias de retenção para evitar perda dos principais clientes")
        
        if len(ranking_completo) - len(ponto_80) > 50:
            recomendacoes.append("📈 **Oportunidade de crescimento**: Grande base de clientes com potencial de aumento de ticket")
            recomendacoes.append("🎯 **Segmentação**: Crie campanhas específicas para diferentes faixas de clientes")
        
        for rec in recomendacoes:
            st.markdown(f"- {rec}")
    
    def _render_client_segments(self, ranking_clientes):
        """Renderiza análise de segmentos de clientes"""
        st.subheader("🎯 Segmentação de Clientes")
        
        # Estatísticas por faixa
        segmentos = ranking_clientes.groupby('Faixa').agg({
            'Valor_Total': ['sum', 'mean', 'count'],
            'Num_Transacoes': 'mean'
        }).round(2)
        
        segmentos.columns = ['Valor_Total', 'Ticket_Medio', 'Qtd_Clientes', 'Transacoes_Media']
        
        # Adicionar percentuais
        total_valor = segmentos['Valor_Total'].sum()
        total_clientes = segmentos['Qtd_Clientes'].sum()
        
        segmentos['Perc_Valor'] = (segmentos['Valor_Total'] / total_valor * 100).round(1)
        segmentos['Perc_Clientes'] = (segmentos['Qtd_Clientes'] / total_clientes * 100).round(1)
        
        # Exibir tabela
        st.dataframe(segmentos, use_container_width=True)
        
        # Insights por segmento
        col1, col2, col3 = st.columns(3)
        
        faixas_ordem = ['Grupo A (R$ 1.500+)', 'Grupo B (R$ 500-1.499)', 'Grupo C (R$ 0-499)']
        cores = ['🥇', '🥈', '🥉']
        
        for i, (faixa, emoji) in enumerate(zip(faixas_ordem, cores)):
            if faixa in segmentos.index:
                dados = segmentos.loc[faixa]
                
                with [col1, col2, col3][i]:
                    st.markdown(f"### {emoji} {faixa.split('(')[0].strip()}")
                    st.metric("👥 Clientes", int(dados['Qtd_Clientes']))
                    st.metric("💰 Participação", f"{dados['Perc_Valor']:.1f}%")
                    st.metric("🎫 Ticket Médio", formatar_moeda(dados['Ticket_Medio']))
                    st.metric("🔄 Transações Média", f"{dados['Transacoes_Media']:.1f}")