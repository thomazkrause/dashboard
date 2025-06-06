import streamlit as st
import pandas as pd
from data_processor import DataProcessor
from metrics_calculator import MetricsCalculator
from visualizations import Visualizations
from ui_components import UIComponents
from utils import formatar_moeda, get_ordem_faixas

# Configuração da página
st.set_page_config(page_title="Dashboard Faturamento", page_icon="💰", layout="wide")

# Título principal
st.title("📊 Dashboard de Análise de Faturamento")
st.markdown("---")

# Inicializar componentes UI (fora do if para estar sempre disponível)
ui = UIComponents()

# Upload do arquivo
uploaded_file = st.sidebar.file_uploader("📁 Upload do CSV", type=['csv'])

if uploaded_file:
    # Carregar e processar dados
    df = pd.read_csv(uploaded_file)
    st.success(f"✅ {len(df)} registros carregados!")
    
    # Inicializar processador de dados
    processor = DataProcessor(df)
    df = processor.df
    
    # Inicializar calculadora de métricas
    calculator = MetricsCalculator(df)
    
    # Inicializar visualizações
    viz = Visualizations()
    
    # Calcular LTV por cliente
    ltv_por_cliente = processor.get_ltv_por_cliente()
    
    # Exibir KPIs principais
    kpis = calculator.calculate_basic_kpis()
    ui.display_basic_kpis(kpis)
    
    # Exibir valores por situação
    valores_situacao = calculator.calculate_valores_por_situacao()
    ui.display_valores_situacao(valores_situacao)
    
    # Exibir métricas avançadas
    advanced_metrics = calculator.calculate_advanced_metrics()
    ui.display_advanced_metrics(advanced_metrics)
    
    # Análise por Faixa de Cliente
    st.header("🏆 Análise por Faixa de Cliente (LTV)")
    
    if not ltv_por_cliente.empty:
        # Calcular estatísticas por faixa
        faixa_stats = calculator.calculate_faixa_stats(ltv_por_cliente)
        
        if not faixa_stats.empty:
            # Ordenar por importância
            ordem_faixas = get_ordem_faixas()
            faixa_stats = faixa_stats.reindex(ordem_faixas)
            
            # Exibir resumo por faixa
            ui.display_faixa_summary(faixa_stats)
            
            # Gráficos de faixa
            col1, col2 = st.columns(2)
            
            with col1:
                fig_pizza = viz.create_faixa_pizza_chart(faixa_stats)
                st.plotly_chart(fig_pizza, use_container_width=True)
            
            with col2:
                fig_bar = viz.create_faixa_bar_chart(faixa_stats)
                st.plotly_chart(fig_bar, use_container_width=True)
            
            # Evolução mensal por faixa
            st.subheader("📈 Evolução Mensal por Faixa de Cliente")
            
            if 'Mes_Ano' in df.columns:
                df_com_faixa = processor.get_df_com_faixa(ltv_por_cliente)
                
                if not df_com_faixa.empty:
                    evolucao_mensal = df_com_faixa.groupby(['Mes_Ano', 'Faixa_Cliente'])['Total'].sum().reset_index()
                    evolucao_mensal['Mes_Ano_Str'] = evolucao_mensal['Mes_Ano'].astype(str)
                    
                    fig_evolucao = viz.create_evolucao_mensal_chart(evolucao_mensal)
                    st.plotly_chart(fig_evolucao, use_container_width=True)
                    
                    # Tabela de evolução
                    pivot_evolucao = evolucao_mensal.pivot(
                        index='Mes_Ano_Str', 
                        columns='Faixa_Cliente', 
                        values='Total'
                    ).fillna(0)
                    st.write("📋 **Tabela de Evolução Mensal:**")
                    st.dataframe(pivot_evolucao.round(2), use_container_width=True)
    
    # Ranking de Clientes
    st.header("🏆 Ranking de Clientes por Valor")
    
    ranking_clientes = calculator.calculate_ranking_clientes()
    
    if not ranking_clientes.empty:
        total_geral = ranking_clientes['Valor_Total'].sum()
        
        col1, col2 = st.columns([2, 1])
        
        with col1:
            st.subheader("🥇 Top 20 Clientes")
            
            # Formatação para exibição
            ranking_display = ranking_clientes.head(20).copy()
            ranking_display['Valor_Total'] = ranking_display['Valor_Total'].apply(formatar_moeda)
            ranking_display['Percentual'] = ranking_display['Percentual'].apply(lambda x: f"{x:.2f}%")
            ranking_display['Percentual_Acumulado'] = ranking_display['Percentual_Acumulado'].apply(lambda x: f"{x:.2f}%")
            
            # Renomear colunas para exibição
            ranking_display = ranking_display[['Nome', 'Valor_Total', 'Percentual', 'Percentual_Acumulado', 'Num_Transacoes', 'Faixa']]
            ranking_display.columns = ['Cliente', 'Valor Total', '% Individual', '% Acumulado', 'Transações', 'Faixa']
            
            st.dataframe(ranking_display, use_container_width=True, hide_index=True)
        
        with col2:
            ui.display_ranking_analysis(ranking_clientes, total_geral)
        
        # Gráfico de Pareto
        st.subheader("📈 Análise de Pareto - Concentração de Clientes")
        
        pareto_data = ranking_clientes.head(30)
        fig_pareto = viz.create_pareto_chart(pareto_data)
        st.plotly_chart(fig_pareto, use_container_width=True)
    
    # Evolução Mensal por Status
    st.header("📊 Evolução Mensal por Status")
    
    if 'Mes_Ano' in df.columns and 'Total' in df.columns and 'Situação' in df.columns:
        df_mensal_status = df.groupby(['Mes_Ano', 'Situação'])['Total'].sum().reset_index()
        df_mensal_status['Mes_Ano_Str'] = df_mensal_status['Mes_Ano'].astype(str)
        
        fig_mensal = viz.create_evolucao_status_chart(df_mensal_status)
        st.plotly_chart(fig_mensal, use_container_width=True)
    
    # Análises Visuais
    st.header("📊 Análises Visuais")
    
    col1, col2 = st.columns(2)
    
    with col1:
        if 'Situação' in df.columns:
            situacao_counts = df['Situação'].value_counts()
            fig_situacao = viz.create_situacao_pie_chart(situacao_counts)
            st.plotly_chart(fig_situacao, use_container_width=True)
    
    with col2:
        if 'Paga com' in df.columns:
            metodos_pagamento = df['Paga com'].value_counts()
            fig_pagamento = viz.create_pagamento_pie_chart(metodos_pagamento)
            st.plotly_chart(fig_pagamento, use_container_width=True)
    
    # Dados Detalhados
    st.header("📋 Dados Detalhados")
    
    col1, col2 = st.columns(2)
    
    with col1:
        situacoes_disponiveis = ['Todas']
        if 'Situação' in df.columns:
            situacoes_disponiveis += list(df['Situação'].unique())
        situacao_selecionada = st.selectbox("🔍 Filtrar por situação:", situacoes_disponiveis)
    
    with col2:
        metodos_disponiveis = ['Todos']
        if 'Paga com' in df.columns:
            metodos_disponiveis += list(df['Paga com'].unique())
        metodo_selecionado = st.selectbox("🔍 Filtrar por método de pagamento:", metodos_disponiveis)
    
    # Aplicar filtros
    df_filtrado = processor.apply_filters(situacao_selecionada, metodo_selecionado)
    
    if len(df_filtrado) != len(df):
        st.info(f"📊 Exibindo {len(df_filtrado)} de {len(df)} registros (filtrados)")
    
    st.dataframe(df_filtrado.head(50), use_container_width=True)
    
    if len(df_filtrado) > 50:
        st.info(f"Mostrando 50 de {len(df_filtrado)} registros filtrados")

else:
    # Exibir instruções quando não há arquivo carregado
    ui.display_instructions()