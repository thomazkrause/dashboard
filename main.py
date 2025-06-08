import streamlit as st
import pandas as pd
import sys
import os

# Adicionar o diretório atual ao path
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.append(current_dir)

# Imports básicos
from database import DatabaseManager
from data_processor import DataProcessor
from metrics_calculator import MetricsCalculator
from visualizations import Visualizations
from ui_components import UIComponents

# Configuração da página
st.set_page_config(
    page_title="Dashboard Faturamento", 
    page_icon="💰", 
    layout="wide",
    initial_sidebar_state="expanded"
)

# CSS personalizado
st.markdown("""
<style>
    .main-header {
        text-align: center;
        padding: 1rem 0;
        margin-bottom: 2rem;
    }
    .stTabs [data-baseweb="tab-list"] {
        gap: 2rem;
    }
    .stTabs [data-baseweb="tab"] {
        height: 3rem;
        padding-left: 1rem;
        padding-right: 1rem;
    }
</style>
""", unsafe_allow_html=True)

# Título principal
st.markdown('<div class="main-header">', unsafe_allow_html=True)
st.title("📊 Dashboard de Análise de Faturamento v0.3")
st.markdown("*Análise completa com dados persistentes - Interface em Abas*")
st.markdown('</div>', unsafe_allow_html=True)
st.markdown("---")

def check_tabs_availability():
    """Verifica se as abas estão disponíveis"""
    try:
        from tabs_manager import TabsManager
        return True, TabsManager
    except ImportError:
        return False, None

def init_components():
    """Inicializa todos os componentes necessários"""
    db = DatabaseManager()
    ui = UIComponents()
    return db, ui

def render_sidebar(db):
    """Renderiza a sidebar com controles de dados"""
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
    else:
        st.sidebar.error("❌ Erro de conexão")
    
    st.sidebar.markdown("---")
    
    # Upload de novos dados
    st.sidebar.subheader("📁 Upload de Dados")
    uploaded_file = st.sidebar.file_uploader("Carregar CSV", type=['csv'])
    
    if uploaded_file:
        return handle_file_upload(uploaded_file, db)
    
    return None

def handle_file_upload(uploaded_file, db):
    """Manipula upload de arquivo"""
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
        
        return new_df
    
    except Exception as e:
        st.sidebar.error(f"❌ Erro ao ler arquivo: {str(e)}")
        return None

def render_fallback_dashboard(df, processor, calculator, viz, ui):
    """Renderiza dashboard básico se as abas não estiverem disponíveis"""
    st.warning("⚠️ Sistema de abas não disponível. Usando interface básica.")
    
    # KPIs básicos
    st.header("📈 KPIs Principais")
    kpis = calculator.calculate_basic_kpis()
    ui.display_basic_kpis(kpis)
    
    # Valores por situação
    valores_situacao = calculator.calculate_valores_por_situacao()
    ui.display_valores_situacao(valores_situacao)
    
    # Métricas avançadas
    advanced_metrics = calculator.calculate_advanced_metrics()
    ui.display_advanced_metrics(advanced_metrics)
    
    st.markdown("---")
    
    # Análise por faixa
    st.header("🏆 Análise por Faixa de Cliente")
    ltv_por_cliente = processor.get_ltv_por_cliente()
    
    if not ltv_por_cliente.empty:
        faixa_stats = calculator.calculate_faixa_stats(ltv_por_cliente)
        if not faixa_stats.empty:
            ui.display_faixa_summary(faixa_stats)
            
            col1, col2 = st.columns(2)
            with col1:
                fig_pizza = viz.create_faixa_pizza_chart(faixa_stats)
                st.plotly_chart(fig_pizza, use_container_width=True)
            
            with col2:
                fig_bar = viz.create_faixa_bar_chart(faixa_stats)
                st.plotly_chart(fig_bar, use_container_width=True)

def render_no_data_message():
    """Renderiza mensagem quando não há dados"""
    st.info("📝 **Nenhum dado encontrado no banco.**")
    
    col1, col2, col3 = st.columns([1,2,1])
    with col2:
        st.markdown("""
        ### 🚀 Como começar:
        
        1. **📁 Upload**: Use a barra lateral para fazer upload do seu CSV
        2. **💾 Salvar**: Clique em "Salvar no Banco" para persistir os dados
        3. **📊 Analisar**: O dashboard será carregado automaticamente
        """)

def main():
    """Função principal da aplicação"""
    # Verificar disponibilidade das abas
    tabs_available, TabsManager = check_tabs_availability()
    
    if tabs_available:
        st.success("✅ Sistema de abas carregado com sucesso!")
    else:
        st.warning("⚠️ Sistema de abas não disponível - usando interface básica")
    
    # Inicializar componentes
    db, ui = init_components()
    
    # Renderizar sidebar
    uploaded_df = render_sidebar(db)
    
    try:
        # Carregar dados do banco
        with st.spinner("Carregando dados..."):
            df = db.get_all_faturamento()
        
        if not df.empty:
            st.success(f"✅ {len(df)} registros carregados!")
            
            # Processar dados
            processor = DataProcessor(df)
            df = processor.df
            
            # Inicializar componentes de análise
            calculator = MetricsCalculator(df)
            viz = Visualizations()
            
            # Renderizar dashboard
            if tabs_available:
                try:
                    tabs_manager = TabsManager(df, processor, calculator, viz, ui)
                    tabs_manager.render_tabs()
                except Exception as e:
                    st.error(f"❌ Erro no sistema de abas: {e}")
                    st.info("🔄 Usando interface básica...")
                    render_fallback_dashboard(df, processor, calculator, viz, ui)
            else:
                render_fallback_dashboard(df, processor, calculator, viz, ui)
            
        else:
            render_no_data_message()
            
    except Exception as e:
        st.error(f"❌ Erro ao carregar dados: {str(e)}")
        
        # Debug adicional
        with st.expander("🔍 Debug do erro"):
            import traceback
            st.code(traceback.format_exc())

if __name__ == "__main__":
    main()