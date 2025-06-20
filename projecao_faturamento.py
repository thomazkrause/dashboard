import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import numpy as np

class ProjecaoFaturamento:
    def __init__(self, df):
        self.df = df
        self.ano_atual = 2025
        
    def calcular_mrr_historico(self):
        """Calcula o MRR (Monthly Recurring Revenue) histórico baseado nos dados reais"""
        if self.df.empty:
            return pd.DataFrame()
        
        # Filtrar transações pagas OU transferências
        condicao_paga = self.df['Situação'].str.lower() == 'paga'
        
        if 'Paga com' in self.df.columns:
            condicao_transferencia = self.df['Paga com'].str.lower().str.contains('transferência', na=False)
            df_mrr = self.df[condicao_paga | condicao_transferencia].copy()
        else:
            df_mrr = self.df[condicao_paga].copy()
        
        if df_mrr.empty:
            return pd.DataFrame()
        
        if 'Data de criação' in df_mrr.columns:
            df_mrr['Data de criação'] = pd.to_datetime(df_mrr['Data de criação'], errors='coerce')
            df_mrr = df_mrr[df_mrr['Data de criação'].dt.year == self.ano_atual]
            
            if df_mrr.empty:
                return pd.DataFrame()
            
            df_mrr['Mes_Ano'] = df_mrr['Data de criação'].dt.to_period('M')
            mrr_historico = df_mrr.groupby('Mes_Ano')['Total'].sum().reset_index()
            mrr_historico['Mes_Ano_Str'] = mrr_historico['Mes_Ano'].astype(str)
            mrr_historico['Mes'] = mrr_historico['Mes_Ano'].dt.month
            mrr_historico['Ano'] = mrr_historico['Mes_Ano'].dt.year
            
            # Ordenar por mês para garantir ordem correta
            mrr_historico = mrr_historico.sort_values('Mes')
            
            return mrr_historico
        
        return pd.DataFrame()
    
    def calcular_mrr_atual(self, mrr_historico):
        """Calcula o MRR atual baseado no último mês com dados"""
        if mrr_historico.empty:
            return 10000
        
        # Pegar o último valor disponível (mais recente)
        ultimo_mrr = mrr_historico['Total'].iloc[-1]
        return ultimo_mrr
    
    def get_ultimo_mes_com_dados(self, mrr_historico):
        """Retorna o último mês que tem dados reais"""
        if mrr_historico.empty:
            return datetime.now().month - 1  # Mês anterior ao atual
        
        return mrr_historico['Mes'].iloc[-1]
    
    def get_estatisticas_mrr(self):
        """Retorna estatísticas detalhadas sobre o MRR calculado"""
        if self.df.empty:
            return {}
        
        total_transacoes = len(self.df)
        transacoes_pagas = len(self.df[self.df['Situação'].str.lower() == 'paga'])
        
        transacoes_transferencia = 0
        transacoes_mrr_total = transacoes_pagas
        
        if 'Paga com' in self.df.columns:
            mask_transferencia = self.df['Paga com'].str.lower().str.contains('transferência', na=False)
            transacoes_transferencia = len(self.df[mask_transferencia])
            
            mask_paga = self.df['Situação'].str.lower() == 'paga'
            transacoes_mrr_total = len(self.df[mask_paga | mask_transferencia])
        
        return {
            'total_transacoes': total_transacoes,
            'transacoes_pagas': transacoes_pagas,
            'transacoes_transferencia': transacoes_transferencia,
            'transacoes_mrr_total': transacoes_mrr_total,
            'percentual_mrr': (transacoes_mrr_total / total_transacoes * 100) if total_transacoes > 0 else 0
        }
    
    def gerar_projecao_anual(self, mrr_historico, taxa_crescimento_mensal):
        """Gera a projeção anual completa (histórico + projeção)"""
        meses_2025 = []
        nomes_meses = ['Jan', 'Fev', 'Mar', 'Abr', 'Mai', 'Jun', 
                      'Jul', 'Ago', 'Set', 'Out', 'Nov', 'Dez']
        
        for mes in range(1, 13):
            data_mes = datetime(self.ano_atual, mes, 1)
            periodo = pd.Period(year=self.ano_atual, month=mes, freq='M')
            meses_2025.append({
                'Mes': mes,
                'Ano': self.ano_atual,
                'Mes_Ano': periodo,
                'Mes_Ano_Str': f"{self.ano_atual}-{mes:02d}",
                'Data': data_mes,
                'Nome_Mes': nomes_meses[mes-1]
            })
        
        df_completo = pd.DataFrame(meses_2025)
        
        # Mergir com dados históricos
        if not mrr_historico.empty:
            df_completo = df_completo.merge(
                mrr_historico[['Mes', 'Ano', 'Total']], 
                on=['Mes', 'Ano'], 
                how='left'
            )
        else:
            df_completo['Total'] = np.nan
        
        # Calcular MRR base para projeção
        mrr_base = self.calcular_mrr_atual(mrr_historico)
        ultimo_mes_dados = self.get_ultimo_mes_com_dados(mrr_historico)
        
        # **DEBUG EXPANDIDO**
        with st.expander("🔍 **Debug Detalhado do Cálculo MRR**", expanded=True):
            st.write("### 📊 **Informações Base:**")
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.metric("💰 MRR Base", f"R$ {mrr_base:,.2f}")
            with col2:
                st.metric("📅 Último Mês c/ Dados", nomes_meses[ultimo_mes_dados-1] if ultimo_mes_dados <= 12 else "N/A")
            with col3:
                st.metric("📈 Taxa Crescimento", f"{taxa_crescimento_mensal}%")
            
            st.write("### 📋 **Dados Históricos Encontrados:**")
            if not mrr_historico.empty:
                historico_debug = mrr_historico.copy()
                historico_debug['Mes_Nome'] = historico_debug['Mes'].apply(lambda x: nomes_meses[x-1])
                historico_debug['Total_Formatado'] = historico_debug['Total'].apply(lambda x: f"R$ {x:,.2f}")
                st.dataframe(
                    historico_debug[['Mes_Nome', 'Total_Formatado']].rename(columns={'Mes_Nome': 'Mês', 'Total_Formatado': 'MRR Real'}),
                    use_container_width=True,
                    hide_index=True
                )
            else:
                st.info("❌ Nenhum dado histórico encontrado")
            
            st.write("### 🧮 **Cálculo da Projeção (Passo a Passo):**")
            st.write("**Fórmula:** `MRR_Projetado = MRR_Base × (1 + Taxa/100)^Meses_Crescimento`")
            st.write("")
        
        # Lista para armazenar informações de debug
        debug_calculos = []
        
        # Preencher projeções
        for idx, row in df_completo.iterrows():
            mes_nome = nomes_meses[row['Mes']-1]
            
            if pd.isna(row['Total']):
                if row['Mes'] <= ultimo_mes_dados:
                    # Mês passado sem dados
                    df_completo.at[idx, 'Total'] = 0
                    df_completo.at[idx, 'Tipo'] = 'Histórico'
                    debug_calculos.append({
                        'Mês': mes_nome,
                        'Tipo': 'Histórico (sem dados)',
                        'Valor': 'R$ 0,00',
                        'Cálculo': 'Mês anterior sem dados históricos',
                        'Fórmula': 'N/A'
                    })
                else:
                    # Projeção: calcular crescimento a partir do último mês com dados
                    meses_crescimento = row['Mes'] - ultimo_mes_dados
                    
                    if mrr_base > 0:
                        valor_projetado = mrr_base * ((1 + taxa_crescimento_mensal/100) ** meses_crescimento)
                    else:
                        valor_projetado = 10000 * ((1 + taxa_crescimento_mensal/100) ** meses_crescimento)
                    
                    df_completo.at[idx, 'Total'] = valor_projetado
                    df_completo.at[idx, 'Tipo'] = 'Projeção'
                    
                    # Calcular fator de crescimento para debug
                    fator_crescimento = (1 + taxa_crescimento_mensal/100) ** meses_crescimento
                    
                    debug_calculos.append({
                        'Mês': mes_nome,
                        'Tipo': 'Projeção',
                        'Valor': f'R$ {valor_projetado:,.2f}',
                        'Cálculo': f'{meses_crescimento} meses após {nomes_meses[ultimo_mes_dados-1]}',
                        'Fórmula': f'{mrr_base:,.2f} × (1.{taxa_crescimento_mensal:02.0f})^{meses_crescimento} = {mrr_base:,.2f} × {fator_crescimento:.6f}'
                    })
            else:
                # Dados históricos reais
                df_completo.at[idx, 'Tipo'] = 'Histórico'
                debug_calculos.append({
                    'Mês': mes_nome,
                    'Tipo': 'Histórico (real)',
                    'Valor': f'R$ {row["Total"]:,.2f}',
                    'Cálculo': 'Dados reais do sistema',
                    'Fórmula': 'Soma das transações MRR do mês'
                })
        
        # Mostrar tabela de debug dentro do expander
        with st.expander("🔍 **Debug Detalhado do Cálculo MRR**", expanded=True):
            st.write("### 📊 **Detalhamento Completo por Mês:**")
            
            # Criar DataFrame para o debug
            df_debug = pd.DataFrame(debug_calculos)
            
            # Aplicar cores baseadas no tipo
            def highlight_tipo(row):
                if 'Histórico (real)' in row['Tipo']:
                    return ['background-color: #d4edda'] * len(row)  # Verde claro
                elif 'Projeção' in row['Tipo']:
                    return ['background-color: #fff3cd'] * len(row)  # Amarelo claro
                else:
                    return ['background-color: #f8d7da'] * len(row)  # Vermelho claro (sem dados)
            
            styled_debug = df_debug.style.apply(highlight_tipo, axis=1)
            st.dataframe(styled_debug, use_container_width=True, hide_index=True)
            
            st.write("### 🎯 **Legenda das Cores:**")
            col1, col2, col3 = st.columns(3)
            with col1:
                st.success("🟢 **Verde**: Dados históricos reais")
            with col2:
                st.warning("🟡 **Amarelo**: Projeções calculadas")
            with col3:
                st.error("🔴 **Vermelho**: Meses sem dados")
            
            st.write("### 📈 **Validação dos Cálculos:**")
            
            # Mostrar alguns exemplos de validação
            projecoes = [calc for calc in debug_calculos if calc['Tipo'] == 'Projeção']
            if projecoes:
                st.write("**Exemplos de Validação Manual:**")
                for i, proj in enumerate(projecoes[:3]):  # Mostrar apenas os 3 primeiros
                    st.code(f"""
Mês: {proj['Mês']}
{proj['Fórmula']}
Resultado: {proj['Valor']}
                    """)
            
            # Resumo final
            total_historico = len([c for c in debug_calculos if 'Histórico (real)' in c['Tipo']])
            total_projecoes = len([c for c in debug_calculos if 'Projeção' in c['Tipo']])
            total_sem_dados = len([c for c in debug_calculos if 'sem dados' in c['Tipo']])
            
            st.write("### 📊 **Resumo:**")
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("📅 Meses c/ Dados Reais", total_historico)
            with col2:
                st.metric("🔮 Meses Projetados", total_projecoes)
            with col3:
                st.metric("❌ Meses sem Dados", total_sem_dados)
        
        return df_completo
    
    def criar_grafico_projecao(self, df_projecao):
        """Cria o gráfico de projeção de faturamento"""
        fig = go.Figure()
        
        df_historico = df_projecao[df_projecao['Tipo'] == 'Histórico']
        df_projecao_futura = df_projecao[df_projecao['Tipo'] == 'Projeção']
        
        if not df_historico.empty:
            fig.add_trace(go.Scatter(
                x=df_historico['Nome_Mes'],
                y=df_historico['Total'],
                mode='lines+markers',
                name='MRR Real (Paga + Transferência)',
                line=dict(color='#2E8B57', width=3),
                marker=dict(size=8, color='#2E8B57'),
                hovertemplate='<b>%{x}</b><br>Valor: R$ %{y:,.2f}<br>Status: Real<extra></extra>'
            ))
        
        if not df_projecao_futura.empty:
            fig.add_trace(go.Scatter(
                x=df_projecao_futura['Nome_Mes'],
                y=df_projecao_futura['Total'],
                mode='lines+markers',
                name='Projeção MRR',
                line=dict(color='#FF8C00', width=3, dash='dash'),
                marker=dict(size=8, color='#FF8C00'),
                hovertemplate='<b>%{x}</b><br>Valor: R$ %{y:,.2f}<br>Status: Projeção<extra></extra>'
            ))
        
        fig.update_layout(
            title=f'📈 Projeção de MRR (Monthly Recurring Revenue) - {self.ano_atual}',
            xaxis_title='Mês',
            yaxis_title='MRR (R$)',
            height=500,
            hovermode='x unified',
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=1.02,
                xanchor="right",
                x=1
            ),
            yaxis=dict(
                tickformat=',.0f'
            )
        )
        
        return fig
    
    def mostrar_interface(self):
        """Mostra a interface completa da projeção de faturamento"""
        st.header("📊 Projeção de MRR (Monthly Recurring Revenue) 2025")
        
        mrr_historico = self.calcular_mrr_historico()
        stats_mrr = self.get_estatisticas_mrr()
        
        with st.expander("ℹ️ Critérios para Cálculo do MRR"):
            col1, col2 = st.columns(2)
            
            with col1:
                st.info("""
                **📋 Transações incluídas no MRR:**
                - ✅ Situação = "Paga" 
                - 🏦 Método = "Transferência" (qualquer situação)
                
                **🎯 Objetivo:** Capturar receita recorrente real e comprometida
                """)
            
            with col2:
                if stats_mrr:
                    st.metric("📊 Total de Transações", stats_mrr['total_transacoes'])
                    st.metric("💰 Transações no MRR", stats_mrr['transacoes_mrr_total'])
                    st.metric("📈 % MRR do Total", f"{stats_mrr['percentual_mrr']:.1f}%")
        
        if mrr_historico.empty:
            st.warning("⚠️ Nenhum dado de MRR encontrado para 2025. A projeção será baseada em valores estimados.")
        else:
            st.success(f"✅ {len(mrr_historico)} meses com dados de MRR encontrados.")
        
        col1, col2, col3 = st.columns([2, 1, 1])
        
        with col1:
            st.subheader("⚙️ Configurações da Projeção")
        
        with col2:
            taxa_crescimento = st.number_input(
                "📈 Taxa de Crescimento Mensal (%)",
                min_value=-50.0,
                max_value=100.0,
                value=5.0,
                step=0.1,
                format="%.1f",
                help="Taxa de crescimento mensal aplicada na projeção do MRR"
            )
        
        with col3:
            if st.button("🔄 Atualizar Projeção", type="primary"):
                st.rerun()
        
        # Gerar projeção (aqui o debug será mostrado)
        df_projecao = self.gerar_projecao_anual(mrr_historico, taxa_crescimento)
        
        # Calcular métricas
        mrr_real_acumulado = df_projecao[df_projecao['Tipo'] == 'Histórico']['Total'].sum()
        mrr_projetado = df_projecao[df_projecao['Tipo'] == 'Projeção']['Total'].sum()
        mrr_total_ano = mrr_real_acumulado + mrr_projetado
        
        mrr_atual = self.calcular_mrr_atual(mrr_historico)
        
        # Mostrar KPIs
        st.subheader("📊 Resumo da Projeção MRR")
        col1, col2, col3, col4, col5 = st.columns(5)
        
        with col1:
            st.metric(
                "💰 MRR Real Acumulado (YTD)",
                f"R$ {mrr_real_acumulado:,.2f}",
                help="MRR real acumulado no ano (Paga + Transferência)"
            )
        
        with col2:
            st.metric(
                "🔮 Projeção MRR Restante",
                f"R$ {mrr_projetado:,.2f}",
                help="Projeção de MRR para os meses restantes do ano"
            )
        
        with col3:
            st.metric(
                "🎯 MRR Total Projetado 2025",
                f"R$ {mrr_total_ano:,.2f}",
                help="MRR total projetado para o ano"
            )
        
        with col4:
            st.metric(
                "📈 MRR Base",
                f"R$ {mrr_atual:,.2f}",
                help="MRR base usado para projeção"
            )
        
        with col5:
            if mrr_real_acumulado > 0:
                crescimento_anual = ((mrr_total_ano / mrr_real_acumulado) - 1) * 100
            else:
                crescimento_anual = 0
            st.metric(
                "📊 Crescimento Anual",
                f"{crescimento_anual:.1f}%",
                help="Crescimento anual estimado do MRR"
            )
        
        # Gráfico principal
        fig = self.criar_grafico_projecao(df_projecao)
        st.plotly_chart(fig, use_container_width=True)
        
        # Tabela detalhada
        st.subheader("📋 Detalhamento Mensal do MRR")
        
        df_tabela = df_projecao.copy()
        df_tabela['Total_Formatado'] = df_tabela['Total'].apply(lambda x: f"R$ {x:,.2f}")
        df_tabela['Status'] = df_tabela['Tipo'].apply(
            lambda x: "✅ Real" if x == "Histórico" else "🔮 Projeção"
        )
        
        df_exibicao = df_tabela[['Nome_Mes', 'Total_Formatado', 'Status']].copy()
        df_exibicao.columns = ['Mês', 'MRR', 'Status']
        
        mes_atual_nome = datetime.now().strftime('%b')
        
        def highlight_current_month(row):
            if row['Mês'] == mes_atual_nome:
                return ['background-color: #e3f2fd'] * len(row)
            return [''] * len(row)
        
        styled_df = df_exibicao.style.apply(highlight_current_month, axis=1)
        st.dataframe(styled_df, use_container_width=True, hide_index=True)
        
        # Informações adicionais
        st.subheader("ℹ️ Informações da Projeção")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.info(f"""
            **📅 Período Base:** Janeiro a Dezembro {self.ano_atual}
            
            **📊 Metodologia MRR:**
            - ✅ Transações com situação "Paga"
            - 🏦 Transações com método "Transferência" 
            - 💰 MRR atual: R$ {mrr_atual:,.2f}
            - 📈 Taxa de crescimento mensal: {taxa_crescimento:.1f}%
            """)
        
        with col2:
            meses_com_dados = len(mrr_historico) if not mrr_historico.empty else 0
            mes_atual = datetime.now().month
            meses_projetados = 12 - mes_atual
            
            st.info(f"""
            **🔢 Estatísticas:**
            - Meses com dados reais: {meses_com_dados}
            - Meses projetados: {meses_projetados}
            - Transações no MRR: {stats_mrr.get('transacoes_mrr_total', 0)}
            - Última atualização: {datetime.now().strftime('%d/%m/%Y %H:%M')}
            """)
        
        # Cenários alternativos
        if st.checkbox("🎯 Ver Cenários Alternativos de MRR"):
            st.subheader("🔄 Análise de Cenários MRR")
            
            cenarios = {
                'Conservador': taxa_crescimento - 2,
                'Atual': taxa_crescimento,
                'Otimista': taxa_crescimento + 3
            }
            
            resultados_cenarios = {}
            
            for nome_cenario, taxa_cenario in cenarios.items():
                df_cenario = self.gerar_projecao_anual(mrr_historico, taxa_cenario)
                total_cenario = df_cenario['Total'].sum()
                resultados_cenarios[nome_cenario] = total_cenario
            
            # Mostrar comparação de cenários
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.metric(
                    "🐌 Cenário Conservador",
                    f"R$ {resultados_cenarios['Conservador']:,.2f}",
                    f"{cenarios['Conservador']:.1f}% a.m."
                )
            
            with col2:
                st.metric(
                    "📊 Cenário Atual",
                    f"R$ {resultados_cenarios['Atual']:,.2f}",
                    f"{cenarios['Atual']:.1f}% a.m."
                )
            
            with col3:
                st.metric(
                    "🚀 Cenário Otimista",
                    f"R$ {resultados_cenarios['Otimista']:,.2f}",
                    f"{cenarios['Otimista']:.1f}% a.m."
                )