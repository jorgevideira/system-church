# Gateway de WhatsApp em Dev

Este ambiente cria um gateway próprio apenas para `dev`, sem alterar `prod`.

## Como funciona

- O backend do System Church continua enviando notificações para `WHATSAPP_WEBHOOK_URL`.
- Em `dev`, essa URL aponta para o serviço `whatsapp-gateway`.
- O gateway usa `whatsapp-web.js` para:
  - abrir a sessão do WhatsApp Web
  - gerar o QR Code dentro do sistema
  - consultar o estado da conexão
  - desconectar a sessão quando quiser testar novamente
  - enviar texto e mídia, incluindo o QR de check-in do evento

## Fluxo de conexão

1. Suba o ambiente `dev`.
2. Acesse `Configurações > WhatsApp` no sistema.
3. Clique em `Preparar instância`.
4. Clique em `Gerar QR`.
5. Leia o QR Code com o WhatsApp do aparelho que será usado no disparo.

## Payload esperado pelo gateway

Texto simples:

```json
{
  "to": "5511999999999",
  "message": "Pagamento confirmado para sua inscrição.",
  "event_notification_id": 123
}
```

Texto com mídia:

```json
{
  "to": "5511999999999",
  "message": "Pagamento confirmado para sua inscrição.",
  "media": [
    {
      "mime_type": "image/png",
      "filename": "checkin.png",
      "data_base64": "<png em base64>",
      "caption": "QR de check-in"
    }
  ],
  "event_notification_id": 123
}
```

## Endpoints do gateway

- `GET /health`
- `GET /messages`
- `GET /events`
- `GET /evolution/status`
- `POST /evolution/setup`
- `POST /evolution/connect`
- `POST /evolution/logout`
- `POST /evolution/webhook`
- `POST /send`
- `GET /`

## Variáveis principais do dev

- `WHATSAPP_WEBHOOK_URL=http://whatsapp-gateway:8090/send`
- `WHATSAPP_WEBHOOK_TOKEN=dev-whatsapp-gateway-token`
- `WHATSAPP_WEBJS_CLIENT_ID=system-church-dev`
- `WHATSAPP_WEBJS_CONNECT_WAIT_MS=15000`
- `WHATSAPP_WEBJS_AUTOLOAD=true`

## Observações

- Tudo isso está limitado ao `docker-compose.dev.yml`.
- O `prod` não recebe esse serviço nem essa configuração.
- O histórico de mensagens e eventos do gateway fica salvo em JSON dentro do volume `whatsapp_gateway_data`.
