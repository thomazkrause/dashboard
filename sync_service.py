import time
import threading
from datetime import datetime, timedelta
from typing import Dict, List
import streamlit as st
import pandas as pd
from iugu_service import IuguService
from database import DatabaseManager

class SyncService:
    def __init__(self, iugu_service: IuguService, database: DatabaseManager):
        self.iugu_service = iugu_service
        self.database = database
        self.is_running = False
        self.sync_thread = None
        self.last_sync = None
        self.sync_interval = 300  # 5 minutos por padrão
    
    def start_sync(self, interval_minutes: int = 5):
        """Inicia sincronização automática"""
        if self.is_running:
            st.warning("⚠️ Sincronização já está rodando")
            return
        
        self.sync_interval = interval_minutes * 60
        self.is_running = True
        
        self.sync_thread = threading.Thread(target=self._sync_loop, daemon=True)
        self.sync_thread.start()
        
        st.success(f"✅ Sincronização iniciada (intervalo: {interval_minutes} minutos)")
    
    def stop_sync(self):
        """Para a sincronização automática"""
        self.is_running = False
        if self.sync_thread:
            self.sync_thread.join(timeout=5)
        st.info("🛑 Sincronização parada")
    
    def _sync_loop(self):
        """Loop principal de sincronização"""
        while self.is_running:
            try:
                self.sync_recent_invoices()
                time.sleep(self.sync_interval)
            except Exception as e:
                st.error(f"❌ Erro na sincronização automática: {str(e)}")
                time.sleep(60)  # Espera 1 minuto antes de tentar novamente
    
    def sync_recent_invoices(self) -> Dict:
        """Sincroniza faturas recentes (últimas 24 horas)"""
        try:
            # Buscar faturas das últimas 24 horas
            yesterday = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")
            
            invoices = self.iugu_service.get_all_invoices(created_at_from=yesterday)
            
            if not invoices:
                return {"status": "success", "new_records": 0, "updated_records": 0}
            
            # Converter para DataFrame
            df_iugu = self.iugu_service.convert_invoices_to_dataframe(invoices)
            
            if df_iugu.empty:
                return {"status": "success", "new_records": 0, "updated_records": 0}
            
            # Buscar dados existentes
            df_existing = self.database.get_all_faturamento()
            
            new_records = 0
            updated_records = 0
            
            if not df_existing.empty and 'iugu_id' in df_existing.columns:
                # Identificar registros novos e atualizados
                existing_ids = set(df_existing['iugu_id'].dropna())
                
                # Novos registros
                df_new = df_iugu[~df_iugu['iugu_id'].isin(existing_ids)]
                if not df_new.empty:
                    result = self.database.insert_faturamento(df_new)
                    new_records = result if result else 0
                
                # Registros para atualizar
                df_update = df_iugu[df_iugu['iugu_id'].isin(existing_ids)]
                if not df_update.empty:
                    updated_records = self._update_existing_records(df_update, df_existing)
            else:
                # Primeira sincronização - inserir todos
                result = self.database.insert_faturamento(df_iugu)
                new_records = result if result else 0
            
            self.last_sync = datetime.now()
            
            return {
                "status": "success",
                "new_records": new_records,
                "updated_records": updated_records,
                "total_processed": len(df_iugu)
            }
            
        except Exception as e:
            st.error(f"❌ Erro na sincronização: {str(e)}")
            return {"status": "error", "message": str(e)}
    
    def _update_existing_records(self, df_update: pd.DataFrame, df_existing: pd.DataFrame) -> int:
        """Atualiza registros existentes que mudaram de status"""
        updated_count = 0
        
        for _, row_iugu in df_update.iterrows():
            try:
                # Encontrar registro existente
                existing_row = df_existing[df_existing['iugu_id'] == row_iugu['iugu_id']]
                
                if not existing_row.empty:
                    existing_status = existing_row.iloc[0]['Situação']
                    new_status = row_iugu['Situação']
                    
                    # Se o status mudou, atualizar
                    if existing_status != new_status:
                        # Para simplificar, vamos deletar e inserir novamente
                        # Em um sistema mais complexo, você faria um UPDATE
                        self.database._delete_by_iugu_id(row_iugu['iugu_id'])
                        
                        # Inserir registro atualizado
                        df_single = pd.DataFrame([row_iugu])
                        self.database.insert_faturamento(df_single)
                        updated_count += 1
            
            except Exception as e:
                st.warning(f"Erro ao atualizar registro {row_iugu.get('iugu_id')}: {str(e)}")
                continue
        
        return updated_count
    
    def sync_full_history(self, months_back: int = 6) -> Dict:
        """Sincronização completa do histórico"""
        try:
            start_date = (datetime.now() - timedelta(days=months_back * 30)).strftime("%Y-%m-%d")
            
            st.info(f"🔄 Sincronizando histórico completo ({months_back} meses)...")
            
            # Buscar todas as faturas do período
            invoices = self.iugu_service.get_all_invoices(created_at_from=start_date)
            
            if not invoices:
                return {"status": "success", "total_records": 0}
            
            # Converter para DataFrame
            df_iugu = self.iugu_service.convert_invoices_to_dataframe(invoices)
            
            if df_iugu.empty:
                return {"status": "success", "total_records": 0}
            
            # Limpar dados existentes e inserir novos
            with st.spinner("Substituindo dados..."):
                self.database.delete_all_data()
                result = self.database.insert_faturamento(df_iugu)
            
            self.last_sync = datetime.now()
            
            return {
                "status": "success",
                "total_records": result if result else 0,
                "period": f"{start_date} até hoje"
            }
            
        except Exception as e:
            st.error(f"❌ Erro na sincronização completa: {str(e)}")
            return {"status": "error", "message": str(e)}
    
    def get_sync_status(self) -> Dict:
        """Retorna status da sincronização"""
        return {
            "is_running": self.is_running,
            "last_sync": self.last_sync,
            "interval_minutes": self.sync_interval / 60 if self.sync_interval else 0
        }
    
    def sync_specific_period(self, start_date: str, end_date: str = None) -> Dict:
        """Sincroniza um período específico"""
        try:
            if end_date is None:
                end_date = datetime.now().strftime("%Y-%m-%d")
            
            st.info(f"🔄 Sincronizando período: {start_date} até {end_date}")
            
            # Buscar faturas do período específico
            invoices = self.iugu_service.get_all_invoices(
                created_at_from=start_date,
                created_at_to=end_date
            )
            
            if not invoices:
                return {"status": "success", "total_records": 0}
            
            # Converter para DataFrame
            df_iugu = self.iugu_service.convert_invoices_to_dataframe(invoices)
            
            if df_iugu.empty:
                return {"status": "success", "total_records": 0}
            
            # Inserir novos registros (sem substituir todos)
            result = self.database.insert_faturamento(df_iugu)
            
            self.last_sync = datetime.now()
            
            return {
                "status": "success",
                "total_records": result if result else 0,
                "period": f"{start_date} até {end_date}"
            }
            
        except Exception as e:
            st.error(f"❌ Erro na sincronização do período: {str(e)}")
            return {"status": "error", "message": str(e)}
    
    def sync_single_invoice(self, invoice_id: str) -> Dict:
        """Sincroniza uma fatura específica"""
        try:
            st.info(f"🔄 Sincronizando fatura: {invoice_id}")
            
            # Buscar fatura específica
            invoice = self.iugu_service.get_invoice_by_id(invoice_id)
            
            if not invoice:
                return {"status": "error", "message": "Fatura não encontrada"}
            
            # Converter para DataFrame
            df_iugu = self.iugu_service.convert_invoices_to_dataframe([invoice])
            
            if df_iugu.empty:
                return {"status": "error", "message": "Erro ao processar fatura"}
            
            # Verificar se já existe
            if self.database.check_iugu_id_exists(invoice_id):
                # Atualizar registro existente
                self.database._delete_by_iugu_id(invoice_id)
                result = self.database.insert_faturamento(df_iugu)
                action = "atualizada"
            else:
                # Inserir novo registro
                result = self.database.insert_faturamento(df_iugu)
                action = "inserida"
            
            self.last_sync = datetime.now()
            
            return {
                "status": "success",
                "action": action,
                "invoice_id": invoice_id,
                "records_affected": result if result else 0
            }
            
        except Exception as e:
            st.error(f"❌ Erro ao sincronizar fatura {invoice_id}: {str(e)}")
            return {"status": "error", "message": str(e)}
    
    def get_sync_statistics(self) -> Dict:
        """Retorna estatísticas detalhadas da sincronização"""
        try:
            # Buscar dados do banco
            df = self.database.get_all_faturamento()
            
            if df.empty:
                return {
                    "total_records": 0,
                    "iugu_records": 0,
                    "upload_records": 0,
                    "last_sync": self.last_sync,
                    "sync_coverage": 0
                }
            
            # Contar registros por origem
            total_records = len(df)
            iugu_records = 0
            upload_records = 0
            
            if 'iugu_id' in df.columns:
                iugu_records = df['iugu_id'].notna().sum()
                upload_records = df['iugu_id'].isna().sum()
            else:
                upload_records = total_records
            
            # Calcular cobertura da sincronização
            sync_coverage = (iugu_records / total_records * 100) if total_records > 0 else 0
            
            return {
                "total_records": total_records,
                "iugu_records": int(iugu_records),
                "upload_records": int(upload_records),
                "last_sync": self.last_sync,
                "sync_coverage": round(sync_coverage, 2),
                "is_running": self.is_running,
                "interval_minutes": self.sync_interval / 60 if self.sync_interval else 0
            }
            
        except Exception as e:
            st.error(f"❌ Erro ao calcular estatísticas: {str(e)}")
            return {
                "total_records": 0,
                "iugu_records": 0,
                "upload_records": 0,
                "last_sync": None,
                "sync_coverage": 0,
                "error": str(e)
            }
    
    def cleanup_old_data(self, days_to_keep: int = 365) -> Dict:
        """Remove dados antigos (mais de X dias)"""
        try:
            cutoff_date = datetime.now() - timedelta(days=days_to_keep)
            
            # Esta funcionalidade seria implementada no DatabaseManager
            # Por enquanto, apenas retorna informação
            
            return {
                "status": "info",
                "message": f"Funcionalidade de limpeza configurada para {days_to_keep} dias"
            }
            
        except Exception as e:
            return {"status": "error", "message": str(e)}