import pandas as pd
from datetime import datetime, timedelta

def classificar_cliente_faixa(valor):
    """Classifica clientes por faixa de pagamento."""
    if valor < 500:
        return 'Grupo C (R$ 0-499)'
    elif valor < 1500:
        return 'Grupo B (R$ 500-1.499)'
    else:
        return 'Grupo A (R$ 1.500+)'

def formatar_moeda(valor):
    """Formata valor em moeda brasileira."""
    return f"R$ {valor:,.2f}"

def get_ordem_faixas():
    """Retorna a ordem padrão das faixas de cliente."""
    return ['Grupo A (R$ 1.500+)', 'Grupo B (R$ 500-1.499)', 'Grupo C (R$ 0-499)']

def get_cores_faixas():
    """Retorna o mapeamento de cores para as faixas."""
    return {
        'Grupo A (R$ 1.500+)': '#FFD700',  # Ouro
        'Grupo B (R$ 500-1.499)': '#C0C0C0',  # Prata
        'Grupo C (R$ 0-499)': '#CD7F32'  # Bronze
    }

def get_cores_situacao():
    """Retorna o mapeamento de cores para situações de pagamento."""
    return {
        'paga': '#2E8B57',
        'pendente': '#FF8C00',
        'expirado': '#DC143C'
    }