import pandas as pd
from datetime import datetime, timedelta
from utils import classificar_cliente_faixa

class DataProcessor:
    def __init__(self, df):
        self.df = df
        self._process_dates()
        self._add_derived_columns()
    
    def _process_dates(self):
        """Converte colunas de data para datetime."""
        if 'Data de criação' in self.df.columns:
            self.df['Data de criação'] = pd.to_datetime(self.df['Data de criação'], errors='coerce')
        if 'Data do pagamento' in self.df.columns:
            self.df['Data do pagamento'] = pd.to_datetime(self.df['Data do pagamento'], errors='coerce')
    
    def _add_derived_columns(self):
        """Adiciona colunas derivadas."""
        if 'Data de criação' in self.df.columns:
            self.df['Mes_Ano'] = self.df['Data de criação'].dt.to_period('M')
        
        # Preencher valores nulos em 'Paga com'
        if 'Paga com' in self.df.columns:
            self.df['Paga com'] = self.df['Paga com'].fillna('Não Informado')
    
    def get_ltv_por_cliente(self):
        """Calcula LTV por cliente."""
        if all(col in self.df.columns for col in ['CPF/CNPJ', 'Total', 'Situação']):
            ltv_por_cliente = self.df[self.df['Situação'].str.lower() == 'paga'].groupby('CPF/CNPJ').agg({
                'Total': 'sum',
                'Nome': 'first'
            }).reset_index()
            ltv_por_cliente.columns = ['CPF/CNPJ', 'LTV_Total', 'Nome']
            ltv_por_cliente['Faixa_Cliente'] = ltv_por_cliente['LTV_Total'].apply(classificar_cliente_faixa)
            return ltv_por_cliente
        return pd.DataFrame()
    
    def get_df_com_faixa(self, ltv_por_cliente):
        """Adiciona informação de faixa ao dataframe."""
        if not ltv_por_cliente.empty and 'Situação' in self.df.columns:
            df_com_faixa = self.df[self.df['Situação'].str.lower() == 'paga'].copy()
            df_com_faixa = df_com_faixa.merge(
                ltv_por_cliente[['CPF/CNPJ', 'Faixa_Cliente']], 
                on='CPF/CNPJ', 
                how='left'
            )
            return df_com_faixa
        return pd.DataFrame()
    
    def apply_filters(self, situacao='Todas', metodo_pagamento='Todos'):
        """Aplica filtros ao dataframe."""
        df_filtrado = self.df.copy()
        
        if situacao != 'Todas' and 'Situação' in df_filtrado.columns:
            df_filtrado = df_filtrado[df_filtrado['Situação'] == situacao]
        
        if metodo_pagamento != 'Todos' and 'Paga com' in df_filtrado.columns:
            if metodo_pagamento == 'Não Informado':
                df_filtrado = df_filtrado[df_filtrado['Paga com'].isna()]
            else:
                df_filtrado = df_filtrado[df_filtrado['Paga com'] == metodo_pagamento]
        
        return df_filtrado