"use strict";

const express = require("express");
const fs = require("fs");
const path = require("path");
const QRCode = require("qrcode");
const { Client, LocalAuth, MessageMedia } = require("whatsapp-web.js");

const APP_TITLE = "WhatsApp Gateway Dev";
const PORT = Number(process.env.PORT || 8090);
const DATA_DIR = process.env.GATEWAY_DATA_DIR || "/data";
const DATA_FILE = path.join(DATA_DIR, "gateway-state.json");
const AUTH_DIR = path.join(DATA_DIR, ".wwebjs_auth");
const GATEWAY_TOKEN = String(process.env.GATEWAY_TOKEN || "").trim();
const CLIENT_ID = String(process.env.WHATSAPP_WEBJS_CLIENT_ID || process.env.EVOLUTION_INSTANCE || "system-church-dev").trim();
const CHROME_PATH = String(process.env.PUPPETEER_EXECUTABLE_PATH || "/usr/bin/chromium").trim();
const CONNECT_WAIT_MS = Number(process.env.WHATSAPP_WEBJS_CONNECT_WAIT_MS || 15000);
const STARTUP_AUTOLOAD = String(process.env.WHATSAPP_WEBJS_AUTOLOAD || "true").trim().toLowerCase() !== "false";

const app = express();
app.use(express.json({ limit: "2mb" }));

let client = null;
let initializePromise = null;

function buildDefaultStore() {
  return {
    status: {
      enabled: true,
      configured: true,
      mode: "whatsapp-web.js",
      instance_name: CLIENT_ID,
      webhook_url: null,
      manager_url: null,
      manager_api_key: null,
      webhook_enabled: false,
      connection_state: "not-started",
      pairing_code: null,
      qr_image: null,
      qr_text: null,
      qr_updated_at: null,
      last_qr_source: null,
      last_error: null,
      last_event: "BOOTSTRAP",
      last_event_at: nowIso(),
      last_webhook_payload: null,
      instance_exists: false,
      reachable: true,
      phone_number: null,
      client_info: null
    },
    messages: [],
    events: []
  };
}

function nowIso() {
  return new Date().toISOString();
}

function ensureDataFile() {
  fs.mkdirSync(DATA_DIR, { recursive: true });
  fs.mkdirSync(AUTH_DIR, { recursive: true });
  if (!fs.existsSync(DATA_FILE)) {
    fs.writeFileSync(DATA_FILE, JSON.stringify(buildDefaultStore(), null, 2));
  }
}

function readStore() {
  ensureDataFile();
  return JSON.parse(fs.readFileSync(DATA_FILE, "utf8"));
}

function writeStore(store) {
  ensureDataFile();
  fs.writeFileSync(DATA_FILE, JSON.stringify(store, null, 2));
}

function patchStatus(patch) {
  const store = readStore();
  store.status = {
    ...store.status,
    ...patch
  };
  writeStore(store);
  return store.status;
}

function appendEvent(source, eventType, payload = null) {
  const store = readStore();
  store.events.unshift({
    id: `${Date.now()}-${Math.random().toString(36).slice(2, 8)}`,
    created_at: nowIso(),
    source,
    event_type: eventType,
    payload
  });
  store.events = store.events.slice(0, 100);
  store.status.last_event = eventType;
  store.status.last_event_at = nowIso();
  if (payload !== null) {
    store.status.last_webhook_payload = payload;
  }
  writeStore(store);
}

function listMessages(limit = 100) {
  return readStore().messages.slice(0, limit);
}

function listEvents(limit = 30) {
  return readStore().events.slice(0, limit);
}

function normalizePhone(value) {
  let digits = String(value || "").replace(/\D+/g, "");
  if (!digits) {
    throw new Error("Recipient phone is required");
  }
  if (digits.startsWith("00")) {
    digits = digits.slice(2);
  }
  if (!digits.startsWith("55")) {
    digits = `55${digits}`;
  }
  return digits;
}

function normalizeConnectionState(value) {
  const state = String(value || "").trim().toLowerCase();
  if (state === "connected") {
    return "open";
  }
  return state;
}

function isSessionReady(connectionState) {
  return normalizeConnectionState(connectionState) === "open";
}

function requireAuth(req) {
  if (!GATEWAY_TOKEN) return;
  const expected = `Bearer ${GATEWAY_TOKEN}`;
  if (req.headers.authorization !== expected) {
    const error = new Error("Invalid gateway token");
    error.statusCode = 401;
    throw error;
  }
}

async function qrToDataUrl(qrText) {
  return QRCode.toDataURL(qrText, {
    errorCorrectionLevel: "M",
    margin: 2,
    width: 360
  });
}

function clearQrState(extra = {}) {
  return patchStatus({
    qr_image: null,
    qr_text: null,
    pairing_code: null,
    qr_updated_at: null,
    last_qr_source: null,
    ...extra
  });
}

function removeChromiumSingletonLocks(dirPath) {
  if (!fs.existsSync(dirPath)) return;
  const entries = fs.readdirSync(dirPath, { withFileTypes: true });
  for (const entry of entries) {
    const fullPath = path.join(dirPath, entry.name);
    if (entry.isDirectory()) {
      removeChromiumSingletonLocks(fullPath);
      continue;
    }
    if (entry.name.startsWith("Singleton")) {
      try {
        fs.rmSync(fullPath, { force: true });
      } catch (_error) {
      }
    }
  }
}

async function createClient() {
  removeChromiumSingletonLocks(AUTH_DIR);
  const authStrategy = new LocalAuth({
    clientId: CLIENT_ID,
    dataPath: AUTH_DIR,
    rmMaxRetries: 5
  });

  const nextClient = new Client({
    authStrategy,
    takeoverOnConflict: true,
    takeoverTimeoutMs: 0,
    restartOnAuthFail: false,
    puppeteer: {
      executablePath: CHROME_PATH,
      headless: true,
      args: [
        "--no-sandbox",
        "--disable-setuid-sandbox",
        "--disable-dev-shm-usage",
        "--disable-gpu",
        "--no-first-run",
        "--no-default-browser-check",
        "--disable-extensions",
        "--disable-background-networking",
        "--disable-background-timer-throttling",
        "--disable-renderer-backgrounding",
        "--disable-features=Translate,BackForwardCache"
      ]
    }
  });

  nextClient.on("qr", async (qrText) => {
    const qrImage = await qrToDataUrl(qrText);
    patchStatus({
      instance_exists: true,
      connection_state: "qr",
      qr_image: qrImage,
      qr_text: qrText,
      qr_updated_at: nowIso(),
      last_qr_source: "whatsapp-web.js",
      last_error: null
    });
    appendEvent("whatsapp-web.js", "QRCODE_UPDATED", {
      has_qr: true
    });
  });

  nextClient.on("loading_screen", (percent, message) => {
    patchStatus({
      instance_exists: true,
      connection_state: "connecting",
      last_error: null
    });
    appendEvent("whatsapp-web.js", "LOADING_SCREEN", {
      percent,
      message
    });
  });

  nextClient.on("authenticated", () => {
    patchStatus({
      instance_exists: true,
      connection_state: "authenticated",
      last_error: null
    });
    appendEvent("whatsapp-web.js", "AUTHENTICATED");
  });

  nextClient.on("ready", async () => {
    let phoneNumber = null;
    let clientInfo = null;
    try {
      const info = nextClient.info || null;
      if (info && info.wid && info.wid.user) {
        phoneNumber = info.wid.user;
      }
      if (typeof nextClient.getWWebVersion === "function") {
        clientInfo = {
          web_version: await nextClient.getWWebVersion()
        };
      }
    } catch (_error) {
    }
    clearQrState({
      instance_exists: true,
      connection_state: "open",
      last_error: null,
      phone_number: phoneNumber,
      client_info: clientInfo
    });
    appendEvent("whatsapp-web.js", "READY", {
      phone_number: phoneNumber
    });
  });

  nextClient.on("auth_failure", (message) => {
    patchStatus({
      instance_exists: true,
      connection_state: "auth_failure",
      last_error: String(message || "Authentication failed")
    });
    appendEvent("whatsapp-web.js", "AUTH_FAILURE", {
      message
    });
  });

  nextClient.on("change_state", (state) => {
    patchStatus({
      instance_exists: true,
      connection_state: normalizeConnectionState(state || "unknown"),
      last_error: null
    });
    appendEvent("whatsapp-web.js", "CONNECTION_UPDATE", {
      state
    });
  });

  nextClient.on("disconnected", (reason) => {
    patchStatus({
      instance_exists: true,
      connection_state: "close",
      last_error: reason ? String(reason) : null
    });
    appendEvent("whatsapp-web.js", "DISCONNECTED", {
      reason
    });
  });

  return nextClient;
}

async function ensureClientStarted() {
  if (client) return client;
  if (!initializePromise) {
    initializePromise = (async () => {
      patchStatus({
        instance_exists: true,
        connection_state: "starting",
        last_error: null
      });
      client = await createClient();
      await client.initialize();
      return client;
    })().finally(() => {
      initializePromise = null;
    });
  }
  return initializePromise;
}

async function destroyClient({ clearSession = false } = {}) {
  const current = client;
  client = null;
  initializePromise = null;
  if (current) {
    try {
      await current.destroy();
    } catch (_error) {
    }
  }
  if (clearSession) {
    try {
      fs.rmSync(AUTH_DIR, { recursive: true, force: true });
    } catch (_error) {
    }
    fs.mkdirSync(AUTH_DIR, { recursive: true });
  }
}

async function waitForQrOrReady(timeoutMs) {
  const startedAt = Date.now();
  while (Date.now() - startedAt < timeoutMs) {
    const status = readStore().status;
    if (status.qr_image || isSessionReady(status.connection_state) || status.connection_state === "auth_failure") {
      return status;
    }
    await new Promise((resolve) => setTimeout(resolve, 500));
  }
  return readStore().status;
}

function getStatusPayload() {
  const status = readStore().status;
  return {
    ...status,
    enabled: true,
    configured: true,
    mode: "whatsapp-web.js",
    instance_name: CLIENT_ID,
    manager_url: null,
    manager_api_key: null,
    webhook_enabled: false,
    instance_exists: status.instance_exists || fs.existsSync(AUTH_DIR),
    reachable: true,
    instance: {
      instanceName: CLIENT_ID,
      connectionStatus: status.connection_state || "not-started",
      number: status.phone_number || null
    }
  };
}

function pushMessageRecord(record) {
  const store = readStore();
  store.messages.unshift(record);
  store.messages = store.messages.slice(0, 300);
  writeStore(store);
}

function updateMessageRecord(id, patch) {
  const store = readStore();
  store.messages = store.messages.map((item) => {
    if (item.id !== id) return item;
    return {
      ...item,
      ...patch,
      updated_at: nowIso()
    };
  });
  writeStore(store);
}

function normalizeMediaEntries(entries) {
  if (!Array.isArray(entries)) return [];
  return entries
    .filter((entry) => entry && typeof entry === "object")
    .map((entry, index) => {
      const mimeType = String(entry.mime_type || entry.mimetype || "application/octet-stream").trim();
      const dataBase64 = String(entry.data_base64 || entry.base64 || "").trim();
      const filename = String(entry.filename || `attachment-${index + 1}`).trim();
      const caption = typeof entry.caption === "string" ? entry.caption : "";
      if (!dataBase64) return null;
      return {
        mimeType,
        dataBase64,
        filename,
        caption
      };
    })
    .filter(Boolean);
}

function buildProviderResponse(response, fallbackBody) {
  return {
    id: response && response.id ? response.id._serialized || null : null,
    to: response && response.to ? response.to : null,
    body: response && response.body ? response.body : fallbackBody,
    timestamp: response && response.timestamp ? response.timestamp : null
  };
}

async function sendViaClient(recipient, payload) {
  await ensureClientStarted();
  const status = getStatusPayload();
  if (!isSessionReady(status.connection_state)) {
    throw new Error("WhatsApp Web ainda não está conectado. Leia o QR Code em dev antes de enviar mensagens.");
  }
  const chatId = `${recipient}@c.us`;
  const message = typeof payload === "string"
    ? payload
    : String((payload && payload.message) || "");
  const mediaEntries = normalizeMediaEntries(payload && payload.media);

  if (!message && mediaEntries.length === 0) {
    throw new Error("Message or media payload is required");
  }

  const providerResponses = [];
  if (mediaEntries.length === 1) {
    const mediaEntry = mediaEntries[0];
    const media = new MessageMedia(mediaEntry.mimeType, mediaEntry.dataBase64, mediaEntry.filename);
    const response = await client.sendMessage(chatId, media, {
      caption: mediaEntry.caption || message || undefined
    });
    providerResponses.push(buildProviderResponse(response, message));
    return providerResponses;
  }

  if (message) {
    const response = await client.sendMessage(chatId, message);
    providerResponses.push(buildProviderResponse(response, message));
  }

  for (const mediaEntry of mediaEntries) {
    const media = new MessageMedia(mediaEntry.mimeType, mediaEntry.dataBase64, mediaEntry.filename);
    const response = await client.sendMessage(chatId, media, {
      caption: mediaEntry.caption || undefined
    });
    providerResponses.push(buildProviderResponse(response, mediaEntry.caption || mediaEntry.filename));
  }

  return providerResponses;
}

app.get("/health", (_req, res) => {
  res.json({
    status: "healthy",
    service: APP_TITLE,
    mode: "whatsapp-web.js",
    instance: CLIENT_ID
  });
});

app.get("/messages", (req, res) => {
  const limit = Math.max(1, Math.min(Number(req.query.limit || 100), 500));
  res.json({ items: listMessages(limit) });
});

app.get("/events", (req, res) => {
  const limit = Math.max(1, Math.min(Number(req.query.limit || 30), 100));
  res.json({ items: listEvents(limit) });
});

app.get("/evolution/status", (_req, res) => {
  res.json(getStatusPayload());
});

app.post("/evolution/setup", async (_req, res, next) => {
  try {
    await ensureClientStarted();
    const status = await waitForQrOrReady(8000);
    res.json({
      accepted: true,
      result: {
        provider: "whatsapp-web.js"
      },
      status
    });
  } catch (error) {
    next(error);
  }
});

app.post("/evolution/connect", async (_req, res, next) => {
  try {
    await ensureClientStarted();
    const status = await waitForQrOrReady(CONNECT_WAIT_MS);
    res.json({
      accepted: true,
      response: {
        provider: "whatsapp-web.js",
        has_qr: Boolean(status.qr_image)
      },
      status
    });
  } catch (error) {
    next(error);
  }
});

app.post("/evolution/logout", async (_req, res, next) => {
  try {
    await destroyClient({ clearSession: true });
    clearQrState({
      instance_exists: false,
      connection_state: "close",
      phone_number: null,
      client_info: null,
      last_error: null
    });
    appendEvent("whatsapp-web.js", "LOGOUT");
    res.json({
      accepted: true,
      response: {
        provider: "whatsapp-web.js",
        logged_out: true
      },
      status: getStatusPayload()
    });
  } catch (error) {
    next(error);
  }
});

app.post("/evolution/webhook", (req, res) => {
  appendEvent("system-church", "WEBHOOK_FORWARD_IGNORED", req.body || null);
  res.json({
    accepted: true,
    provider: "whatsapp-web.js"
  });
});

app.post("/send", async (req, res, next) => {
  try {
    requireAuth(req);
    const recipient = normalizePhone(req.body.to);
    const messageId = `${Date.now()}-${Math.random().toString(36).slice(2, 8)}`;
    pushMessageRecord({
      id: messageId,
      created_at: nowIso(),
      updated_at: nowIso(),
      recipient,
      message: String(req.body.message || ""),
      media_count: Array.isArray(req.body.media) ? req.body.media.length : 0,
      event_notification_id: req.body.event_notification_id || null,
      status: "queued",
      provider: "whatsapp-web.js",
      provider_response: null,
      error_message: null
    });

    const providerResponse = await sendViaClient(recipient, {
      message: String(req.body.message || ""),
      media: req.body.media
    });
    updateMessageRecord(messageId, {
      status: "sent",
      provider_response: providerResponse
    });
    appendEvent("whatsapp-web.js", "SEND_MESSAGE", {
      recipient
    });
    res.json({
      accepted: true,
      gateway_message_id: messageId,
      provider: "whatsapp-web.js",
      recipient
    });
  } catch (error) {
    const messageId = req.body && req.body.id ? String(req.body.id) : null;
    if (messageId) {
      updateMessageRecord(messageId, {
        status: "failed",
        error_message: error.message
      });
    }
    next(error);
  }
});

app.get("/", (_req, res) => {
  const status = getStatusPayload();
  res.type("html").send(`
    <!doctype html>
    <html lang="pt-BR">
      <head>
        <meta charset="utf-8" />
        <meta name="viewport" content="width=device-width, initial-scale=1" />
        <title>${APP_TITLE}</title>
        <style>
          body { font: 16px/1.5 Arial, sans-serif; margin: 0; background: #f4f7f5; color: #18312b; }
          main { max-width: 860px; margin: 0 auto; padding: 24px; }
          section { background: #fff; border: 1px solid #d9e7df; border-radius: 18px; padding: 20px; margin-bottom: 16px; }
          h1, h2 { margin-top: 0; }
          .qr { min-height: 360px; display: grid; place-items: center; border: 2px dashed #cfe0d6; border-radius: 16px; }
          .qr img { max-width: 340px; width: 100%; height: auto; }
          code, pre { white-space: pre-wrap; word-break: break-word; }
          .muted { color: #5d736c; }
        </style>
      </head>
      <body>
        <main>
          <section>
            <h1>${APP_TITLE}</h1>
            <p class="muted">Gateway próprio de dev com <code>whatsapp-web.js</code>.</p>
            <pre>${JSON.stringify(status, null, 2)}</pre>
          </section>
          <section>
            <h2>QR</h2>
            <div class="qr">
              ${status.qr_image ? `<img src="${status.qr_image}" alt="QR Code do WhatsApp" />` : "<p class=\"muted\">Ainda sem QR disponível.</p>"}
            </div>
          </section>
        </main>
      </body>
    </html>
  `);
});

app.use((error, _req, res, _next) => {
  const statusCode = Number(error.statusCode || 500);
  const detail = error.message || "Unexpected error";
  patchStatus({
    last_error: detail
  });
  appendEvent("whatsapp-web.js", "ERROR", {
    detail,
    status_code: statusCode
  });
  res.status(statusCode).json({ detail });
});

async function bootstrap() {
  ensureDataFile();
  appendEvent("gateway", "BOOT");
  if (STARTUP_AUTOLOAD) {
    ensureClientStarted().catch((error) => {
      patchStatus({
        connection_state: "error",
        last_error: error.message
      });
      appendEvent("whatsapp-web.js", "STARTUP_ERROR", {
        detail: error.message
      });
    });
  }
  app.listen(PORT, "0.0.0.0");
}

process.on("SIGTERM", async () => {
  await destroyClient();
  process.exit(0);
});

process.on("SIGINT", async () => {
  await destroyClient();
  process.exit(0);
});

bootstrap().catch((error) => {
  console.error(error);
  process.exit(1);
});
