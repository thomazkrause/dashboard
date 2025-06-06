#!/bin/bash
# Script para executar o dashboard

# Ativar ambiente virtual (se existir)
if [ -d "venv" ]; then
    source venv/bin/activate
fi

# Instalar dependências
pip install -r requirements.txt

# Executar aplicação
streamlit run main.py --server.port 8501 --server.address localhost