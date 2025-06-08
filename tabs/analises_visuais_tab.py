import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from utils import formatar_moeda

class AnalisesVisuaisTab:
    def __init__(self, df, viz):
        self.df = df
        self.viz = viz
    
    def render(self):
        """Renderiza a aba de análises visuais"""
        if self.df.empty:
            st.warning("⚠️ Nenhum dado disponível para análise visual.")
            return
        
        # Análises principais
        self._render_payment_status_analysis()
        self._render_payment_method_analysis()
        self._render_temporal_analysis()
        self._render_value_distribution_analysis()
        self._render_customer_analysis()
        self._render_comparative_analysis()
        self._render_advanced_visualizations()
    
    def _render_payment_status_analysis(self):
        """Renderiza análise de status de pagamento"""
        st.subheader("💳 Análise de Status de Pagamento")
        
        if 'Situação' not in self.df.columns:
            st.warning("⚠️ Coluna 'Situação' não encontrada.")
            return
        
        col1, col2 = st.columns([2, 1])
        
        with col1:
            # Gráfico de pizza principal
            situacao_counts = self.df['Situação'].value_counts()
            fig_situacao = self.viz.create_situacao_pie_chart(situacao_counts)
            st.plotly_chart(fig_situacao, use_container_width=True)
        
        with col2:
            st.write("📊 **Estatísticas por Status**")
            
            total_transacoes = len(self.df)
            
            for situacao, count in situacao_counts.items():
                percentual = (count / total_transacoes) * 100
                
                if situacao.lower() == 'paga':
                    st.metric(f"✅ {situacao}", f"{count:,}", f"{percentual:.1f}%")
                elif situacao.lower() == 'pendente':
                    st.metric(f"⏳ {situacao}", f"{count:,}", f"{percentual:.1f}%")
                elif situacao.lower() == 'expirado':
                    st.metric(f"❌ {situacao}", f"{count:,}", f"{percentual:.1f}%")
                else:
                    st.metric(f"📊 {situacao}", f"{count:,}", f"{percentual:.1f}%")
        
        # Análise de valores por status
        if 'Total' in self.df.columns:
            col1, col2 = st.columns(2)
            
            with col1:
                st.write("💰 **Valores por Status**")
                valores_status = self.df.groupby('Situação')['Total'].agg(['sum', 'mean', 'count']).round(2)
                valores_status.columns = ['Valor_Total', 'Valor_Medio', 'Quantidade']
                
                # Adicionar percentuais
                total_valor = valores_status['Valor_Total'].sum()
                valores_status['Percentual_Valor'] = (valores_status['Valor_Total'] / total_valor * 100).round(1)
                
                # Formatar para exibição
                valores_display = valores_status.copy()
                valores_display['Valor_Total'] = valores_display['Valor_Total'].apply(formatar_moeda)
                valores_display['Valor_Medio'] = valores_display['Valor_Medio'].apply(formatar_moeda)
                
                st.dataframe(valores_display, use_container_width=True)
            
            with col2:
                st.write("📈 **Distribuição de Valores por Status**")
                
                # Gráfico de barras dos valores totais
                fig_valores = px.bar(
                    x=valores_status.index,
                    y=valores_status['Valor_Total'],
                    title="Valor Total por Status",
                    labels={'x': 'Status', 'y': 'Valor Total (R$)'},
                    color=valores_status['Valor_Total'],
                    color_continuous_scale='Blues'
                )
                fig_valores.update_layout(height=300)
                st.plotly_chart(fig_valores, use_container_width=True)
        
        # Análise de eficiência de conversão
        self._render_conversion_analysis()
        
        st.markdown("---")
    
    def _render_conversion_analysis(self):
        """Renderiza análise de conversão"""
        st.write("🎯 **Análise de Conversão**")
        
        if 'Situação' not in self.df.columns:
            return
        
        col1, col2, col3 = st.columns(3)
        
        situacao_counts = self.df['Situação'].value_counts()
        total = len(self.df)
        
        with col1:
            # Taxa de conversão (pagos)
            pagos = situacao_counts.get('Paga', 0) + situacao_counts.get('paga', 0)
            taxa_conversao = (pagos / total) * 100 if total > 0 else 0
            
            if taxa_conversao >= 80:
                st.success(f"🎉 **Excelente Conversão**\n\n{taxa_conversao:.1f}%")
            elif taxa_conversao >= 60:
                st.info(f"👍 **Boa Conversão**\n\n{taxa_conversao:.1f}%")
            else:
                st.warning(f"⚠️ **Conversão Baixa**\n\n{taxa_conversao:.1f}%")
        
        with col2:
            # Taxa de abandono (expirados)
            expirados = situacao_counts.get('Expirado', 0) + situacao_counts.get('expirado', 0)
            taxa_abandono = (expirados / total) * 100 if total > 0 else 0
            
            if taxa_abandono <= 10:
                st.success(f"✅ **Baixo Abandono**\n\n{taxa_abandono:.1f}%")
            elif taxa_abandono <= 25:
                st.warning(f"⚠️ **Abandono Moderado**\n\n{taxa_abandono:.1f}%")
            else:
                st.error(f"🚨 **Alto Abandono**\n\n{taxa_abandono:.1f}%")
        
        with col3:
            # Pendências
            pendentes = situacao_counts.get('Pendente', 0) + situacao_counts.get('pendente', 0)
            taxa_pendencia = (pendentes / total) * 100 if total > 0 else 0
            
            if taxa_pendencia <= 15:
                st.success(f"🟢 **Poucas Pendências**\n\n{taxa_pendencia:.1f}%")
            elif taxa_pendencia <= 30:
                st.info(f"🟡 **Pendências Normais**\n\n{taxa_pendencia:.1f}%")
            else:
                st.warning(f"🟠 **Muitas Pendências**\n\n{taxa_pendencia:.1f}%")
    
    def _render_payment_method_analysis(self):
        """Renderiza análise de métodos de pagamento"""
        st.subheader("💳 Análise de Métodos de Pagamento")
        
        if 'Paga com' not in self.df.columns:
            st.warning("⚠️ Coluna 'Paga com' não encontrada.")
            return
        
        # Filtrar apenas registros com situação paga para análise de método
        df_pagos = self.df.copy()
        if 'Situação' in self.df.columns:
            df_pagos = self.df[self.df['Situação'].str.lower() == 'paga']
        
        if df_pagos.empty:
            st.info("📊 Nenhum registro pago encontrado para análise de métodos.")
            return
        
        col1, col2 = st.columns([2, 1])
        
        with col1:
            # Gráfico de pizza dos métodos
            metodos_pagamento = df_pagos['Paga com'].value_counts()
            fig_pagamento = self.viz.create_pagamento_pie_chart(metodos_pagamento)
            st.plotly_chart(fig_pagamento, use_container_width=True)
        
        with col2:
            st.write("📈 **Top 5 Métodos**")
            
            if 'Total' in df_pagos.columns:
                metodo_stats = df_pagos.groupby('Paga com').agg({
                    'Total': ['sum', 'mean', 'count']
                }).round(2)
                
                metodo_stats.columns = ['Valor_Total', 'Ticket_Medio', 'Quantidade']
                metodo_stats = metodo_stats.sort_values('Valor_Total', ascending=False)
                
                for i, (metodo, stats) in enumerate(metodo_stats.head(5).iterrows()):
                    if pd.notna(metodo):
                        st.metric(
                            f"💳 {metodo}",
                            formatar_moeda(stats['Valor_Total']),
                            f"{int(stats['Quantidade'])} transações"
                        )
        
        # Análise detalhada de métodos
        if 'Total' in df_pagos.columns:
            col1, col2 = st.columns(2)
            
            with col1:
                st.write("📊 **Performance por Método**")
                
                metodo_detalhado = df_pagos.groupby('Paga com').agg({
                    'Total': ['sum', 'mean', 'count'],
                    'CPF/CNPJ': 'nunique' if 'CPF/CNPJ' in df_pagos.columns else lambda x: 0
                }).round(2)
                
                metodo_detalhado.columns = ['Valor_Total', 'Ticket_Medio', 'Qtd_Transacoes', 'Qtd_Clientes']
                
                # Calcular percentuais
                total_valor = metodo_detalhado['Valor_Total'].sum()
                metodo_detalhado['Perc_Valor'] = (metodo_detalhado['Valor_Total'] / total_valor * 100).round(1)
                
                # Formatar para exibição
                metodo_display = metodo_detalhado.copy()
                metodo_display['Valor_Total'] = metodo_display['Valor_Total'].apply(formatar_moeda)
                metodo_display['Ticket_Medio'] = metodo_display['Ticket_Medio'].apply(formatar_moeda)
                
                st.dataframe(
                    metodo_display.sort_values('Perc_Valor', ascending=False), 
                    use_container_width=True
                )
            
            with col2:
                st.write("📈 **Ticket Médio por Método**")
                
                # Gráfico de barras do ticket médio
                ticket_medio_metodo = df_pagos.groupby('Paga com')['Total'].mean().round(2)
                ticket_medio_metodo = ticket_medio_metodo.sort_values(ascending=False).head(8)
                
                fig_ticket = px.bar(
                    x=ticket_medio_metodo.values,
                    y=ticket_medio_metodo.index,
                    orientation='h',
                    title="Ticket Médio por Método",
                    labels={'x': 'Ticket Médio (R$)', 'y': 'Método'},
                    color=ticket_medio_metodo.values,
                    color_continuous_scale='Viridis'
                )
                fig_ticket.update_layout(height=400)
                st.plotly_chart(fig_ticket, use_container_width=True)
        
        # Análise de preferências por valor
        self._render_payment_preferences_analysis(df_pagos)
        
        st.markdown("---")
    
    def _render_payment_preferences_analysis(self, df_pagos):
        """Análise de preferências de pagamento por faixas de valor"""
        if 'Total' not in df_pagos.columns or 'Paga com' not in df_pagos.columns:
            return
        
        st.write("🎯 **Preferências por Faixa de Valor**")
        
        # Criar faixas de valor
        df_temp = df_pagos.copy()
        df_temp['Faixa_Valor'] = pd.cut(
            df_temp['Total'], 
            bins=[0, 100, 500, 1000, 5000, float('inf')],
            labels=['Até R$ 100', 'R$ 100-500', 'R$ 500-1K', 'R$ 1K-5K', 'Acima R$ 5K']
        )
        
        # Criar matriz de métodos por faixa
        metodo_faixa = pd.crosstab(df_temp['Faixa_Valor'], df_temp['Paga com'], normalize='index') * 100
        
        if not metodo_faixa.empty:
            # Heatmap das preferências
            fig_heatmap = px.imshow(
                metodo_faixa.values,
                x=metodo_faixa.columns,
                y=metodo_faixa.index,
                color_continuous_scale='Blues',
                title="Preferência de Método por Faixa de Valor (%)",
                labels={'color': 'Percentual (%)'}
            )
            fig_heatmap.update_layout(height=400)
            st.plotly_chart(fig_heatmap, use_container_width=True)
    
    def _render_temporal_analysis(self):
        """Renderiza análise temporal visual"""
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
        df_temporal['Hora'] = df_temporal['Data de criação'].dt.hour
        df_temporal['Data'] = df_temporal['Data de criação'].dt.date
        
        # Análise por período
        tab1, tab2, tab3, tab4 = st.tabs(["📊 Por Dia da Semana", "📅 Por Mês", "🕐 Por Hora", "📈 Evolução Diária"])
        
        with tab1:
            self._render_weekday_analysis(df_temporal)
        
        with tab2:
            self._render_monthly_analysis(df_temporal)
        
        with tab3:
            self._render_hourly_analysis(df_temporal)
        
        with tab4:
            self._render_daily_evolution(df_temporal)
        
        st.markdown("---")
    
    def _render_weekday_analysis(self, df_temporal):
        """Análise por dia da semana"""
        col1, col2 = st.columns(2)
        
        with col1:
            st.write("📊 **Transações por Dia da Semana**")
            
            dias_semana = df_temporal['Dia_Semana'].value_counts()
            
            # Ordenar dias da semana
            ordem_dias = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
            dias_ordenados = dias_semana.reindex([dia for dia in ordem_dias if dia in dias_semana.index])
            
            # Traduzir nomes
            traducao_dias = {
                'Monday': 'Segunda', 'Tuesday': 'Terça', 'Wednesday': 'Quarta',
                'Thursday': 'Quinta', 'Friday': 'Sexta', 'Saturday': 'Sábado', 'Sunday': 'Domingo'
            }
            
            dias_traduzidos = dias_ordenados.rename(index=traducao_dias)
            
            fig_dias = px.bar(
                x=dias_traduzidos.index,
                y=dias_traduzidos.values,
                title="Distribuição por Dia da Semana",
                labels={'x': 'Dia da Semana', 'y': 'Número de Transações'},
                color=dias_traduzidos.values,
                color_continuous_scale='Blues'
            )
            st.plotly_chart(fig_dias, use_container_width=True)
        
        with col2:
            st.write("💰 **Valores por Dia da Semana**")
            
            if 'Total' in df_temporal.columns:
                valores_dia = df_temporal.groupby('Dia_Semana')['Total'].sum()
                valores_dia_ordenados = valores_dia.reindex([dia for dia in ordem_dias if dia in valores_dia.index])
                valores_dia_traduzidos = valores_dia_ordenados.rename(index=traducao_dias)
                
                fig_valores_dia = px.bar(
                    x=valores_dia_traduzidos.index,
                    y=valores_dia_traduzidos.values,
                    title="Faturamento por Dia da Semana",
                    labels={'x': 'Dia da Semana', 'y': 'Valor Total (R$)'},
                    color=valores_dia_traduzidos.values,
                    color_continuous_scale='Greens'
                )
                st.plotly_chart(fig_valores_dia, use_container_width=True)
                
                # Métricas
                melhor_dia = valores_dia_traduzidos.idxmax()
                pior_dia = valores_dia_traduzidos.idxmin()
                
                col_a, col_b = st.columns(2)
                with col_a:
                    st.metric("🏆 Melhor Dia", melhor_dia, formatar_moeda(valores_dia_traduzidos.max()))
                with col_b:
                    st.metric("📉 Pior Dia", pior_dia, formatar_moeda(valores_dia_traduzidos.min()))
    
    def _render_monthly_analysis(self, df_temporal):
        """Análise por mês"""
        col1, col2 = st.columns(2)
        
        with col1:
            st.write("📅 **Distribuição por Mês**")
            
            vendas_mes = df_temporal.groupby('Mes')['Total'].sum() if 'Total' in df_temporal.columns else df_temporal['Mes'].value_counts().sort_index()
            
            # Criar nomes dos meses
            meses_nomes = {
                1: 'Jan', 2: 'Fev', 3: 'Mar', 4: 'Abr',
                5: 'Mai', 6: 'Jun', 7: 'Jul', 8: 'Ago',
                9: 'Set', 10: 'Out', 11: 'Nov', 12: 'Dez'
            }
            
            vendas_mes_nomes = vendas_mes.rename(index=meses_nomes)
            
            fig_mes = px.bar(
                x=vendas_mes_nomes.index,
                y=vendas_mes_nomes.values,
                title="Distribuição por Mês",
                labels={'x': 'Mês', 'y': 'Valor' if 'Total' in df_temporal.columns else 'Transações'},
                color=vendas_mes_nomes.values,
                color_continuous_scale='Viridis'
            )
            st.plotly_chart(fig_mes, use_container_width=True)
        
        with col2:
            st.write("📊 **Sazonalidade**")
            
            # Análise de trimestres
            df_temporal['Trimestre'] = df_temporal['Data de criação'].dt.quarter
            vendas_trimestre = df_temporal.groupby('Trimestre')['Total'].agg(['sum', 'count', 'mean']).round(2) if 'Total' in df_temporal.columns else df_temporal['Trimestre'].value_counts().sort_index()
            
            if 'Total' in df_temporal.columns:
                vendas_trimestre.columns = ['Valor_Total', 'Qtd_Transacoes', 'Ticket_Medio']
                
                # Renomear índices
                nomes_trimestres = {1: 'Q1', 2: 'Q2', 3: 'Q3', 4: 'Q4'}
                vendas_trimestre.index = vendas_trimestre.index.map(nomes_trimestres)
                
                fig_trimestre = px.bar(
                    x=vendas_trimestre.index,
                    y=vendas_trimestre['Valor_Total'],
                    title="Faturamento por Trimestre",
                    labels={'x': 'Trimestre', 'y': 'Valor Total (R$)'},
                    color=vendas_trimestre['Valor_Total'],
                    color_continuous_scale='Plasma'
                )
                st.plotly_chart(fig_trimestre, use_container_width=True)
                
                # Tabela de trimestres
                vendas_display = vendas_trimestre.copy()
                vendas_display['Valor_Total'] = vendas_display['Valor_Total'].apply(formatar_moeda)
                vendas_display['Ticket_Medio'] = vendas_display['Ticket_Medio'].apply(formatar_moeda)
                
                st.dataframe(vendas_display, use_container_width=True)
    
    def _render_hourly_analysis(self, df_temporal):
        """Análise por hora"""
        if 'Hora' not in df_temporal.columns:
            st.info("📊 Dados de hora não disponíveis")
            return
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.write("🕐 **Distribuição por Hora**")
            
            horas = df_temporal['Hora'].value_counts().sort_index()
            
            fig_hora = px.line(
                x=horas.index,
                y=horas.values,
                title="Transações por Hora do Dia",
                labels={'x': 'Hora', 'y': 'Número de Transações'},
                markers=True
            )
            fig_hora.update_layout(xaxis=dict(tickmode='linear', tick0=0, dtick=2))
            st.plotly_chart(fig_hora, use_container_width=True)
        
        with col2:
            st.write("⏰ **Períodos do Dia**")
            
            # Definir períodos
            def classificar_periodo(hora):
                if 6 <= hora < 12:
                    return 'Manhã'
                elif 12 <= hora < 18:
                    return 'Tarde'
                elif 18 <= hora < 24:
                    return 'Noite'
                else:
                    return 'Madrugada'
            
            df_temporal['Periodo'] = df_temporal['Hora'].apply(classificar_periodo)
            
            if 'Total' in df_temporal.columns:
                periodo_stats = df_temporal.groupby('Periodo')['Total'].agg(['sum', 'count', 'mean']).round(2)
                periodo_stats.columns = ['Valor_Total', 'Qtd_Transacoes', 'Ticket_Medio']
            else:
                periodo_stats = df_temporal['Periodo'].value_counts()
            
            # Gráfico de períodos
            if 'Total' in df_temporal.columns:
                fig_periodo = px.pie(
                    values=periodo_stats['Valor_Total'],
                    names=periodo_stats.index,
                    title="Faturamento por Período do Dia"
                )
                st.plotly_chart(fig_periodo, use_container_width=True)
                
                # Métricas dos períodos
                periodo_top = periodo_stats['Valor_Total'].idxmax()
                st.metric("🌅 Período Mais Forte", periodo_top, formatar_moeda(periodo_stats.loc[periodo_top, 'Valor_Total']))
    
    def _render_daily_evolution(self, df_temporal):
        """Evolução diária"""
        if 'Data' not in df_temporal.columns:
            return
        
        st.write("📈 **Evolução Diária**")
        
        if 'Total' in df_temporal.columns:
            evolucao_diaria = df_temporal.groupby('Data').agg({
                'Total': ['sum', 'count'],
                'CPF/CNPJ': 'nunique' if 'CPF/CNPJ' in df_temporal.columns else lambda x: 0
            }).round(2)
            
            evolucao_diaria.columns = ['Valor_Total', 'Qtd_Transacoes', 'Clientes_Unicos']
            evolucao_diaria = evolucao_diaria.reset_index()
            
            # Gráfico de evolução
            fig_evolucao = make_subplots(
                rows=2, cols=1,
                subplot_titles=('Valor Diário', 'Quantidade Diária'),
                vertical_spacing=0.1
            )
            
            # Valor
            fig_evolucao.add_trace(
                go.Scatter(
                    x=evolucao_diaria['Data'],
                    y=evolucao_diaria['Valor_Total'],
                    mode='lines+markers',
                    name='Valor Total',
                    line=dict(color='blue')
                ),
                row=1, col=1
            )
            
            # Quantidade
            fig_evolucao.add_trace(
                go.Scatter(
                    x=evolucao_diaria['Data'],
                    y=evolucao_diaria['Qtd_Transacoes'],
                    mode='lines+markers',
                    name='Quantidade',
                    line=dict(color='green')
                ),
                row=2, col=1
            )
            
            fig_evolucao.update_layout(height=500, title_text="Evolução Diária de Vendas")
            st.plotly_chart(fig_evolucao, use_container_width=True)
            
            # Estatísticas da evolução
            col1, col2, col3 = st.columns(3)
            
            with col1:
                melhor_dia = evolucao_diaria.loc[evolucao_diaria['Valor_Total'].idxmax()]
                st.metric(
                    "🏆 Melhor Dia (Valor)",
                    melhor_dia['Data'].strftime('%d/%m/%Y'),
                    formatar_moeda(melhor_dia['Valor_Total'])
                )
            
            with col2:
                dia_mais_ativo = evolucao_diaria.loc[evolucao_diaria['Qtd_Transacoes'].idxmax()]
                st.metric(
                    "🚀 Dia Mais Ativo",
                    dia_mais_ativo['Data'].strftime('%d/%m/%Y'),
                    f"{int(dia_mais_ativo['Qtd_Transacoes'])} transações"
                )
            
            with col3:
                media_diaria = evolucao_diaria['Valor_Total'].mean()
                st.metric("📊 Média Diária", formatar_moeda(media_diaria))
    
    def _render_value_distribution_analysis(self):
        """Análise de distribuição de valores"""
        st.subheader("💰 Análise de Distribuição de Valores")
        
        if 'Total' not in self.df.columns:
            st.warning("⚠️ Coluna 'Total' não encontrada.")
            return
        
        valores = self.df['Total'].dropna()
        
        if valores.empty:
            st.warning("⚠️ Nenhum valor válido encontrado.")
            return
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.write("📊 **Histograma de Valores**")
            
            # Histograma
            fig_hist = px.histogram(
                valores,
                nbins=30,
                title="Distribuição de Valores",
                labels={'value': 'Valor (R$)', 'count': 'Frequência'}
            )
            fig_hist.update_layout(height=400)
            st.plotly_chart(fig_hist, use_container_width=True)
        
        with col2:
            st.write("📈 **Box Plot de Valores**")
            
            # Box plot
            fig_box = px.box(
                y=valores,
                title="Análise de Outliers",
                labels={'y': 'Valor (R$)'}
            )
            fig_box.update_layout(height=400)
            st.plotly_chart(fig_box, use_container_width=True)
        
        # Estatísticas detalhadas
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.write("📊 **Estatísticas Básicas**")
            st.metric("💰 Valor Médio", formatar_moeda(valores.mean()))
            st.metric("📊 Mediana", formatar_moeda(valores.median()))
            st.metric("📈 Desvio Padrão", formatar_moeda(valores.std()))
        
        with col2:
            st.write("🎯 **Extremos**")
            st.metric("🔝 Valor Máximo", formatar_moeda(valores.max()))
            st.metric("🔻 Valor Mínimo", formatar_moeda(valores.min()))
            st.metric("📏 Amplitude", formatar_moeda(valores.max() - valores.min()))
        
        with col3:
            st.write("📊 **Quartis**")
            q1, q2, q3 = valores.quantile([0.25, 0.5, 0.75])
st.metric("Q1 (25%)", formatar_moeda(q1))
            st.metric("Q2 (50%)", formatar_moeda(q2))
            st.metric("Q3 (75%)", formatar_moeda(q3))
        
        # Análise por faixas de valor
        st.write("🎯 **Distribuição por Faixas de Valor**")
        
        # Criar faixas automáticas
        faixas = pd.cut(valores, bins=5, precision=0)
        dist_faixas = faixas.value_counts().sort_index()
        
        # Gráfico de faixas
        fig_faixas = px.bar(
            x=[str(interval) for interval in dist_faixas.index],
            y=dist_faixas.values,
            title="Distribuição por Faixas de Valor",
            labels={'x': 'Faixa de Valor', 'y': 'Quantidade'},
            color=dist_faixas.values,
            color_continuous_scale='Viridis'
        )
        fig_faixas.update_xaxes(tickangle=45)
        st.plotly_chart(fig_faixas, use_container_width=True)
        
        st.markdown("---")
    
    def _render_customer_analysis(self):
        """Análise de clientes"""
        st.subheader("👥 Análise de Clientes")
        
        if 'CPF/CNPJ' not in self.df.columns:
            st.warning("⚠️ Coluna 'CPF/CNPJ' não encontrada.")
            return
        
        # Preparar dados de clientes
        df_clientes = self.df.dropna(subset=['CPF/CNPJ'])
        
        if df_clientes.empty:
            st.warning("⚠️ Nenhum dado de cliente válido encontrado.")
            return
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.write("🔄 **Distribuição de Recorrência**")
            
            # Análise de recorrência
            transacoes_por_cliente = df_clientes['CPF/CNPJ'].value_counts()
            
            # Classificar clientes
            def classificar_recorrencia(qtd):
                if qtd == 1:
                    return 'Único'
                elif qtd <= 3:
                    return 'Ocasional'
                elif qtd <= 7:
                    return 'Recorrente'
                else:
                    return 'Fiel'
            
            recorrencia = transacoes_por_cliente.apply(classificar_recorrencia)
            dist_recorrencia = recorrencia.value_counts()
            
            fig_recorrencia = px.pie(
                values=dist_recorrencia.values,
                names=dist_recorrencia.index,
                title="Tipos de Cliente por Recorrência",
                color_discrete_sequence=px.colors.qualitative.Set3
            )
            st.plotly_chart(fig_recorrencia, use_container_width=True)
        
        with col2:
            st.write("📊 **Estatísticas de Recorrência**")
            
            # Métricas de recorrência
            media_transacoes = transacoes_por_cliente.mean()
            max_transacoes = transacoes_por_cliente.max()
            clientes_recorrentes = (transacoes_por_cliente > 1).sum()
            taxa_recorrencia = (clientes_recorrentes / len(transacoes_por_cliente)) * 100
            
            st.metric("📊 Média Transações/Cliente", f"{media_transacoes:.1f}")
            st.metric("🏆 Máx Transações (1 cliente)", max_transacoes)
            st.metric("🔄 Taxa de Recorrência", f"{taxa_recorrencia:.1f}%")
            
            # Top clientes mais ativos
            st.write("🏆 **Top 5 Clientes Mais Ativos**")
            top_clientes = transacoes_por_cliente.head(5)
            
            for i, (cliente, qtd) in enumerate(top_clientes.items(), 1):
                # Pegar nome do cliente se disponível
                if 'Nome' in df_clientes.columns:
                    nome = df_clientes[df_clientes['CPF/CNPJ'] == cliente]['Nome'].iloc[0]
                    label = f"{i}. {nome}"
                else:
                    label = f"{i}. Cliente {i}"
                
                st.write(f"**{label}**: {qtd} transações")
        
        # Análise de valor por cliente
        if 'Total' in df_clientes.columns:
            col1, col2 = st.columns(2)
            
            with col1:
                st.write("💰 **LTV dos Clientes**")
                
                # Calcular LTV por cliente
                ltv_por_cliente = df_clientes.groupby('CPF/CNPJ')['Total'].sum()
                
                # Histograma de LTV
                fig_ltv = px.histogram(
                    ltv_por_cliente.values,
                    nbins=20,
                    title="Distribuição de LTV",
                    labels={'value': 'LTV (R$)', 'count': 'Quantidade de Clientes'}
                )
                st.plotly_chart(fig_ltv, use_container_width=True)
            
            with col2:
                st.write("🎯 **Segmentação por Valor**")
                
                # Segmentar clientes por valor
                def classificar_por_valor(valor):
                    if valor < 500:
                        return 'Bronze (< R$ 500)'
                    elif valor < 1500:
                        return 'Prata (R$ 500-1.500)'
                    else:
                        return 'Ouro (> R$ 1.500)'
                
                segmentacao = ltv_por_cliente.apply(classificar_por_valor)
                dist_segmentacao = segmentacao.value_counts()
                
                fig_segmentacao = px.bar(
                    x=dist_segmentacao.index,
                    y=dist_segmentacao.values,
                    title="Segmentação de Clientes por Valor",
                    color=dist_segmentacao.values,
                    color_continuous_scale='Viridis'
                )
                fig_segmentacao.update_xaxes(tickangle=45)
                st.plotly_chart(fig_segmentacao, use_container_width=True)
        
        st.markdown("---")
    
    def _render_comparative_analysis(self):
        """Renderiza análises comparativas"""
        st.subheader("🔄 Análises Comparativas")
        
        tab1, tab2, tab3 = st.tabs(["📊 Status vs Valor", "💳 Método vs Ticket", "📅 Temporal vs Performance"])
        
        with tab1:
            self._render_status_value_comparison()
        
        with tab2:
            self._render_method_ticket_comparison()
        
        with tab3:
            self._render_temporal_performance_comparison()
        
        st.markdown("---")
    
    def _render_status_value_comparison(self):
        """Comparação entre status e valores"""
        if not all(col in self.df.columns for col in ['Situação', 'Total']):
            st.warning("⚠️ Colunas necessárias não encontradas.")
            return
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.write("🎫 **Ticket Médio por Status**")
            
            ticket_medio_status = self.df.groupby('Situação')['Total'].mean().round(2)
            
            fig_ticket = px.bar(
                x=ticket_medio_status.index,
                y=ticket_medio_status.values,
                title="Ticket Médio por Status",
                labels={'x': 'Status', 'y': 'Ticket Médio (R$)'},
                color=ticket_medio_status.values,
                color_continuous_scale='Blues'
            )
            st.plotly_chart(fig_ticket, use_container_width=True)
        
        with col2:
            st.write("📊 **Distribuição de Valores por Status**")
            
            # Box plot por status
            fig_box_status = px.box(
                self.df,
                x='Situação',
                y='Total',
                title="Distribuição de Valores por Status"
            )
            st.plotly_chart(fig_box_status, use_container_width=True)
        
        # Tabela comparativa
        st.write("📋 **Resumo Comparativo**")
        
        resumo_status = self.df.groupby('Situação')['Total'].agg(['count', 'sum', 'mean', 'median', 'std']).round(2)
        resumo_status.columns = ['Quantidade', 'Valor_Total', 'Média', 'Mediana', 'Desvio_Padrão']
        
        # Formatar valores monetários
        resumo_display = resumo_status.copy()
        for col in ['Valor_Total', 'Média', 'Mediana', 'Desvio_Padrão']:
            resumo_display[col] = resumo_display[col].apply(formatar_moeda)
        
        st.dataframe(resumo_display, use_container_width=True)
    
    def _render_method_ticket_comparison(self):
        """Comparação entre métodos e tickets"""
        if not all(col in self.df.columns for col in ['Paga com', 'Total']):
            st.warning("⚠️ Colunas necessárias não encontradas.")
            return
        
        # Filtrar apenas registros pagos
        df_pagos = self.df[self.df['Situação'].str.lower() == 'paga'] if 'Situação' in self.df.columns else self.df
        df_pagos = df_pagos.dropna(subset=['Paga com', 'Total'])
        
        if df_pagos.empty:
            st.warning("⚠️ Nenhum dado válido para comparação.")
            return
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.write("💳 **Ticket Médio por Método**")
            
            ticket_por_metodo = df_pagos.groupby('Paga com')['Total'].mean().round(2).sort_values(ascending=False)
            
            fig_metodo_ticket = px.bar(
                x=ticket_por_metodo.values,
                y=ticket_por_metodo.index,
                orientation='h',
                title="Ticket Médio por Método de Pagamento",
                labels={'x': 'Ticket Médio (R$)', 'y': 'Método'},
                color=ticket_por_metodo.values,
                color_continuous_scale='Greens'
            )
            fig_metodo_ticket.update_layout(height=400)
            st.plotly_chart(fig_metodo_ticket, use_container_width=True)
        
        with col2:
            st.write("📊 **Volume vs Ticket Médio**")
            
            # Scatter plot volume vs ticket médio
            metodo_stats = df_pagos.groupby('Paga com').agg({
                'Total': ['count', 'mean']
            }).round(2)
            metodo_stats.columns = ['Volume', 'Ticket_Medio']
            metodo_stats = metodo_stats.reset_index()
            
            fig_scatter = px.scatter(
                metodo_stats,
                x='Volume',
                y='Ticket_Medio',
                text='Paga com',
                title="Volume vs Ticket Médio por Método",
                labels={'Volume': 'Número de Transações', 'Ticket_Medio': 'Ticket Médio (R$)'},
                size='Volume',
                color='Ticket_Medio',
                color_continuous_scale='Viridis'
            )
            fig_scatter.update_traces(textposition='top center')
            st.plotly_chart(fig_scatter, use_container_width=True)
    
    def _render_temporal_performance_comparison(self):
        """Comparação temporal de performance"""
        if 'Data de criação' not in self.df.columns:
            st.warning("⚠️ Coluna 'Data de criação' não encontrada.")
            return
        
        df_temp = self.df.copy()
        df_temp['Data de criação'] = pd.to_datetime(df_temp['Data de criação'], errors='coerce')
        df_temp = df_temp.dropna(subset=['Data de criação'])
        
        if df_temp.empty:
            return
        
        df_temp['Mes_Ano'] = df_temp['Data de criação'].dt.to_period('M')
        df_temp['Dia_Semana'] = df_temp['Data de criação'].dt.day_name()
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.write("📅 **Performance Mensal**")
            
            if 'Total' in df_temp.columns:
                performance_mensal = df_temp.groupby('Mes_Ano').agg({
                    'Total': ['sum', 'count', 'mean']
                }).round(2)
                performance_mensal.columns = ['Valor_Total', 'Quantidade', 'Ticket_Medio']
                performance_mensal = performance_mensal.reset_index()
                performance_mensal['Mes_Ano_Str'] = performance_mensal['Mes_Ano'].astype(str)
                
                # Gráfico de linha dupla
                fig_mensal = make_subplots(
                    rows=1, cols=1,
                    specs=[[{"secondary_y": True}]]
                )
                
                fig_mensal.add_trace(
                    go.Scatter(
                        x=performance_mensal['Mes_Ano_Str'],
                        y=performance_mensal['Valor_Total'],
                        mode='lines+markers',
                        name='Valor Total',
                        line=dict(color='blue')
                    ),
                    secondary_y=False
                )
                
                fig_mensal.add_trace(
                    go.Scatter(
                        x=performance_mensal['Mes_Ano_Str'],
                        y=performance_mensal['Quantidade'],
                        mode='lines+markers',
                        name='Quantidade',
                        line=dict(color='red')
                    ),
                    secondary_y=True
                )
                
                fig_mensal.update_xaxes(title_text="Período")
                fig_mensal.update_yaxes(title_text="Valor (R$)", secondary_y=False)
                fig_mensal.update_yaxes(title_text="Quantidade", secondary_y=True)
                fig_mensal.update_layout(title_text="Performance Mensal")
                
                st.plotly_chart(fig_mensal, use_container_width=True)
        
        with col2:
            st.write("📊 **Performance por Dia da Semana**")
            
            if 'Total' in df_temp.columns:
                performance_semanal = df_temp.groupby('Dia_Semana').agg({
                    'Total': ['sum', 'mean', 'count']
                }).round(2)
                performance_semanal.columns = ['Valor_Total', 'Ticket_Medio', 'Quantidade']
                
                # Ordenar dias da semana
                ordem_dias = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
                performance_semanal = performance_semanal.reindex([dia for dia in ordem_dias if dia in performance_semanal.index])
                
                # Radar chart
                fig_radar = go.Figure()
                
                # Normalizar valores para o radar (0-100)
                valor_norm = (performance_semanal['Valor_Total'] / performance_semanal['Valor_Total'].max()) * 100
                ticket_norm = (performance_semanal['Ticket_Medio'] / performance_semanal['Ticket_Medio'].max()) * 100
                
                fig_radar.add_trace(go.Scatterpolar(
                    r=valor_norm.values,
                    theta=performance_semanal.index,
                    fill='toself',
                    name='Valor Total'
                ))
                
                fig_radar.add_trace(go.Scatterpolar(
                    r=ticket_norm.values,
                    theta=performance_semanal.index,
                    fill='toself',
                    name='Ticket Médio'
                ))
                
                fig_radar.update_layout(
                    polar=dict(
                        radialaxis=dict(
                            visible=True,
                            range=[0, 100]
                        )),
                    showlegend=True,
                    title="Performance por Dia da Semana"
                )
                
                st.plotly_chart(fig_radar, use_container_width=True)
    
    def _render_advanced_visualizations(self):
        """Renderiza visualizações avançadas"""
        st.subheader("🚀 Visualizações Avançadas")
        
        tab1, tab2, tab3 = st.tabs(["🔥 Heatmaps", "🌐 Correlações", "📈 Tendências"])
        
        with tab1:
            self._render_heatmaps()
        
        with tab2:
            self._render_correlations()
        
        with tab3:
            self._render_trends()
    
    def _render_heatmaps(self):
        """Renderiza heatmaps"""
        if not all(col in self.df.columns for col in ['Data de criação']):
            st.warning("⚠️ Dados temporais necessários para heatmaps.")
            return
        
        df_temp = self.df.copy()
        df_temp['Data de criação'] = pd.to_datetime(df_temp['Data de criação'], errors='coerce')
        df_temp = df_temp.dropna(subset=['Data de criação'])
        
        if df_temp.empty:
            return
        
        df_temp['Hora'] = df_temp['Data de criação'].dt.hour
        df_temp['Dia_Semana'] = df_temp['Data de criação'].dt.day_name()
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.write("🔥 **Heatmap: Dia da Semana vs Hora**")
            
            # Criar matriz hora vs dia da semana
            heatmap_data = df_temp.groupby(['Dia_Semana', 'Hora']).size().unstack(fill_value=0)
            
            # Ordenar dias da semana
            ordem_dias = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
            heatmap_data = heatmap_data.reindex([dia for dia in ordem_dias if dia in heatmap_data.index])
            
            fig_heatmap = px.imshow(
                heatmap_data.values,
                x=heatmap_data.columns,
                y=heatmap_data.index,
                color_continuous_scale='Blues',
                title="Atividade por Dia da Semana e Hora",
                labels={'color': 'Número de Transações'}
            )
            st.plotly_chart(fig_heatmap, use_container_width=True)
        
        with col2:
            if 'Situação' in df_temp.columns and 'Total' in df_temp.columns:
                st.write("🔥 **Heatmap: Status vs Faixa de Valor**")
                
                # Criar faixas de valor
                df_temp['Faixa_Valor'] = pd.cut(
                    df_temp['Total'], 
                    bins=5, 
                    labels=['Muito Baixo', 'Baixo', 'Médio', 'Alto', 'Muito Alto']
                )
                
                # Criar matriz status vs faixa
                heatmap_status = pd.crosstab(df_temp['Situação'], df_temp['Faixa_Valor'])
                
                fig_heatmap_status = px.imshow(
                    heatmap_status.values,
                    x=heatmap_status.columns,
                    y=heatmap_status.index,
                    color_continuous_scale='Reds',
                    title="Status vs Faixa de Valor",
                    labels={'color': 'Quantidade'}
                )
                st.plotly_chart(fig_heatmap_status, use_container_width=True)
    
    def _render_correlations(self):
        """Renderiza análise de correlações"""
        # Selecionar apenas colunas numéricas
        numeric_cols = self.df.select_dtypes(include=['number']).columns
        
        if len(numeric_cols) < 2:
            st.warning("⚠️ Poucos dados numéricos para análise de correlação.")
            return
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.write("🌐 **Matriz de Correlação**")
            
            # Calcular correlações
            corr_matrix = self.df[numeric_cols].corr()
            
            fig_corr = px.imshow(
                corr_matrix.values,
                x=corr_matrix.columns,
                y=corr_matrix.index,
                color_continuous_scale='RdBu',
                zmin=-1, zmax=1,
                title="Matriz de Correlação",
                labels={'color': 'Correlação'}
            )
            st.plotly_chart(fig_corr, use_container_width=True)
        
        with col2:
            st.write("📊 **Correlações Mais Fortes**")
            
            # Encontrar correlações mais fortes (excluindo diagonal)
            corr_flat = corr_matrix.where(
                ~pd.np.triu(pd.np.ones(corr_matrix.shape)).astype(bool)
            ).stack().sort_values(ascending=False)
            
            st.write("**Correlações Positivas Mais Fortes:**")
            for (var1, var2), corr in corr_flat.head(5).items():
                if corr > 0.1:  # Apenas correlações significativas
                    st.write(f"- {var1} ↔ {var2}: {corr:.3f}")
            
            st.write("**Correlações Negativas Mais Fortes:**")
            for (var1, var2), corr in corr_flat.tail(5).items():
                if corr < -0.1:  # Apenas correlações significativas
                    st.write(f"- {var1} ↔ {var2}: {corr:.3f}")
    
    def _render_trends(self):
        """Renderiza análise de tendências"""
        if 'Data de criação' not in self.df.columns or 'Total' not in self.df.columns:
            st.warning("⚠️ Dados temporais e de valor necessários para análise de tendências.")
            return
        
        df_trends = self.df.copy()
        df_trends['Data de criação'] = pd.to_datetime(df_trends['Data de criação'], errors='coerce')
        df_trends = df_trends.dropna(subset=['Data de criação', 'Total'])
        
        if len(df_trends) < 10:
            st.warning("⚠️ Poucos dados para análise de tendências confiável.")
            return
        
        # Agrupar por data
        df_trends['Data'] = df_trends['Data de criação'].dt.date
        trends_daily = df_trends.groupby('Data').agg({
            'Total': ['sum', 'count', 'mean']
        }).round(2)
        trends_daily.columns = ['Valor_Total', 'Quantidade', 'Ticket_Medio']
        trends_daily = trends_daily.reset_index()
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.write("📈 **Tendência de Crescimento**")
            
            # Calcular tendência linear simples
            from scipy.stats import linregress
            
            x = range(len(trends_daily))
            y = trends_daily['Valor_Total'].values
            
            slope, intercept, r_value, p_value, std_err = linregress(x, y)
            
            # Criar linha de tendência
            trend_line = [slope * i + intercept for i in x]
            
            fig_trend = go.Figure()
            
            fig_trend.add_trace(go.Scatter(
                x=trends_daily['Data'],
                y=trends_daily['Valor_Total'],
                mode='lines+markers',
                name='Valor Real',
                line=dict(color='blue')
            ))
            
            fig_trend.add_trace(go.Scatter(
                x=trends_daily['Data'],
                y=trend_line,
                mode='lines',
                name='Tendência',
                line=dict(color='red', dash='dash')
            ))
            
            fig_trend.update_layout(
                title=f"Tendência de Crescimento (R² = {r_value**2:.3f})",
                xaxis_title="Data",
                yaxis_title="Valor Total (R$)"
            )
            
            st.plotly_chart(fig_trend, use_container_width=True)
        
        with col2:
            st.write("📊 **Métricas de Tendência**")
            
            # Calcular métricas
            crescimento_diario = slope
            r_squared = r_value ** 2
            
            # Classificar tendência
            if slope > 0 and r_squared > 0.7:
                tendencia_label = "📈 Crescimento Forte"
                tendencia_color = "success"
            elif slope > 0 and r_squared > 0.3:
                tendencia_label = "📈 Crescimento Moderado"
                tendencia_color = "info"
            elif abs(slope) <= 0.01:
                tendencia_label = "➡️ Estável"
                tendencia_color = "warning"
            else:
                tendencia_label = "📉 Declínio"
                tendencia_color = "error"
            
            if tendencia_color == "success":
                st.success(tendencia_label)
            elif tendencia_color == "info":
                st.info(tendencia_label)
            elif tendencia_color == "warning":
                st.warning(tendencia_label)
            else:
                st.error(tendencia_label)
            
            st.metric("📊 R² (Qualidade da Tendência)", f"{r_squared:.3f}")
            st.metric("📈 Crescimento Diário Médio", formatar_moeda(crescimento_diario))
            
            # Projeção simples para próximos 30 dias
            if slope > 0:
                projecao_30d = crescimento_diario * 30
                st.metric("🔮 Projeção 30 dias", formatar_moeda(projecao_30d))