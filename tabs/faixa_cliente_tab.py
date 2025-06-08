import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from utils import get_ordem_faixas, formatar_moeda, classificar_cliente_faixa

class FaixaClienteTab:
    def __init__(self, df, processor, calculator, viz, ui):
        self.df = df
        self.processor = processor
        self.calculator = calculator
        self.viz = viz
        self.ui = ui
    
    def render(self):
        """Renderiza a aba de análise por faixa de cliente"""
        if self.df.empty:
            st.warning("⚠️ Nenhum dado disponível para análise por faixa de cliente.")
            return
        
        # Calcular LTV por cliente
        ltv_por_cliente = self.processor.get_ltv_por_cliente()
        
        if ltv_por_cliente.empty:
            st.warning("⚠️ Não foi possível calcular LTV. Verifique se existem dados com situação 'Paga'.")
            self._render_no_data_guidance()
            return
        
        # Calcular estatísticas por faixa
        faixa_stats = self.calculator.calculate_faixa_stats(ltv_por_cliente)
        
        if faixa_stats.empty:
            st.error("❌ Erro ao calcular estatísticas por faixa.")
            return
        
        # Ordenar por importância
        ordem_faixas = get_ordem_faixas()
        faixa_stats = faixa_stats.reindex([f for f in ordem_faixas if f in faixa_stats.index])
        
        # Renderizar seções
        self._render_overview_section(faixa_stats, ltv_por_cliente)
        self._render_distribution_analysis(faixa_stats, ltv_por_cliente)
        self._render_performance_comparison(faixa_stats, ltv_por_cliente)
        self._render_monthly_evolution(ltv_por_cliente)
        self._render_migration_analysis(ltv_por_cliente)
        self._render_growth_opportunities(faixa_stats, ltv_por_cliente)
        self._render_strategic_recommendations(faixa_stats)
    
    def _render_no_data_guidance(self):
        """Renderiza orientações quando não há dados"""
        st.info("📋 **Para análise por faixa de cliente, são necessários:**")
        st.write("- Dados com situação 'Paga'")
        st.write("- Campo CPF/CNPJ para identificar clientes únicos")
        st.write("- Campo 'Total' com valores das transações")
        
        if 'Situação' in self.df.columns:
            situacoes = self.df['Situação'].value_counts()
            st.write("🔍 **Situações disponíveis:**")
            for sit, count in situacoes.items():
                st.write(f"- {sit}: {count:,} registros")
    
    def _render_overview_section(self, faixa_stats, ltv_por_cliente):
        """Renderiza seção de visão geral"""
        st.subheader("📊 Visão Geral por Faixa de Cliente")
        
        # KPIs gerais
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
        
        # Resumo executivo por faixa
        st.markdown("---")
        self.ui.display_faixa_summary(faixa_stats)
        
        st.markdown("---")
    
    def _render_distribution_analysis(self, faixa_stats, ltv_por_cliente):
        """Renderiza análise de distribuição"""
        st.subheader("📊 Análise de Distribuição por Faixa")
        
        tab1, tab2, tab3 = st.tabs(["💰 Faturamento", "👥 Clientes", "🎫 Performance"])
        
        with tab1:
            self._render_revenue_distribution(faixa_stats)
        
        with tab2:
            self._render_customer_distribution(faixa_stats, ltv_por_cliente)
        
        with tab3:
            self._render_performance_distribution(faixa_stats)
    
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
        st.write("📈 **Análise de Concentração de Faturamento**")
        
        col1, col2, col3 = st.columns(3)
        
        # Regra 80/20 adaptada
        faturamento_acumulado = faixa_stats['Percentual_Faturamento'].cumsum()
        
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
            if herfindahl > 5000:  # Alta concentração
                st.error(f"📊 **Alta Concentração**\n\nÍndice: {herfindahl:.0f}")
            elif herfindahl > 3333:  # Concentração moderada
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
        
        # Análise de densidade por faixa
        st.write("📊 **Análise de Densidade por Faixa**")
        
        # Calcular densidade (clientes por faixa de valor)
        densidade_data = []
        for faixa in faixa_stats.index:
            clientes_faixa = faixa_stats.loc[faixa, 'Qtd_Clientes']
            faturamento_faixa = faixa_stats.loc[faixa, 'Faturamento_Total']
            densidade = clientes_faixa / faturamento_faixa * 1000 if faturamento_faixa > 0 else 0
            
            densidade_data.append({
                'Faixa': faixa,
                'Densidade': densidade,
                'Clientes': clientes_faixa,
                'Faturamento': faturamento_faixa
            })
        
        densidade_df = pd.DataFrame(densidade_data)
        
        col1, col2, col3 = st.columns(3)
        
        for i, row in densidade_df.iterrows():
            with [col1, col2, col3][i % 3]:
                emoji = ['🥇', '🥈', '🥉'][i] if i < 3 else '📊'
                st.metric(
                    f"{emoji} {row['Faixa'].split('(')[0].strip()}",
                    f"{row['Densidade']:.1f}",
                    "clientes por R$ 1k"
                )
    
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
            # Radar chart de performance
            st.write("📊 **Comparativo de Performance**")
            
            # Normalizar métricas para 0-100
            max_faturamento = faixa_stats['Faturamento_Total'].max()
            max_clientes = faixa_stats['Qtd_Clientes'].max()
            max_ticket = faixa_stats['Ticket_Medio'].max()
            
            fig_radar = go.Figure()
            
            for faixa in faixa_stats.index:
                stats = faixa_stats.loc[faixa]
                
                valores_norm = [
                    (stats['Faturamento_Total'] / max_faturamento) * 100,
                    (stats['Qtd_Clientes'] / max_clientes) * 100,
                    (stats['Ticket_Medio'] / max_ticket) * 100,
                    stats['Percentual_Faturamento']
                ]
                
                fig_radar.add_trace(go.Scatterpolar(
                    r=valores_norm,
                    theta=['Faturamento', 'Clientes', 'Ticket Médio', '% Participação'],
                    fill='toself',
                    name=faixa.split('(')[0].strip(),
                    line=dict(color=self.viz.cores_faixas.get(faixa, '#1f77b4'))
                ))
            
            fig_radar.update_layout(
                polar=dict(
                    radialaxis=dict(
                        visible=True,
                        range=[0, 100]
                    )
                ),
                showlegend=True,
                title="Comparativo de Performance",
                height=400
            )
            
            st.plotly_chart(fig_radar, use_container_width=True)
        
        # Tabela de performance detalhada
        st.write("📋 **Tabela de Performance Detalhada**")
        
        performance_display = faixa_stats.copy()
        performance_display['Faturamento_Total'] = performance_display['Faturamento_Total'].apply(formatar_moeda)
        performance_display['Ticket_Medio'] = performance_display['Ticket_Medio'].apply(formatar_moeda)
        
        # Adicionar eficiência (faturamento por cliente)
        performance_display['Eficiencia_Cliente'] = (faixa_stats['Faturamento_Total'] / faixa_stats['Qtd_Clientes']).apply(formatar_moeda)
        
        st.dataframe(performance_display, use_container_width=True)
    
    def _render_performance_comparison(self, faixa_stats, ltv_por_cliente):
        """Renderiza comparação de performance entre faixas"""
        st.subheader("🔍 Comparação de Performance entre Faixas")
        
        # Análise de gaps entre faixas
        col1, col2 = st.columns(2)
        
        with col1:
            st.write("📊 **Gaps de Performance**")
            
            # Calcular gaps entre faixas consecutivas
            faixas_ordenadas = ['Grupo A (R$ 1.500+)', 'Grupo B (R$ 500-1.499)', 'Grupo C (R$ 0-499)']
            gaps_data = []
            
            for i in range(len(faixas_ordenadas) - 1):
                faixa_superior = faixas_ordenadas[i]
                faixa_inferior = faixas_ordenadas[i + 1]
                
                if faixa_superior in faixa_stats.index and faixa_inferior in faixa_stats.index:
                    ticket_superior = faixa_stats.loc[faixa_superior, 'Ticket_Medio']
                    ticket_inferior = faixa_stats.loc[faixa_inferior, 'Ticket_Medio']
                    
                    gap_ticket = ((ticket_superior - ticket_inferior) / ticket_inferior) * 100 if ticket_inferior > 0 else 0
                    
                    gaps_data.append({
                        'Gap': f"{faixa_superior.split('(')[0].strip()} vs {faixa_inferior.split('(')[0].strip()}",
                        'Diferenca_Ticket': gap_ticket,
                        'Valor_Superior': ticket_superior,
                        'Valor_Inferior': ticket_inferior
                    })
            
            for gap in gaps_data:
                st.metric(
                    gap['Gap'],
                    f"{gap['Diferenca_Ticket']:.0f}%",
                    f"{formatar_moeda(gap['Valor_Superior'])} vs {formatar_moeda(gap['Valor_Inferior'])}"
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
        
        # Análise de potencial de crescimento
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
            col1, col2 = st.columns(2)
            
            for i, pot in enumerate(potencial_data):
                with [col1, col2][i % 2]:
                    st.markdown(f"""
                    **🎯 {pot['Faixa']}**
                    - Clientes potenciais: {pot['Clientes_Potencial']:.0f}
                    - Valor adicional: {formatar_moeda(pot['Valor_Adicional'])}
                    - Estratégia: {pot['Estrategia']}
                    """)
        
        st.markdown("---")
    
    def _render_monthly_evolution(self, ltv_por_cliente):
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
        if tipo_grafico == 'Linha':
            fig_evolucao = px.line(
                evolucao_mensal,
                x='Mes_Ano_Str',
                y=metrica_evolucao,
                color='Faixa_Cliente',
                title=f'Evolução Mensal - {metrica_evolucao.replace("_", " ")}',
                labels={metrica_evolucao: metrica_evolucao.replace("_", " "), 'Mes_Ano_Str': 'Período'},
                color_discrete_map=self.viz.cores_faixas,
                markers=True
            )
        elif tipo_grafico == 'Área':
            fig_evolucao = px.area(
                evolucao_mensal,
                x='Mes_Ano_Str',
                y=metrica_evolucao,
                color='Faixa_Cliente',
                title=f'Evolução Mensal - {metrica_evolucao.replace("_", " ")}',
                labels={metrica_evolucao: metrica_evolucao.replace("_", " "), 'Mes_Ano_Str': 'Período'},
                color_discrete_map=self.viz.cores_faixas
            )
        else:  # Barras
            fig_evolucao = px.bar(
                evolucao_mensal,
                x='Mes_Ano_Str',
                y=metrica_evolucao,
                color='Faixa_Cliente',
                title=f'Evolução Mensal - {metrica_evolucao.replace("_", " ")}',
                labels={metrica_evolucao: metrica_evolucao.replace("_", " "), 'Mes_Ano_Str': 'Período'},
                color_discrete_map=self.viz.cores_faixas
            )
        
        fig_evolucao.update_layout(height=400)
        st.plotly_chart(fig_evolucao, use_container_width=True)
        
        # Análise de crescimento por faixa
        self._analyze_monthly_growth(evolucao_mensal)
        
        # Tabela de evolução
        st.write("📋 **Tabela de Evolução Mensal**")
        
        # Pivot para melhor visualização
        pivot_evolucao = evolucao_mensal.pivot(
            index='Mes_Ano_Str', 
            columns='Faixa_Cliente', 
            values=metrica_evolucao
        ).fillna(0)
        
        # Formatar valores se necessário
        if metrica_evolucao == 'Valor_Total':
            pivot_display = pivot_evolucao.applymap(lambda x: formatar_moeda(x) if x > 0 else '-')
        else:
            pivot_display = pivot_evolucao.applymap(lambda x: f"{x:,.0f}" if x > 0 else '-')
        
        st.dataframe(pivot_display, use_container_width=True)
        
        st.markdown("---")
    
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
                # Crescimento do último período
                ultimo_valor = df_faixa['Valor_Total'].iloc[-1]
                penultimo_valor = df_faixa['Valor_Total'].iloc[-2]
                
                if penultimo_valor > 0:
                    crescimento_ultimo = ((ultimo_valor - penultimo_valor) / penultimo_valor) * 100
                else:
                    crescimento_ultimo = 0
                
                # Crescimento médio
                if len(df_faixa) > 2:
                    crescimentos = []
                    for i in range(1, len(df_faixa)):
                        valor_anterior = df_faixa['Valor_Total'].iloc[i-1]
                        valor_atual = df_faixa['Valor_Total'].iloc[i]
                        
                        if valor_anterior > 0:
                            cresc = ((valor_atual - valor_anterior) / valor_anterior) * 100
                            crescimentos.append(cresc)
                    
                    crescimento_medio = sum(crescimentos) / len(crescimentos) if crescimentos else 0
                else:
                    crescimento_medio = crescimento_ultimo
                
                crescimento_data.append({
                    'Faixa': faixa,
                    'Crescimento_Ultimo': crescimento_ultimo,
                    'Crescimento_Medio': crescimento_medio,
                    'Valor_Atual': ultimo_valor
                })
        
        # Exibir crescimentos
        if crescimento_data:
            cols = st.columns(len(crescimento_data))
            
            for i, dados in enumerate(crescimento_data):
                with cols[i]:
                    emoji = {'Grupo A': '🥇', 'Grupo B': '🥈', 'Grupo C': '🥉'}.get(dados['Faixa'].split('(')[0].strip(), '📊')
                    
                    # Definir cor baseada no crescimento
                    if dados['Crescimento_Ultimo'] > 10:
                        delta_color = "normal"
                    elif dados['Crescimento_Ultimo'] < -10:
                        delta_color = "inverse"
                    else:
                        delta_color = "off"
                    
                    st.metric(
                        f"{emoji} {dados['Faixa'].split('(')[0].strip()}",
                        formatar_moeda(dados['Valor_Atual']),
                        f"{dados['Crescimento_Ultimo']:+.1f}% (último período)",
                        delta_color=delta_color
                    )
                    
                    st.caption(f"Crescimento médio: {dados['Crescimento_Medio']:+.1f}%")
        
        # Insights de crescimento
        st.write("💡 **Insights de Crescimento:**")
        
        insights = []
        
        # Faixa com maior crescimento
        if crescimento_data:
            melhor_crescimento = max(crescimento_data, key=lambda x: x['Crescimento_Ultimo'])
            if melhor_crescimento['Crescimento_Ultimo'] > 5:
                insights.append(f"🚀 {melhor_crescimento['Faixa'].split('(')[0].strip()} lidera crescimento ({melhor_crescimento['Crescimento_Ultimo']:+.1f}%)")
            
    # Faixa com declínio
            pior_crescimento = min(crescimento_data, key=lambda x: x['Crescimento_Ultimo'])
            if pior_crescimento['Crescimento_Ultimo'] < -5:
                insights.append(f"📉 {pior_crescimento['Faixa'].split('(')[0].strip()} em declínio ({pior_crescimento['Crescimento_Ultimo']:+.1f}%)")
            
            # Estabilidade
            crescimentos_absolutos = [abs(d['Crescimento_Ultimo']) for d in crescimento_data]
            if max(crescimentos_absolutos) < 5:
                insights.append("📊 Crescimento estável em todas as faixas")
            
            # Divergência entre faixas
            diferenca_max = max(d['Crescimento_Ultimo'] for d in crescimento_data) - min(d['Crescimento_Ultimo'] for d in crescimento_data)
            if diferenca_max > 20:
                insights.append(f"⚠️ Grande divergência entre faixas ({diferenca_max:.1f}pp)")
        
        for insight in insights:
            st.markdown(f"- {insight}")
    def _render_migration_analysis(self, ltv_por_cliente):
        """Renderiza análise de migração entre faixas"""
        st.subheader("🔄 Análise de Migração entre Faixas")
        
        # Verificar se há dados suficientes para análise temporal
        if 'Data de criação' not in self.df.columns:
            st.info("📅 Análise de migração requer dados temporais (Data de criação).")
            return
        
        # Simular análise de migração baseada em períodos
        df_temporal = self.df.copy()
        df_temporal['Data de criação'] = pd.to_datetime(df_temporal['Data de criação'], errors='coerce')
        df_temporal = df_temporal.dropna(subset=['Data de criação'])
        
        if df_temporal.empty:
            st.warning("⚠️ Não há dados temporais válidos para análise de migração.")
            return
        
        # Dividir em dois períodos para análise
        data_mediana = df_temporal['Data de criação'].median()
        
        # Primeiro período
        df_periodo1 = df_temporal[df_temporal['Data de criação'] <= data_mediana]
        df_periodo1 = df_periodo1[df_periodo1['Situação'].str.lower() == 'paga']
        
        if not df_periodo1.empty:
            ltv_periodo1 = df_periodo1.groupby('CPF/CNPJ')['Total'].sum().reset_index()
            ltv_periodo1.columns = ['CPF/CNPJ', 'LTV_P1']
            ltv_periodo1['Faixa_P1'] = ltv_periodo1['LTV_P1'].apply(classificar_cliente_faixa)
        else:
            ltv_periodo1 = pd.DataFrame()
        
        # Segundo período
        df_periodo2 = df_temporal[df_temporal['Data de criação'] > data_mediana]
        df_periodo2 = df_periodo2[df_periodo2['Situação'].str.lower() == 'paga']
        
        if not df_periodo2.empty:
            ltv_periodo2 = df_periodo2.groupby('CPF/CNPJ')['Total'].sum().reset_index()
            ltv_periodo2.columns = ['CPF/CNPJ', 'LTV_P2']
            ltv_periodo2['Faixa_P2'] = ltv_periodo2['LTV_P2'].apply(classificar_cliente_faixa)
        else:
            ltv_periodo2 = pd.DataFrame()
        
        # Analisar migração apenas se há dados em ambos períodos
        if not ltv_periodo1.empty and not ltv_periodo2.empty:
            # Clientes que aparecem em ambos períodos
            migracao = ltv_periodo1.merge(ltv_periodo2, on='CPF/CNPJ', how='inner')
            
            if not migracao.empty:
                # Matriz de migração
                matriz_migracao = pd.crosstab(
                    migracao['Faixa_P1'], 
                    migracao['Faixa_P2'], 
                    normalize='index'
                ) * 100
                
                col1, col2 = st.columns(2)
                
                with col1:
                    st.write("📊 **Matriz de Migração (%)**")
                    st.write("*Linhas: Faixa Período 1 → Colunas: Faixa Período 2*")
                    
                    # Formatar matriz para exibição
                    matriz_display = matriz_migracao.round(1).astype(str) + '%'
                    st.dataframe(matriz_display, use_container_width=True)
                
                with col2:
                    st.write("🎯 **Análise de Movimentação**")
                    
                    # Calcular movimentações
                    total_clientes_migracao = len(migracao)
                    
                    # Upgrades (moveram para faixa superior)
                    upgrades = 0
                    downgrades = 0
                    manteve = 0
                    
                    for _, cliente in migracao.iterrows():
                        faixa_p1 = cliente['Faixa_P1']
                        faixa_p2 = cliente['Faixa_P2']
                        
                        if faixa_p1 == faixa_p2:
                            manteve += 1
                        elif self._comparar_faixas(faixa_p2, faixa_p1) > 0:
                            upgrades += 1
                        else:
                            downgrades += 1
                    
                    st.metric("📈 Upgrades", f"{upgrades}", f"{upgrades/total_clientes_migracao*100:.1f}%")
                    st.metric("📉 Downgrades", f"{downgrades}", f"{downgrades/total_clientes_migracao*100:.1f}%")
                    st.metric("➡️ Mantiveram", f"{manteve}", f"{manteve/total_clientes_migracao*100:.1f}%")
                
                # Insights de migração
                self._display_migration_insights(migracao, upgrades, downgrades, manteve, total_clientes_migracao)
            else:
                st.info("📊 Não há clientes suficientes com atividade em ambos os períodos para análise de migração.")
        else:
            st.info("📊 Dados insuficientes para análise de migração entre períodos.")
        
        st.markdown("---")
    
    def _comparar_faixas(self, faixa1, faixa2):
        """Compara duas faixas retornando: 1 se faixa1 > faixa2, -1 se faixa1 < faixa2, 0 se iguais"""
        ordem = {
            'Grupo C (R$ 0-499)': 1,
            'Grupo B (R$ 500-1.499)': 2,
            'Grupo A (R$ 1.500+)': 3
        }
        
        valor1 = ordem.get(faixa1, 0)
        valor2 = ordem.get(faixa2, 0)
        
        if valor1 > valor2:
            return 1
        elif valor1 < valor2:
            return -1
        else:
            return 0
    
    def _display_migration_insights(self, migracao, upgrades, downgrades, manteve, total):
        """Exibe insights da análise de migração"""
        st.write("💡 **Insights de Migração:**")
        
        insights = []
        
        # Taxa de mobilidade
        taxa_mobilidade = ((upgrades + downgrades) / total) * 100
        if taxa_mobilidade > 30:
            insights.append(f"🔄 Alta mobilidade entre faixas ({taxa_mobilidade:.1f}%)")
        elif taxa_mobilidade < 10:
            insights.append(f"🔒 Baixa mobilidade - clientes estáveis ({taxa_mobilidade:.1f}%)")
        
        # Direção predominante
        if upgrades > downgrades * 2:
            insights.append("📈 Movimento predominante: UPGRADES - crescimento da base")
        elif downgrades > upgrades * 2:
            insights.append("📉 Movimento predominante: DOWNGRADES - atenção necessária")
        else:
            insights.append("⚖️ Movimento equilibrado entre upgrades e downgrades")
        
        # Retenção por faixa
        for faixa in migracao['Faixa_P1'].unique():
            clientes_faixa = migracao[migracao['Faixa_P1'] == faixa]
            mantiveram_faixa = len(clientes_faixa[clientes_faixa['Faixa_P1'] == clientes_faixa['Faixa_P2']])
            taxa_retencao = (mantiveram_faixa / len(clientes_faixa)) * 100
            
            if taxa_retencao < 60:
                insights.append(f"⚠️ {faixa.split('(')[0].strip()}: baixa retenção na faixa ({taxa_retencao:.1f}%)")
        
        for insight in insights:
            st.markdown(f"- {insight}")
    
    def _render_growth_opportunities(self, faixa_stats, ltv_por_cliente):
        """Renderiza análise de oportunidades de crescimento"""
        st.subheader("🚀 Oportunidades de Crescimento")
        
        tab1, tab2, tab3 = st.tabs(["📈 Potencial de Upgrade", "🎯 Expansão de Base", "💎 Otimização de Valor"])
        
        with tab1:
            self._render_upgrade_potential(faixa_stats, ltv_por_cliente)
        
        with tab2:
            self._render_base_expansion(faixa_stats)
        
        with tab3:
            self._render_value_optimization(faixa_stats, ltv_por_cliente)
    
    def _render_upgrade_potential(self, faixa_stats, ltv_por_cliente):
        """Análise de potencial de upgrade"""
        st.write("📈 **Potencial de Upgrade entre Faixas**")
        
        upgrade_scenarios = []
        
        # Cenário 1: Grupo C → Grupo B
        if 'Grupo C (R$ 0-499)' in faixa_stats.index:
            clientes_c = faixa_stats.loc['Grupo C (R$ 0-499)', 'Qtd_Clientes']
            
            # Assumir que 10% podem migrar para Grupo B
            upgrade_c_b = int(clientes_c * 0.10)
            valor_adicional_c_b = upgrade_c_b * 250  # Valor médio adicional por upgrade
            
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
            
            # Assumir que 5% podem migrar para Grupo A
            upgrade_b_a = int(clientes_b * 0.05)
            valor_adicional_b_a = upgrade_b_a * 500  # Valor médio adicional por upgrade
            
            upgrade_scenarios.append({
                'Cenario': 'Grupo B → A',
                'Clientes': upgrade_b_a,
                'Valor_Adicional': valor_adicional_b_a,
                'Taxa_Conversao': '5%',
                'Estrategias': ['Programa VIP', 'Atendimento premium', 'Ofertas exclusivas']
            })
        
        # Exibir cenários
        for scenario in upgrade_scenarios:
            with st.container():
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
        
        # Resumo do potencial total
        if upgrade_scenarios:
            total_clientes_upgrade = sum(s['Clientes'] for s in upgrade_scenarios)
            total_valor_adicional = sum(s['Valor_Adicional'] for s in upgrade_scenarios)
            
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.metric("🎯 Total Clientes Upgrade", f"{total_clientes_upgrade:,}")
            
            with col2:
                st.metric("💰 Valor Adicional Total", formatar_moeda(total_valor_adicional))
            
            with col3:
                percentual_atual = (total_valor_adicional / faixa_stats['Faturamento_Total'].sum()) * 100
                st.metric("📈 % do Faturamento Atual", f"{percentual_atual:.1f}%")
    
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
        
        # Análise de distribuição dentro de cada faixa
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
            
            oportunidades = []
            
            for faixa in faixa_stats.index:
                clientes_faixa = ltv_por_cliente[ltv_por_cliente['Faixa_Cliente'] == faixa]
                
                if not clientes_faixa.empty:
                    # Identificar outliers inferiores (potencial de crescimento)
                    q1 = clientes_faixa['LTV_Total'].quantile(0.25)
                    outliers_baixos = clientes_faixa[clientes_faixa['LTV_Total'] < q1 * 0.5]
                    
                    if len(outliers_baixos) > 0:
                        valor_potencial = len(outliers_baixos) * (q1 - outliers_baixos['LTV_Total'].mean())
                        
                        oportunidades.append({
                            'Faixa': faixa.split('(')[0].strip(),
                            'Clientes_Baixo_Performance': len(outliers_baixos),
                            'Valor_Potencial': valor_potencial,
                            'Acao': 'Campanhas de reativação'
                        })
            
            for op in oportunidades:
                st.write(f"**{op['Faixa']}:**")
                st.write(f"• Clientes sub-performando: {op['Clientes_Baixo_Performance']}")
                st.write(f"• Potencial de valor: {formatar_moeda(op['Valor_Potencial'])}")
                st.write(f"• Ação recomendada: {op['Acao']}")
                st.write("")
        
        # Matriz de priorização
        st.write("🎯 **Matriz de Priorização de Ações**")
        
        prioridades = []
        
        for faixa in faixa_stats.index:
            stats = faixa_stats.loc[faixa]
            
            # Calcular score de prioridade (impacto vs esforço)
            impacto = stats['Percentual_Faturamento']  # Quanto maior o %, maior o impacto
            facilidade = 100 - stats['Ticket_Medio'] / 100  # Quanto menor o ticket, mais fácil de influenciar
            
            score_prioridade = (impacto * 0.7) + (facilidade * 0.3)
            
            prioridades.append({
                'Faixa': faixa.split('(')[0].strip(),
                'Impacto': impacto,
                'Facilidade': facilidade,
                'Score': score_prioridade,
                'Recomendacao': self._get_priority_recommendation(score_prioridade)
            })
        
        prioridades_df = pd.DataFrame(prioridades).sort_values('Score', ascending=False)
        
        # Visualizar matriz
        fig_matriz = px.scatter(
            prioridades_df,
            x='Facilidade',
            y='Impacto',
            text='Faixa',
            size='Score',
            title="Matriz de Priorização: Impacto vs Facilidade",
            labels={'Facilidade': 'Facilidade de Implementação', 'Impacto': 'Impacto no Faturamento (%)'}
        )
        
        fig_matriz.update_traces(textposition='top center')
        fig_matriz.update_layout(height=400)
        st.plotly_chart(fig_matriz, use_container_width=True)
        
        # Tabela de prioridades
        st.write("📋 **Ranking de Prioridades**")
        
        prioridades_display = prioridades_df[['Faixa', 'Score', 'Recomendacao']].copy()
        prioridades_display['Score'] = prioridades_display['Score'].round(1)
        prioridades_display.columns = ['Faixa', 'Score de Prioridade', 'Recomendação']
        
        st.dataframe(prioridades_display, use_container_width=True, hide_index=True)
        
        st.markdown("---")
    
    def _get_priority_recommendation(self, score):
        """Retorna recomendação baseada no score de prioridade"""
        if score > 70:
            return "🔥 Prioridade ALTA - Ação imediata"
        elif score > 50:
            return "⚡ Prioridade MÉDIA - Ação em 30 dias"
        else:
            return "🔄 Prioridade BAIXA - Monitoramento"
    
    def _render_strategic_recommendations(self, faixa_stats):
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
        
        # ROI esperado
        st.write("💰 **Projeção de ROI das Estratégias**")
        
        total_faturamento = faixa_stats['Faturamento_Total'].sum()
        
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