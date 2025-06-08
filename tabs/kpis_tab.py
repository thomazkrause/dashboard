import streamlit as st

class KPIsTab:
    def __init__(self, df, calculator, ui):
        self.df = df
        self.calculator = calculator
        self.ui = ui
    
    def render(self):
        """Renderiza a aba de KPIs principais"""
        # Remover: st.header("📈 KPIs Principais") - já está no título da aba
        
        # KPIs básicos
        kpis = self.calculator.calculate_basic_kpis()
        self.ui.display_basic_kpis(kpis)
        
        st.markdown("---")
        
        # Valores por situação
        valores_situacao = self.calculator.calculate_valores_por_situacao()
        self.ui.display_valores_situacao(valores_situacao)
        
        st.markdown("---")
        
        # Métricas avançadas
        advanced_metrics = self.calculator.calculate_advanced_metrics()
        self.ui.display_advanced_metrics(advanced_metrics)
        
        # Insights automáticos
        self._display_insights(kpis, valores_situacao, advanced_metrics)
    
    def _display_insights(self, kpis, valores, metrics):
        """Exibe insights automáticos baseados nos KPIs"""
        st.subheader("💡 Insights Automáticos")
        
        insights = []
        
        # Análise da taxa de conversão
        if kpis['taxa_conversao'] > 80:
            insights.append("✅ **Excelente taxa de conversão!** Mais de 80% dos clientes efetuaram pagamento.")
        elif kpis['taxa_conversao'] > 60:
            insights.append("👍 **Boa taxa de conversão.** Considere estratégias para melhorar ainda mais.")
        else:
            insights.append("⚠️ **Taxa de conversão baixa.** Foque em melhorar o processo de pagamento.")
        
        # Análise do valor em risco
        if valores['valor_risco'] > valores['valor_pago'] * 0.3:
            insights.append("🚨 **Alto valor em risco!** Mais de 30% do valor está pendente/expirado.")
        elif valores['valor_risco'] > valores['valor_pago'] * 0.15:
            insights.append("⚡ **Valor em risco moderado.** Monitore os pagamentos pendentes.")
        
        # Análise do LTV médio
        if metrics['ltv_medio'] > 1000:
            insights.append("💎 **Alto valor por cliente!** LTV médio acima de R$ 1.000.")
        
        # Análise de churn
        if metrics['churn_rate'] > 25:
            insights.append("📉 **Taxa de churn alta.** Implemente estratégias de retenção.")
        elif metrics['churn_rate'] < 10:
            insights.append("🎯 **Excelente retenção de clientes!** Taxa de churn baixa.")
        
        for insight in insights:
            st.markdown(f"- {insight}")
        
        if not insights:
            st.info("📊 Continue coletando dados para gerar insights mais precisos.")