import streamlit as st
import pandas as pd
from utils import formatar_moeda
from datetime import datetime, timedelta

class DadosDetalhadosTab:
    def __init__(self, df, processor):
        self.df = df
        self.processor = processor
    
    def render(self):
        """Renderiza a aba de dados detalhados"""
        # Verificar se há dados
        if self.df.empty:
            st.warning("⚠️ Nenhum dado disponível para análise.")
            return
        
        # Filtros avançados
        df_filtrado = self._render_filters()
        
        # Estatísticas dos dados filtrados
        self._render_filtered_stats(df_filtrado)
        
        # Tabela de dados
        self._render_data_table(df_filtrado)
        
        # Opções de exportação e análise
        self._render_export_and_analysis(df_filtrado)
    
    def _render_filters(self):
        """Renderiza filtros avançados e retorna dados filtrados"""
        st.subheader("🔍 Filtros Avançados")
        
        # Criar containers para organização
        with st.container():
            col1, col2, col3, col4 = st.columns(4)
            
            # Filtro por situação
            with col1:
                situacoes_disponiveis = ['Todas']
                if 'Situação' in self.df.columns:
                    situacoes_disponiveis += sorted(list(self.df['Situação'].dropna().unique()))
                situacao_selecionada = st.selectbox("📊 Situação:", situacoes_disponiveis, key="filtro_situacao")
            
            # Filtro por método de pagamento
            with col2:
                metodos_disponiveis = ['Todos']
                if 'Paga com' in self.df.columns:
                    metodos_unicos = [m for m in self.df['Paga com'].dropna().unique() if str(m) != 'nan']
                    metodos_disponiveis += ['Não Informado'] + sorted(metodos_unicos)
                metodo_selecionado = st.selectbox("💳 Método:", metodos_disponiveis, key="filtro_metodo")
            
            # Filtro por faixa de valor
            with col3:
                if 'Total' in self.df.columns and self.df['Total'].notna().any():
                    valor_min = float(self.df['Total'].min())
                    valor_max = float(self.df['Total'].max())
                    if valor_min != valor_max:
                        faixa_valor = st.slider(
                            "💰 Faixa de Valor:",
                            valor_min, valor_max,
                            (valor_min, valor_max),
                            key="filtro_valor"
                        )
                    else:
                        faixa_valor = (valor_min, valor_max)
                        st.write(f"💰 Valor único: {formatar_moeda(valor_min)}")
                else:
                    faixa_valor = (0, 0)
                    st.write("💰 Dados de valor indisponíveis")
            
            # Filtro por período
            with col4:
                if 'Data de criação' in self.df.columns:
                    df_temp = self.df.dropna(subset=['Data de criação'])
                    if not df_temp.empty:
                        data_min = df_temp['Data de criação'].min()
                        data_max = df_temp['Data de criação'].max()
                        
                        if pd.notna(data_min) and pd.notna(data_max):
                            # Converter para date se for datetime
                            if hasattr(data_min, 'date'):
                                data_min_date = data_min.date()
                                data_max_date = data_max.date()
                            else:
                                data_min_date = data_min
                                data_max_date = data_max
                            
                            periodo = st.date_input(
                                "📅 Período:",
                                value=(data_min_date, data_max_date),
                                min_value=data_min_date,
                                max_value=data_max_date,
                                key="filtro_periodo"
                            )
                        else:
                            periodo = None
                            st.write("📅 Datas inválidas")
                    else:
                        periodo = None
                        st.write("📅 Sem dados de data")
                else:
                    periodo = None
                    st.write("📅 Coluna de data ausente")
        
        # Filtros adicionais em uma segunda linha
        with st.container():
            col1, col2, col3, col4 = st.columns(4)
            
            # Filtro por cliente
            with col1:
                if 'Nome' in self.df.columns:
                    clientes_unicos = ['Todos'] + sorted(list(self.df['Nome'].dropna().unique()))
                    if len(clientes_unicos) > 1:
                        cliente_selecionado = st.selectbox("👤 Cliente:", clientes_unicos[:100], key="filtro_cliente")  # Limitar a 100 para performance
                    else:
                        cliente_selecionado = 'Todos'
                else:
                    cliente_selecionado = 'Todos'
            
            # Filtro por faixa de taxa
            with col2:
                if 'Taxa' in self.df.columns and self.df['Taxa'].notna().any():
                    taxa_min = float(self.df['Taxa'].min())
                    taxa_max = float(self.df['Taxa'].max())
                    if taxa_min != taxa_max:
                        faixa_taxa = st.slider(
                            "📈 Faixa de Taxa:",
                            taxa_min, taxa_max,
                            (taxa_min, taxa_max),
                            key="filtro_taxa"
                        )
                    else:
                        faixa_taxa = (taxa_min, taxa_max)
                else:
                    faixa_taxa = (0, 0)
            
            # Filtro por número de transações (para clientes recorrentes)
            with col3:
                if 'CPF/CNPJ' in self.df.columns:
                    transacoes_por_cliente = self.df['CPF/CNPJ'].value_counts()
                    min_transacoes = st.number_input(
                        "🔄 Min. Transações:",
                        min_value=1,
                        max_value=int(transacoes_por_cliente.max()) if len(transacoes_por_cliente) > 0 else 1,
                        value=1,
                        key="filtro_min_transacoes"
                    )
                else:
                    min_transacoes = 1
            
            # Filtro de busca de texto
            with col4:
                texto_busca = st.text_input("🔍 Busca por texto:", key="filtro_texto")
        
        # Aplicar todos os filtros
        df_filtrado = self._apply_all_filters(
            situacao_selecionada, metodo_selecionado, faixa_valor, periodo,
            cliente_selecionado, faixa_taxa, min_transacoes, texto_busca
        )
        
        return df_filtrado
    
    def _apply_all_filters(self, situacao, metodo, faixa_valor, periodo, cliente, faixa_taxa, min_transacoes, texto_busca):
        """Aplica todos os filtros ao dataframe"""
        df_filtrado = self.df.copy()
        
        # Filtro por situação
        if situacao != 'Todas' and 'Situação' in df_filtrado.columns:
            df_filtrado = df_filtrado[df_filtrado['Situação'] == situacao]
        
        # Filtro por método de pagamento
        if metodo != 'Todos' and 'Paga com' in df_filtrado.columns:
            if metodo == 'Não Informado':
                df_filtrado = df_filtrado[df_filtrado['Paga com'].isna()]
            else:
                df_filtrado = df_filtrado[df_filtrado['Paga com'] == metodo]
        
        # Filtro por faixa de valor
        if 'Total' in df_filtrado.columns and faixa_valor != (0, 0):
            df_filtrado = df_filtrado[
                (df_filtrado['Total'] >= faixa_valor[0]) & 
                (df_filtrado['Total'] <= faixa_valor[1])
            ]
        
        # Filtro por período
        if periodo and 'Data de criação' in df_filtrado.columns and len(periodo) == 2:
            data_inicio, data_fim = periodo
            # Converter datetime para date para comparação
            df_filtrado['data_temp'] = df_filtrado['Data de criação'].dt.date
            df_filtrado = df_filtrado[
                (df_filtrado['data_temp'] >= data_inicio) &
                (df_filtrado['data_temp'] <= data_fim)
            ]
            df_filtrado = df_filtrado.drop('data_temp', axis=1)
        
        # Filtro por cliente
        if cliente != 'Todos' and 'Nome' in df_filtrado.columns:
            df_filtrado = df_filtrado[df_filtrado['Nome'] == cliente]
        
        # Filtro por faixa de taxa
        if 'Taxa' in df_filtrado.columns and faixa_taxa != (0, 0):
            df_filtrado = df_filtrado[
                (df_filtrado['Taxa'] >= faixa_taxa[0]) & 
                (df_filtrado['Taxa'] <= faixa_taxa[1])
            ]
        
        # Filtro por número mínimo de transações
        if min_transacoes > 1 and 'CPF/CNPJ' in df_filtrado.columns:
            clientes_recorrentes = df_filtrado['CPF/CNPJ'].value_counts()
            clientes_qualificados = clientes_recorrentes[clientes_recorrentes >= min_transacoes].index
            df_filtrado = df_filtrado[df_filtrado['CPF/CNPJ'].isin(clientes_qualificados)]
        
        # Filtro de busca por texto
        if texto_busca and texto_busca.strip():
            texto_busca = texto_busca.strip().lower()
            # Buscar em colunas de texto
            colunas_texto = ['Nome', 'CPF/CNPJ', 'Paga com']
            mascara_busca = pd.Series(False, index=df_filtrado.index)
            
            for col in colunas_texto:
                if col in df_filtrado.columns:
                    mascara_busca |= df_filtrado[col].astype(str).str.lower().str.contains(texto_busca, na=False)
            
            df_filtrado = df_filtrado[mascara_busca]
        
        return df_filtrado
    
    def _render_filtered_stats(self, df_filtrado):
        """Renderiza estatísticas dos dados filtrados"""
        st.subheader("📊 Estatísticas dos Dados Filtrados")
        
        # Primeira linha de métricas
        col1, col2, col3, col4, col5 = st.columns(5)
        
        with col1:
            st.metric("📊 Total Registros", f"{len(df_filtrado):,}")
        
        with col2:
            if 'CPF/CNPJ' in df_filtrado.columns:
                clientes_unicos = df_filtrado['CPF/CNPJ'].nunique()
                st.metric("👥 Clientes Únicos", f"{clientes_unicos:,}")
        
        with col3:
            if 'Total' in df_filtrado.columns:
                valor_total = df_filtrado['Total'].sum()
                st.metric("💰 Valor Total", formatar_moeda(valor_total))
        
        with col4:
            if 'Total' in df_filtrado.columns and len(df_filtrado) > 0:
                ticket_medio = df_filtrado['Total'].mean()
                st.metric("🎫 Ticket Médio", formatar_moeda(ticket_medio))
        
        with col5:
            if 'Taxa' in df_filtrado.columns:
                taxa_total = df_filtrado['Taxa'].sum()
                st.metric("📈 Taxa Total", formatar_moeda(taxa_total))
        
        # Segunda linha de métricas
        if len(df_filtrado) > 0:
            col1, col2, col3, col4, col5 = st.columns(5)
            
            with col1:
                if 'Total' in df_filtrado.columns:
                    valor_max = df_filtrado['Total'].max()
                    st.metric("🔝 Maior Valor", formatar_moeda(valor_max))
            
            with col2:
                if 'Total' in df_filtrado.columns:
                    valor_min = df_filtrado['Total'].min()
                    st.metric("🔻 Menor Valor", formatar_moeda(valor_min))
            
            with col3:
                if 'CPF/CNPJ' in df_filtrado.columns:
                    transacoes_por_cliente = df_filtrado['CPF/CNPJ'].value_counts()
                    max_transacoes = transacoes_por_cliente.max() if len(transacoes_por_cliente) > 0 else 0
                    st.metric("🔄 Max Trans/Cliente", max_transacoes)
            
            with col4:
                if 'Situação' in df_filtrado.columns:
                    situacao_mais_comum = df_filtrado['Situação'].mode()
                    if len(situacao_mais_comum) > 0:
                        st.metric("📈 Status Dominante", situacao_mais_comum.iloc[0])
            
            with col5:
                # Período dos dados filtrados
                if 'Data de criação' in df_filtrado.columns:
                    datas_validas = df_filtrado['Data de criação'].dropna()
                    if len(datas_validas) > 0:
                        periodo_dias = (datas_validas.max() - datas_validas.min()).days
                        st.metric("📅 Período (dias)", periodo_dias)
        
        # Comparação com total se houve filtro
        if len(df_filtrado) != len(self.df):
            percentual_filtrado = (len(df_filtrado) / len(self.df)) * 100
            if len(df_filtrado) == 0:
                st.error("❌ Nenhum registro encontrado com os filtros aplicados.")
            else:
                st.info(f"📊 Exibindo {percentual_filtrado:.1f}% do total de registros ({len(df_filtrado):,} de {len(self.df):,})")
        
        st.markdown("---")
    
    def _render_data_table(self, df_filtrado):
        """Renderiza tabela de dados com paginação"""
        st.subheader("📋 Tabela de Dados")
        
        if df_filtrado.empty:
            st.warning("⚠️ Nenhum registro encontrado com os filtros aplicados.")
            return
        
        # Controles de exibição
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            registros_por_pagina = st.selectbox(
                "📄 Registros por página:",
                [10, 25, 50, 100, 200],
                index=2,
                key="registros_pagina"
            )
        
        with col2:
            # Calcular número de páginas
            total_paginas = (len(df_filtrado) - 1) // registros_por_pagina + 1
            pagina_atual = st.number_input(
                f"📖 Página (1 a {total_paginas}):",
                min_value=1,
                max_value=total_paginas,
                value=1,
                key="pagina_atual"
            )
        
        with col3:
            # Ordenação
            colunas_ordenacao = [''] + list(df_filtrado.columns)
            coluna_ordenacao = st.selectbox("🔄 Ordenar por:", colunas_ordenacao, key="coluna_ordenacao")
        
        with col4:
            if coluna_ordenacao:
                ordem_crescente = st.selectbox("📊 Ordem:", ["Decrescente", "Crescente"], key="ordem")
                ordem_crescente = ordem_crescente == "Crescente"
            else:
                ordem_crescente = False
        
        # Aplicar ordenação se especificada
        if coluna_ordenacao and coluna_ordenacao != '':
            df_ordenado = df_filtrado.sort_values(coluna_ordenacao, ascending=ordem_crescente)
        else:
            df_ordenado = df_filtrado.copy()
        
        # Aplicar paginação
        inicio = (pagina_atual - 1) * registros_por_pagina
        fim = inicio + registros_por_pagina
        df_pagina = df_ordenado.iloc[inicio:fim]
        
        # Controles de colunas a exibir
        with st.expander("🔧 Personalizar Colunas Exibidas"):
            colunas_disponiveis = list(df_filtrado.columns)
            colunas_selecionadas = st.multiselect(
                "Selecione as colunas:",
                colunas_disponiveis,
                default=colunas_disponiveis,
                key="colunas_selecionadas"
            )
            
            if not colunas_selecionadas:
                colunas_selecionadas = colunas_disponiveis
        
        # Filtrar colunas selecionadas
        df_display = df_pagina[colunas_selecionadas].copy()
        
        # Formatar colunas monetárias para exibição
        for col in df_display.columns:
            if col in ['Total', 'Taxa'] and col in df_display.columns:
                df_display[col] = df_display[col].apply(lambda x: formatar_moeda(x) if pd.notna(x) else 'N/A')
            elif col == 'Data de criação' and col in df_display.columns:
                df_display[col] = df_display[col].apply(lambda x: x.strftime('%d/%m/%Y %H:%M') if pd.notna(x) else 'N/A')
            elif col == 'Data do pagamento' and col in df_display.columns:
                df_display[col] = df_display[col].apply(lambda x: x.strftime('%d/%m/%Y %H:%M') if pd.notna(x) else 'N/A')
        
        # Exibir tabela
        st.dataframe(df_display, use_container_width=True, hide_index=True)
        
        # Informações da paginação
        st.caption(f"Mostrando registros {inicio + 1} a {min(fim, len(df_filtrado))} de {len(df_filtrado)} total")
        
        # Navegação rápida
        if total_paginas > 1:
            col1, col2, col3, col4, col5 = st.columns(5)
            
            with col1:
                if st.button("⏮️ Primeira", disabled=pagina_atual == 1):
                    st.session_state.pagina_atual = 1
                    st.rerun()
            
            with col2:
                if st.button("◀️ Anterior", disabled=pagina_atual == 1):
                    st.session_state.pagina_atual = max(1, pagina_atual - 1)
                    st.rerun()
            
            with col3:
                st.write(f"Página {pagina_atual} de {total_paginas}")
            
            with col4:
                if st.button("▶️ Próxima", disabled=pagina_atual == total_paginas):
                    st.session_state.pagina_atual = min(total_paginas, pagina_atual + 1)
                    st.rerun()
            
            with col5:
                if st.button("⏭️ Última", disabled=pagina_atual == total_paginas):
                    st.session_state.pagina_atual = total_paginas
                    st.rerun()
        
        st.markdown("---")
    
    def _render_export_and_analysis(self, df_filtrado):
        """Renderiza opções de exportação e análises"""
        col1, col2 = st.columns(2)
        
        with col1:
            self._render_export_options(df_filtrado)
        
        with col2:
            self._render_quick_analysis(df_filtrado)
    
    def _render_export_options(self, df_filtrado):
        """Renderiza opções de exportação"""
        st.subheader("💾 Opções de Exportação")
        
        if df_filtrado.empty:
            st.info("📊 Nenhum dado para exportar.")
            return
        
        # Preparar dados para exportação (sem formatação)
        df_export = df_filtrado.copy()
        
        # Converter datetime para string se necessário
        for col in df_export.columns:
            if df_export[col].dtype == 'datetime64[ns]':
                df_export[col] = df_export[col].dt.strftime('%d/%m/%Y %H:%M:%S')
        
        col_a, col_b, col_c = st.columns(3)
        
        with col_a:
            # Download CSV
            csv_data = df_export.to_csv(index=False, encoding='utf-8-sig')
            st.download_button(
                label="📥 Download CSV",
                data=csv_data,
                file_name=f"dados_faturamento_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                mime="text/csv",
                help="Baixar dados em formato CSV"
            )
        
        with col_b:
            # Download Excel
            try:
                from io import BytesIO
                excel_buffer = BytesIO()
                
                with pd.ExcelWriter(excel_buffer, engine='openpyxl') as writer:
                    df_export.to_excel(writer, sheet_name='Dados', index=False)
                    
                    # Adicionar estatísticas em uma segunda aba
                    if 'Total' in df_export.columns:
                        stats_df = pd.DataFrame({
                            'Métrica': ['Registros', 'Valor Total', 'Valor Médio', 'Valor Máximo', 'Valor Mínimo'],
                            'Valor': [
                                len(df_export),
                                df_export['Total'].sum(),
                                df_export['Total'].mean(),
                                df_export['Total'].max(),
                                df_export['Total'].min()
                            ]
                        })
                        stats_df.to_excel(writer, sheet_name='Estatísticas', index=False)
                
                excel_data = excel_buffer.getvalue()
                
                st.download_button(
                    label="📊 Download Excel",
                    data=excel_data,
                    file_name=f"dados_faturamento_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                    help="Baixar dados em formato Excel com estatísticas"
                )
            except ImportError:
                st.info("📊 Excel export requer openpyxl")
        
        with col_c:
            # Download JSON
            json_data = df_export.to_json(orient='records', date_format='iso', force_ascii=False)
            st.download_button(
                label="📄 Download JSON",
                data=json_data,
                file_name=f"dados_faturamento_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                mime="application/json",
                help="Baixar dados em formato JSON"
            )
        
        # Informações sobre a exportação
        st.info(f"📊 {len(df_filtrado):,} registros serão exportados")
    
    def _render_quick_analysis(self, df_filtrado):
        """Renderiza análise rápida dos dados"""
        st.subheader("🔍 Análise Rápida")
        
        if df_filtrado.empty:
            st.info("📊 Nenhum dado para analisar.")
            return
        
        # Botões de análise
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("📈 Gerar Resumo Estatístico", key="btn_resumo"):
                self._show_summary_stats(df_filtrado)
        
        with col2:
            if st.button("🔍 Análise de Qualidade", key="btn_qualidade"):
                self._show_data_quality_analysis(df_filtrado)
        
        # Análises automáticas
        with st.expander("📊 Insights Automáticos", expanded=False):
            self._show_automatic_insights(df_filtrado)
    
    def _show_summary_stats(self, df_filtrado):
        """Mostra estatísticas resumidas dos dados filtrados"""
        st.subheader("📈 Resumo Estatístico Detalhado")
        
        # Análise de valores
        if 'Total' in df_filtrado.columns:
            col1, col2 = st.columns(2)
            
            with col1:
                st.write("💰 **Estatísticas de Valores:**")
                stats_valores = df_filtrado['Total'].describe()
                
                for stat, value in stats_valores.items():
                    if stat == 'count':
                        st.write(f"- **{stat.capitalize()}**: {int(value):,}")
                    else:
                        st.write(f"- **{stat.capitalize()}**: {formatar_moeda(value)}")
            
            with col2:
                st.write("📊 **Análise de Distribuição:**")
                
                # Quartis
                q1, q2, q3 = df_filtrado['Total'].quantile([0.25, 0.5, 0.75])
                st.write(f"- **Q1 (25%)**: {formatar_moeda(q1)}")
                st.write(f"- **Q2 (50%)**: {formatar_moeda(q2)}")
                st.write(f"- **Q3 (75%)**: {formatar_moeda(q3)}")
                
                # IQR e outliers
                iqr = q3 - q1
                limite_inferior = q1 - 1.5 * iqr
                limite_superior = q3 + 1.5 * iqr
                
                outliers = df_filtrado[
                    (df_filtrado['Total'] < limite_inferior) | 
                    (df_filtrado['Total'] > limite_superior)
                ]
                
                st.write(f"- **IQR**: {formatar_moeda(iqr)}")
                st.write(f"- **Outliers**: {len(outliers)} ({len(outliers)/len(df_filtrado)*100:.1f}%)")
        
        # Distribuições categóricas
        categoricas = ['Situação', 'Paga com', 'Nome']
        
        for col in categoricas:
            if col in df_filtrado.columns:
                st.write(f"📊 **Distribuição - {col}:**")
                dist = df_filtrado[col].value_counts().head(10)
                
                for valor, count in dist.items():
                    if pd.notna(valor):
                        percentual = (count / len(df_filtrado)) * 100
                        st.write(f"- **{valor}**: {count:,} ({percentual:.1f}%)")
                
                if len(df_filtrado[col].unique()) > 10:
                    st.write(f"- *... e mais {len(df_filtrado[col].unique()) - 10} valores*")
                
                st.write("")
    
    def _show_data_quality_analysis(self, df_filtrado):
        """Mostra análise de qualidade dos dados"""
        st.subheader("🔍 Análise de Qualidade dos Dados")
        
        # Análise de completude
        st.write("📊 **Completude por Coluna:**")
        
        completude_data = []
        for col in df_filtrado.columns:
            total = len(df_filtrado)
            nao_nulos = df_filtrado[col].notna().sum()
            percentual = (nao_nulos / total) * 100 if total > 0 else 0
            
            completude_data.append({
                'Coluna': col,
                'Preenchidos': nao_nulos,
                'Total': total,
                'Completude (%)': percentual
            })
        
        completude_df = pd.DataFrame(completude_data)
        completude_df = completude_df.sort_values('Completude (%)', ascending=False)
        
        # Colorir baseado na completude
        def color_completude(val):
            if val >= 95:
                return 'background-color: #d4edda'  # Verde
            elif val >= 80:
                return 'background-color: #fff3cd'  # Amarelo
            else:
                return 'background-color: #f8d7da'  # Vermelho
        
        styled_df = completude_df.style.applymap(color_completude, subset=['Completude (%)'])
        st.dataframe(styled_df, use_container_width=True, hide_index=True)
        
        # Análise de duplicatas
        st.write("🔍 **Análise de Duplicatas:**")
        
        if 'CPF/CNPJ' in df_filtrado.columns:
            duplicatas_cliente = df_filtrado['CPF/CNPJ'].duplicated().sum()
            st.write(f"- **Clientes com múltiplas transações**: {duplicatas_cliente:,}")
        
        duplicatas_completas = df_filtrado.duplicated().sum()
        st.write(f"- **Registros completamente duplicados**: {duplicatas_completas:,}")
        
        # Análise de consistência
        st.write("✅ **Análise de Consistência:**")
        
        issues = []
        
        # Verificar valores negativos em campos monetários
        for col in ['Total', 'Taxa']:
            if col in df_filtrado.columns:
                negativos = (df_filtrado[col] < 0).sum()
                if negativos > 0:
                    issues.append(f"Valores negativos em {col}: {negativos:,}")
        
        # Verificar datas inconsistentes
        if all(col in df_filtrado.columns for col in ['Data de criação', 'Data do pagamento']):
            df_temp = df_filtrado.dropna(subset=['Data de criação', 'Data do pagamento'])
            if not df_temp.empty:
                datas_inconsistentes = (df_temp['Data do pagamento'] < df_temp['Data de criação']).sum()
                if datas_inconsistentes > 0:
                    issues.append(f"Pagamentos antes da criação: {datas_inconsistentes:,}")
        
        # Verificar situações inconsistentes
        if 'Situação' in df_filtrado.columns:
            situacoes_validas = ['Paga', 'Pendente', 'Expirado', 'paga', 'pendente', 'expirado']
            situacoes_invalidas = ~df_filtrado['Situação'].isin(situacoes_validas)
            if situacoes_invalidas.any():
                count_invalidas = situacoes_invalidas.sum()
                issues.append(f"Situações não padronizadas: {count_invalidas:,}")
        
        # Verificar valores zerados
        if 'Total' in df_filtrado.columns:
            valores_zero = (df_filtrado['Total'] == 0).sum()
            if valores_zero > 0:
                issues.append(f"Transações com valor zero: {valores_zero:,}")
        
        if issues:
            for issue in issues:
                st.warning(f"⚠️ {issue}")
        else:
            st.success("✅ Nenhum problema de consistência identificado")
        
        # Score de qualidade geral
        score_completude = completude_df['Completude (%)'].mean()
        score_duplicatas = max(0, 100 - (duplicatas_completas / len(df_filtrado) * 100))
        score_consistencia = max(0, 100 - (len(issues) * 10))
        
        score_geral = (score_completude + score_duplicatas + score_consistencia) / 3
        
        st.write("🎯 **Score de Qualidade Geral:**")
        st.progress(score_geral / 100)
        st.write(f"**{score_geral:.1f}/100**")
        
        if score_geral >= 90:
            st.success("🏆 Excelente qualidade de dados!")
        elif score_geral >= 75:
            st.info("👍 Boa qualidade de dados")
        elif score_geral >= 60:
            st.warning("⚠️ Qualidade moderada - considere melhorias")
        else:
            st.error("🚨 Qualidade baixa - requer atenção imediata")
    
    def _show_automatic_insights(self, df_filtrado):
        """Mostra insights automáticos dos dados"""
        st.write("💡 **Insights Automáticos:**")
        
        insights = []
        
        # Insights sobre volume de dados
        if len(df_filtrado) > 1000:
            insights.append("📊 **Grande volume de dados** - análises estatísticas são mais confiáveis")
        elif len(df_filtrado) < 100:
            insights.append("⚠️ **Volume pequeno de dados** - interpretações devem ser cautelosas")
        
        # Insights sobre clientes
        if 'CPF/CNPJ' in df_filtrado.columns:
            clientes_unicos = df_filtrado['CPF/CNPJ'].nunique()
            transacoes_por_cliente = df_filtrado['CPF/CNPJ'].value_counts()
            
            if clientes_unicos > 0:
                media_transacoes = len(df_filtrado) / clientes_unicos
                
                if media_transacoes > 3:
                    insights.append(f"🔄 **Alta recorrência** - {media_transacoes:.1f} transações por cliente em média")
                elif media_transacoes < 1.5:
                    insights.append(f"👤 **Baixa recorrência** - maioria dos clientes faz apenas 1 transação")
                
                # Cliente mais ativo
                cliente_top = transacoes_por_cliente.index[0]
                max_transacoes = transacoes_por_cliente.iloc[0]
                if max_transacoes > 10:
                    insights.append(f"🏆 **Cliente super ativo** - {max_transacoes} transações do mesmo cliente")
        
        # Insights sobre valores
        if 'Total' in df_filtrado.columns:
            valores = df_filtrado['Total']
            cv = (valores.std() / valores.mean()) * 100 if valores.mean() > 0 else 0
            
            if cv > 100:
                insights.append(f"📈 **Alta variabilidade** nos valores (CV: {cv:.1f}%)")
            elif cv < 30:
                insights.append(f"📊 **Valores homogêneos** (CV: {cv:.1f}%)")
            
            # Concentração de valores
            top_10_percent = int(len(valores) * 0.1)
            if top_10_percent > 0:
                concentracao = valores.nlargest(top_10_percent).sum() / valores.sum() * 100
                if concentracao > 50:
                    insights.append(f"💎 **Concentração alta** - top 10% representa {concentracao:.1f}% do valor")
        
        # Insights sobre situações
        if 'Situação' in df_filtrado.columns:
            situacao_dist = df_filtrado['Situação'].value_counts(normalize=True) * 100
            
            for situacao, percent in situacao_dist.items():
                if situacao.lower() == 'paga' and percent > 80:
                    insights.append(f"✅ **Alta taxa de conversão** - {percent:.1f}% pagas")
                elif situacao.lower() == 'expirado' and percent > 20:
                    insights.append(f"⚠️ **Muitas transações expiradas** - {percent:.1f}%")
                elif situacao.lower() == 'pendente' and percent > 30:
                    insights.append(f"⏳ **Muitas pendências** - {percent:.1f}% ainda pendentes")
        
        # Insights sobre métodos de pagamento
        if 'Paga com' in df_filtrado.columns:
            metodos = df_filtrado['Paga com'].value_counts()
            if len(metodos) > 0:
                metodo_dominante = metodos.index[0]
                percentual_dominante = (metodos.iloc[0] / len(df_filtrado)) * 100
                
                if percentual_dominante > 70:
                    insights.append(f"💳 **Método dominante** - {percentual_dominante:.1f}% usa {metodo_dominante}")
                elif len(metodos) > 5:
                    insights.append(f"💳 **Diversidade de métodos** - {len(metodos)} métodos diferentes")
        
        # Insights temporais
        if 'Data de criação' in df_filtrado.columns:
            datas_validas = df_filtrado['Data de criação'].dropna()
            if len(datas_validas) > 1:
                periodo = (datas_validas.max() - datas_validas.min()).days
                
                if periodo > 365:
                    insights.append(f"📅 **Dados históricos** - período de {periodo} dias")
                elif periodo < 30:
                    insights.append(f"📅 **Período recente** - apenas {periodo} dias")
                
                # Análise de frequência
                if periodo > 0:
                    frequencia_diaria = len(datas_validas) / periodo
                    if frequencia_diaria > 10:
                        insights.append(f"🚀 **Alto volume diário** - {frequencia_diaria:.1f} transações/dia")
                    elif frequencia_diaria < 1:
                        insights.append(f"📉 **Baixo volume diário** - {frequencia_diaria:.1f} transações/dia")
        
        # Insights sobre taxas
        if 'Taxa' in df_filtrado.columns:
            taxas = df_filtrado['Taxa'].dropna()
            if len(taxas) > 0 and 'Total' in df_filtrado.columns:
                valores_correspondentes = df_filtrado.loc[taxas.index, 'Total']
                if len(valores_correspondentes) > 0:
                    percentual_taxa_medio = (taxas / valores_correspondentes * 100).mean()
                    
                    if percentual_taxa_medio > 10:
                        insights.append(f"💰 **Taxa alta** - {percentual_taxa_medio:.1f}% em média")
                    elif percentual_taxa_medio < 3:
                        insights.append(f"💰 **Taxa baixa** - {percentual_taxa_medio:.1f}% em média")
        
        # Exibir insights
        if insights:
            for insight in insights:
                st.markdown(f"- {insight}")
        else:
            st.info("📊 Continue coletando dados para gerar insights mais precisos")
        
        # Recomendações baseadas nos insights
        st.write("🎯 **Recomendações:**")
        
        recomendacoes = []
        
        # Baseado na qualidade dos dados
        if 'CPF/CNPJ' in df_filtrado.columns:
            cpf_faltando = df_filtrado['CPF/CNPJ'].isna().sum()
            if cpf_faltando > len(df_filtrado) * 0.1:
                recomendacoes.append("🔧 Melhorar coleta de dados de clientes (CPF/CNPJ)")
        
        # Baseado na conversão
        if 'Situação' in df_filtrado.columns:
            situacao_dist = df_filtrado['Situação'].value_counts(normalize=True)
            if 'expirado' in situacao_dist.index or 'Expirado' in situacao_dist.index:
                expirado_key = 'expirado' if 'expirado' in situacao_dist.index else 'Expirado'
                if situacao_dist[expirado_key] > 0.15:
                    recomendacoes.append("⏰ Revisar prazos de vencimento para reduzir expirados")
        
        # Baseado na recorrência
        if 'CPF/CNPJ' in df_filtrado.columns and len(df_filtrado) > 0:
            transacoes_por_cliente = df_filtrado['CPF/CNPJ'].value_counts()
            clientes_unicos = len(transacoes_por_cliente)
            if clientes_unicos > 0:
                recorrencia = len(df_filtrado) / clientes_unicos
                if recorrencia < 2:
                    recomendacoes.append("🎯 Implementar estratégias de retenção de clientes")
        
        # Baseado na concentração
        if 'Total' in df_filtrado.columns and len(df_filtrado) > 10:
            top_10_percent = int(len(df_filtrado) * 0.1)
            if top_10_percent > 0:
                concentracao = df_filtrado['Total'].nlargest(top_10_percent).sum() / df_filtrado['Total'].sum()
                if concentracao > 0.6:
                    recomendacoes.append("⚖️ Diversificar base de clientes para reduzir concentração")
        
        if recomendacoes:
            for rec in recomendacoes:
                st.markdown(f"- {rec}")
        else:
            st.success("✅ Dados em boa forma - continue monitorando!")