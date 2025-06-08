# webhook_handler.py
from flask import Flask, request, jsonify
import json
from datetime import datetime
from database import DatabaseManager
from iugu_service import IuguService

app = Flask(__name__)

# Configurar seus tokens aqui
IUGU_TOKEN = "seu_token_aqui"
WEBHOOK_SECRET = "seu_webhook_secret_aqui"  # Configure no painel da Iugu

@app.route('/webhook/iugu', methods=['POST'])
def handle_iugu_webhook():
    try:
        # Verificar se é um webhook válido da Iugu
        signature = request.headers.get('X-Iugu-Signature')
        
        # Aqui você deve verificar a assinatura do webhook
        # Por simplicidade, vamos pular essa verificação
        
        data = request.get_json()
        
        # Processar diferentes tipos de eventos
        event_type = data.get('event')
        
        if event_type in ['invoice.created', 'invoice.status_changed', 'invoice.payment_completed']:
            invoice_id = data.get('data', {}).get('id')
            
            if invoice_id:
                # Buscar fatura atualizada da API
                iugu_service = IuguService(IUGU_TOKEN)
                invoice = iugu_service.get_invoice_by_id(invoice_id)
                
                if invoice:
                    # Converter para DataFrame
                    df = iugu_service.convert_invoices_to_dataframe([invoice])
                    
                    # Atualizar banco de dados
                    db = DatabaseManager()
                    
                    # Verificar se já existe
                    if db.check_iugu_id_exists(invoice_id):
                        # Atualizar registro existente
                        db._delete_by_iugu_id(invoice_id)
                    
                    # Inserir/atualizar
                    db.insert_faturamento(df)
                    
                    return jsonify({"status": "success", "message": f"Invoice {invoice_id} processed"})
        
        return jsonify({"status": "ignored", "message": "Event type not handled"})
        
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=False)