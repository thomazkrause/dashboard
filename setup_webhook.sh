# setup_webhook.sh
#!/bin/bash

echo "🔧 Configurando webhook da Iugu..."

# URL do seu servidor (substitua pela sua URL real)
WEBHOOK_URL="https://api-accounting.talqui.chat/webhooks/iugu/invoice-update"
IUGU_TOKEN="433118AEADA80C229DB09897CAA5D8043FCBADD50A785D863C54195C6C3784E8"

# Criar webhook na Iugu
curl -X POST "https://api.iugu.com/v1/web_hooks" \
  -u "$IUGU_TOKEN:" \
  -H "Content-Type: application/json" \
  -d '{
    "event": "all",
    "url": "'$WEBHOOK_URL'",
    "authorization": "seu_webhook_secret_aqui"
  }'

echo "✅ Webhook configurado!"