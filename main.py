import streamlit as st
import pandas as pd
from database import DatabaseManager
from data_processor import DataProcessor
from metrics_calculator import MetricsCalculator
from visualizations import Visualizations
from ui_components import UIComponents
from projecao_faturamento import ProjecaoFaturamento  # Nova importação
from utils import formatar_moeda, get_ordem_faixas
from datetime import datetime, timedelta

# Configuração da página
st.set_page_config(
    page_title="Dashboard Faturamento", 
    page_icon="💰", 
    layout="wide",
    initial_sidebar_state="expanded"
)

# Inicializar banco de dados
@st.cache_resource
def init_database():
    return DatabaseManager()

# CSS personalizado
st.markdown("""
<style>
    .main-header {
        text-align: center;
        padding: 1rem 0;
        margin-bottom: 2rem;
    }
    .database-status {
        padding: 0.5rem;
        border-radius: 0.5rem;
        margin-bottom: 1rem;
    }
    .cliente-header {
        background: linear-gradient(90deg, #f0f2f6, #ffffff);
        padding: 1rem;
        border-radius: 0.5rem;
        margin-bottom: 1rem;
        border-left: 4px solid #1f77b4;
    }
</style>
""", unsafe_allow_html=True)

# Título principal
st.markdown('<div class="main-header">', unsafe_allow_html=True)
st.title("📊 Dashboard de Análise de Faturamento")
st.markdown("*Dados persistentes com Supabase*")
st.markdown('</div>', unsafe_allow_html=True)
st.markdown("---")

# Inicializar componentes
db = init_database()
ui = UIComponents()

# Sidebar - Gerenciamento de Dados
st.sidebar.header("💾 Gerenciamento de Dados")

# Status da conexão
if db.test_connection():
    if db.mode == "supabase":
        st.sidebar.success("✅ Conectado ao Supabase")
    else:
        st.sidebar.warning("⚠️ Modo Memória (dados temporários)")
    
    # Estatísticas do banco
    stats = db.get_stats()
    if stats:
        st.sidebar.metric("📊 Total de Registros", stats.get('total_records', 0))
        st.sidebar.info(f"🔧 Modo: {stats.get('mode', 'Unknown')}")
        if stats.get('last_update'):
            try:
                last_update = datetime.fromisoformat(stats['last_update'].replace('Z', '+00:00'))
                st.sidebar.info(f"🕒 Última atualização: {last_update.strftime('%d/%m/%Y %H:%M')}")
            except:
                st.sidebar.info(f"🕒 Última atualização: {stats['last_update']}")
else:
    st.sidebar.error("❌ Erro de conexão")

st.sidebar.markdown("---")

# Upload de novos dados
st.sidebar.subheader("📁 Upload de Dados")
uploaded_file = st.sidebar.file_uploader("Carregar CSV", type=['csv'])

if uploaded_file:
    try:
        new_df = pd.read_csv(uploaded_file)
        st.sidebar.success(f"✅ {len(new_df)} registros no arquivo")
        
        # Preview dos dados
        with st.sidebar.expander("👀 Preview dos dados"):
            st.dataframe(new_df.head(3))
        
        col1, col2 = st.sidebar.columns(2)
        
        with col1:
            if st.button("💾 Salvar no Banco", type="primary"):
                with st.spinner("Salvando dados..."):
                    result = db.insert_faturamento(new_df)
                    if result:
                        st.success(f"✅ {result} registros salvos!")
                        st.rerun()
                    else:
                        st.error("❌ Erro ao salvar!")
        
        with col2:
            if st.button("🔄 Substituir Dados"):
                if st.checkbox("⚠️ Confirmar substituição"):
                    with st.spinner("Substituindo dados..."):
                        db.delete_all_data()
                        result = db.insert_faturamento(new_df)
                        if result:
                            st.success(f"✅ Dados substituídos! {result} registros")
                            st.rerun()
                        else:
                            st.error("❌ Erro na substituição!")
    
    except Exception as e:
        st.sidebar.error(f"❌ Erro ao ler arquivo: {str(e)}")

st.sidebar.markdown("---")

# Gerenciamento avançado
with st.sidebar.expander("⚙️ Gerenciamento Avançado"):
    if st.button("🗑️ Limpar Todos os Dados", type="secondary"):
        if st.checkbox("⚠️ CONFIRMO que quero apagar TODOS os dados"):
            if db.delete_all_data():
                st.success("🗑️ Todos os dados foram removidos!")
                st.rerun()
            else:
                st.error("❌ Erro ao limpar dados!")

def show_cliente_historico(df):
    """Exibe o histórico de um cliente específico"""
    st.header("👤 Histórico do Cliente")
    
    if df.empty:
        st.warning("⚠️ Nenhum dado disponível para análise de clientes.")
        return
    
    # Verificar se as colunas necessárias existem
    if 'CPF/CNPJ' not in df.columns or 'Nome' not in df.columns:
        st.error("❌ Colunas 'CPF/CNPJ' e 'Nome' são necessárias para esta análise.")
        return
    
    # Obter lista de clientes únicos com seus nomes
    clientes_df = df.groupby('CPF/CNPJ')['Nome'].first().reset_index()
    clientes_df['display_name'] = clientes_df['Nome'] + " (" + clientes_df['CPF/CNPJ'] + ")"
    clientes_df = clientes_df.sort_values('Nome')
    
    if len(clientes_df) == 0:
        st.warning("⚠️ Nenhum cliente encontrado nos dados.")
        return
    
    # Selectbox para escolher o cliente
    col1, col2 = st.columns([2, 1])
    
    with col1:
        cliente_selecionado = st.selectbox(
            "🔍 Selecione um cliente:",
            options=clientes_df['CPF/CNPJ'].tolist(),
            format_func=lambda x: clientes_df[clientes_df['CPF/CNPJ'] == x]['display_name'].iloc[0],
            key="cliente_historico_select"
        )
    
    with col2:
        # Filtro por situação
        situacoes_disponiveis = ['Todas'] + list(df['Situação'].unique()) if 'Situação' in df.columns else ['Todas']
        situacao_filtro = st.selectbox("📊 Filtrar por situação:", situacoes_disponiveis)
    
    if cliente_selecionado:
        # Filtrar dados do cliente selecionado
        cliente_data = df[df['CPF/CNPJ'] == cliente_selecionado].copy()
        
        if situacao_filtro != 'Todas':
            cliente_data = cliente_data[cliente_data['Situação'] == situacao_filtro]
        
        # Ordenar por data de criação (mais recente primeiro)
        if 'Data de criação' in cliente_data.columns:
            cliente_data = cliente_data.sort_values('Data de criação', ascending=False)
        
        # Informações do cliente
        nome_cliente = cliente_data['Nome'].iloc[0] if not cliente_data.empty else "N/A"
        
        st.markdown(f"""
        <div class="cliente-header">
            <h3>👤 {nome_cliente}</h3>
            <p><strong>CPF/CNPJ:</strong> {cliente_selecionado}</p>
        </div>
        """, unsafe_allow_html=True)
        
        if cliente_data.empty:
            st.info(f"📄 Nenhuma transação encontrada para {nome_cliente} com os filtros aplicados.")
            return
        
        # KPIs do cliente
        st.subheader("📈 Resumo do Cliente")
        
        col1, col2, col3, col4, col5 = st.columns(5)
        
        total_transacoes = len(cliente_data)
        valor_total = cliente_data['Total'].sum() if 'Total' in cliente_data.columns else 0
        valor_medio = cliente_data['Total'].mean() if 'Total' in cliente_data.columns else 0
        transacoes_pagas = len(cliente_data[cliente_data['Situação'] == 'paga']) if 'Situação' in cliente_data.columns else 0
        taxa_conversao = (transacoes_pagas / total_transacoes * 100) if total_transacoes > 0 else 0
        
        with col1:
            st.metric("📋 Total Transações", total_transacoes)
        with col2:
            st.metric("💰 Valor Total", formatar_moeda(valor_total))
        with col3:
            st.metric("🎫 Ticket Médio", formatar_moeda(valor_medio))
        with col4:
            st.metric("✅ Transações Pagas", transacoes_pagas)
        with col5:
            st.metric("📊 Taxa Conversão", f"{taxa_conversao:.1f}%")
        
        # Resumo por situação (apenas texto)
        if 'Situação' in cliente_data.columns:
            st.subheader("📊 Resumo por Situação")
            situacao_counts = cliente_data['Situação'].value_counts()
            
            # Apenas resumo textual
            st.write("**Distribuição das Transações:**")
            for situacao in situacao_counts.index:
                count = situacao_counts[situacao]
                valor_situacao = cliente_data[cliente_data['Situação'] == situacao]['Total'].sum()
                st.write(f"• **{situacao}**: {count} transações - {formatar_moeda(valor_situacao)}")
        
        # Evolução temporal (se houver dados de data)
        if 'Data de criação' in cliente_data.columns:
            st.subheader("📈 Evolução Temporal")
            
            # Agrupar por mês
            cliente_data_temporal = cliente_data.copy()
            cliente_data_temporal['Mes_Ano'] = pd.to_datetime(cliente_data_temporal['Data de criação']).dt.to_period('M')
            evolucao_mensal = cliente_data_temporal.groupby('Mes_Ano').agg({
                'Total': 'sum',
                'CPF/CNPJ': 'count'
            }).reset_index()
            evolucao_mensal.columns = ['Mes_Ano', 'Valor_Total', 'Num_Transacoes']
            evolucao_mensal['Mes_Ano_Str'] = evolucao_mensal['Mes_Ano'].astype(str)
            
            if len(evolucao_mensal) > 1:
                import plotly.express as px
                fig_evolucao = px.line(
                    evolucao_mensal,
                    x='Mes_Ano_Str',
                    y='Valor_Total',
                    title=f'Evolução Mensal do Faturamento - {nome_cliente}',
                    labels={'Valor_Total': 'Valor (R$)', 'Mes_Ano_Str': 'Período'},
                    markers=True
                )
                fig_evolucao.update_layout(height=400)
                st.plotly_chart(fig_evolucao, use_container_width=True)
        
        # Tabela detalhada do histórico
        st.subheader("📋 Histórico Detalhado de Transações")
        
        # Preparar dados para exibição
        historico_display = cliente_data.copy()
        
        # Formatação das colunas para exibição
        colunas_exibir = []
        colunas_rename = {}
        
        if 'Data de criação' in historico_display.columns:
            historico_display['Data de criação'] = pd.to_datetime(historico_display['Data de criação']).dt.strftime('%d/%m/%Y %H:%M')
            colunas_exibir.append('Data de criação')
            colunas_rename['Data de criação'] = 'Data Criação'
        
        if 'Total' in historico_display.columns:
            historico_display['Total_Formatado'] = historico_display['Total'].apply(formatar_moeda)
            colunas_exibir.append('Total_Formatado')
            colunas_rename['Total_Formatado'] = 'Valor'
        
        if 'Taxa' in historico_display.columns:
            historico_display['Taxa_Formatada'] = historico_display['Taxa'].apply(formatar_moeda)
            colunas_exibir.append('Taxa_Formatada')
            colunas_rename['Taxa_Formatada'] = 'Taxa'
        
        if 'Situação' in historico_display.columns:
            colunas_exibir.append('Situação')
            colunas_rename['Situação'] = 'Status'
        
        if 'Paga com' in historico_display.columns:
            colunas_exibir.append('Paga com')
            colunas_rename['Paga com'] = 'Método Pagamento'
        
        if 'Data do pagamento' in historico_display.columns:
            historico_display['Data do pagamento'] = pd.to_datetime(historico_display['Data do pagamento'], errors='coerce').dt.strftime('%d/%m/%Y %H:%M')
            colunas_exibir.append('Data do pagamento')
            colunas_rename['Data do pagamento'] = 'Data Pagamento'
        
        # Exibir apenas as colunas disponíveis
        historico_final = historico_display[colunas_exibir].rename(columns=colunas_rename)
        
        # Exibir tabela sem formatação de cor de fundo
        st.dataframe(historico_final, use_container_width=True, hide_index=True)
        
        # Informações adicionais
        st.info(f"📊 Exibindo {len(historico_final)} transações para {nome_cliente}")
        
        # Botão para download do histórico do cliente
        if st.button("📥 Baixar Histórico do Cliente", key="download_cliente"):
            csv = cliente_data.to_csv(index=False)
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"historico_{nome_cliente.replace(' ', '_')}_{timestamp}.csv"
            st.download_button(
                label="📁 Download CSV",
                data=csv,
                file_name=filename,
                mime='text/csv'
            )

# Carregar dados do banco
try:
    with st.spinner("Carregando dados do banco..."):
        df = db.get_all_faturamento()
    
    if not df.empty:
        st.success(f"✅ {len(df)} registros carregados do banco de dados!")
        
        # Processar dados
        processor = DataProcessor(df)
        df = processor.df
        
        # Inicializar componentes de análise
        calculator = MetricsCalculator(df)
        viz = Visualizations()
        
        # Calcular LTV por cliente
        ltv_por_cliente = processor.get_ltv_por_cliente()
        
        # **ABAS DO DASHBOARD**
        tab1, tab2, tab3 = st.tabs(["📊 Dashboard Principal", "👤 Histórico de Cliente", "📈 Projeção de Faturamento"])
        
        with tab1:
            # **DASHBOARD PRINCIPAL - TODOS OS GRÁFICOS E INDICADORES**
            
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
                    else:
                        st.warning("⚠️ Coluna 'Mes_Ano' não encontrada. Verifique o processamento de datas.")
            else:
                st.warning("⚠️ Não foi possível calcular LTV por cliente. Verifique se existem dados com situação 'Paga'.")
            
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
            else:
                st.warning("⚠️ Não foi possível calcular ranking de clientes.")
            
            # Evolução Mensal por Status
            st.header("📊 Evolução Mensal por Status")
            
            if 'Mes_Ano' in df.columns and 'Total' in df.columns and 'Situação' in df.columns:
                df_mensal_status = df.groupby(['Mes_Ano', 'Situação'])['Total'].sum().reset_index()
                df_mensal_status['Mes_Ano_Str'] = df_mensal_status['Mes_Ano'].astype(str)
                
                fig_mensal = viz.create_evolucao_status_chart(df_mensal_status)
                st.plotly_chart(fig_mensal, use_container_width=True)
            else:
                st.warning("⚠️ Dados insuficientes para evolução mensal por status.")
            
            # Análises Visuais
            st.header("📊 Análises Visuais")
            
            col1, col2 = st.columns(2)
            
            with col1:
                if 'Situação' in df.columns:
                    situacao_counts = df['Situação'].value_counts()
                    fig_situacao = viz.create_situacao_pie_chart(situacao_counts)
                    st.plotly_chart(fig_situacao, use_container_width=True)
                else:
                    st.warning("⚠️ Coluna 'Situação' não encontrada.")
            
            with col2:
                if 'Paga com' in df.columns:
                    metodos_pagamento = df['Paga com'].value_counts()
                    fig_pagamento = viz.create_pagamento_pie_chart(metodos_pagamento)
                    st.plotly_chart(fig_pagamento, use_container_width=True)
                else:
                    st.warning("⚠️ Coluna 'Paga com' não encontrada.")
            
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
        
        with tab2:
            # **ABA DE HISTÓRICO DE CLIENTE**
            show_cliente_historico(df)
        
        with tab3:
            # **ABA DE PROJEÇÃO DE FATURAMENTO**
            projecao = ProjecaoFaturamento(df)
            projecao.mostrar_interface()
        
    else:
        # Instruções quando não há dados
        st.info("📝 **Nenhum dado encontrado no banco.**")
        
        col1, col2, col3 = st.columns([1,2,1])
        with col2:
            st.markdown("""
            ### 🚀 Como começar:
            
            1. **📁 Upload**: Use a barra lateral para fazer upload do seu CSV
            2. **💾 Salvar**: Clique em "Salvar no Banco" para persistir os dados
            3. **📊 Analisar**: O dashboard será carregado automaticamente
            
            ### 📋 Formato esperado do CSV:
            - `Nome`: Nome do cliente
            - `CPF/CNPJ`: Documento do cliente  
            - `Total`: Valor da transação
            - `Taxa`: Taxa cobrada
            - `Situação`: Status (Paga, Pendente, Expirado)
            - `Paga com`: Método de pagamento
            - `Data de criação`: Data da transação
            - `Data do pagamento`: Data do pagamento (se aplicável)
            """)
        
        ui.display_instructions()
        
except Exception as e:
    st.error(f"❌ Erro ao carregar dados: {str(e)}")
    st.info("💡 Verifique a conexão com o Supabase e tente novamente.")
    
    # Debug adicional
    with st.expander("🔍 Debug do erro"):
        import traceback
        st.code(traceback.format_exc())