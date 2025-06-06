"""
Arquivo de configurações centralizadas do projeto
"""

# Configurações de cores
COLORS = {
    'faixas': {
        'Grupo A (R$ 1.500+)': '#FFD700',  # Ouro
        'Grupo B (R$ 500-1.499)': '#C0C0C0',  # Prata
        'Grupo C (R$ 0-499)': '#CD7F32'  # Bronze
    },
    'situacoes': {
        'paga': '#2E8B57',
        'pendente': '#FF8C00',
        'expirado': '#DC143C'
    }
}

# Configurações de valores
VALORES_FAIXA = {
    'grupo_c_max': 500,
    'grupo_b_max': 1500
}

# Configurações de análise
ANALISE_CONFIG = {
    'dias_churn': 60,
    'top_clientes_display': 20,
    'top_clientes_pareto': 30,
    'percentual_concentracao_alto': 50,
    'percentual_concentracao_moderado': 30
}

# Configurações de formatação
FORMATO_MOEDA = {
    'prefixo': 'R$',
    'separador_decimal': ',',
    'separador_milhar': '.'
}