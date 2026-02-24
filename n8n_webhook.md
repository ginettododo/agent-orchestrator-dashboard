---
name: InviaPayload_n8n
description: Inviare dati strutturati dal bot a n8n tramite HTTP Webhook su rete Tailscale.
---

# Istruzioni Esecutive
Quando devi delegare task a n8n o inviare dati per triggerare un'automazione, devi eseguire una richiesta HTTP POST (tramite script JS interno o CURL) secondo i seguenti parametri stretti.

# Routing e Rete 
- **Endpoint Tassativo**: `http://100.99.114.7:5678/webhook/<TUO-ENDPOINT>`
- DIVIETO ASSOLUTO di chiamare `localhost`, `n8n` o qualsiasi hostname interno di Docker.

# Configurazione Richiesta
- Method: `POST`
- Header: `Content-Type: application/json`
- Body: Payload JSON compatibile con l'attesa di n8n.

# Esempio Modello
```javascript
const response = await fetch("http://100.99.114.7:5678/webhook/il-tuo-webhook-id", {
  method: "POST",
  headers: { "Content-Type": "application/json" },
  body: JSON.stringify({ azione: "ticket_creato", data: Date.now() })
});
```
