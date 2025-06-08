import requests
import pandas as pd
from datetime import datetime
import streamlit as st
from typing import Dict, List, Optional

class IuguService:
    def __init__(self, api_token: str):
        """
        Inicializa o serviço da Iugu
        
        Args:
            api_token: Token da API da Iugu
        """
        self.api_token = api_token
        self.base_url = "https://api.iugu.com/v1"
        self.headers = {
            "Accept": "application/json",
            "Content-Type": "application/json"
        }
        self.auth = (api_token, "")  # Iugu usa HTTP Basic Auth com token como username
    
    def test_connection(self) -> bool:
        """Testa a conexão com a API da Iugu"""
        try:
            response = requests.get(
                f"{self.base_url}/accounts",
                auth=self.auth,
                headers=self.headers,
                timeout=10
            )
            return response.status_code == 200
        except Exception as e:
            return False
    
    def get_invoices(self, limit: int = 100, created_at_from: str = None, created_at_to: str = None) -> List[Dict]:
        """
        Busca faturas da Iugu
        
        Args:
            limit: Número máximo de faturas para buscar
            created_at_from: Data inicial (formato: YYYY-MM-DD)
            created_at_to: Data final (formato: YYYY-MM-DD)
        """
        try:
            params = {
                "limit": min(limit, 100),  # Iugu limita em 100 por request
                "sortBy": "created_at",
                "sortOrder": "desc"
            }
            
            if created_at_from:
                params["created_at_from"] = created_at_from
            if created_at_to:
                params["created_at_to"] = created_at_to
            
            response = requests.get(
                f"{self.base_url}/invoices",
                auth=self.auth,
                headers=self.headers,
                params=params,
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                return data.get("items", [])
            else:
                st.error(f"Erro API Iugu: {response.status_code}")
                return []
                
        except Exception as e:
            st.error(f"Erro ao buscar faturas: {str(e)}")
            return []
    
    def get_all_invoices(self, created_at_from: str = None, created_at_to: str = None) -> List[Dict]:
        """
        Busca todas as faturas usando paginação
        """
        all_invoices = []
        page = 0
        
        while True:
            try:
                params = {
                    "limit": 100,
                    "start": page * 100,
                    "sortBy": "created_at",
                    "sortOrder": "desc"
                }
                
                if created_at_from:
                    params["created_at_from"] = created_at_from
                if created_at_to:
                    params["created_at_to"] = created_at_to
                
                response = requests.get(
                    f"{self.base_url}/invoices",
                    auth=self.auth,
                    headers=self.headers,
                    params=params,
                    timeout=30
                )
                
                if response.status_code == 200:
                    data = response.json()
                    items = data.get("items", [])
                    
                    if not items:
                        break
                    
                    all_invoices.extend(items)
                    
                    # Se retornou menos que 100, chegamos ao fim
                    if len(items) < 100:
                        break
                    
                    page += 1
                else:
                    break
                    
            except Exception as e:
                break
        
        return all_invoices
    
    def convert_invoices_to_dataframe(self, invoices: List[Dict]) -> pd.DataFrame:
        """
        Converte faturas da Iugu para DataFrame compatível com o sistema atual
        """
        records = []
        
        for invoice in invoices:
            try:
                # Mapear status da Iugu para o formato usado no sistema
                status_mapping = {
                    "paid": "Paga",
                    "pending": "Pendente",
                    "canceled": "Expirado",
                    "expired": "Expirado",
                    "draft": "Pendente"
                }
                
                # Extrair método de pagamento
                payment_method = "Não Informado"
                if invoice.get("paid_at"):
                    payment_method = "PIX"  # Simplificado por enquanto
                
                record = {
                    "Nome": invoice.get("email", ""),
                    "CPF/CNPJ": invoice.get("payer", {}).get("cpf_cnpj", ""),
                    "Total": float(invoice.get("total_cents", 0)) / 100,  # Iugu usa centavos
                    "Taxa": float(invoice.get("taxes_paid", 0)) / 100,
                    "Situação": status_mapping.get(invoice.get("status"), "Pendente"),
                    "Paga com": payment_method,
                    "Data de criação": invoice.get("created_at"),
                    "Data do pagamento": invoice.get("paid_at"),
                    "iugu_id": invoice.get("id"),
                    "iugu_url": invoice.get("secure_url", "")
                }
                
                # Tentar extrair nome do payer se disponível
                if invoice.get("payer", {}).get("name"):
                    record["Nome"] = invoice.get("payer", {}).get("name")
                
                records.append(record)
                
            except Exception as e:
                continue
        
        return pd.DataFrame(records)
    
    def get_invoice_by_id(self, invoice_id: str) -> Optional[Dict]:
        """Busca uma fatura específica pelo ID"""
        try:
            response = requests.get(
                f"{self.base_url}/invoices/{invoice_id}",
                auth=self.auth,
                headers=self.headers,
                timeout=10
            )
            
            if response.status_code == 200:
                return response.json()
            else:
                return None
                
        except Exception as e:
            return None