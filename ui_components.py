import streamlit as st
from utils import formatar_moeda, get_ordem_faixas

class UIComponents:
    @staticmethod
    def display_basic_kpis(kpis):
        """Exibe KPIs básicos."""
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
    def display_faixa_summary(faixa_stats):
        """Exibe resumo por faixa de cliente."""
        col1, col2, col3 = st.columns(3)
        
        ordem_faixas = get_ordem_faixas()
        
        with col1:
            if 'Grupo A (R$ 1.500+)' in faixa_stats.index:
                grupo_a = faixa_stats.loc['Grupo A (R$ 1.500+)']
                st.metric(
                    "🥇 Grupo A (Premium)",
                    formatar_moeda(grupo_a['Faturamento_Total']),
                    f"{grupo_a['Percentual_Faturamento']:.1f}% do total"
                )
                st.write(f"👥 {int(grupo_a['Qtd_Clientes'])} clientes")
                st.write(f"🎫 Ticket médio: {formatar_moeda(grupo_a['Ticket_Medio'])}")
        
        with col2:
            if 'Grupo B (R$ 500-1.499)' in faixa_stats.index:
                grupo_b = faixa_stats.loc['Grupo B (R$ 500-1.499)']
                st.metric(
                    "🥈 Grupo B (Médio)",
                    formatar_moeda(grupo_b['Faturamento_Total']),
                    f"{grupo_b['Percentual_Faturamento']:.1f}% do total"
                )
                st.write(f"👥 {int(grupo_b['Qtd_Clientes'])} clientes")
                st.write(f"🎫 Ticket médio: {formatar_moeda(grupo_b['Ticket_Medio'])}")
        
        with col3:
            if 'Grupo C (R$ 0-499)' in faixa_stats.index:
                grupo_c = faixa_stats.loc['Grupo C (R$ 0-499)']
                st.metric(
                    "🥉 Grupo C (Básico)",
                    formatar_moeda(grupo_c['Faturamento_Total']),
                    f"{grupo_c['Percentual_Faturamento']:.1f}% do total"
                )
                st.write(f"👥 {int(grupo_c['Qtd_Clientes'])} clientes")
                st.write(f"🎫 Ticket médio: {formatar_moeda(grupo_c['Ticket_Medio'])}")
    
    @staticmethod
    def display_ranking_analysis(ranking_clientes, total_geral):
        """Exibe análise de concentração de clientes."""
        st.subheader("📊 Análise de Concentração")
        
        # Análise 80/20
        top_20_percent = int(len(ranking_clientes) * 0.2)
        valor_top_20 = ranking_clientes.head(top_20_percent)['Valor_Total'].sum()
        percentual_80_20 = (valor_top_20 / total_geral * 100)
        
        st.metric("📈 Regra 80/20", f"{percentual_80_20:.1f}%", "Top 20% dos clientes")
        
        # Top 10 clientes
        top_10_valor = ranking_clientes.head(10)['Valor_Total'].sum()
        percentual_top_10 = (top_10_valor / total_geral * 100)
        
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
        
        st.markdown("### 📖 Como usar:")
        st.markdown("""
        1. **Upload**: Faça upload do seu arquivo CSV na barra lateral
        2. **KPIs**: Visualize indicadores principais, LTV e Churn
        3. **Faixas de Cliente**: Analise grupos A, B e C por valor
        4. **Ranking**: Veja top clientes e concentração de faturamento
        5. **Evolução**: Acompanhe tendências mensais por faixa
        6. **Pareto**: Entenda a distribuição 80/20 dos clientes
        """)
    
    @staticmethod
    def display_kpi_grid(kpis_data, title="📊 Indicadores"):
        """Exibe grid genérico de KPIs."""
        st.subheader(title)
        
        # Calcular número de colunas baseado na quantidade de KPIs
        num_kpis = len(kpis_data)
        if num_kpis <= 3:
            cols = st.columns(num_kpis)
        elif num_kpis <= 6:
            cols = st.columns(3)
        else:
            cols = st.columns(4)
        
        for i, (label, value, delta) in enumerate(kpis_data):
            col_index = i % len(cols)
            with cols[col_index]:
                if delta:
                    st.metric(label, value, delta)
                else:
                    st.metric(label, value)
    
    @staticmethod
    def display_comparison_metrics(current_data, previous_data, labels):
        """Exibe métricas com comparação período anterior."""
        st.subheader("📊 Comparação com Período Anterior")
        
        cols = st.columns(len(current_data))
        
        for i, (current, previous, label) in enumerate(zip(current_data, previous_data, labels)):
            with cols[i]:
                if previous > 0:
                    delta_value = current - previous
                    delta_percent = ((current - previous) / previous) * 100
                    delta_text = f"{delta_percent:+.1f}%"
                else:
                    delta_value = current
                    delta_text = "Novo"
                
                if isinstance(current, (int, float)) and current >= 1000:
                    display_value = formatar_moeda(current)
                else:
                    display_value = str(current)
                
                st.metric(label, display_value, delta_text)
    
    @staticmethod
    def display_performance_cards(data_list):
        """Exibe cards de performance."""
        for card_data in data_list:
            with st.container():
                st.markdown(f"""
                <div style="
                    padding: 1rem;
                    border-radius: 0.5rem;
                    border: 1px solid #e0e0e0;
                    margin-bottom: 1rem;
                    background-color: #f8f9fa;
                ">
                    <h4 style="margin-top: 0;">{card_data['title']}</h4>
                    <p style="font-size: 2rem; margin: 0.5rem 0; font-weight: bold;">
                        {card_data['value']}
                    </p>
                    <p style="margin: 0; color: #666;">
                        {card_data.get('description', '')}
                    </p>
                </div>
                """, unsafe_allow_html=True)
    
    @staticmethod
    def display_status_indicators(status_data):
        """Exibe indicadores de status com cores."""
        cols = st.columns(len(status_data))
        
        for i, (status, value, color) in enumerate(status_data):
            with cols[i]:
                # Definir cor baseada no status
                if color == 'success':
                    st.success(f"✅ **{status}**\n\n{value}")
                elif color == 'warning':
                    st.warning(f"⚠️ **{status}**\n\n{value}")
                elif color == 'error':
                    st.error(f"❌ **{status}**\n\n{value}")
                else:
                    st.info(f"ℹ️ **{status}**\n\n{value}")
    
    @staticmethod
    def display_trend_indicators(trends_data):
        """Exibe indicadores de tendência."""
        st.subheader("📈 Indicadores de Tendência")
        
        cols = st.columns(len(trends_data))
        
        for i, trend in enumerate(trends_data):
            with cols[i]:
                # Determinar ícone e cor da tendência
                if trend['direction'] == 'up':
                    icon = "📈"
                    delta_color = "normal"
                elif trend['direction'] == 'down':
                    icon = "📉"
                    delta_color = "inverse"
                else:
                    icon = "➡️"
                    delta_color = "off"
                
                st.metric(
                    f"{icon} {trend['label']}", 
                    trend['value'],
                    trend.get('delta', ''),
                    delta_color=delta_color
                )
    
    @staticmethod
    def display_alert_panel(alerts):
        """Exibe painel de alertas."""
        if not alerts:
            return
        
        st.subheader("🚨 Alertas e Notificações")
        
        for alert in alerts:
            alert_type = alert.get('type', 'info')
            message = alert.get('message', '')
            
            if alert_type == 'error':
                st.error(f"🚨 {message}")
            elif alert_type == 'warning':
                st.warning(f"⚠️ {message}")
            elif alert_type == 'success':
                st.success(f"✅ {message}")
            else:
                st.info(f"ℹ️ {message}")
    
    @staticmethod
    def display_summary_table(data, title="📋 Resumo", format_columns=None):
        """Exibe tabela de resumo formatada."""
        st.subheader(title)
        
        if format_columns:
            # Aplicar formatação às colunas especificadas
            styled_data = data.style
            
            for col, format_type in format_columns.items():
                if col in data.columns:
                    if format_type == 'currency':
                        styled_data = styled_data.format({col: lambda x: formatar_moeda(x)})
                    elif format_type == 'percentage':
                        styled_data = styled_data.format({col: '{:.1f}%'})
                    elif format_type == 'integer':
                        styled_data = styled_data.format({col: '{:,.0f}'})
            
            st.dataframe(styled_data, use_container_width=True)
        else:
            st.dataframe(data, use_container_width=True)
    
    @staticmethod
    def display_progress_bars(progress_data):
        """Exibe barras de progresso."""
        st.subheader("📊 Progresso dos Objetivos")
        
        for item in progress_data:
            label = item['label']
            current = item['current']
            target = item['target']
            
            progress = min(current / target, 1.0) if target > 0 else 0
            
            st.write(f"**{label}**")
            st.progress(progress)
            st.write(f"{formatar_moeda(current) if current >= 1000 else current} / {formatar_moeda(target) if target >= 1000 else target}")
            st.write(f"Progresso: {progress * 100:.1f}%")
            st.markdown("---")
    
    @staticmethod
    def display_insights_panel(insights, title="💡 Insights"):
        """Exibe painel de insights."""
        st.subheader(title)
        
        for insight in insights:
            # Determinar ícone baseado no tipo
            insight_type = insight.get('type', 'info')
            message = insight.get('message', '')
            
            if insight_type == 'positive':
                st.markdown(f"✅ {message}")
            elif insight_type == 'negative':
                st.markdown(f"⚠️ {message}")
            elif insight_type == 'neutral':
                st.markdown(f"📊 {message}")
            else:
                st.markdown(f"💡 {message}")
    
    @staticmethod
    def display_data_quality_panel(quality_data):
        """Exibe painel de qualidade dos dados."""
        st.subheader("🔍 Qualidade dos Dados")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric(
                "📊 Completude", 
                f"{quality_data.get('completeness', 0):.1f}%",
                help="Percentual de dados preenchidos"
            )
        
        with col2:
            st.metric(
                "✅ Válidos", 
                f"{quality_data.get('validity', 0):.1f}%",
                help="Percentual de dados válidos"
            )
        
        with col3:
            st.metric(
                "🎯 Consistência", 
                f"{quality_data.get('consistency', 0):.1f}%",
                help="Percentual de dados consistentes"
            )
        
        # Alertas de qualidade
        issues = quality_data.get('issues', [])
        if issues:
            st.warning("⚠️ **Problemas identificados:**")
            for issue in issues:
                st.write(f"- {issue}")
    
    @staticmethod
    def create_metric_card(title, value, change=None, color="blue"):
        """Cria um card de métrica customizado."""
        change_text = ""
        if change is not None:
            if change > 0:
                change_text = f"<span style='color: green;'>▲ {change:+.1f}%</span>"
            elif change < 0:
                change_text = f"<span style='color: red;'>▼ {change:+.1f}%</span>"
            else:
                change_text = f"<span style='color: gray;'>─ {change:.1f}%</span>"
        
        st.markdown(f"""
        <div style="
            padding: 1rem;
            border-radius: 0.5rem;
            border-left: 4px solid {color};
            background-color: rgba(0,0,0,0.05);
            margin-bottom: 1rem;
        ">
            <h4 style="margin: 0 0 0.5rem 0; color: #333;">{title}</h4>
            <p style="font-size: 1.5rem; margin: 0; font-weight: bold; color: {color};">
                {value}
            </p>
            {f'<p style="margin: 0.5rem 0 0 0; font-size: 0.9rem;">{change_text}</p>' if change_text else ''}
        </div>
        """, unsafe_allow_html=True)