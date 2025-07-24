import streamlit as st
import pandas as pd
from datetime import datetime
import traceback

class DatabaseManager:
    def __init__(self):
        self.supabase = None
        self.mode = "memory"  # memory ou supabase
        
        try:
            # Tentar carregar secrets
            if hasattr(st.secrets, "SUPABASE_URL") and hasattr(st.secrets, "SUPABASE_KEY"):
                from supabase import create_client, Client
                url = st.secrets["SUPABASE_URL"]
                key = st.secrets["SUPABASE_KEY"]
                self.supabase = create_client(url, key)
                self.mode = "supabase"
                st.sidebar.success("🔗 Conectado ao Supabase")
            else:
                st.sidebar.warning("⚠️ Usando modo de memória (dados não persistem)")
                self._init_memory_storage()
        except Exception as e:
            st.sidebar.error(f"⚠️ Erro Supabase: {str(e)}")
            st.sidebar.info("🔄 Usando modo de memória")
            self._init_memory_storage()
    
    def _init_memory_storage(self):
        """Inicializa armazenamento em memória"""
        if 'database' not in st.session_state:
            st.session_state.database = pd.DataFrame()
    
    def test_connection(self):
        """Testa conexão"""
        if self.mode == "supabase" and self.supabase:
            try:
                result = self.supabase.table('faturamento').select("count").execute()
                return True
            except Exception as e:
                st.error(f"❌ Erro de conexão Supabase: {str(e)}")
                return False
        return True  # Modo memória sempre "conectado"
    
    def insert_faturamento(self, df):
        """Insere dados"""
        if self.mode == "supabase" and self.supabase:
            return self._insert_supabase(df)
        else:
            return self._insert_memory(df)
    
    def _convert_date(self, date_value):
        """Converte qualquer formato de data para ISO string"""
        if pd.isna(date_value) or date_value is None or date_value == '':
            return None
        
        try:
            if isinstance(date_value, str):
                # Se já é string, tentar converter para datetime primeiro
                parsed_date = pd.to_datetime(date_value, errors='coerce')
                if pd.notna(parsed_date):
                    return parsed_date.isoformat()
                else:
                    return None
            elif hasattr(date_value, 'isoformat'):
                # Já é datetime
                return date_value.isoformat()
            else:
                # Tentar converter para datetime
                parsed_date = pd.to_datetime(date_value, errors='coerce')
                if pd.notna(parsed_date):
                    return parsed_date.isoformat()
                else:
                    return None
        except Exception:
            return None
    
    def _safe_float(self, value):
        """Converte valor para float de forma segura"""
        if pd.isna(value) or value is None or value == '':
            return 0.0
        
        try:
            # Se for string, limpar caracteres especiais
            if isinstance(value, str):
                # Remover espaços e caracteres não numéricos (exceto . e ,)
                cleaned = value.strip().replace(' ', '').replace('R$', '').replace('%', '')
                # Tratar vírgula decimal brasileira
                if ',' in cleaned and '.' in cleaned:
                    # Formato: 1.234,56
                    cleaned = cleaned.replace('.', '').replace(',', '.')
                elif ',' in cleaned:
                    # Formato: 1234,56
                    cleaned = cleaned.replace(',', '.')
                
                return float(cleaned) if cleaned else 0.0
            else:
                return float(value)
        except (ValueError, TypeError):
            return 0.0
    
    def _insert_supabase(self, df):
        """Inserir no Supabase"""
        try:
            records = []
            
            for _, row in df.iterrows():
                record = {
                    'nome': str(row.get('Nome', '')) if pd.notna(row.get('Nome')) else '',
                    'cpf_cnpj': str(row.get('CPF/CNPJ', '')) if pd.notna(row.get('CPF/CNPJ')) else '',
                    'total': self._safe_float(row.get('Total')),
                    'taxa': self._safe_float(row.get('Taxa')),
                    'situacao': str(row.get('Situação', '')) if pd.notna(row.get('Situação')) else '',
                    'paga_com': str(row.get('Paga com', '')) if pd.notna(row.get('Paga com')) else '',
                    'data_criacao': self._convert_date(row.get('Data de criação')),
                    'data_pagamento': self._convert_date(row.get('Data do pagamento')),
                }
                
                # Adicionar campos específicos da Iugu se existirem
                if 'iugu_id' in row:
                    record['iugu_id'] = str(row.get('iugu_id', '')) if pd.notna(row.get('iugu_id')) else None
                if 'iugu_url' in row:
                    record['iugu_url'] = str(row.get('iugu_url', '')) if pd.notna(row.get('iugu_url')) else None
                
                records.append(record)
            
            # Inserir em lotes
            batch_size = 1000
            total_inserted = 0
            
            progress_placeholder = st.empty()
            
            for i in range(0, len(records), batch_size):
                batch = records[i:i + batch_size]
                
                try:
                    result = self.supabase.table('faturamento').insert(batch).execute()
                    total_inserted += len(batch)
                    
                    # Mostrar progresso
                    if len(records) > batch_size:
                        progress = total_inserted / len(records)
                        progress_placeholder.progress(progress, f"Inserindo... {total_inserted}/{len(records)}")
                        
                except Exception as batch_error:
                    st.error(f"❌ Erro no lote {i//batch_size + 1}: {str(batch_error)}")
                    continue
            
            progress_placeholder.empty()
            return total_inserted
            
        except Exception as e:
            st.error(f"❌ Erro ao inserir no Supabase: {str(e)}")
            st.error(f"Detalhes: {traceback.format_exc()}")
            return False
    
    def _insert_memory(self, df):
        """Inserir na memória"""
        try:
            # Processar as datas antes de armazenar
            df_processed = df.copy()
            
            # Converter datas para datetime se possível
            date_columns = ['Data de criação', 'Data do pagamento']
            for col in date_columns:
                if col in df_processed.columns:
                    df_processed[col] = pd.to_datetime(df_processed[col], errors='coerce')
            
            st.session_state.database = pd.concat([st.session_state.database, df_processed], ignore_index=True)
            return len(df)
        except Exception as e:
            st.error(f"❌ Erro ao salvar em memória: {str(e)}")
            return False
    
    def get_all_faturamento(self):
        """Busca todos os dados"""
        if self.mode == "supabase" and self.supabase:
            return self._get_supabase()
        else:
            return self._get_memory()
    
    def _get_supabase(self):
        """Buscar do Supabase"""
        try:
            result = self.supabase.table('faturamento').select("*").order('created_at', desc=True).execute()
            
            if result.data:
                df = pd.DataFrame(result.data)
                
                # Converter e renomear colunas
                if 'data_criacao' in df.columns:
                    df['Data de criação'] = pd.to_datetime(df['data_criacao'], errors='coerce')
                if 'data_pagamento' in df.columns:
                    df['Data do pagamento'] = pd.to_datetime(df['data_pagamento'], errors='coerce')
                
                column_mapping = {
                    'nome': 'Nome',
                    'cpf_cnpj': 'CPF/CNPJ',
                    'total': 'Total',
                    'taxa': 'Taxa',
                    'situacao': 'Situação',
                    'paga_com': 'Paga com'
                }
                
                df = df.rename(columns=column_mapping)
                
                # Debug: verificar se as colunas estão corretas
                expected_columns = ['Nome', 'CPF/CNPJ', 'Total', 'Taxa', 'Situação', 'Paga com', 'Data de criação']
                missing_columns = [col for col in expected_columns if col not in df.columns]
                if missing_columns:
                    st.warning(f"⚠️ Colunas faltando: {missing_columns}")
                
                return df
            else:
                return pd.DataFrame()
                
        except Exception as e:
            st.error(f"❌ Erro ao buscar do Supabase: {str(e)}")
            return pd.DataFrame()
    
    def _get_memory(self):
        """Buscar da memória"""
        return st.session_state.database.copy()
    
    def get_faturamento_by_period(self, start_date, end_date):
        """Busca dados por período"""
        if self.mode == "supabase" and self.supabase:
            try:
                result = self.supabase.table('faturamento').select("*").gte(
                    'data_criacao', start_date.isoformat()
                ).lte('data_criacao', end_date.isoformat()).execute()
                
                if result.data:
                    df = pd.DataFrame(result.data)
                    # Aplicar mesmo mapeamento de colunas
                    if 'data_criacao' in df.columns:
                        df['Data de criação'] = pd.to_datetime(df['data_criacao'], errors='coerce')
                    if 'data_pagamento' in df.columns:
                        df['Data do pagamento'] = pd.to_datetime(df['data_pagamento'], errors='coerce')
                    
                    column_mapping = {
                        'nome': 'Nome',
                        'cpf_cnpj': 'CPF/CNPJ',
                        'total': 'Total',
                        'taxa': 'Taxa',
                        'situacao': 'Situação',
                        'paga_com': 'Paga com'
                    }
                    
                    df = df.rename(columns=column_mapping)
                    return df
                else:
                    return pd.DataFrame()
                    
            except Exception as e:
                st.error(f"❌ Erro ao buscar por período: {str(e)}")
                return pd.DataFrame()
        else:
            # Buscar da memória por período
            df = self._get_memory()
            if not df.empty and 'Data de criação' in df.columns:
                mask = (df['Data de criação'] >= start_date) & (df['Data de criação'] <= end_date)
                return df.loc[mask]
            return pd.DataFrame()
    
    def delete_all_data(self):
        """Limpa todos os dados"""
        if self.mode == "supabase" and self.supabase:
            try:
                result = self.supabase.table('faturamento').delete().neq('id', 0).execute()
                return True
            except Exception as e:
                st.error(f"❌ Erro ao limpar Supabase: {str(e)}")
                return False
        else:
            st.session_state.database = pd.DataFrame()
            return True
    
    def get_stats(self):
        """Retorna estatísticas"""
        if self.mode == "supabase" and self.supabase:
            try:
                result = self.supabase.table('faturamento').select("id", count="exact").execute()
                total_records = result.count
                
                last_result = self.supabase.table('faturamento').select("created_at").order('created_at', desc=True).limit(1).execute()
                last_update = last_result.data[0]['created_at'] if last_result.data else None
                
                return {
                    'total_records': total_records,
                    'last_update': last_update,
                    'mode': 'Supabase'
                }
            except Exception as e:
                st.error(f"❌ Erro ao buscar stats: {str(e)}")
                return {'total_records': 0, 'mode': 'Memory (Error)'}
        else:
            df = st.session_state.database
            return {
                'total_records': len(df),
                'last_update': datetime.now().isoformat(),
                'mode': 'Memory'
            }
    
    def backup_data(self):
        """Faz backup dos dados em CSV"""
        try:
            df = self.get_all_faturamento()
            if not df.empty:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"backup_faturamento_{timestamp}.csv"
                return df.to_csv(index=False), filename
            else:
                return None, None
        except Exception as e:
            st.error(f"❌ Erro ao fazer backup: {str(e)}")
            return None, None
    
    def get_unique_values(self, column):
        """Retorna valores únicos de uma coluna"""
        try:
            df = self.get_all_faturamento()
            if not df.empty and column in df.columns:
                return df[column].dropna().unique().tolist()
            return []
        except Exception as e:
            st.error(f"❌ Erro ao buscar valores únicos: {str(e)}")
            return []
    
    # NOVOS MÉTODOS PARA SUPORTE À IUGU
    def _delete_by_iugu_id(self, iugu_id: str):
        """Deleta registro específico pelo ID da Iugu"""
        if self.mode == "supabase" and self.supabase:
            try:
                # Verificar se existe coluna iugu_id na tabela
                result = self.supabase.table('faturamento').delete().eq('iugu_id', iugu_id).execute()
                return True
            except Exception as e:
                st.error(f"❌ Erro ao deletar por iugu_id: {str(e)}")
                return False
        else:
            # Modo memória
            if 'iugu_id' in st.session_state.database.columns:
                st.session_state.database = st.session_state.database[
                    st.session_state.database['iugu_id'] != iugu_id
                ]
                return True
            return False
    
    def check_iugu_id_exists(self, iugu_id: str) -> bool:
        """Verifica se um registro com iugu_id já existe"""
        if self.mode == "supabase" and self.supabase:
            try:
                result = self.supabase.table('faturamento').select("id").eq('iugu_id', iugu_id).execute()
                return len(result.data) > 0
            except Exception:
                return False
        else:
            df = st.session_state.database
            if not df.empty and 'iugu_id' in df.columns:
                return iugu_id in df['iugu_id'].values
            return False
    
    def update_by_iugu_id(self, iugu_id: str, update_data: dict):
        """Atualiza registro específico pelo ID da Iugu"""
        if self.mode == "supabase" and self.supabase:
            try:
                result = self.supabase.table('faturamento').update(update_data).eq('iugu_id', iugu_id).execute()
                return len(result.data) > 0
            except Exception as e:
                st.error(f"❌ Erro ao atualizar por iugu_id: {str(e)}")
                return False
        else:
            # Modo memória - atualizar DataFrame
            if 'iugu_id' in st.session_state.database.columns:
                mask = st.session_state.database['iugu_id'] == iugu_id
                if mask.any():
                    for key, value in update_data.items():
                        if key in st.session_state.database.columns:
                            st.session_state.database.loc[mask, key] = value
                    return True
            return False
    
    def get_iugu_records(self):
        """Retorna apenas registros que vieram da Iugu"""
        df = self.get_all_faturamento()
        if not df.empty and 'iugu_id' in df.columns:
            return df[df['iugu_id'].notna()]
        return pd.DataFrame()
    
    def get_last_sync_date(self):
        """Retorna a data da última sincronização com base no registro mais recente da Iugu"""
        df = self.get_iugu_records()
        if not df.empty and 'Data de criação' in df.columns:
            return df['Data de criação'].max()
        return None
    
    def clean_duplicate_iugu_records(self):
        """Remove registros duplicados da Iugu (mantém o mais recente)"""
        if self.mode == "supabase" and self.supabase:
            try:
                # Para Supabase, seria necessário uma query mais complexa
                # Por simplicidade, vamos fazer pelo Python
                df = self.get_all_faturamento()
                if not df.empty and 'iugu_id' in df.columns:
                    # Identificar duplicatas
                    duplicates = df[df['iugu_id'].notna()].duplicated(subset=['iugu_id'], keep='last')
                    if duplicates.any():
                        # Deletar duplicatas (isso é uma implementação simplificada)
                        duplicate_ids = df[duplicates]['iugu_id'].unique()
                        for iugu_id in duplicate_ids:
                            self._delete_by_iugu_id(iugu_id)
                        return len(duplicate_ids)
                return 0
            except Exception as e:
                st.error(f"❌ Erro ao limpar duplicatas: {str(e)}")
                return 0
        else:
            # Modo memória
            if 'iugu_id' in st.session_state.database.columns:
                before_count = len(st.session_state.database)
                st.session_state.database = st.session_state.database.drop_duplicates(
                    subset=['iugu_id'], 
                    keep='last'
                ).reset_index(drop=True)
                after_count = len(st.session_state.database)
                return before_count - after_count
            return 0