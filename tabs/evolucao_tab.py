import streamlit as st
import pandas as pd

class EvolucaoTab:
    def __init__(self, df, viz):
        self.df = df
        self.viz = viz
    
    def render(self):
        """Renderiza a aba de evolução mensal"""
        if not self._check_required_columns():
            st.error("❌ Dados insuficientes para análise temporal.")
            self._render_requirements_info()
            return
        
        # Gráfico principal
        self._render_monthly_evolution()
        
        st.markdown("---")
        
        # Tabela de dados
        self._render_monthly_table()
        
        st.markdown("---")
        
        # Análise de tendências
        self._render_trend_analysis()
        
        st.markdown("---")
        
        # Análise sazonal
        self._render_seasonal_analysis()
    
    def _check_required_columns(self):
        """Verifica se as colunas necessárias existem"""
        required_cols = ['Mes_Ano', 'Total', 'Situação']
        return all(col in self.df.columns for col in required_cols)
    
    def _render_requirements_info(self):
        """Renderiza informações sobre requisitos de dados"""
        st.info("📋 **Colunas necessárias para análise temporal:**")
        st.write("- `Mes_Ano`: Período da transação")
        st.write("- `Total`: Valor da transação")
        st.write("- `Situação`: Status do pagamento")
        
        st.write("🔍 **Colunas disponíveis no dataset:**")
        st.write(list(self.df.columns))
    
    def _render_monthly_evolution(self):
        """Renderiza o gráfico de evolução mensal"""
        st.subheader("📈 Evolução Mensal por Status")
        
        df_mensal_status = self.df.groupby(['Mes_Ano', 'Situação'])['Total'].sum().reset_index()
        df_mensal_status['Mes_Ano_Str'] = df_mensal_status['Mes_Ano'].astype(str)
        
        # Gráfico principal
        fig_mensal = self.viz.create_evolucao_status_chart(df_mensal_status)
        st.plotly_chart(fig_mensal, use_container_width=True)
        
        # Resumo rápido da evolução
        self._render_evolution_summary(df_mensal_status)
    
    def _render_evolution_summary(self, df_mensal_status):
        """Renderiza resumo da evolução"""
        st.subheader("📊 Resumo da Evolução")
        
        # Agrupar por mês (total)
        evolucao_total = df_mensal_status.groupby('Mes_Ano_Str')['Total'].sum()
        
        if len(evolucao_total) >= 2:
            col1, col2, col3, col4 = st.columns(4)
            
            # Valor atual vs anterior
            valor_atual = evolucao_total.iloc[-1]
            valor_anterior = evolucao_total.iloc[-2]
            crescimento = ((valor_atual - valor_anterior) / valor_anterior) * 100 if valor_anterior > 0 else 0
            
            with col1:
                st.metric("💰 Último Mês", f"R$ {valor_atual:,.2f}")
            
            with col2:
                st.metric(
                    "📈 Crescimento", 
                    f"{crescimento:+.1f}%",
                    delta=f"R$ {valor_atual - valor_anterior:,.2f}"
                )
            
            with col3:
                # Melhor mês
                melhor_mes_idx = evolucao_total.idxmax()
                melhor_valor = evolucao_total.max()
                st.metric("🏆 Melhor Mês", melhor_mes_idx)
                st.caption(f"R$ {melhor_valor:,.2f}")
            
            with col4:
                # Média mensal
                media_mensal = evolucao_total.mean()
                st.metric("📊 Média Mensal", f"R$ {media_mensal:,.2f}")
        else:
            st.info("📊 Necessários pelo menos 2 meses de dados para análise comparativa.")
    
    def _render_monthly_table(self):
        """Renderiza tabela com dados mensais"""
        st.subheader("📋 Dados Mensais Detalhados")
        
        # Criar tabela mais detalhada
        df_mensal_detalhado = self.df.groupby(['Mes_Ano', 'Situação']).agg({
            'Total': ['sum', 'mean', 'count'],
            'CPF/CNPJ': 'nunique' if 'CPF/CNPJ' in self.df.columns else lambda x: 0
        }).round(2)
        
        df_mensal_detalhado.columns = ['Valor_Total', 'Valor_Medio', 'Qtd_Transacoes', 'Qtd_Clientes']
        df_mensal_detalhado = df_mensal_detalhado.reset_index()
        
        # Criar abas para diferentes visualizações
        tab_valor, tab_qtd, tab_clientes = st.tabs(["💰 Valores", "📊 Quantidades", "👥 Clientes"])
        
        with tab_valor:
            # Pivot para valores
            pivot_valor = df_mensal_detalhado.pivot(
                index='Mes_Ano', 
                columns='Situação', 
                values='Valor_Total'
            ).fillna(0)
            
            # Adicionar totais
            pivot_valor['Total_Geral'] = pivot_valor.sum(axis=1)
            
            st.dataframe(pivot_valor.style.format("R$ {:,.2f}"), use_container_width=True)
            
            # Gráfico de área
            if len(pivot_valor) > 1:
                st.subheader("📊 Evolução dos Valores")
                st.area_chart(pivot_valor.drop('Total_Geral', axis=1))
        
        with tab_qtd:
            # Pivot para quantidades
            pivot_qtd = df_mensal_detalhado.pivot(
                index='Mes_Ano', 
                columns='Situação', 
                values='Qtd_Transacoes'
            ).fillna(0)
            
            # Adicionar totais
            pivot_qtd['Total_Geral'] = pivot_qtd.sum(axis=1)
            
            st.dataframe(pivot_qtd.style.format("{:,.0f}"), use_container_width=True)
            
            # Gráfico de barras
            if len(pivot_qtd) > 1:
                st.subheader("📊 Evolução das Quantidades")
                st.bar_chart(pivot_qtd.drop('Total_Geral', axis=1))
        
        with tab_clientes:
            if 'CPF/CNPJ' in self.df.columns:
                # Pivot para clientes únicos
                pivot_clientes = df_mensal_detalhado.pivot(
                    index='Mes_Ano', 
                    columns='Situação', 
                    values='Qtd_Clientes'
                ).fillna(0)
                
                # Adicionar totais
                pivot_clientes['Total_Geral'] = pivot_clientes.sum(axis=1)
                
                st.dataframe(pivot_clientes.style.format("{:,.0f}"), use_container_width=True)
                
                # Gráfico de linha
                if len(pivot_clientes) > 1:
                    st.subheader("📊 Evolução de Clientes Únicos")
                    st.line_chart(pivot_clientes.drop('Total_Geral', axis=1))
            else:
                st.info("📊 Dados de clientes não disponíveis (coluna CPF/CNPJ ausente)")
    
    def _render_trend_analysis(self):
        """Renderiza análise de tendências"""
        st.subheader("📈 Análise de Tendências")
        
        # Calcular tendências por situação
        df_mensal_total = self.df.groupby(['Mes_Ano', 'Situação'])['Total'].sum().reset_index()
        
        col1, col2 = st.columns(2)
        
        with col1:
            self._render_growth_metrics(df_mensal_total)
        
        with col2:
            self._render_trend_insights(df_mensal_total)
    
    def _render_growth_metrics(self, df_mensal_total):
        """Renderiza métricas de crescimento"""
        st.write("📊 **Métricas de Crescimento**")
        
        # Crescimento total geral
        total_por_mes = df_mensal_total.groupby('Mes_Ano')['Total'].sum()
        total_por_mes = total_por_mes.sort_index()
        
        if len(total_por_mes) >= 2:
            # Crescimento mês a mês
            crescimentos = total_por_mes.pct_change() * 100
            crescimentos = crescimentos.dropna()
            
            # Métricas
            ultimo_crescimento = crescimentos.iloc[-1] if len(crescimentos) > 0 else 0
            crescimento_medio = crescimentos.mean() if len(crescimentos) > 0 else 0
            
            st.metric("📈 Último Crescimento", f"{ultimo_crescimento:.1f}%")
            st.metric("📊 Crescimento Médio", f"{crescimento_medio:.1f}%")
            
            # Volatilidade
            volatilidade = crescimentos.std() if len(crescimentos) > 1 else 0
            st.metric("📉 Volatilidade", f"{volatilidade:.1f}%")
            
            # Tendência geral
            if len(total_por_mes) >= 3:
                # Simples regressão linear (tendência)
                x = range(len(total_por_mes))
                y = total_por_mes.values
                
                # Calcular correlação como proxy para tendência
                correlacao = pd.Series(x).corr(pd.Series(y))
                
                if correlacao > 0.5:
                    st.success("🚀 **Tendência de Crescimento Forte**")
                elif correlacao > 0.2:
                    st.info("📈 **Tendência de Crescimento Moderado**")
                elif correlacao > -0.2:
                    st.warning("📊 **Tendência Estável**")
                else:
                    st.error("📉 **Tendência de Declínio**")
        else:
            st.info("📊 Necessários mais dados para análise de tendências")
    
    def _render_trend_insights(self, df_mensal_total):
        """Renderiza insights de tendência"""
        st.write("💡 **Insights de Tendência**")
        
        insights = []
        
        # Análise por situação
        for situacao in df_mensal_total['Situação'].unique():
            df_situacao = df_mensal_total[df_mensal_total['Situação'] == situacao]
            valores_situacao = df_situacao.groupby('Mes_Ano')['Total'].sum().sort_index()
            
            if len(valores_situacao) >= 2:
                crescimento_situacao = valores_situacao.pct_change().mean() * 100
                
                if abs(crescimento_situacao) > 5:  # Crescimento significativo
                    if crescimento_situacao > 0:
                        insights.append(f"📈 **{situacao}**: Crescimento médio de {crescimento_situacao:.1f}% ao mês")
                    else:
                        insights.append(f"📉 **{situacao}**: Declínio médio de {abs(crescimento_situacao):.1f}% ao mês")
        
        # Análise de sazonalidade básica
        if 'Data de criação' in self.df.columns:
            df_temp = self.df.copy()
            df_temp['Mes'] = df_temp['Data de criação'].dt.month
            df_temp['Dia_Semana'] = df_temp['Data de criação'].dt.day_name()
            
            # Mês mais forte
            vendas_por_mes = df_temp.groupby('Mes')['Total'].sum()
            mes_mais_forte = vendas_por_mes.idxmax()
            
            meses_nomes = {
                1: 'Janeiro', 2: 'Fevereiro', 3: 'Março', 4: 'Abril',
                5: 'Maio', 6: 'Junho', 7: 'Julho', 8: 'Agosto',
                9: 'Setembro', 10: 'Outubro', 11: 'Novembro', 12: 'Dezembro'
            }
            
            insights.append(f"📅 **Sazonalidade**: {meses_nomes.get(mes_mais_forte, mes_mais_forte)} é o mês mais forte")
            
            # Dia da semana mais forte
            vendas_por_dia = df_temp.groupby('Dia_Semana')['Total'].sum()
            dia_mais_forte = vendas_por_dia.idxmax()
            insights.append(f"📆 **Padrão Semanal**: {dia_mais_forte} é o dia mais forte")
        
        # Exibir insights
        for insight in insights:
            st.markdown(f"- {insight}")
        
        if not insights:
            st.info("📊 Continue coletando dados para gerar insights mais precisos.")
    
    def _render_seasonal_analysis(self):
        """Renderiza análise sazonal"""
        if 'Data de criação' not in self.df.columns:
            st.info("📅 Análise sazonal não disponível (coluna 'Data de criação' ausente)")
            return
        
        st.subheader("📅 Análise Sazonal")
        
        df_sazonal = self.df.copy()
        df_sazonal['Mes'] = df_sazonal['Data de criação'].dt.month
        df_sazonal['Trimestre'] = df_sazonal['Data de criação'].dt.quarter
        df_sazonal['Dia_Semana'] = df_sazonal['Data de criação'].dt.day_name()
        df_sazonal['Hora'] = df_sazonal['Data de criação'].dt.hour
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.write("📊 **Distribuição por Mês**")
            vendas_mes = df_sazonal.groupby('Mes')['Total'].sum()
            
            # Criar nomes dos meses
            meses_nomes = {
                1: 'Jan', 2: 'Fev', 3: 'Mar', 4: 'Abr',
                5: 'Mai', 6: 'Jun', 7: 'Jul', 8: 'Ago',
                9: 'Set', 10: 'Out', 11: 'Nov', 12: 'Dez'
            }
            
            vendas_mes.index = vendas_mes.index.map(meses_nomes)
            st.bar_chart(vendas_mes)
            
            # Melhor e pior mês
            melhor_mes = vendas_mes.idxmax()
            pior_mes = vendas_mes.idxmin()
            
            st.metric("🏆 Melhor Mês", melhor_mes, f"R$ {vendas_mes.max():,.2f}")
            st.metric("📉 Pior Mês", pior_mes, f"R$ {vendas_mes.min():,.2f}")
        
        with col2:
            st.write("📊 **Distribuição por Dia da Semana**")
            vendas_dia = df_sazonal.groupby('Dia_Semana')['Total'].sum()
            
            # Ordenar dias da semana
            ordem_dias = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
            vendas_dia = vendas_dia.reindex([dia for dia in ordem_dias if dia in vendas_dia.index])
            
            # Traduzir nomes
            traducao_dias = {
                'Monday': 'Segunda', 'Tuesday': 'Terça', 'Wednesday': 'Quarta',
                'Thursday': 'Quinta', 'Friday': 'Sexta', 'Saturday': 'Sábado', 'Sunday': 'Domingo'
            }
            
            vendas_dia.index = vendas_dia.index.map(traducao_dias)
            st.bar_chart(vendas_dia)
            
            # Melhor e pior dia
            melhor_dia = vendas_dia.idxmax()
            pior_dia = vendas_dia.idxmin()
            
            st.metric("🏆 Melhor Dia", melhor_dia, f"R$ {vendas_dia.max():,.2f}")
            st.metric("📉 Pior Dia", pior_dia, f"R$ {vendas_dia.min():,.2f}")
        
        # Análise por trimestre
        st.write("📊 **Análise Trimestral**")
        vendas_trimestre = df_sazonal.groupby('Trimestre')['Total'].agg(['sum', 'count', 'mean']).round(2)
        vendas_trimestre.columns = ['Valor_Total', 'Qtd_Transacoes', 'Ticket_Medio']
        
        # Renomear índices
        nomes_trimestres = {1: 'Q1', 2: 'Q2', 3: 'Q3', 4: 'Q4'}
        vendas_trimestre.index = vendas_trimestre.index.map(nomes_trimestres)
        
        st.dataframe(vendas_trimestre.style.format({
            'Valor_Total': 'R$ {:,.2f}',
            'Ticket_Medio': 'R$ {:,.2f}',
            'Qtd_Transacoes': '{:,.0f}'
        }), use_container_width=True)
        
        # Insights sazonais
        self._render_seasonal_insights(df_sazonal)
    
    def _render_seasonal_insights(self, df_sazonal):
        """Renderiza insights sazonais"""
        st.write("💡 **Insights Sazonais**")
        
        insights = []
        
        # Análise de concentração por período
        vendas_mes = df_sazonal.groupby('Mes')['Total'].sum()
        vendas_trimestre = df_sazonal.groupby('Trimestre')['Total'].sum()
        vendas_dia = df_sazonal.groupby('Dia_Semana')['Total'].sum()
        
        # Concentração mensal
        mes_top = vendas_mes.idxmax()
        concentracao_mes = (vendas_mes.max() / vendas_mes.sum()) * 100
        
        if concentracao_mes > 20:
            insights.append(f"📊 **Alta concentração** no mês {mes_top} ({concentracao_mes:.1f}% do total)")
        
        # Análise fim de semana vs dias úteis
        dias_uteis = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday']
        fim_semana = ['Saturday', 'Sunday']
        
        vendas_uteis = df_sazonal[df_sazonal['Dia_Semana'].isin(dias_uteis)]['Total'].sum()
        vendas_fim_semana = df_sazonal[df_sazonal['Dia_Semana'].isin(fim_semana)]['Total'].sum()
        
        if vendas_fim_semana > 0:
            ratio_semana = vendas_uteis / vendas_fim_semana
            insights.append(f"📈 Dias úteis representam **{ratio_semana:.1f}x** mais vendas que fins de semana")
        
        # Análise de horários (se disponível)
        if 'Hora' in df_sazonal.columns:
            vendas_hora = df_sazonal.groupby('Hora')['Total'].sum()
            hora_pico = vendas_hora.idxmax()
            insights.append(f"🕐 Horário de pico: **{hora_pico}h**")
            
            # Períodos do dia
            manha = df_sazonal[df_sazonal['Hora'].between(6, 11)]['Total'].sum()
            tarde = df_sazonal[df_sazonal['Hora'].between(12, 17)]['Total'].sum()
            noite = df_sazonal[df_sazonal['Hora'].between(18, 23)]['Total'].sum()
            
            periodo_valores = {'Manhã': manha, 'Tarde': tarde, 'Noite': noite}
            periodo_top = max(periodo_valores.items(), key=lambda x: x[1])[0]
            insights.append(f"🌅 Período mais forte: **{periodo_top}**")
        
        # Análise de variabilidade
        cv_mensal = (vendas_mes.std() / vendas_mes.mean()) * 100
        if cv_mensal > 30:
            insights.append(f"⚡ **Alta variabilidade** entre meses (CV: {cv_mensal:.1f}%)")
        elif cv_mensal < 15:
            insights.append(f"📊 **Distribuição equilibrada** entre meses (CV: {cv_mensal:.1f}%)")
        
        # Exibir insights
        for insight in insights:
            st.markdown(f"- {insight}")
        
        if not insights:
            st.info("📊 Continue coletando dados para gerar insights sazonais mais precisos.")