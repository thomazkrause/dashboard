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
        
    def get_mes_atual(self):
        """Retorna o mês atual"""
        return datetime.now().month
    
    def get_ultimo_mes_encerrado(self):
        """Retorna o último mês que já foi encerrado (mês anterior ao atual)"""
        mes_atual = self.get_mes_atual()
        return mes_atual - 1 if mes_atual > 1 else 12
        
    def calcular_faturamento_historico(self):
        """Calcula o faturamento bruto histórico baseado em todas as transações pagas"""
        if self.df.empty:
            return pd.DataFrame()
        
        # Filtrar apenas transações pagas
        df_pagos = self.df[self.df['Situação'].str.lower() == 'paga'].copy()
        
        if df_pagos.empty:
            return pd.DataFrame()
        
        if 'Data de criação' in df_pagos.columns:
            df_pagos['Data de criação'] = pd.to_datetime(df_pagos['Data de criação'], errors='coerce')
            df_pagos = df_pagos[df_pagos['Data de criação'].dt.year == self.ano_atual]
            
            if df_pagos.empty:
                return pd.DataFrame()
            
            # Agrupar por mês e somar o faturamento bruto
            df_pagos['Mes_Ano'] = df_pagos['Data de criação'].dt.to_period('M')
            faturamento_historico = df_pagos.groupby('Mes_Ano')['Total'].sum().reset_index()
            faturamento_historico['Mes_Ano_Str'] = faturamento_historico['Mes_Ano'].astype(str)
            faturamento_historico['Mes'] = faturamento_historico['Mes_Ano'].dt.month
            faturamento_historico['Ano'] = faturamento_historico['Mes_Ano'].dt.year
            
            # Ordenar por mês para garantir ordem correta
            faturamento_historico = faturamento_historico.sort_values('Mes')
            
            return faturamento_historico
        
        return pd.DataFrame()
    
    def calcular_faturamento_base(self, faturamento_historico):
        """Calcula o faturamento base para projeção (último mês encerrado)"""
        if faturamento_historico.empty:
            return 50000  # Valor padrão para demonstração quando não há dados
        
        ultimo_mes_encerrado = self.get_ultimo_mes_encerrado()
        
        # Filtrar apenas dados até o último mês encerrado
        dados_ate_mes_encerrado = faturamento_historico[faturamento_historico['Mes'] <= ultimo_mes_encerrado]
        
        if dados_ate_mes_encerrado.empty:
            # Se não há dados até o mês encerrado, usar o último disponível
            ultimo_faturamento = faturamento_historico['Total'].iloc[-1]
        else:
            # Usar o último mês encerrado com dados
            ultimo_faturamento = dados_ate_mes_encerrado['Total'].iloc[-1]
        
        return ultimo_faturamento
    
    def calcular_faturamento_mes_atual(self, faturamento_historico):
        """Calcula faturamento atual do mês corrente e faz projeção"""
        mes_atual = self.get_mes_atual()
        ultimo_mes_encerrado = self.get_ultimo_mes_encerrado()
        
        # Faturamento atual do mês corrente (até hoje)
        faturamento_atual_mes = 0
        if not faturamento_historico.empty:
            dados_mes_atual = faturamento_historico[faturamento_historico['Mes'] == mes_atual]
            if not dados_mes_atual.empty:
                faturamento_atual_mes = dados_mes_atual['Total'].iloc[0]
        
        # Faturamento do mês anterior (base para comparação)
        faturamento_mes_anterior = 0
        if not faturamento_historico.empty:
            dados_mes_anterior = faturamento_historico[faturamento_historico['Mes'] == ultimo_mes_encerrado]
            if not dados_mes_anterior.empty:
                faturamento_mes_anterior = dados_mes_anterior['Total'].iloc[0]
        
        # Calcular diferença (novas receitas)
        diferenca_receitas = faturamento_atual_mes - faturamento_mes_anterior if faturamento_mes_anterior > 0 else 0
        
        # Projeção para o mês atual (baseada no crescimento observado)
        if faturamento_mes_anterior > 0 and diferenca_receitas > 0:
            # Se há crescimento, projeta continuidade
            projecao_mes_atual = faturamento_mes_anterior + diferenca_receitas
        elif faturamento_mes_anterior > 0:
            # Se não há crescimento significativo, usa o mês anterior como base
            projecao_mes_atual = faturamento_mes_anterior
        else:
            # Se não há dados do mês anterior, usa valor atual ou padrão
            projecao_mes_atual = faturamento_atual_mes if faturamento_atual_mes > 0 else 50000
        
        return {
            'faturamento_atual_mes': faturamento_atual_mes,
            'faturamento_mes_anterior': faturamento_mes_anterior,
            'diferenca_receitas': diferenca_receitas,
            'projecao_mes_atual': projecao_mes_atual,
            'percentual_crescimento': (diferenca_receitas / faturamento_mes_anterior * 100) if faturamento_mes_anterior > 0 else 0
        }
    
    def get_ultimo_mes_com_dados_encerrado(self, faturamento_historico):
        """Retorna o último mês encerrado que tem dados reais"""
        if faturamento_historico.empty:
            return self.get_ultimo_mes_encerrado()
        
        ultimo_mes_encerrado = self.get_ultimo_mes_encerrado()
        
        # Filtrar apenas dados até o último mês encerrado
        dados_ate_mes_encerrado = faturamento_historico[faturamento_historico['Mes'] <= ultimo_mes_encerrado]
        
        if dados_ate_mes_encerrado.empty:
            return self.get_ultimo_mes_encerrado()
        
        return dados_ate_mes_encerrado['Mes'].iloc[-1]
    
    def get_estatisticas_faturamento(self):
        """Retorna estatísticas detalhadas sobre o faturamento"""
        if self.df.empty:
            return {}
        
        total_transacoes = len(self.df)
        transacoes_pagas = len(self.df[self.df['Situação'].str.lower() == 'paga'])
        valor_total_pago = self.df[self.df['Situação'].str.lower() == 'paga']['Total'].sum()
        valor_total_geral = self.df['Total'].sum()
        
        return {
            'total_transacoes': total_transacoes,
            'transacoes_pagas': transacoes_pagas,
            'valor_total_pago': valor_total_pago,
            'valor_total_geral': valor_total_geral,
            'percentual_pago': (transacoes_pagas / total_transacoes * 100) if total_transacoes > 0 else 0,
            'percentual_valor_pago': (valor_total_pago / valor_total_geral * 100) if valor_total_geral > 0 else 0
        }
    
    def gerar_projecao_anual(self, faturamento_historico, taxa_crescimento_mensal):
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
        if not faturamento_historico.empty:
            df_completo = df_completo.merge(
                faturamento_historico[['Mes', 'Ano', 'Total']], 
                on=['Mes', 'Ano'], 
                how='left'
            )
        else:
            df_completo['Total'] = np.nan
        
        # Calcular informações para projeção
        faturamento_base = self.calcular_faturamento_base(faturamento_historico)
        ultimo_mes_dados_encerrado = self.get_ultimo_mes_com_dados_encerrado(faturamento_historico)
        ultimo_mes_encerrado = self.get_ultimo_mes_encerrado()
        mes_atual = self.get_mes_atual()
        
        # Calcular projeção para o mês atual
        info_mes_atual = self.calcular_faturamento_mes_atual(faturamento_historico)
        
        # **DEBUG EXPANDIDO**
        with st.expander("🔍 **Debug Detalhado do Cálculo de Projeção**", expanded=True):
            st.write("### 📊 **Informações Base:**")
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.metric("💰 Faturamento Base", f"R$ {faturamento_base:,.2f}")
            with col2:
                st.metric("📅 Último Mês Encerrado", nomes_meses[ultimo_mes_encerrado-1])
            with col3:
                st.metric("📊 Mês Atual", nomes_meses[mes_atual-1])
            with col4:
                st.metric("📈 Taxa Crescimento", f"{taxa_crescimento_mensal}%")
            
            # Análise específica do mês atual
            st.write("### 🎯 **Análise do Mês Atual:**")
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.metric(
                    f"💵 {nomes_meses[mes_atual-1]} (Atual)",
                    f"R$ {info_mes_atual['faturamento_atual_mes']:,.2f}",
                    help="Faturamento já realizado no mês atual"
                )
            
            with col2:
                st.metric(
                    f"📊 {nomes_meses[ultimo_mes_encerrado-1]} (Anterior)",
                    f"R$ {info_mes_atual['faturamento_mes_anterior']:,.2f}",
                    help="Faturamento do mês anterior (base para comparação)"
                )
            
            with col3:
                delta_valor = info_mes_atual['diferenca_receitas']
                delta_cor = "normal" if delta_valor >= 0 else "inverse"
                st.metric(
                    "📈 Diferença",
                    f"R$ {abs(delta_valor):,.2f}",
                    delta=f"{info_mes_atual['percentual_crescimento']:+.1f}%",
                    help="Diferença entre mês atual e anterior"
                )
            
            with col4:
                st.metric(
                    f"🔮 Projeção {nomes_meses[mes_atual-1]}",
                    f"R$ {info_mes_atual['projecao_mes_atual']:,.2f}",
                    help="Projeção para o mês atual baseada na tendência"
                )
            
            # Explicação da lógica do mês atual
            if info_mes_atual['diferenca_receitas'] > 0:
                st.success(f"✅ **Crescimento Detectado**: O mês atual já tem R$ {info_mes_atual['diferenca_receitas']:,.2f} a mais que o mês anterior. Projetando continuidade do crescimento.")
            elif info_mes_atual['diferenca_receitas'] < 0:
                st.warning(f"⚠️ **Redução Detectada**: O mês atual tem R$ {abs(info_mes_atual['diferenca_receitas']):,.2f} a menos que o mês anterior. Projeção conservadora baseada no mês anterior.")
            else:
                st.info("📊 **Estabilidade**: Faturamento similar ao mês anterior. Projeção mantém o nível atual.")
            
            st.write("### 📋 **Faturamento Histórico Encontrado:**")
            if not faturamento_historico.empty:
                historico_debug = faturamento_historico.copy()
                historico_debug['Mes_Nome'] = historico_debug['Mes'].apply(lambda x: nomes_meses[x-1])
                historico_debug['Total_Formatado'] = historico_debug['Total'].apply(lambda x: f"R$ {x:,.2f}")
                historico_debug['Status_Mes'] = historico_debug['Mes'].apply(
                    lambda x: "🔒 Encerrado" if x < mes_atual else ("📅 Em andamento" if x == mes_atual else "⏳ Futuro")
                )
                st.dataframe(
                    historico_debug[['Mes_Nome', 'Total_Formatado', 'Status_Mes']].rename(
                        columns={'Mes_Nome': 'Mês', 'Total_Formatado': 'Faturamento Real', 'Status_Mes': 'Status'}
                    ),
                    use_container_width=True,
                    hide_index=True
                )
            else:
                st.info("❌ Nenhum dado histórico encontrado")
            
            st.write("### 🧮 **Metodologia de Cálculo:**")
            st.write("**Para meses futuros:** `Faturamento_Projetado = Faturamento_Base × (1 + Taxa/100)^Meses_Crescimento`")
            st.write(f"**Para mês atual:** Comparação com {nomes_meses[ultimo_mes_encerrado-1]} + incremento de novas receitas detectadas")
            st.write("")
        
        # Lista para armazenar informações de debug
        debug_calculos = []
        
        # Preencher projeções
        for idx, row in df_completo.iterrows():
            mes_nome = nomes_meses[row['Mes']-1]
            
            if pd.isna(row['Total']):
                if row['Mes'] < mes_atual:
                    # Mês passado sem dados
                    df_completo.at[idx, 'Total'] = 0
                    df_completo.at[idx, 'Tipo'] = 'Histórico'
                    debug_calculos.append({
                        'Mês': mes_nome,
                        'Tipo': 'Histórico (sem dados)',
                        'Valor': 'R$ 0,00',
                        'Cálculo': 'Mês encerrado sem dados históricos',
                        'Fórmula': 'N/A'
                    })
                elif row['Mes'] == mes_atual:
                    # Mês atual - usar projeção especial
                    df_completo.at[idx, 'Total'] = info_mes_atual['projecao_mes_atual']
                    df_completo.at[idx, 'Tipo'] = 'Projeção Atual'
                    
                    calculo_descricao = f"Base: {nomes_meses[ultimo_mes_encerrado-1]} + incremento observado"
                    if info_mes_atual['diferenca_receitas'] != 0:
                        formula_descricao = f"{info_mes_atual['faturamento_mes_anterior']:,.2f} + {info_mes_atual['diferenca_receitas']:,.2f} = {info_mes_atual['projecao_mes_atual']:,.2f}"
                    else:
                        formula_descricao = f"Baseado no mês anterior: {info_mes_atual['projecao_mes_atual']:,.2f}"
                    
                    debug_calculos.append({
                        'Mês': mes_nome,
                        'Tipo': 'Projeção (mês atual)',
                        'Valor': f'R$ {info_mes_atual["projecao_mes_atual"]:,.2f}',
                        'Cálculo': calculo_descricao,
                        'Fórmula': formula_descricao
                    })
                else:
                    # Meses futuros - usar crescimento exponencial
                    meses_crescimento = row['Mes'] - mes_atual
                    
                    # Base para crescimento é a projeção do mês atual
                    base_crescimento = info_mes_atual['projecao_mes_atual']
                    
                    if base_crescimento > 0:
                        valor_projetado = base_crescimento * ((1 + taxa_crescimento_mensal/100) ** meses_crescimento)
                    else:
                        valor_projetado = 50000 * ((1 + taxa_crescimento_mensal/100) ** meses_crescimento)
                    
                    df_completo.at[idx, 'Total'] = valor_projetado
                    df_completo.at[idx, 'Tipo'] = 'Projeção'
                    
                    # Calcular fator de crescimento para debug
                    fator_crescimento = (1 + taxa_crescimento_mensal/100) ** meses_crescimento
                    
                    debug_calculos.append({
                        'Mês': mes_nome,
                        'Tipo': 'Projeção (futuro)',
                        'Valor': f'R$ {valor_projetado:,.2f}',
                        'Cálculo': f'{meses_crescimento} meses após {nomes_meses[mes_atual-1]} (projetado)',
                        'Fórmula': f'{base_crescimento:,.2f} × (1.{taxa_crescimento_mensal:02.0f})^{meses_crescimento} = {base_crescimento:,.2f} × {fator_crescimento:.6f}'
                    })
            else:
                # Dados históricos reais
                if row['Mes'] < mes_atual:
                    status_mes = "Histórico (encerrado)"
                elif row['Mes'] == mes_atual:
                    status_mes = "Histórico (em andamento)"
                else:
                    status_mes = "Histórico (futuro)"
                    
                df_completo.at[idx, 'Tipo'] = 'Histórico'
                debug_calculos.append({
                    'Mês': mes_nome,
                    'Tipo': status_mes,
                    'Valor': f'R$ {row["Total"]:,.2f}',
                    'Cálculo': 'Dados reais do sistema',
                    'Fórmula': 'Soma de todas as transações pagas do mês'
                })
        
        # Mostrar tabela de debug dentro do expander (SEM COR DE FUNDO)
        with st.expander("🔍 **Debug Detalhado do Cálculo de Projeção**", expanded=True):
            st.write("### 📊 **Detalhamento Completo por Mês:**")
            
            # Criar DataFrame para o debug
            df_debug = pd.DataFrame(debug_calculos)
            
            # Exibir tabela SEM formatação de cor
            st.dataframe(df_debug, use_container_width=True, hide_index=True)
            
            st.write("### 🎯 **Legenda dos Tipos:**")
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.info("📊 **Histórico**: Dados reais do sistema")
            with col2:
                st.info("🎯 **Projeção (mês atual)**: Baseada na comparação com mês anterior")
            with col3:
                st.info("🔮 **Projeção (futuro)**: Crescimento exponencial")
            with col4:
                st.info("❌ **Sem dados**: Meses sem faturamento")
            
            st.write("### 📈 **Validação dos Cálculos:**")
            
            # Mostrar alguns exemplos de validação
            projecoes = [calc for calc in debug_calculos if 'Projeção' in calc['Tipo']]
            if projecoes:
                st.write("**Exemplos de Validação Manual:**")
                for i, proj in enumerate(projecoes[:3]):  # Mostrar apenas os 3 primeiros
                    st.code(f"""
Mês: {proj['Mês']}
Tipo: {proj['Tipo']}
{proj['Fórmula']}
Resultado: {proj['Valor']}
                    """)
            
            # Resumo final
            total_historico = len([c for c in debug_calculos if 'Histórico' in c['Tipo']])
            total_projecao_atual = len([c for c in debug_calculos if 'mês atual' in c['Tipo']])
            total_projecao_futura = len([c for c in debug_calculos if 'futuro' in c['Tipo']])
            total_sem_dados = len([c for c in debug_calculos if 'sem dados' in c['Tipo']])
            
            st.write("### 📊 **Resumo:**")
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("📊 Dados Históricos", total_historico)
            with col2:
                st.metric("🎯 Projeção Mês Atual", total_projecao_atual)
            with col3:
                st.metric("🔮 Projeções Futuras", total_projecao_futura)
            with col4:
                st.metric("❌ Sem Dados", total_sem_dados)
        
        return df_completo
    
    def criar_grafico_projecao(self, df_projecao):
        """Cria o gráfico de projeção de faturamento"""
        fig = go.Figure()
        
        df_historico = df_projecao[df_projecao['Tipo'] == 'Histórico']
        df_projecao_atual = df_projecao[df_projecao['Tipo'] == 'Projeção Atual']
        df_projecao_futura = df_projecao[df_projecao['Tipo'] == 'Projeção']
        
        if not df_historico.empty:
            fig.add_trace(go.Scatter(
                x=df_historico['Nome_Mes'],
                y=df_historico['Total'],
                mode='lines+markers',
                name='Faturamento Real',
                line=dict(color='#2E8B57', width=3),
                marker=dict(size=8, color='#2E8B57'),
                hovertemplate='<b>%{x}</b><br>Valor: R$ %{y:,.2f}<br>Status: Real<extra></extra>'
            ))
        
        if not df_projecao_atual.empty:
            fig.add_trace(go.Scatter(
                x=df_projecao_atual['Nome_Mes'],
                y=df_projecao_atual['Total'],
                mode='lines+markers',
                name='Projeção Mês Atual',
                line=dict(color='#FF6B35', width=3),
                marker=dict(size=10, color='#FF6B35', symbol='star'),
                hovertemplate='<b>%{x}</b><br>Valor: R$ %{y:,.2f}<br>Status: Projeção Atual<extra></extra>'
            ))
        
        if not df_projecao_futura.empty:
            fig.add_trace(go.Scatter(
                x=df_projecao_futura['Nome_Mes'],
                y=df_projecao_futura['Total'],
                mode='lines+markers',
                name='Projeção Futura',
                line=dict(color='#FF8C00', width=3, dash='dash'),
                marker=dict(size=8, color='#FF8C00'),
                hovertemplate='<b>%{x}</b><br>Valor: R$ %{y:,.2f}<br>Status: Projeção<extra></extra>'
            ))
        
        fig.update_layout(
            title=f'📈 Projeção de Faturamento Bruto - {self.ano_atual}',
            xaxis_title='Mês',
            yaxis_title='Faturamento (R$)',
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
        st.header("📊 Projeção de Faturamento Bruto 2025")
        
        faturamento_historico = self.calcular_faturamento_historico()
        stats_faturamento = self.get_estatisticas_faturamento()
        info_mes_atual = self.calcular_faturamento_mes_atual(faturamento_historico)
        
        with st.expander("ℹ️ Critérios para Projeção de Faturamento"):
            col1, col2 = st.columns(2)
            
            with col1:
                st.info("""
                **📋 Metodologia:**
                - ✅ Apenas transações com situação "Paga"
                - 🎯 Mês atual: Comparação com mês anterior + novas receitas
                - 🔮 Meses futuros: Crescimento exponencial baseado na taxa
                
                **🎯 Objetivo:** Projeção inteligente considerando tendências atuais
                """)
            
            with col2:
                if stats_faturamento:
                    st.metric("📊 Total de Transações", stats_faturamento['total_transacoes'])
                    st.metric("💰 Transações Pagas", stats_faturamento['transacoes_pagas'])
                    st.metric("📈 % Transações Pagas", f"{stats_faturamento['percentual_pago']:.1f}%")
                    st.metric("💵 Valor Total Pago", f"R$ {stats_faturamento['valor_total_pago']:,.2f}")
        
        if faturamento_historico.empty:
            st.warning("⚠️ Nenhum dado de faturamento encontrado para 2025. A projeção será baseada em valores estimados.")
        else:
            st.success(f"✅ {len(faturamento_historico)} meses com dados de faturamento encontrados.")
        
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
                help="Taxa de crescimento mensal aplicada na projeção do faturamento"
            )
        
        with col3:
            if st.button("🔄 Atualizar Projeção", type="primary"):
                st.rerun()
        
        # Gerar projeção (aqui o debug será mostrado)
        df_projecao = self.gerar_projecao_anual(faturamento_historico, taxa_crescimento)
        
        # Calcular métricas
        faturamento_real_acumulado = df_projecao[df_projecao['Tipo'] == 'Histórico']['Total'].sum()
        faturamento_projecao_atual = df_projecao[df_projecao['Tipo'] == 'Projeção Atual']['Total'].sum()
        faturamento_projecao_futura = df_projecao[df_projecao['Tipo'] == 'Projeção']['Total'].sum()
        faturamento_total_ano = faturamento_real_acumulado + faturamento_projecao_atual + faturamento_projecao_futura
        
        faturamento_base = self.calcular_faturamento_base(faturamento_historico)
        
        # Mostrar KPIs
        st.subheader("📊 Resumo da Projeção de Faturamento")
        col1, col2, col3, col4, col5 = st.columns(5)
        
        with col1:
            st.metric(
                "💰 Faturamento Real (YTD)",
                f"R$ {faturamento_real_acumulado:,.2f}",
                help="Faturamento real acumulado no ano"
            )
        
        with col2:
            st.metric(
                "🎯 Projeção Mês Atual",
                f"R$ {faturamento_projecao_atual:,.2f}",
                delta=f"{info_mes_atual['percentual_crescimento']:+.1f}%",
                help="Projeção para o mês atual baseada na tendência observada"
            )
        
        with col3:
            st.metric(
                "🔮 Projeção Restante",
                f"R$ {faturamento_projecao_futura:,.2f}",
                help="Projeção para os meses restantes do ano"
            )
        
        with col4:
            st.metric(
                "🎯 Total Projetado 2025",
                f"R$ {faturamento_total_ano:,.2f}",
                help="Faturamento total projetado para o ano"
            )
        
        with col5:
            if faturamento_real_acumulado > 0:
                crescimento_anual = ((faturamento_total_ano / faturamento_real_acumulado) - 1) * 100
            else:
                crescimento_anual = 0
            st.metric(
                "📊 Crescimento Anual",
                f"{crescimento_anual:.1f}%",
                help="Crescimento anual estimado"
            )
        
        # Gráfico principal
        fig = self.criar_grafico_projecao(df_projecao)
        st.plotly_chart(fig, use_container_width=True)
        
        # Tabela detalhada
        st.subheader("📋 Detalhamento Mensal do Faturamento")
        
        df_tabela = df_projecao.copy()
        df_tabela['Total_Formatado'] = df_tabela['Total'].apply(lambda x: f"R$ {x:,.2f}")
        df_tabela['Status'] = df_tabela['Tipo'].apply(
            lambda x: "✅ Real" if x == "Histórico" else ("🎯 Projeção Atual" if x == "Projeção Atual" else "🔮 Projeção")
        )
        
        df_exibicao = df_tabela[['Nome_Mes', 'Total_Formatado', 'Status']].copy()
        df_exibicao.columns = ['Mês', 'Faturamento', 'Status']
        
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
        
        ultimo_mes_encerrado = self.get_ultimo_mes_encerrado()
        mes_atual = self.get_mes_atual()
        nomes_meses = ['Jan', 'Fev', 'Mar', 'Abr', 'Mai', 'Jun', 
                      'Jul', 'Ago', 'Set', 'Out', 'Nov', 'Dez']
        
        with col1:
            st.info(f"""
            **📅 Período Base:** Janeiro a Dezembro {self.ano_atual}
            
            **📊 Metodologia:**
            - ✅ Transações com situação "Paga"
            - 🔒 Último mês encerrado: {nomes_meses[ultimo_mes_encerrado-1]}
            - 🎯 Mês atual ({nomes_meses[mes_atual-1]}): Projeção baseada na tendência
            - 📈 Taxa de crescimento: {taxa_crescimento:.1f}%
            """)
        
        with col2:
            meses_com_dados = len(faturamento_historico) if not faturamento_historico.empty else 0
            meses_projetados = 12 - mes_atual
            
            st.info(f"""
            **🔢 Estatísticas:**
            - Meses com dados reais: {meses_com_dados}
            - Projeção mês atual: {nomes_meses[mes_atual-1]}
            - Meses futuros projetados: {meses_projetados}
            - Transações pagas: {stats_faturamento.get('transacoes_pagas', 0)}
            - Última atualização: {datetime.now().strftime('%d/%m/%Y %H:%M')}
            """)
        
        # Análise detalhada do mês atual
        st.subheader("🎯 Análise Detalhada do Mês Atual")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.info(f"""
            **📊 {nomes_meses[mes_atual-1]} (Atual)**
            
            - Faturamento até agora: R$ {info_mes_atual['faturamento_atual_mes']:,.2f}
            - Projeção para o mês: R$ {info_mes_atual['projecao_mes_atual']:,.2f}
            """)
        
        with col2:
            st.info(f"""
            **📈 Comparação com {nomes_meses[ultimo_mes_encerrado-1]}**
            
            - Mês anterior: R$ {info_mes_atual['faturamento_mes_anterior']:,.2f}
            - Diferença: R$ {info_mes_atual['diferenca_receitas']:,.2f}
            - Variação: {info_mes_atual['percentual_crescimento']:+.1f}%
            """)
        
        with col3:
            if info_mes_atual['diferenca_receitas'] > 0:
                st.success(f"""
                **✅ Tendência Positiva**
                
                - Crescimento detectado
                - Novas receitas: R$ {info_mes_atual['diferenca_receitas']:,.2f}
                - Projeção otimista aplicada
                """)
            elif info_mes_atual['diferenca_receitas'] < 0:
                st.warning(f"""
                **⚠️ Tendência de Redução**
                
                - Redução de: R$ {abs(info_mes_atual['diferenca_receitas']):,.2f}
                - Projeção conservadora
                - Baseada no mês anterior
                """)
            else:
                st.info(f"""
                **📊 Tendência Estável**
                
                - Faturamento similar
                - Projeção mantém nível atual
                - Base: mês anterior
                """)
        
        # Cenários alternativos
        if st.checkbox("🎯 Ver Cenários Alternativos de Faturamento"):
            st.subheader("🔄 Análise de Cenários")
            
            cenarios = {
                'Conservador': taxa_crescimento - 2,
                'Atual': taxa_crescimento,
                'Otimista': taxa_crescimento + 3
            }
            
            resultados_cenarios = {}
            
            for nome_cenario, taxa_cenario in cenarios.items():
                df_cenario = self.gerar_projecao_anual(faturamento_historico, taxa_cenario)
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