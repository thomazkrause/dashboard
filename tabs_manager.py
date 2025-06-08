import streamlit as st
import sys
import os

# Adicionar o diretório atual ao path se necessário
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.append(current_dir)

# Imports das abas
try:
    from tabs.kpis_tab import KPIsTab
    from tabs.evolucao_tab import EvolucaoTab
    from tabs.faixa_cliente_tab import FaixaClienteTab
    from tabs.ranking_tab import RankingTab
    from tabs.analises_visuais_tab_simple import AnalisesVisuaisTab
    from tabs.dados_detalhados_tab import DadosDetalhadosTab
except ImportError as e:
    st.error(f"Erro ao importar abas: {e}")
    st.stop()

class TabsManager:
    def __init__(self, df, processor, calculator, viz, ui):
        self.df = df
        self.processor = processor
        self.calculator = calculator
        self.viz = viz
        self.ui = ui
        
        # Inicializar todas as abas
        try:
            self.kpis_tab = KPIsTab(df, calculator, ui)
            self.evolucao_tab = EvolucaoTab(df, viz)
            self.faixa_tab = FaixaClienteTab(df, processor, calculator, viz, ui)
            self.ranking_tab = RankingTab(df, calculator, viz, ui)
            self.visuais_tab = AnalisesVisuaisTab(df, viz)
            self.dados_tab = DadosDetalhadosTab(df, processor)
        except Exception as e:
            st.error(f"Erro ao inicializar abas: {e}")
            st.stop()
    
    def render_tabs(self):
        """Renderiza todas as abas do dashboard"""
        tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
            "📈 KPIs Principais",
            "📊 Evolução Mensal",
            "🏆 Análise por Faixa",
            "🥇 Ranking de Clientes",
            "📊 Análises Visuais",
            "📋 Dados Detalhados"
        ])
        
        with tab1:
            try:
                self.kpis_tab.render()
            except Exception as e:
                st.error(f"Erro na aba KPIs: {e}")
        
        with tab2:
            try:
                self.evolucao_tab.render()
            except Exception as e:
                st.error(f"Erro na aba Evolução: {e}")
        
        with tab3:
            try:
                self.faixa_tab.render()
            except Exception as e:
                st.error(f"Erro na aba Faixa: {e}")
        
        with tab4:
            try:
                self.ranking_tab.render()
            except Exception as e:
                st.error(f"Erro na aba Ranking: {e}")
        
        with tab5:
            try:
                self.visuais_tab.render()
            except Exception as e:
                st.error(f"Erro na aba Visuais: {e}")
        
        with tab6:
            try:
                self.dados_tab.render()
            except Exception as e:
                st.error(f"Erro na aba Dados: {e}")