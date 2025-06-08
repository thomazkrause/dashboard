import streamlit as st
import pandas as pd
from datetime import datetime, date
import re

class FormComponents:
    @staticmethod
    def validate_cpf_cnpj(document):
        """Valida CPF ou CNPJ"""
        if not document:
            return False, "Documento é obrigatório"
        
        # Remove caracteres especiais
        clean_doc = re.sub(r'[^0-9]', '', document)
        
        if len(clean_doc) == 11:
            # Validação básica de CPF
            if len(set(clean_doc)) == 1:
                return False, "CPF inválido"
            return True, "CPF válido"
        elif len(clean_doc) == 14:
            # Validação básica de CNPJ
            if len(set(clean_doc)) == 1:
                return False, "CNPJ inválido"
            return True, "CNPJ válido"
        else:
            return False, "Documento deve ter 11 dígitos (CPF) ou 14 dígitos (CNPJ)"
    
    @staticmethod
    def format_currency_input(value):
        """Formata entrada de moeda"""
        if value is None or value == "":
            return 0.0
        
        try:
            # Remove caracteres especiais e converte
            clean_value = str(value).replace('R$', '').replace('.', '').replace(',', '.').strip()
            return float(clean_value)
        except (ValueError, TypeError):
            return 0.0
    
    @staticmethod
    def create_manual_form():
        """Cria formulário para inserção manual de registro"""
        st.subheader("✏️ Inserir Novo Registro")
        
        with st.form("manual_record_form", clear_on_submit=True):
            # Organizar em colunas para melhor layout
            col1, col2 = st.columns(2)
            
            with col1:
                # Dados do Cliente
                st.markdown("**👤 Dados do Cliente**")
                nome = st.text_input(
                    "Nome Completo *",
                    placeholder="Ex: João Silva Santos",
                    help="Nome completo do cliente"
                )
                
                cpf_cnpj = st.text_input(
                    "CPF/CNPJ *",
                    placeholder="Ex: 123.456.789-00 ou 12.345.678/0001-90",
                    help="CPF (11 dígitos) ou CNPJ (14 dígitos)"
                )
                
                # Validação em tempo real do documento
                if cpf_cnpj:
                    is_valid, message = FormComponents.validate_cpf_cnpj(cpf_cnpj)
                    if is_valid:
                        st.success(f"✅ {message}")
                    else:
                        st.error(f"❌ {message}")
                
                # Valores Financeiros
                st.markdown("**💰 Valores**")
                total = st.number_input(
                    "Valor Total (R$) *",
                    min_value=0.0,
                    value=0.0,
                    step=0.01,
                    format="%.2f",
                    help="Valor total da transação"
                )
                
                taxa = st.number_input(
                    "Taxa (R$)",
                    min_value=0.0,
                    value=0.0,
                    step=0.01,
                    format="%.2f",
                    help="Taxa cobrada na transação"
                )
            
            with col2:
                # Status e Pagamento
                st.markdown("**📊 Status e Pagamento**")
                situacao = st.selectbox(
                    "Situação *",
                    options=["Paga", "Pendente", "Expirado"],
                    help="Status atual da transação"
                )
                
                metodos_pagamento = [
                    "Cartão de Crédito",
                    "Cartão de Débito", 
                    "PIX",
                    "Boleto",
                    "Transferência Bancária",
                    "Dinheiro",
                    "Não Informado"
                ]
                
                paga_com = st.selectbox(
                    "Método de Pagamento",
                    options=metodos_pagamento,
                    index=6,  # "Não Informado" como padrão
                    help="Como foi realizado o pagamento"
                )
                
                # Datas
                st.markdown("**📅 Datas**")
                data_criacao = st.date_input(
                    "Data de Criação *",
                    value=date.today(),
                    help="Data quando a transação foi criada"
                )
                
                data_pagamento = st.date_input(
                    "Data do Pagamento",
                    value=None,
                    help="Data quando foi efetuado o pagamento (opcional)"
                )
                
                # Horário (opcional)
                incluir_horario = st.checkbox("Incluir horário específico")
                
                if incluir_horario:
                    hora_criacao = st.time_input(
                        "Horário de Criação",
                        value=datetime.now().time(),
                        help="Horário específico da criação"
                    )
                else:
                    hora_criacao = None
            
            # Botões de ação
            st.markdown("---")
            col1, col2, col3 = st.columns([2, 1, 1])
            
            with col1:
                st.markdown("**📝 Campos obrigatórios marcados com ***")
            
            with col2:
                submitted = st.form_submit_button(
                    "💾 Salvar Registro",
                    type="primary",
                    use_container_width=True
                )
            
            with col3:
                reset_form = st.form_submit_button(
                    "🔄 Limpar",
                    use_container_width=True
                )
            
            # Validação e processamento
            if submitted:
                # Validações obrigatórias
                errors = []
                
                if not nome.strip():
                    errors.append("Nome é obrigatório")
                
                if not cpf_cnpj.strip():
                    errors.append("CPF/CNPJ é obrigatório")
                else:
                    is_valid, message = FormComponents.validate_cpf_cnpj(cpf_cnpj)
                    if not is_valid:
                        errors.append(f"CPF/CNPJ: {message}")
                
                if total <= 0:
                    errors.append("Valor total deve ser maior que zero")
                
                if not data_criacao:
                    errors.append("Data de criação é obrigatória")
                
                # Se há erros, mostrar e não processar
                if errors:
                    st.error("❌ **Erros encontrados:**")
                    for error in errors:
                        st.error(f"• {error}")
                    return None
                
                # Processar datas
                if incluir_horario and hora_criacao:
                    data_criacao_final = datetime.combine(data_criacao, hora_criacao)
                else:
                    data_criacao_final = datetime.combine(data_criacao, datetime.min.time())
                
                data_pagamento_final = None
                if data_pagamento:
                    data_pagamento_final = datetime.combine(data_pagamento, datetime.min.time())
                
                # Criar registro
                novo_registro = {
                    'Nome': nome.strip(),
                    'CPF/CNPJ': cpf_cnpj.strip(),
                    'Total': total,
                    'Taxa': taxa,
                    'Situação': situacao,
                    'Paga com': paga_com if paga_com != "Não Informado" else None,
                    'Data de criação': data_criacao_final,
                    'Data do pagamento': data_pagamento_final
                }
                
                return novo_registro
            
            if reset_form:
                st.rerun()
        
        return None
    
    @staticmethod
    def display_form_preview(registro):
        """Exibe preview do registro antes de salvar"""
        st.subheader("👀 Preview do Registro")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("**📋 Dados Inseridos:**")
            st.write(f"**Nome:** {registro['Nome']}")
            st.write(f"**CPF/CNPJ:** {registro['CPF/CNPJ']}")
            st.write(f"**Valor Total:** R$ {registro['Total']:,.2f}")
            st.write(f"**Taxa:** R$ {registro['Taxa']:,.2f}")
        
        with col2:
            st.write(f"**Situação:** {registro['Situação']}")
            st.write(f"**Método Pagamento:** {registro['Paga com'] or 'Não Informado'}")
            st.write(f"**Data Criação:** {registro['Data de criação'].strftime('%d/%m/%Y %H:%M')}")
            if registro['Data do pagamento']:
                st.write(f"**Data Pagamento:** {registro['Data do pagamento'].strftime('%d/%m/%Y')}")
            else:
                st.write("**Data Pagamento:** Não informada")
        
        # Confirmar salvamento
        col1, col2, col3 = st.columns([2, 1, 1])
        
        with col2:
            if st.button("✅ Confirmar e Salvar", type="primary", use_container_width=True):
                return True
        
        with col3:
            if st.button("❌ Cancelar", use_container_width=True):
                return False
        
        return None
    
    @staticmethod
    def create_bulk_form():
        """Cria formulário para inserção de múltiplos registros"""
        st.subheader("📋 Inserção em Lote")
        
        with st.expander("➕ Adicionar Múltiplos Registros"):
            # Template para download
            st.markdown("**📥 Template para Inserção em Lote:**")
            
            template_data = {
                'Nome': ['João Silva', 'Maria Santos', 'Pedro Oliveira'],
                'CPF/CNPJ': ['12345678901', '98765432100', '11122233344'],
                'Total': [150.00, 300.50, 75.25],
                'Taxa': [5.00, 10.00, 2.50],
                'Situação': ['Paga', 'Pendente', 'Paga'],
                'Paga com': ['PIX', 'Cartão', 'Boleto'],
                'Data de criação': ['2024-01-15', '2024-01-16', '2024-01-17'],
                'Data do pagamento': ['2024-01-15', '', '2024-01-17']
            }
            
            template_df = pd.DataFrame(template_data)
            
            # Botão para download do template
            csv_template = template_df.to_csv(index=False)
            st.download_button(
                label="📥 Baixar Template CSV",
                data=csv_template,
                file_name="template_registros.csv",
                mime="text/csv",
                help="Baixe este template, preencha com seus dados e faça upload"
            )
            
            # Área de texto para inserção manual
            st.markdown("**✏️ Ou cole seus dados aqui (formato CSV):**")
            
            bulk_text = st.text_area(
                "Dados CSV",
                height=200,
                placeholder="Nome,CPF/CNPJ,Total,Taxa,Situação,Paga com,Data de criação,Data do pagamento\nJoão Silva,12345678901,150.00,5.00,Paga,PIX,2024-01-15,2024-01-15",
                help="Cole seus dados no formato CSV (separados por vírgula)"
            )
            
            if st.button("📊 Processar Dados em Lote"):
                if bulk_text.strip():
                    try:
                        # Processar dados CSV
                        from io import StringIO
                        csv_data = StringIO(bulk_text)
                        df_bulk = pd.read_csv(csv_data)
                        
                        # Validar colunas obrigatórias
                        required_cols = ['Nome', 'CPF/CNPJ', 'Total', 'Situação']
                        missing_cols = [col for col in required_cols if col not in df_bulk.columns]
                        
                        if missing_cols:
                            st.error(f"❌ Colunas obrigatórias faltando: {', '.join(missing_cols)}")
                        else:
                            st.success(f"✅ {len(df_bulk)} registros processados com sucesso!")
                            st.dataframe(df_bulk)
                            
                            return df_bulk
                    
                    except Exception as e:
                        st.error(f"❌ Erro ao processar dados: {str(e)}")
                        st.info("💡 Verifique o formato dos dados e tente novamente")
                else:
                    st.warning("⚠️ Insira os dados para processar")
        
        return None