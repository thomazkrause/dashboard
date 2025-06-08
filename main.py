import streamlit as st
import pandas as pd
from database import DatabaseManager
from data_processor import DataProcessor
from metrics_calculator import MetricsCalculator
from visualizations import Visualizations
from ui_components import UIComponents
from utils import formatar_moeda, get_ordem_faixas
from datetime import datetime, timedelta

# Importações para sincronização com Iugu
try:
    from iugu_service import IuguService
    from sync_service import SyncService
    IUGU_AVAILABLE = True
except ImportError:
    IUGU_AVAILABLE = False

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
    .sync-status {
        padding: 0.5rem;
        border-radius: 0.25rem;
        margin: 0.25rem 0;
    }
    .sync-running {
        background-color: #d4edda;
        border: 1px solid #c3e6cb;
        color: #155724;
    }
    .sync-stopped {
        background-color: #f8d7da;
        border: 1px solid #f5c6cb;
        color: #721c24;
    }
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
    }
    .stTabs [data-baseweb="tab"] {
        height: 50px;
        padding-left: 20px;
        padding-right: 20px;
    }
</style>
""", unsafe_allow_html=True)

# Título principal
st.markdown('<div class="main-header">', unsafe_allow_html=True)
st.title("📊 Dashboard de Análise de Faturamento")
st.markdown("*Dados persistentes com Supabase + Sincronização Iugu*")
st.markdown('</div>', unsafe_allow_html=True)
st.markdown("---")

# Inicializar componentes
db = init_database()
ui = UIComponents()

# **SIDEBAR - Gerenciamento de Dados e Iugu**
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

# **SEÇÃO IUGU - Sincronização**
if IUGU_AVAILABLE:
    st.sidebar.subheader("🔄 Sincronização Iugu")
    
    # Input para token da API
    iugu_token = st.sidebar.text_input(
        "Token da API Iugu",
        type="password",
        help="Insira seu token da API da Iugu para sincronização automática",
        key="iugu_token_input"
    )
    
    if iugu_token:
        # Inicializar serviços da Iugu
        try:
            if 'iugu_service' not in st.session_state or st.session_state.get('current_token') != iugu_token:
                st.session_state.iugu_service = IuguService(iugu_token)
                st.session_state.current_token = iugu_token
            
            if 'sync_service' not in st.session_state:
                st.session_state.sync_service = SyncService(st.session_state.iugu_service, db)
            
            # Testar conexão com Iugu
            if st.session_state.iugu_service.test_connection():
                st.sidebar.success("✅ Conectado à Iugu")
                
                # Status da Sincronização
                sync_status = st.session_state.sync_service.get_sync_status()
                
                if sync_status['is_running']:
                    st.sidebar.markdown(
                        '<div class="sync-status sync-running">🔄 <strong>Sincronização Ativa</strong></div>',
                        unsafe_allow_html=True
                    )
                    if sync_status['last_sync']:
                        st.sidebar.info(f"🕒 Última sync: {sync_status['last_sync'].strftime('%H:%M:%S')}")
                    
                    if st.sidebar.button("🛑 Parar Sincronização", key="stop_sync"):
                        st.session_state.sync_service.stop_sync()
                        st.rerun()
                else:
                    st.sidebar.markdown(
                        '<div class="sync-status sync-stopped">⏸️ <strong>Sincronização Inativa</strong></div>',
                        unsafe_allow_html=True
                    )
                    
                    col1, col2 = st.sidebar.columns([1, 1])
                    with col1:
                        sync_interval = st.selectbox("Intervalo (min)", [5, 10, 15, 30, 60], index=0, key="sync_interval_select")
                    with col2:
                        if st.button("▶️ Iniciar", key="start_sync"):
                            st.session_state.sync_service.start_sync(sync_interval)
                            st.success(f"✅ Sincronização iniciada ({sync_interval}min)")
                            st.rerun()
                
                # Sincronizações manuais
                st.sidebar.markdown("**⚙️ Sincronização Manual:**")
                col1, col2 = st.sidebar.columns(2)
                
                with col1:
                    if st.button("🔄 Recente", key="sync_recent"):
                        with st.spinner("Sincronizando..."):
                            result = st.session_state.sync_service.sync_recent_invoices()
                            if result['status'] == 'success':
                                if result['new_records'] > 0 or result['updated_records'] > 0:
                                    st.success(f"✅ {result['new_records']} novos, {result['updated_records']} atualizados")
                                    st.rerun()
                                else:
                                    st.info("ℹ️ Nenhuma atualização necessária")
                            else:
                                st.error(f"❌ {result.get('message', 'Erro')}")
                
                with col2:
                    if st.button("📊 Completa", key="sync_full"):
                        with st.sidebar.expander("⚙️ Configurar"):
                            months_back = st.slider("Meses atrás", 1, 12, 6, key="months_slider")
                            confirm_full = st.checkbox("⚠️ Confirmar", key="confirm_full")
                        
                        if confirm_full:
                            with st.spinner(f"Sincronizando {months_back} meses..."):
                                result = st.session_state.sync_service.sync_full_history(months_back)
                                if result['status'] == 'success':
                                    st.success(f"✅ {result['total_records']} registros")
                                    st.rerun()
                                else:
                                    st.error(f"❌ {result.get('message', 'Erro')}")
            else:
                st.sidebar.error("❌ Erro na conexão com Iugu")
        except Exception as e:
            st.sidebar.error(f"❌ Erro Iugu: {str(e)}")
    else:
        st.sidebar.info("💡 Insira o token da Iugu para sincronização")

st.sidebar.markdown("---")

# **Upload de dados (seção original)**
st.sidebar.subheader("📁 Upload de Dados")
uploaded_file = st.sidebar.file_uploader("Carregar CSV", type=['csv'])

if uploaded_file:
    try:
        new_df = pd.read_csv(uploaded_file)
        st.sidebar.success(f"✅ {len(new_df)} registros no arquivo")
        
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

# **ÁREA PRINCIPAL - Carregar dados e criar abas**
try:
    with st.spinner("Carregando dados do banco..."):
        df = db.get_all_faturamento()
    
    if not df.empty:
        # Indicadores de status no topo
        col1, col2, col3 = st.columns([2, 1, 1])
        
        with col1:
            st.success(f"✅ {len(df)} registros carregados do banco de dados!")
        
        with col2:
            if 'iugu_id' in df.columns and not df['iugu_id'].isna().all():
                iugu_count = df['iugu_id'].notna().sum()
                st.info(f"🔄 {iugu_count} registros da Iugu")
            
        with col3:
            if IUGU_AVAILABLE and 'sync_service' in st.session_state:
                sync_status = st.session_state.sync_service.get_sync_status()
                if sync_status['last_sync']:
                    st.info(f"🕒 Sync: {sync_status['last_sync'].strftime('%H:%M')}")
        
        # Processar dados
        processor = DataProcessor(df)
        df = processor.df
        
        # Inicializar componentes
        calculator = MetricsCalculator(df)
        viz = Visualizations()
        ltv_por_cliente = processor.get_ltv_por_cliente()
        
        # **SISTEMA DE ABAS**
        tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
            "📈 KPIs Principais", 
            "🏆 Análise por Faixa", 
            "🥇 Ranking de Clientes", 
            "📊 Evolução Temporal", 
            "📋 Dados Detalhados",
            "🔄 Sincronização Iugu"
        ])
        
        # **ABA 1: KPIs PRINCIPAIS**
        with tab1:
            st.header("📈 Indicadores Principais")
            
            # KPIs básicos
            kpis = calculator.calculate_basic_kpis()
            ui.display_basic_kpis(kpis)
            
            # Valores por situação
            valores_situacao = calculator.calculate_valores_por_situacao()
            ui.display_valores_situacao(valores_situacao)
            
            # Métricas avançadas
            advanced_metrics = calculator.calculate_advanced_metrics()
            ui.display_advanced_metrics(advanced_metrics)
            
            # Gráficos de pizza - Status e Métodos de Pagamento
            st.subheader("📊 Distribuições")
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
        
        # **ABA 2: ANÁLISE POR FAIXA**
        with tab2:
            st.header("🏆 Análise por Faixa de Cliente (LTV)")
            
            if not ltv_por_cliente.empty:
                faixa_stats = calculator.calculate_faixa_stats(ltv_por_cliente)
                
                if not faixa_stats.empty:
                    # Ordenar por importância
                    ordem_faixas = get_ordem_faixas()
                    faixa_stats = faixa_stats.reindex(ordem_faixas)
                    
                    # Resumo por faixa
                    ui.display_faixa_summary(faixa_stats)
                    
                    # Gráficos de faixa
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        fig_pizza = viz.create_faixa_pizza_chart(faixa_stats)
                        st.plotly_chart(fig_pizza, use_container_width=True)
                    
                    with col2:
                        fig_bar = viz.create_faixa_bar_chart(faixa_stats)
                        st.plotly_chart(fig_bar, use_container_width=True)
                    
                    # Tabela de estatísticas por faixa
                    st.subheader("📋 Estatísticas Detalhadas por Faixa")
                    faixa_display = faixa_stats.copy()
                    faixa_display['Faturamento_Total'] = faixa_display['Faturamento_Total'].apply(formatar_moeda)
                    faixa_display['Ticket_Medio'] = faixa_display['Ticket_Medio'].apply(formatar_moeda)
                    faixa_display.columns = ['Faturamento Total', 'Ticket Médio', 'Qtd Clientes', '% do Faturamento']
                    st.dataframe(faixa_display, use_container_width=True)
            else:
                st.warning("⚠️ Não foi possível calcular LTV por cliente. Verifique se existem dados com situação 'Paga'.")
        
        # **ABA 3: RANKING DE CLIENTES**
        with tab3:
            st.header("🥇 Ranking de Clientes por Valor")
            
            ranking_clientes = calculator.calculate_ranking_clientes()
            
            if not ranking_clientes.empty:
                total_geral = ranking_clientes['Valor_Total'].sum()
                
                col1, col2 = st.columns([2, 1])
                
                with col1:
                    st.subheader("🏆 Top 20 Clientes")
                    
                    # Formatação para exibição
                    ranking_display = ranking_clientes.head(20).copy()
                    ranking_display['Valor_Total'] = ranking_display['Valor_Total'].apply(formatar_moeda)
                    ranking_display['Percentual'] = ranking_display['Percentual'].apply(lambda x: f"{x:.2f}%")
                    ranking_display['Percentual_Acumulado'] = ranking_display['Percentual_Acumulado'].apply(lambda x: f"{x:.2f}%")
                    
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
        
        # **ABA 4: EVOLUÇÃO TEMPORAL**
        with tab4:
            st.header("📊 Evolução Temporal")
            
            # Evolução mensal por faixa
            if not ltv_por_cliente.empty and 'Mes_Ano' in df.columns:
                st.subheader("📈 Evolução Mensal por Faixa de Cliente")
                
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
                    st.write("📋 **Tabela de Evolução Mensal por Faixa:**")
                    st.dataframe(pivot_evolucao.round(2), use_container_width=True)
            
            # Evolução mensal por status
            st.subheader("📊 Evolução Mensal por Status de Pagamento")
            
            if 'Mes_Ano' in df.columns and 'Total' in df.columns and 'Situação' in df.columns:
                df_mensal_status = df.groupby(['Mes_Ano', 'Situação'])['Total'].sum().reset_index()
                df_mensal_status['Mes_Ano_Str'] = df_mensal_status['Mes_Ano'].astype(str)
                
                fig_mensal = viz.create_evolucao_status_chart(df_mensal_status)
                st.plotly_chart(fig_mensal, use_container_width=True)
            else:
                st.warning("⚠️ Dados insuficientes para evolução mensal por status.")
        
        # **ABA 5: DADOS DETALHADOS**
        with tab5:
            st.header("📋 Dados Detalhados")
            
            # Filtros
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
            
            # Mostrar dados com indicação de origem
            df_display = df_filtrado.head(100).copy()
            
            # Adicionar coluna indicativa se há dados da Iugu
            if 'iugu_id' in df_display.columns:
                df_display['Origem'] = df_display['iugu_id'].apply(
                    lambda x: '🔄 Iugu' if pd.notna(x) else '📁 Upload'
                )
            
            st.dataframe(df_display, use_container_width=True)
            
            if len(df_filtrado) > 100:
                st.info(f"Mostrando 100 de {len(df_filtrado)} registros filtrados")
            
            # Opção de download
            if not df_filtrado.empty:
                csv = df_filtrado.to_csv(index=False)
                st.download_button(
                    label="📥 Download CSV Filtrado",
                    data=csv,
                    file_name=f"faturamento_filtrado_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                    mime="text/csv"
                )
        
        # **ABA 6: SINCRONIZAÇÃO IUGU**
        with tab6:
            if IUGU_AVAILABLE:
                st.header("🔄 Sincronização com Iugu")
                
                if 'sync_service' in st.session_state:
                    # Estatísticas detalhadas
                    stats = st.session_state.sync_service.get_sync_statistics()
                    
                    st.subheader("📊 Estatísticas de Sincronização")
                    
                    col1, col2, col3, col4 = st.columns(4)
                    
                    with col1:
                        st.metric("📊 Total de Registros", stats['total_records'])
                    
                    with col2:
                        st.metric("🔄 Registros da Iugu", stats['iugu_records'])
                    
                    with col3:
                        st.metric("📁 Registros de Upload", stats['upload_records'])
                    
                    with col4:
                        st.metric("📈 Cobertura Iugu", f"{stats['sync_coverage']:.1f}%")
                    
                    # Status da sincronização
                    st.subheader("⚙️ Status da Sincronização")
                    
                    sync_status = st.session_state.sync_service.get_sync_status()
                    
                    if sync_status['is_running']:
                        st.success("✅ Sincronização automática ativa")
                        st.info(f"⏱️ Intervalo: {int(sync_status['interval_minutes'])} minutos")
                        if sync_status['last_sync']:
                            st.info(f"🕒 Última sincronização: {sync_status['last_sync'].strftime('%d/%m/%Y %H:%M:%S')}")
                    else:
                        st.warning("⏸️ Sincronização automática inativa")
                    
                    # Opções de sincronização específica
                    st.subheader("🎯 Sincronização Específica")
                    
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        st.write("**📅 Sincronizar por Período:**")
                        start_date = st.date_input("Data inicial", value=datetime.now() - timedelta(days=30))
                        end_date = st.date_input("Data final", value=datetime.now())
                        
                        if st.button("🔄 Sincronizar Período"):
                            with st.spinner("Sincronizando período específico..."):
                                result = st.session_state.sync_service.sync_specific_period(
                                    start_date.strftime("%Y-%m-%d"),
                                    end_date.strftime("%Y-%m-%d")
                                )
                                if result['status'] == 'success':
                                    st.success(f"✅ {result['total_records']} registros sincronizados")
                                else:
                                    st.error(f"❌ {result['message']}")
                    
                    with col2:
                        st.write("**🔍 Sincronizar Fatura Específica:**")
                        invoice_id = st.text_input("ID da Fatura na Iugu")
                        
                        if st.button("🔄 Sincronizar Fatura"):
                            if invoice_id:
                                with st.spinner(f"Sincronizando fatura {invoice_id}..."):
                                    result = st.session_state.sync_service.sync_single_invoice(invoice_id)
                                    if result['status'] == 'success':
                                        st.success(f"✅ Fatura {result['action']}")
                                    else:
                                        st.error(f"❌ {result['message']}")
                            else:
                                st.warning("⚠️ Insira o ID da fatura")
                    
                    # Debug: mostrar dados da Iugu
                    with st.expander("🔍 Debug - Dados da Iugu"):
                        iugu_records = db.get_iugu_records() if hasattr(db, 'get_iugu_records') else pd.DataFrame()
                        if not iugu_records.empty:
                            st.write(f"Encontrados {len(iugu_records)} registros da Iugu:")
                            st.dataframe(iugu_records.head(10))
                        else:
                            st.info("Nenhum registro da Iugu encontrado")
                
                else:
                    st.info("💡 Configure o token da Iugu na barra lateral para usar a sincronização")
            else:
                st.error("❌ Módulos da Iugu não disponíveis")
                st.info("Instale as dependências: `pip install requests`")

    else:
        # Instruções quando não há dados
        st.info("📝 **Nenhum dado encontrado no banco.**")
        
        col1, col2, col3 = st.columns([1,2,1])
        with col2:
            st.markdown("""
            ### 🚀 Como começar:
            
            **Opção 1 - Upload Manual:**
            1. **📁 Upload**: Use a barra lateral para fazer upload do seu CSV
            2. **💾 Salvar**: Clique em "Salvar no Banco" para persistir os dados
            3. **📊 Analisar**: O dashboard será carregado automaticamente
            
            **Opção 2 - Sincronização Iugu:**
            1. **🔑 Token**: Insira seu token da API da Iugu na barra lateral
            2. **🔄 Sincronizar**: Use "Sync Completa" para importar seu histórico
            3. **⚙️ Automatizar**: Configure sincronização automática
            
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

# **Rodapé com informações do sistema**
st.markdown("---")
col1, col2, col3 = st.columns(3)

with col1:
    st.markdown("**💾 Banco de Dados:**")
    if db.mode == "supabase":
        st.success("✅ Supabase conectado")
    else:
        st.warning("⚠️ Modo memória")

with col2:
   st.markdown("**🔄 Sincronização:**")
   if IUGU_AVAILABLE and 'sync_service' in st.session_state:
       sync_status = st.session_state.sync_service.get_sync_status()
       if sync_status['is_running']:
           st.success("✅ Iugu ativa")
       else:
           st.info("⏸️ Iugu inativa")
   else:
       st.info("⚠️ Iugu indisponível")

with col3:
   st.markdown("**📊 Dashboard:**")
   st.info(f"📅 {datetime.now().strftime('%d/%m/%Y %H:%M')}")