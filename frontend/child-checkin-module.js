(function () {
  const apiPrefix = "/api/v1/child-checkin";

  const el = {
    moduleKidsBtn: document.getElementById("moduleKidsBtn"),
    kidsModule: document.getElementById("kidsModule"),
    kidsModuleContent: document.getElementById("kidsModuleContent"),
    financeModule: document.getElementById("financeModule"),
    cellsModule: document.getElementById("cellsModule"),
    bibleSchoolModule: document.getElementById("bibleSchoolModule"),
    eventsModule: document.getElementById("eventsModule"),
    usersModule: document.getElementById("usersModule"),
    moduleFinanceBtn: document.getElementById("moduleFinanceBtn"),
    moduleCellsBtn: document.getElementById("moduleCellsBtn"),
    moduleBibleSchoolBtn: document.getElementById("moduleBibleSchoolBtn"),
    moduleEventsBtn: document.getElementById("moduleEventsBtn"),
    moduleUsersBtn: document.getElementById("moduleUsersBtn"),
    cellsKidsCheckinView: document.getElementById("cellsKidsCheckinView"),
    kidsRefreshBtn: document.getElementById("kidsRefreshBtn"),
    kidsMessage: document.getElementById("kidsMessage"),
    kidsPublicPageLink: document.getElementById("kidsPublicPageLink"),
    kidsNavOpsBtn: document.getElementById("kidsNavOpsBtn"),
    kidsNavCheckoutsBtn: document.getElementById("kidsNavCheckoutsBtn"),
    kidsNavMonitorBtn: document.getElementById("kidsNavMonitorBtn"),
    kidsNavCadastroBtn: document.getElementById("kidsNavCadastroBtn"),
    kidsNavNotifsBtn: document.getElementById("kidsNavNotifsBtn"),
    kidsOpsView: document.getElementById("kidsOpsView"),
    kidsCheckoutsView: document.getElementById("kidsCheckoutsView"),
    kidsMonitorView: document.getElementById("kidsMonitorView"),
    kidsCadastroView: document.getElementById("kidsCadastroView"),
    kidsNotifsView: document.getElementById("kidsNotifsView"),
    kidsAdvancedPanel: document.getElementById("kidsAdvancedPanel"),

    kidsQuickQrForm: document.getElementById("kidsQuickQrForm"),
    kidsQuickQrPayload: document.getElementById("kidsQuickQrPayload"),
    kidsOpsContextName: document.getElementById("kidsOpsContextName"),
    kidsOpsContextSuggestions: document.getElementById("kidsOpsContextSuggestions"),
    kidsOpsPresets: document.getElementById("kidsOpsPresets"),
    kidsOpsPresetsEditBtn: document.getElementById("kidsOpsPresetsEditBtn"),
    kidsQuickQrScanBtn: document.getElementById("kidsQuickQrScanBtn"),
    kidsQrScannerModal: document.getElementById("kidsQrScannerModal"),
    kidsQrScannerVideo: document.getElementById("kidsQrScannerVideo"),
    kidsQrScannerCloseBtn: document.getElementById("kidsQrScannerCloseBtn"),
    kidsQrScannerStatus: document.getElementById("kidsQrScannerStatus"),
    kidsCheckinResultModal: document.getElementById("kidsCheckinResultModal"),
    kidsCheckinResultCloseBtn: document.getElementById("kidsCheckinResultCloseBtn"),
    kidsCheckinResultBody: document.getElementById("kidsCheckinResultBody"),
    kidsCheckinResultPrintBtn: document.getElementById("kidsCheckinResultPrintBtn"),
    kidsCheckinResultNewScanBtn: document.getElementById("kidsCheckinResultNewScanBtn"),
    kidsCheckoutModal: document.getElementById("kidsCheckoutModal"),
    kidsCheckoutCloseBtn: document.getElementById("kidsCheckoutCloseBtn"),
    kidsCheckoutCancelBtn: document.getElementById("kidsCheckoutCancelBtn"),
    kidsCheckoutConfirmBtn: document.getElementById("kidsCheckoutConfirmBtn"),
    kidsCheckoutScanBtn: document.getElementById("kidsCheckoutScanBtn"),
    kidsCheckoutToken: document.getElementById("kidsCheckoutToken"),
    kidsCheckoutGuardianSelect: document.getElementById("kidsCheckoutGuardianSelect"),
    kidsCheckoutPickupName: document.getElementById("kidsCheckoutPickupName"),
    kidsCheckoutMessage: document.getElementById("kidsCheckoutMessage"),
    kidsPrinterModeSelect: document.getElementById("kidsPrinterModeSelect"),
    kidsQuickVisitorForm: document.getElementById("kidsQuickVisitorForm"),
    kidsQuickVisitorChildName: document.getElementById("kidsQuickVisitorChildName"),
    kidsQuickVisitorResponsible: document.getElementById("kidsQuickVisitorResponsible"),
    kidsQuickVisitorPhone: document.getElementById("kidsQuickVisitorPhone"),
    kidsQuickVisitorRoom: document.getElementById("kidsQuickVisitorRoom"),
    kidsMonitorForm: document.getElementById("kidsMonitorForm"),
    kidsMonitorRoomName: document.getElementById("kidsMonitorRoomName"),
    kidsMonitorDate: document.getElementById("kidsMonitorDate"),
    kidsMonitorBody: document.getElementById("kidsMonitorBody"),
    kidsVirtualCardSearchForm: document.getElementById("kidsVirtualCardSearchForm"),
    kidsVirtualCardFamilyCode: document.getElementById("kidsVirtualCardFamilyCode"),
    kidsVirtualCardsResult: document.getElementById("kidsVirtualCardsResult"),
    kidsRoomForm: document.getElementById("kidsRoomForm"),
    kidsRoomName: document.getElementById("kidsRoomName"),
    kidsRoomAgeRange: document.getElementById("kidsRoomAgeRange"),
    kidsRoomMinAgeYears: document.getElementById("kidsRoomMinAgeYears"),
    kidsRoomMaxAgeYears: document.getElementById("kidsRoomMaxAgeYears"),
    kidsRoomCapacity: document.getElementById("kidsRoomCapacity"),
    kidsRoomDescription: document.getElementById("kidsRoomDescription"),
    kidsRoomsBody: document.getElementById("kidsRoomsBody"),

    kidsSummaryTotal: document.getElementById("kidsSummaryTotal"),
    kidsSummaryActive: document.getElementById("kidsSummaryActive"),
    kidsSummaryCheckout: document.getElementById("kidsSummaryCheckout"),
    kidsSummaryVisitors: document.getElementById("kidsSummaryVisitors"),
    kidsSummaryAlerts: document.getElementById("kidsSummaryAlerts"),

    kidsFamilyForm: document.getElementById("kidsFamilyForm"),
    kidsFamilyName: document.getElementById("kidsFamilyName"),
    kidsFamilyResponsible: document.getElementById("kidsFamilyResponsible"),
    kidsFamilyPhone: document.getElementById("kidsFamilyPhone"),
    kidsFamilyEmail: document.getElementById("kidsFamilyEmail"),
    kidsFamilyNotes: document.getElementById("kidsFamilyNotes"),

    kidsChildForm: document.getElementById("kidsChildForm"),
    kidsChildFamilyId: document.getElementById("kidsChildFamilyId"),
    kidsChildName: document.getElementById("kidsChildName"),
    kidsChildBirthDate: document.getElementById("kidsChildBirthDate"),
    kidsChildAgeGroup: document.getElementById("kidsChildAgeGroup"),
    kidsChildRoom: document.getElementById("kidsChildRoom"),
    kidsChildGender: document.getElementById("kidsChildGender"),
    kidsChildPhotoUrl: document.getElementById("kidsChildPhotoUrl"),
    kidsChildAllergies: document.getElementById("kidsChildAllergies"),
    kidsChildMedical: document.getElementById("kidsChildMedical"),
    kidsChildSpecial: document.getElementById("kidsChildSpecial"),
    kidsChildBehavior: document.getElementById("kidsChildBehavior"),

    kidsGuardianForm: document.getElementById("kidsGuardianForm"),
    kidsGuardianFamilyId: document.getElementById("kidsGuardianFamilyId"),
    kidsGuardianName: document.getElementById("kidsGuardianName"),
    kidsGuardianRelationship: document.getElementById("kidsGuardianRelationship"),
    kidsGuardianPhone: document.getElementById("kidsGuardianPhone"),
    kidsGuardianPhotoUrl: document.getElementById("kidsGuardianPhotoUrl"),
    kidsGuardianAuthorized: document.getElementById("kidsGuardianAuthorized"),

    kidsCheckinForm: document.getElementById("kidsCheckinForm"),
    kidsFamilySearch: document.getElementById("kidsFamilySearch"),
    kidsCheckinFamilyId: document.getElementById("kidsCheckinFamilyId"),
    kidsCheckinContextType: document.getElementById("kidsCheckinContextType"),
    kidsCheckinContextName: document.getElementById("kidsCheckinContextName"),
    kidsCheckinRoomName: document.getElementById("kidsCheckinRoomName"),
    kidsCheckinAccompaniedBy: document.getElementById("kidsCheckinAccompaniedBy"),
    kidsCheckinChildrenList: document.getElementById("kidsCheckinChildrenList"),

    kidsVisitorForm: document.getElementById("kidsVisitorForm"),
    kidsVisitorChildName: document.getElementById("kidsVisitorChildName"),
    kidsVisitorAge: document.getElementById("kidsVisitorAge"),
    kidsVisitorResponsible: document.getElementById("kidsVisitorResponsible"),
    kidsVisitorPhone: document.getElementById("kidsVisitorPhone"),
    kidsVisitorRoom: document.getElementById("kidsVisitorRoom"),
    kidsVisitorContext: document.getElementById("kidsVisitorContext"),
    kidsVisitorNotes: document.getElementById("kidsVisitorNotes"),

    kidsNotifyForm: document.getElementById("kidsNotifyForm"),
    kidsNotifyChannel: document.getElementById("kidsNotifyChannel"),
    kidsNotifyType: document.getElementById("kidsNotifyType"),
    kidsNotifyFamilyId: document.getElementById("kidsNotifyFamilyId"),
    kidsNotifyChildId: document.getElementById("kidsNotifyChildId"),
    kidsNotifyMessage: document.getElementById("kidsNotifyMessage"),

    kidsActiveCheckinsBody: document.getElementById("kidsActiveCheckinsBody"),
    kidsActiveCheckinsQuickBody: document.getElementById("kidsActiveCheckinsQuickBody"),
    kidsFamiliesBody: document.getElementById("kidsFamiliesBody"),
    kidsChildrenBody: document.getElementById("kidsChildrenBody"),
    kidsNotificationsBody: document.getElementById("kidsNotificationsBody"),
    kidsActiveCheckinsAdminBody: document.getElementById("kidsActiveCheckinsAdminBody"),
  };

  if (!el.moduleKidsBtn || !el.kidsModule || !el.kidsModuleContent || !el.cellsKidsCheckinView) return;

  if (el.cellsKidsCheckinView.parentElement !== el.kidsModuleContent) {
    el.kidsModuleContent.appendChild(el.cellsKidsCheckinView);
  }
  el.cellsKidsCheckinView.classList.remove("cells-view");

  const state = {
    initialized: false,
    families: [],
    children: [],
    activeCheckins: [],
    notifications: [],
    roomMonitoringRows: [],
    rooms: [],
    settings: { ops_context_presets: [] },
  };

  function hasKidsAccess() {
    const isAdmin = localStorage.getItem("currentUserIsAdmin") === "true";
    if (isAdmin) return true;

    let permissions = [];
    try {
      const raw = localStorage.getItem("currentUserPermissions");
      permissions = raw ? JSON.parse(raw) : [];
    } catch (_error) {
      permissions = [];
    }

    if (!Array.isArray(permissions)) return false;
    return permissions.some((name) => typeof name === "string" && name.indexOf("cells_kids_") === 0);
  }

  function canManageKids() {
    const isAdmin = localStorage.getItem("currentUserIsAdmin") === "true";
    if (isAdmin) return true;

    let permissions = [];
    try {
      const raw = localStorage.getItem("currentUserPermissions");
      permissions = raw ? JSON.parse(raw) : [];
    } catch (_error) {
      permissions = [];
    }

    if (!Array.isArray(permissions)) return false;
    return permissions.some((name) =>
      typeof name === "string" &&
      (
        name === "cells_kids_manage" ||
        name === "cells_kids_edit" ||
        name === "cells_kids_create"
      )
    );
  }

  if (!hasKidsAccess()) {
    el.moduleKidsBtn.classList.add("hide");
  }

  function token() {
    return String(localStorage.getItem("accessToken") || "");
  }

  function setMessage(text, isError) {
    if (!el.kidsMessage) return;
    el.kidsMessage.textContent = text || "";
    el.kidsMessage.style.color = isError ? "#b42318" : "#5f6b6d";
  }

  function setKidsNavActive(key) {
    const pairs = [
      ["ops", el.kidsNavOpsBtn],
      ["checkouts", el.kidsNavCheckoutsBtn],
      ["monitor", el.kidsNavMonitorBtn],
      ["cadastro", el.kidsNavCadastroBtn],
      ["notifs", el.kidsNavNotifsBtn],
    ];
    pairs.forEach(([name, btn]) => {
      if (!btn) return;
      btn.classList.toggle("active", name === key);
    });
    localStorage.setItem("kidsNavSection", String(key || "ops"));
  }

  function showKidsSection(key) {
    const normalized = String(key || "ops").trim() || "ops";
    const views = {
      ops: el.kidsOpsView,
      checkouts: el.kidsCheckoutsView,
      monitor: el.kidsMonitorView,
      cadastro: el.kidsCadastroView,
      notifs: el.kidsNotifsView,
    };

    const effectiveKey = Object.prototype.hasOwnProperty.call(views, normalized) ? normalized : "ops";
    Object.entries(views).forEach(([name, node]) => {
      if (!node) return;
      node.classList.toggle("hide", name !== effectiveKey);
    });

    setKidsNavActive(effectiveKey);
  }

  function printerMode() {
    const raw = String(localStorage.getItem("kidsPrinterMode") || "").trim();
    if (raw === "band" || raw === "label" || raw === "both") return raw;
    return "both";
  }

  function lastContextName() {
    const raw = String(localStorage.getItem("kidsLastContextName") || "").trim();
    return raw || "Culto Domingo";
  }

  function pushContextSuggestion(value) {
    if (!el.kidsOpsContextSuggestions) return;
    const normalized = String(value || "").trim();
    if (!normalized) return;
    const existing = Array.from(el.kidsOpsContextSuggestions.querySelectorAll("option")).map((opt) => String(opt.value || "").trim());
    if (existing.includes(normalized)) return;
    const opt = document.createElement("option");
    opt.value = normalized;
    el.kidsOpsContextSuggestions.appendChild(opt);
  }

  function setOpsContextName(name) {
    if (!el.kidsOpsContextName) return;
    const value = String(name || "").trim();
    el.kidsOpsContextName.value = value;
    if (value) {
      localStorage.setItem("kidsLastContextName", value);
      pushContextSuggestion(value);
    }
  }

  function normalizeOpsPresets(raw) {
    const list = Array.isArray(raw) ? raw : [];
    return list
      .map((item) => ({
        label: String(item && item.label ? item.label : "").trim(),
        context_name: String(item && item.context_name ? item.context_name : "").trim(),
      }))
      .filter((item) => item.label && item.context_name)
      .slice(0, 12);
  }

  function renderOpsPresets(presets) {
    if (!el.kidsOpsPresets) return;
    const rows = normalizeOpsPresets(presets);
    if (!rows.length) {
      el.kidsOpsPresets.innerHTML = '<span class="tiny">Sem atalhos.</span>';
      return;
    }
    el.kidsOpsPresets.innerHTML = "";
    rows.forEach((preset) => {
      const btn = document.createElement("button");
      btn.type = "button";
      btn.className = "btn ghost btn-mini";
      btn.textContent = preset.label;
      btn.addEventListener("click", function () {
        setOpsContextName(preset.context_name);
      });
      el.kidsOpsPresets.appendChild(btn);
    });
  }

  async function loadKidsSettings() {
    const settings = await api("/settings");
    state.settings = settings && typeof settings === "object" ? settings : { ops_context_presets: [] };
    const presets = normalizeOpsPresets(state.settings.ops_context_presets);
    renderOpsPresets(presets);
    presets.forEach((preset) => pushContextSuggestion(preset.context_name));
  }

  function presetsToEditorText(presets) {
    const rows = normalizeOpsPresets(presets);
    return rows.map((row) => `${row.label}|${row.context_name}`).join("\n");
  }

  function parseEditorText(text) {
    const lines = String(text || "")
      .split("\n")
      .map((line) => line.trim())
      .filter(Boolean);

    const out = [];
    lines.forEach((line) => {
      const parts = line.split("|");
      const label = String(parts[0] || "").trim();
      const contextName = String(parts.slice(1).join("|") || "").trim();
      if (!label || !contextName) return;
      out.push({ label, context_name: contextName });
    });
    return normalizeOpsPresets(out);
  }

  function openLabelsForCheckins(checkinIds, autoPrint, options) {
    const ids = Array.isArray(checkinIds)
      ? checkinIds.map((value) => Number(value)).filter((value) => Number.isFinite(value) && value > 0)
      : [];
    if (!ids.length) return;

    const opts = options && typeof options === "object" ? options : {};
    const layout = String(opts.layout || "").trim() || printerMode();
    const autoClose = Boolean(opts.autoClose);

    const params = new URLSearchParams();
    params.set("checkins", ids.join(","));
    if (autoPrint) params.set("autoprint", "1");
    params.set("layout", layout);
    if (autoClose) params.set("autoclose", "1");
    const url = `/kids-label.html?${params.toString()}`;

    const win = window.open(url, "_blank");
    if (!win) {
      setMessage(`Pop-up bloqueado. Abra manualmente: ${url}`, true);
    }
  }

  function parseKidsQrPayload(raw) {
    const text = String(raw || "").trim();
    if (!text) return null;
    const parts = text.split(":");
    if (parts.length < 4) return null;
    if (parts[0] !== "KIDS") return null;
    return {
      tenant_slug: parts[1] || "",
      family_code: parts[2] || "",
      child_id: Number(parts[3] || 0),
    };
  }

  function suggestRoomFromQrPayload(raw) {
    const parsed = parseKidsQrPayload(raw);
    if (!parsed || !parsed.child_id) return;
    const child = state.children.find((row) => Number(row.id) === Number(parsed.child_id));
    if (!child) return;
    const room = String(child.room_name || "").trim();
    if (!room) return;

    if (el.kidsQrScannerStatus) el.kidsQrScannerStatus.textContent = `Sala sugerida: ${room}.`;
  }

  let qrScannerStream = null;
  let qrScannerActive = false;
  let qrScannerDetector = null;
  let qrScannerMode = "";
  let qrScannerCanvas = null;
  let qrScannerCtx = null;
  let qrScannerLastScanAt = 0;
  let qrScannerOnResult = null;

  function hasJsQr() {
    return typeof window.jsQR === "function";
  }

  function ensureQrCanvas() {
    if (qrScannerCanvas && qrScannerCtx) return;
    qrScannerCanvas = document.createElement("canvas");
    qrScannerCtx = qrScannerCanvas.getContext("2d", { willReadFrequently: true });
  }

  async function openQrScanner(opts) {
    if (!el.kidsQrScannerModal || !el.kidsQrScannerVideo) return;
    qrScannerOnResult = opts && typeof opts.onResult === "function" ? opts.onResult : null;

    if (!("mediaDevices" in navigator) || typeof navigator.mediaDevices.getUserMedia !== "function") {
      setMessage("Este navegador nao suporta camera. Digite o QR payload manualmente.", true);
      return;
    }

    qrScannerDetector = null;
    qrScannerMode = "";

    if ("BarcodeDetector" in window) {
      try {
        qrScannerDetector = new window.BarcodeDetector({ formats: ["qr_code"] });
        qrScannerMode = "native";
      } catch (_error) {
        qrScannerDetector = null;
        qrScannerMode = "";
      }
    }
    if (!qrScannerMode && hasJsQr()) {
      ensureQrCanvas();
      qrScannerMode = "jsqr";
    }
    if (!qrScannerMode) {
      setMessage("Leitor de QR indisponivel neste navegador. Digite o QR payload manualmente.", true);
      return;
    }

    el.kidsQrScannerModal.classList.remove("hide");
    el.kidsQrScannerModal.setAttribute("aria-hidden", "false");
    if (el.kidsQrScannerStatus) el.kidsQrScannerStatus.textContent = "Abrindo camera...";

    try {
      qrScannerStream = await navigator.mediaDevices.getUserMedia({
        video: { facingMode: "environment" },
        audio: false,
      });
    } catch (error) {
      const name = error && typeof error === "object" && "name" in error ? String(error.name) : "";
      const hint =
        name === "NotAllowedError" ? "Permissao negada para camera." :
        name === "NotFoundError" ? "Camera nao encontrada." :
        "Falha ao abrir camera.";
      setMessage(`${hint} Digite o QR payload manualmente.`, true);
      return;
    }
    el.kidsQrScannerVideo.srcObject = qrScannerStream;
    qrScannerActive = true;
    if (el.kidsQrScannerStatus) {
      el.kidsQrScannerStatus.textContent =
        qrScannerMode === "native" ? "Aponte para o QR." : "Aponte para o QR (modo compatibilidade).";
    }
    qrScannerLastScanAt = 0;
    requestAnimationFrame(scanQrFrame);
  }

  function closeQrScanner() {
    qrScannerActive = false;
    qrScannerOnResult = null;
    if (el.kidsQrScannerModal) {
      el.kidsQrScannerModal.classList.add("hide");
      el.kidsQrScannerModal.setAttribute("aria-hidden", "true");
    }
    if (el.kidsQrScannerVideo) {
      el.kidsQrScannerVideo.pause();
      el.kidsQrScannerVideo.srcObject = null;
    }
    if (qrScannerStream) {
      const tracks = qrScannerStream.getTracks ? qrScannerStream.getTracks() : [];
      tracks.forEach((track) => track.stop());
    }
    qrScannerStream = null;
    qrScannerDetector = null;
    qrScannerMode = "";
    if (el.kidsQrScannerStatus) el.kidsQrScannerStatus.textContent = "Aponte a camera para o QR da carteirinha.";
  }

  async function scanQrFrame() {
    if (!qrScannerActive || !el.kidsQrScannerVideo) return;
    try {
      const now = Date.now();
      // Throttle to keep UI smooth on mobile.
      if (qrScannerLastScanAt && now - qrScannerLastScanAt < 120) {
        requestAnimationFrame(scanQrFrame);
        return;
      }
      qrScannerLastScanAt = now;

      let raw = "";
      if (qrScannerMode === "native" && qrScannerDetector) {
        const barcodes = await qrScannerDetector.detect(el.kidsQrScannerVideo);
        if (Array.isArray(barcodes) && barcodes.length) {
          raw = String(barcodes[0] && barcodes[0].rawValue || "").trim();
        }
      } else if (qrScannerMode === "jsqr" && hasJsQr() && qrScannerCtx && qrScannerCanvas) {
        const vw = Number(el.kidsQrScannerVideo.videoWidth || 0);
        const vh = Number(el.kidsQrScannerVideo.videoHeight || 0);
        if (vw > 0 && vh > 0) {
          const maxSide = 720;
          const scale = Math.min(1, maxSide / Math.max(vw, vh));
          const tw = Math.max(1, Math.round(vw * scale));
          const th = Math.max(1, Math.round(vh * scale));
          qrScannerCanvas.width = tw;
          qrScannerCanvas.height = th;
          qrScannerCtx.drawImage(el.kidsQrScannerVideo, 0, 0, tw, th);
          const imageData = qrScannerCtx.getImageData(0, 0, tw, th);
          const code = window.jsQR(imageData.data, imageData.width, imageData.height, { inversionAttempts: "attemptBoth" });
          if (code && code.data) raw = String(code.data).trim();
        }
      }

      if (raw) {
        const cb = qrScannerOnResult;
        closeQrScanner();
        if (cb) {
          cb(raw);
        } else {
          // Backwards-compatible: fill ops QR payload + auto-submit.
          if (el.kidsQuickQrPayload) el.kidsQuickQrPayload.value = raw;
          suggestRoomFromQrPayload(raw);
          setMessage("QR lido com sucesso.", false);

          if (el.kidsOpsContextName && !String(el.kidsOpsContextName.value || "").trim()) {
            setOpsContextName(lastContextName());
          }
          if (el.kidsQuickQrForm && typeof el.kidsQuickQrForm.requestSubmit === "function") {
            el.kidsQuickQrForm.requestSubmit();
          }
        }
        return;
      }
    } catch (_error) {
      if (el.kidsQrScannerStatus) el.kidsQrScannerStatus.textContent = "Falha ao ler. Tente aproximar o QR.";
    }
    requestAnimationFrame(scanQrFrame);
  }

  function escapeHtml(value) {
    return String(value == null ? "" : value)
      .replaceAll("&", "&amp;")
      .replaceAll("<", "&lt;")
      .replaceAll(">", "&gt;")
      .replaceAll('"', "&quot;")
      .replaceAll("'", "&#39;");
  }

  function openCheckinResultModal(payload, checkinId) {
    if (!el.kidsCheckinResultModal || !el.kidsCheckinResultBody) return;
    const id = Number(checkinId || (payload && payload.checkin_id) || 0);
    const childName = payload && payload.child_name ? String(payload.child_name) : "-";
    const roomName = payload && payload.room_name ? String(payload.room_name) : "-";
    const contextName = payload && payload.context_name ? String(payload.context_name) : "-";
    const code = payload && payload.security_code ? String(payload.security_code) : "-";
    const token = payload && payload.qr_token ? String(payload.qr_token) : "";

    el.kidsCheckinResultBody.innerHTML = `
      <div style="display:grid; gap:0.35rem;">
        <div><strong>${escapeHtml(childName)}</strong></div>
        <div>Sala: <strong>${escapeHtml(roomName)}</strong></div>
        <div>Culto: <strong>${escapeHtml(contextName)}</strong></div>
        <div>Codigo de seguranca: <strong style="font-family:ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, 'Liberation Mono', 'Courier New', monospace;">${escapeHtml(code)}</strong></div>
        ${token ? `<div class="tiny">QR token (pulseira): <span style="font-family:ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, 'Liberation Mono', 'Courier New', monospace;">${escapeHtml(token)}</span></div>` : ""}
      </div>
    `;
    el.kidsCheckinResultModal.dataset.checkinId = String(id || "");
    el.kidsCheckinResultModal.classList.remove("hide");
    el.kidsCheckinResultModal.setAttribute("aria-hidden", "false");
  }

  function closeCheckinResultModal() {
    if (!el.kidsCheckinResultModal) return;
    el.kidsCheckinResultModal.classList.add("hide");
    el.kidsCheckinResultModal.setAttribute("aria-hidden", "true");
    el.kidsCheckinResultModal.dataset.checkinId = "";
    if (el.kidsCheckinResultBody) el.kidsCheckinResultBody.innerHTML = "";
  }

  let checkoutModalState = { checkinId: 0, context: null };

  function setCheckoutMessage(text, isError) {
    if (!el.kidsCheckoutMessage) return;
    el.kidsCheckoutMessage.textContent = text || "";
    el.kidsCheckoutMessage.style.color = isError ? "#b42318" : "#5f6b6d";
  }

  function openCheckoutModalWithContext(checkinId, context, suggestedToken) {
    if (!el.kidsCheckoutModal || !el.kidsCheckoutGuardianSelect) return;
    checkoutModalState = { checkinId: Number(checkinId || 0), context: context || null };
    setCheckoutMessage("", false);
    if (el.kidsCheckoutToken) el.kidsCheckoutToken.value = String(suggestedToken || "");
    if (el.kidsCheckoutPickupName) el.kidsCheckoutPickupName.value = "";
    const guardians = Array.isArray(context && context.guardians) ? context.guardians : [];
    const authorized = guardians.filter((g) => g && g.is_authorized);
    el.kidsCheckoutGuardianSelect.innerHTML =
      `<option value="">Selecione</option>` +
      authorized.map((g) => `<option value="${Number(g.id)}">${escapeHtml(g.full_name || "-")}</option>`).join("");

    el.kidsCheckoutModal.classList.remove("hide");
    el.kidsCheckoutModal.setAttribute("aria-hidden", "false");
    if (el.kidsCheckoutToken) el.kidsCheckoutToken.focus();
  }

  function closeCheckoutModal() {
    checkoutModalState = { checkinId: 0, context: null };
    if (!el.kidsCheckoutModal) return;
    el.kidsCheckoutModal.classList.add("hide");
    el.kidsCheckoutModal.setAttribute("aria-hidden", "true");
    setCheckoutMessage("", false);
    if (el.kidsCheckoutToken) el.kidsCheckoutToken.value = "";
    if (el.kidsCheckoutPickupName) el.kidsCheckoutPickupName.value = "";
    if (el.kidsCheckoutGuardianSelect) el.kidsCheckoutGuardianSelect.innerHTML = "";
  }

  function asDate(value) {
    if (!value) return "-";
    const text = String(value);
    const date = text.length >= 10 ? text.slice(0, 10) : text;
    const parts = date.split("-");
    if (parts.length !== 3) return date;
    return `${parts[2]}/${parts[1]}/${parts[0]}`;
  }

  async function api(path, options) {
    const auth = token();
    if (!auth) throw new Error("Sessao nao autenticada.");

    const requestOptions = options || {};
    const headers = Object.assign({}, requestOptions.headers || {}, { Authorization: `Bearer ${auth}` });
    if (requestOptions.body && !headers["Content-Type"]) {
      headers["Content-Type"] = "application/json";
    }

    const response = await fetch(`${apiPrefix}${path}`, {
      method: requestOptions.method || "GET",
      headers,
      body: requestOptions.body || undefined,
    });

    if (!response.ok) {
      let detail = `Erro ${response.status}`;
      try {
        const body = await response.json();
        if (body && typeof body.detail === "string") detail = body.detail;
      } catch (_error) {
      }
      throw new Error(detail);
    }

    if (response.status === 204) return null;
    return response.json();
  }

  async function publicApi(path, options) {
    const requestOptions = options || {};
    const headers = Object.assign({}, requestOptions.headers || {});
    if (requestOptions.body && !headers["Content-Type"]) {
      headers["Content-Type"] = "application/json";
    }

    const response = await fetch(`${apiPrefix}/public${path}`, {
      method: requestOptions.method || "GET",
      headers,
      body: requestOptions.body || undefined,
    });

    if (!response.ok) {
      let detail = `Erro ${response.status}`;
      try {
        const body = await response.json();
        if (body && typeof body.detail === "string") detail = body.detail;
      } catch (_error) {
      }
      throw new Error(detail);
    }

    if (response.status === 204) return null;
    return response.json();
  }

  function activeTenantSlug() {
    return String(localStorage.getItem("activeTenantSlug") || "").trim();
  }

  function hideKidsView() {
    if (el.cellsKidsCheckinView) el.cellsKidsCheckinView.classList.add("hide");
    if (el.moduleKidsBtn) el.moduleKidsBtn.classList.remove("active");
  }

  function setActiveTopModule(moduleName) {
    const isFinance = moduleName === "finance";
    const isCells = moduleName === "cells";
    const isKids = moduleName === "kids";
    const isSchool = moduleName === "school";
    const isEvents = moduleName === "events";
    const isUsers = moduleName === "users";

    if (el.moduleFinanceBtn) el.moduleFinanceBtn.classList.toggle("active", isFinance);
    if (el.moduleCellsBtn) el.moduleCellsBtn.classList.toggle("active", isCells);
    if (el.moduleKidsBtn) el.moduleKidsBtn.classList.toggle("active", isKids);
    if (el.moduleBibleSchoolBtn) el.moduleBibleSchoolBtn.classList.toggle("active", isSchool);
    if (el.moduleEventsBtn) el.moduleEventsBtn.classList.toggle("active", isEvents);
    if (el.moduleUsersBtn) el.moduleUsersBtn.classList.toggle("active", isUsers);

    if (el.financeModule) el.financeModule.classList.toggle("hide", !isFinance);
    if (el.cellsModule) el.cellsModule.classList.toggle("hide", !isCells);
    if (el.kidsModule) el.kidsModule.classList.toggle("hide", !isKids);
    if (el.bibleSchoolModule) el.bibleSchoolModule.classList.toggle("hide", !isSchool);
    if (el.eventsModule) el.eventsModule.classList.toggle("hide", !isEvents);
    if (el.usersModule) el.usersModule.classList.toggle("hide", !isUsers);
  }

  function showKidsView() {
    setActiveTopModule("kids");
    el.cellsKidsCheckinView.classList.remove("hide");
  }

  function fillFamilySelect(select, families, placeholder) {
    if (!select) return;
    const options = families
      .map((family) => `<option value="${family.id}">${escapeHtml(family.family_name)} (${escapeHtml(family.family_code)})</option>`)
      .join("");
    select.innerHTML = `<option value="">${escapeHtml(placeholder)}</option>` + options;
  }

  function renderFamiliesTable() {
    if (!el.kidsFamiliesBody) return;
    if (!state.families.length) {
      el.kidsFamiliesBody.innerHTML = '<tr><td colspan="5">Sem registros.</td></tr>';
      return;
    }

    el.kidsFamiliesBody.innerHTML = state.families
      .map((family) => `<tr>
        <td>${family.id}</td>
        <td>${escapeHtml(family.family_name)}</td>
        <td>${escapeHtml(family.primary_responsible_name || "-")}</td>
        <td>${escapeHtml(family.phone_primary || "-")}</td>
        <td>${escapeHtml(family.family_code || "-")}</td>
      </tr>`)
      .join("");
  }

  function renderChildrenTable() {
    if (!el.kidsChildrenBody) return;
    if (!state.children.length) {
      el.kidsChildrenBody.innerHTML = '<tr><td colspan="6">Sem registros.</td></tr>';
      return;
    }

    const familyById = new Map(
      (Array.isArray(state.families) ? state.families : []).map((family) => [Number(family.id), family]),
    );

    el.kidsChildrenBody.innerHTML = state.children
      .map((child) => {
        const alerts = [child.allergies, child.medical_restrictions, child.special_needs].filter(Boolean).join(" | ");
        const fam = familyById.get(Number(child.family_id)) || null;
        const familyName = fam && fam.family_name ? String(fam.family_name) : "-";
        const familyCode = fam && fam.family_code ? String(fam.family_code) : "";
        const familyPhone = fam && fam.phone_primary ? String(fam.phone_primary) : "";
        const familyMeta = [familyCode, familyPhone].filter(Boolean).join(" | ");
        return `<tr>
          <td>${child.id}</td>
          <td>${escapeHtml(child.full_name)}</td>
          <td>
            <div>${escapeHtml(familyName)}</div>
            <div class="tiny">${escapeHtml(familyMeta || "-")}</div>
          </td>
          <td>${escapeHtml(child.room_name || "-")}</td>
          <td>${escapeHtml(alerts || "-")}</td>
          <td>${child.is_visitor ? "Sim" : "Nao"}</td>
        </tr>`;
      })
      .join("");
  }

  function renderNotificationsTable() {
    if (!el.kidsNotificationsBody) return;
    if (!state.notifications.length) {
      el.kidsNotificationsBody.innerHTML = '<tr><td colspan="5">Sem registros.</td></tr>';
      return;
    }

    el.kidsNotificationsBody.innerHTML = state.notifications
      .map((row) => `<tr>
        <td>${escapeHtml(row.channel || "-")}</td>
        <td>${escapeHtml(row.message_type || "-")}</td>
        <td>${escapeHtml(row.message || "-")}</td>
        <td>${escapeHtml(row.delivery_status || "-")}</td>
        <td>${escapeHtml(asDate(row.created_at))}</td>
      </tr>`)
      .join("");
  }

  function renderFamilyChildrenList(container, familyId, checkboxClassName) {
    if (!container || !familyId) {
      if (container) container.innerHTML = '<div class="tiny">Selecione uma familia para listar as criancas.</div>';
      return;
    }
    const rows = state.children.filter((child) => Number(child.family_id) === familyId && child.is_active);

    if (!rows.length) {
      container.innerHTML = '<div class="tiny">Sem criancas cadastradas para esta familia.</div>';
      return;
    }

    container.innerHTML = rows
      .map((child) => {
        const alerts = [child.allergies, child.medical_restrictions, child.special_needs].filter(Boolean).join(" | ");
        const alertLabel = alerts ? `<div class="tiny" style="color:#b42318">${escapeHtml(alerts)}</div>` : "";
        return `<label style="display:block; padding:0.45rem; border-bottom:1px solid #ececec;">
          <input type="checkbox" class="${checkboxClassName}" value="${child.id}"> ${escapeHtml(child.full_name)}
          <span class="tiny" style="margin-left:0.35rem;">Sala: ${escapeHtml(child.room_name || "-")}</span>
          ${alertLabel}
        </label>`;
      })
      .join("");
  }

  function renderCheckinChildrenList() {
    const advancedFamilyId = Number(el.kidsCheckinFamilyId ? el.kidsCheckinFamilyId.value || 0 : 0);
    renderFamilyChildrenList(el.kidsCheckinChildrenList, advancedFamilyId, "kids-checkin-child");
  }

  function renderActiveCheckins() {
    const childNameById = new Map(state.children.map((child) => [Number(child.id), child.full_name]));
    const tableHtml = state.activeCheckins
      .map((item) => `<tr>
        <td>${item.id}</td>
        <td>${escapeHtml(childNameById.get(Number(item.child_id)) || `Crianca ${item.child_id}`)}</td>
        <td>${escapeHtml(item.room_name || "-")}</td>
        <td>${escapeHtml(asDate(item.checkin_at))}</td>
        <td>${escapeHtml(item.security_code || "-")}</td>
        <td>
          <button class="btn ghost btn-inline kids-label-btn" data-checkin-id="${item.id}" type="button">Etiqueta</button>
          <button class="btn ghost btn-inline kids-band-btn" data-checkin-id="${item.id}" type="button">Pulseira</button>
          <button class="btn ghost btn-inline kids-checkout-btn" data-checkin-id="${item.id}" data-security-code="${escapeHtml(item.security_code || "")}" type="button">Check-out</button>
        </td>
      </tr>`)
      .join("");

    const emptyHtml = '<tr><td colspan="6">Sem criancas em sala.</td></tr>';
    if (el.kidsActiveCheckinsBody) {
      el.kidsActiveCheckinsBody.innerHTML = state.activeCheckins.length ? tableHtml : emptyHtml;
    }
    if (el.kidsActiveCheckinsQuickBody) {
      el.kidsActiveCheckinsQuickBody.innerHTML = state.activeCheckins.length ? tableHtml : emptyHtml;
    }
    if (el.kidsActiveCheckinsAdminBody) {
      el.kidsActiveCheckinsAdminBody.innerHTML = state.activeCheckins.length ? tableHtml : emptyHtml;
    }
  }

  function renderMonitoringRows() {
    if (!el.kidsMonitorBody) return;
    if (!state.roomMonitoringRows.length) {
      el.kidsMonitorBody.innerHTML = '<tr><td colspan="4">Sem criancas nesta sala.</td></tr>';
      return;
    }

    el.kidsMonitorBody.innerHTML = state.roomMonitoringRows
      .map((row) => {
        const whatsappLink = row.whatsapp_link || "";
        const action = whatsappLink
          ? `<a class="btn ghost btn-inline" href="${escapeHtml(whatsappLink)}" target="_blank" rel="noopener">Chamar no WhatsApp</a>`
          : '<span class="tiny">Sem WhatsApp</span>';
        return `<tr>
          <td>${escapeHtml(row.child_name || "-")}</td>
          <td>${escapeHtml(row.family_name || "-")}</td>
          <td>${escapeHtml(row.phone_primary || "-")}</td>
          <td>${action}</td>
        </tr>`;
      })
      .join("");
  }

  function renderVirtualCards(payload) {
    if (!el.kidsVirtualCardsResult) return;
    const cards = Array.isArray(payload && payload.cards) ? payload.cards : [];
    if (!cards.length) {
      el.kidsVirtualCardsResult.innerHTML = '<p class="tiny">Nenhuma carteirinha encontrada para este codigo.</p>';
      return;
    }

    el.kidsVirtualCardsResult.innerHTML = cards
      .map((card) => {
        const guardians = Array.isArray(card.guardians) ? card.guardians : [];
        const guardiansText = guardians
          .map((guardian) => `${escapeHtml(guardian.full_name || "-")} (${guardian.is_authorized ? "autorizado" : "nao autorizado"})`)
          .join("<br>");
        return `<article class="panel" style="margin-bottom:0.5rem;">
          <strong>${escapeHtml(card.child_name || "Crianca")}</strong>
          <div class="tiny">Sala: ${escapeHtml(card.room_name || "-")}</div>
          <div class="tiny">Codigo familia: ${escapeHtml(card.family_code || "-")}</div>
          <div class="tiny">QR payload: ${escapeHtml(card.qr_payload || "-")}</div>
          <div class="tiny" style="margin-top:0.4rem;">Responsaveis:<br>${guardiansText || "-"}</div>
        </article>`;
      })
      .join("");
  }

  function renderRoomsTable() {
    if (!el.kidsRoomsBody) return;
    if (!state.rooms.length) {
      el.kidsRoomsBody.innerHTML = '<tr><td colspan="4">Sem salas cadastradas.</td></tr>';
      return;
    }
    el.kidsRoomsBody.innerHTML = state.rooms
      .map((room) => `<tr>
        <td>${escapeHtml(room.name || "-")}</td>
        <td>${escapeHtml(room.age_range_label || "-")}</td>
        <td>${room.capacity ? escapeHtml(String(room.capacity)) : "-"}</td>
        <td>${room.is_active ? "Ativa" : "Inativa"}</td>
      </tr>`)
      .join("");
  }

  async function loadSummary() {
    const summary = await api("/summary");
    if (el.kidsSummaryTotal) el.kidsSummaryTotal.textContent = String(summary.total_checkins || 0);
    if (el.kidsSummaryActive) el.kidsSummaryActive.textContent = String(summary.active_checkins || 0);
    if (el.kidsSummaryCheckout) el.kidsSummaryCheckout.textContent = String(summary.completed_checkouts || 0);
    if (el.kidsSummaryVisitors) el.kidsSummaryVisitors.textContent = String(summary.visitors || 0);
    if (el.kidsSummaryAlerts) el.kidsSummaryAlerts.textContent = String(summary.alerts_count || 0);
  }

  async function loadFamilies(query) {
    const q = query ? `?q=${encodeURIComponent(query)}` : "";
    const families = await api(`/families${q}`);
    state.families = Array.isArray(families) ? families : [];
    fillFamilySelect(el.kidsChildFamilyId, state.families, "Selecione");
    fillFamilySelect(el.kidsGuardianFamilyId, state.families, "Selecione");
    fillFamilySelect(el.kidsCheckinFamilyId, state.families, "Selecione");
    renderFamiliesTable();
  }

  async function loadChildren() {
    const children = await api("/children");
    state.children = Array.isArray(children) ? children : [];
    renderChildrenTable();
    renderCheckinChildrenList();
  }

  async function loadActiveCheckins() {
    const checkins = await api("/checkins?status=checked_in");
    state.activeCheckins = Array.isArray(checkins) ? checkins : [];
    renderActiveCheckins();
  }

  async function loadNotifications() {
    const notifications = await api("/notifications?limit=30");
    state.notifications = Array.isArray(notifications) ? notifications : [];
    renderNotificationsTable();
  }

  async function loadRooms() {
    const rows = await api("/rooms");
    state.rooms = Array.isArray(rows) ? rows : [];
    renderRoomsTable();
  }

  async function refreshAll() {
    await Promise.all([loadSummary(), loadFamilies(), loadChildren(), loadActiveCheckins(), loadNotifications(), loadRooms()]);
  }

  async function loadRoomMonitoring() {
    const roomName = el.kidsMonitorRoomName ? el.kidsMonitorRoomName.value.trim() : "";
    if (!roomName) {
      state.roomMonitoringRows = [];
      renderMonitoringRows();
      return;
    }

    const params = new URLSearchParams();
    if (el.kidsMonitorDate && el.kidsMonitorDate.value) params.set("day", el.kidsMonitorDate.value);
    const suffix = params.toString() ? `?${params.toString()}` : "";
    const rows = await api(`/rooms/${encodeURIComponent(roomName)}/monitoring${suffix}`);
    state.roomMonitoringRows = Array.isArray(rows) ? rows : [];
    renderMonitoringRows();
  }

  async function searchVirtualCards() {
    const tenantSlug = activeTenantSlug();
    if (!tenantSlug) throw new Error("Tenant ativo nao encontrado.");
    const familyCode = el.kidsVirtualCardFamilyCode ? el.kidsVirtualCardFamilyCode.value.trim() : "";
    if (!familyCode) throw new Error("Informe o codigo da familia.");

    const payload = await publicApi(
      `/tenants/${encodeURIComponent(tenantSlug)}/virtual-cards?family_code=${encodeURIComponent(familyCode)}`,
    );
    renderVirtualCards(payload);
  }

  async function ensureInitialized() {
    if (state.initialized) return;
    await refreshAll();
    try {
      await loadKidsSettings();
    } catch (_error) {
      // Settings are optional; keep the module usable even if this call fails.
      renderOpsPresets([
        { label: "Dom 09h", context_name: "Culto Domingo 09h" },
        { label: "Dom 19h", context_name: "Culto Domingo 19h" },
        { label: "Qua 20h", context_name: "Culto Quarta 20h" },
      ]);
      pushContextSuggestion("Culto Domingo 09h");
      pushContextSuggestion("Culto Domingo 19h");
      pushContextSuggestion("Culto Quarta 20h");
    }
    state.initialized = true;
  }

  async function openKidsModule() {
    if (el.kidsPublicPageLink) {
      const slug = activeTenantSlug();
      el.kidsPublicPageLink.href = slug
        ? `/kids-public.html?tenant=${encodeURIComponent(slug)}`
        : "/kids-public.html";
    }
    showKidsView();
    await ensureInitialized();
    if (el.kidsPrinterModeSelect) {
      el.kidsPrinterModeSelect.value = printerMode();
    }
    if (el.kidsOpsContextName && !String(el.kidsOpsContextName.value || "").trim()) {
      setOpsContextName(lastContextName());
    } else if (el.kidsOpsContextName) {
      pushContextSuggestion(el.kidsOpsContextName.value);
    }
    pushContextSuggestion(lastContextName());
    const savedNav = String(localStorage.getItem("kidsNavSection") || "ops").trim() || "ops";
    showKidsSection(savedNav);
    setMessage("Modulo infantil (dev) pronto para operacao.", false);
  }

  async function handleError(action, fallback) {
    try {
      await action();
    } catch (error) {
      const message = error instanceof Error ? error.message : fallback;
      setMessage(message || fallback, true);
    }
  }

  async function performCheckout(checkinId, suggestedCode) {
    const context = await api(`/checkins/${checkinId}/checkout-context`);
    openCheckoutModalWithContext(checkinId, context, suggestedCode || "");
  }

  el.moduleKidsBtn.addEventListener("click", function () {
    handleError(openKidsModule, "Falha ao abrir modulo infantil.");
  });

  if (el.kidsNavOpsBtn) el.kidsNavOpsBtn.addEventListener("click", function () { showKidsSection("ops"); });
  if (el.kidsNavCheckoutsBtn) el.kidsNavCheckoutsBtn.addEventListener("click", function () { showKidsSection("checkouts"); });
  if (el.kidsNavMonitorBtn) el.kidsNavMonitorBtn.addEventListener("click", function () { showKidsSection("monitor"); });
  if (el.kidsNavCadastroBtn) el.kidsNavCadastroBtn.addEventListener("click", function () { showKidsSection("cadastro"); });
  if (el.kidsNavNotifsBtn) el.kidsNavNotifsBtn.addEventListener("click", function () { showKidsSection("notifs"); });

  if (el.kidsRefreshBtn) {
    el.kidsRefreshBtn.addEventListener("click", function () {
      handleError(refreshAll, "Falha ao atualizar dados do modulo infantil.");
    });
  }

  if (el.kidsFamilySearch) {
    el.kidsFamilySearch.addEventListener("change", function () {
      handleError(function () { return loadFamilies(el.kidsFamilySearch.value.trim()); }, "Falha ao buscar familias.");
    });
  }

  if (el.kidsCheckinFamilyId) {
    el.kidsCheckinFamilyId.addEventListener("change", renderCheckinChildrenList);
  }

  if (el.kidsRoomForm) {
    el.kidsRoomForm.addEventListener("submit", function (event) {
      event.preventDefault();
      handleError(async function () {
        const minYearsRaw = el.kidsRoomMinAgeYears ? String(el.kidsRoomMinAgeYears.value || "").trim() : "";
        const maxYearsRaw = el.kidsRoomMaxAgeYears ? String(el.kidsRoomMaxAgeYears.value || "").trim() : "";
        const capRaw = el.kidsRoomCapacity ? String(el.kidsRoomCapacity.value || "").trim() : "";
        const minYears = minYearsRaw ? Number(minYearsRaw) : null;
        const maxYears = maxYearsRaw ? Number(maxYearsRaw) : null;
        const capacity = capRaw ? Number(capRaw) : null;
        const minMonths = minYears != null && Number.isFinite(minYears) ? Math.max(0, Math.round(minYears * 12)) : null;
        const maxMonths = maxYears != null && Number.isFinite(maxYears) ? Math.max(0, Math.round(maxYears * 12)) : null;

        await api("/rooms", {
          method: "POST",
          body: JSON.stringify({
            name: el.kidsRoomName ? el.kidsRoomName.value.trim() : "",
            age_range_label: el.kidsRoomAgeRange ? el.kidsRoomAgeRange.value.trim() || null : null,
            min_age_months: minMonths,
            max_age_months: maxMonths,
            capacity: capacity && Number.isFinite(capacity) && capacity > 0 ? capacity : null,
            description: el.kidsRoomDescription ? el.kidsRoomDescription.value.trim() || null : null,
          }),
        });
        if (el.kidsRoomForm) el.kidsRoomForm.reset();
        await loadRooms();
        setMessage("Sala cadastrada com sucesso.", false);
      }, "Falha ao cadastrar sala.");
    });
  }

  if (el.kidsQuickQrForm) {
    el.kidsQuickQrForm.addEventListener("submit", function (event) {
      event.preventDefault();
      handleError(async function () {
        if (el.kidsOpsContextName) {
          const name = String(el.kidsOpsContextName.value || "").trim();
          if (name) localStorage.setItem("kidsLastContextName", name);
          else el.kidsOpsContextName.value = lastContextName();
        }
        const row = await api("/checkins/scan-qr", {
          method: "POST",
          body: JSON.stringify({
            qr_payload: el.kidsQuickQrPayload ? el.kidsQuickQrPayload.value.trim() : "",
            context_name: el.kidsOpsContextName ? el.kidsOpsContextName.value.trim() : "",
            context_type: "culto",
            room_name_override: null,
            accompanied_by_name: null,
          }),
        });
        if (el.kidsQuickQrForm) el.kidsQuickQrForm.reset();
        await Promise.all([loadSummary(), loadActiveCheckins(), loadChildren()]);
        const checkinId = row && row.id ? Number(row.id) : 0;
        if (!checkinId) throw new Error("Falha ao identificar o check-in.");

        // Print based on selected mode.
        const mode = printerMode();
        openLabelsForCheckins([checkinId], true, { layout: mode, autoClose: mode !== "both" });

        // Show a clear modal result (no extra clicks needed).
        const labelPayload = await api(`/checkins/${checkinId}/label`);
        openCheckinResultModal(labelPayload, checkinId);
        setMessage(`Check-in via QR realizado (ID ${checkinId}).`, false);
      }, "Falha no check-in via QR.");
    });
  }

  if (el.kidsQuickQrScanBtn) {
    el.kidsQuickQrScanBtn.addEventListener("click", function () {
      handleError(function () {
        return openQrScanner({
          onResult: function (raw) {
            if (el.kidsQuickQrPayload) el.kidsQuickQrPayload.value = String(raw || "").trim();
            suggestRoomFromQrPayload(raw);
            setMessage("QR lido com sucesso.", false);
            if (el.kidsOpsContextName && !String(el.kidsOpsContextName.value || "").trim()) {
              setOpsContextName(lastContextName());
            }
            if (el.kidsQuickQrForm && typeof el.kidsQuickQrForm.requestSubmit === "function") {
              el.kidsQuickQrForm.requestSubmit();
            }
          },
        });
      }, "Falha ao abrir leitor de QR.");
    });
  }

  if (el.kidsPrinterModeSelect) {
    el.kidsPrinterModeSelect.addEventListener("change", function () {
      const value = String(el.kidsPrinterModeSelect.value || "").trim();
      if (value === "band" || value === "label" || value === "both") {
        localStorage.setItem("kidsPrinterMode", value);
      } else {
        localStorage.setItem("kidsPrinterMode", "both");
      }
    });
  }

  if (el.kidsOpsContextName) {
    el.kidsOpsContextName.addEventListener("change", function () {
      const name = String(el.kidsOpsContextName.value || "").trim();
      if (name) {
        localStorage.setItem("kidsLastContextName", name);
        pushContextSuggestion(name);
      }
    });
  }

  if (el.kidsOpsPresetsEditBtn) {
    el.kidsOpsPresetsEditBtn.classList.toggle("hide", !canManageKids());
    el.kidsOpsPresetsEditBtn.addEventListener("click", function () {
      handleError(async function () {
        const initial = presetsToEditorText(state.settings && state.settings.ops_context_presets ? state.settings.ops_context_presets : []);
        const raw = window.prompt(
          "Edite os atalhos (1 por linha) no formato: ROTULO|NOME DO CULTO\n\nEx:\nDom 09h|Culto Domingo 09h\nQua 20h|Culto Quarta 20h",
          initial || "Dom 09h|Culto Domingo 09h\nDom 19h|Culto Domingo 19h\nQua 20h|Culto Quarta 20h",
        );
        if (raw == null) return;
        const parsed = parseEditorText(raw);
        const updated = await api("/settings", {
          method: "PUT",
          body: JSON.stringify({ ops_context_presets: parsed }),
        });
        state.settings = updated;
        const presets = normalizeOpsPresets(updated && updated.ops_context_presets ? updated.ops_context_presets : []);
        renderOpsPresets(presets);
        presets.forEach((preset) => pushContextSuggestion(preset.context_name));
        setMessage("Atalhos atualizados.", false);
      }, "Falha ao atualizar atalhos.");
    });
  }

  if (el.kidsQrScannerCloseBtn) {
    el.kidsQrScannerCloseBtn.addEventListener("click", function () {
      closeQrScanner();
    });
  }

  if (el.kidsCheckinResultCloseBtn) el.kidsCheckinResultCloseBtn.addEventListener("click", closeCheckinResultModal);
  if (el.kidsCheckinResultPrintBtn) {
    el.kidsCheckinResultPrintBtn.addEventListener("click", function () {
      const id = el.kidsCheckinResultModal ? Number(el.kidsCheckinResultModal.dataset.checkinId || 0) : 0;
      if (!id) return;
      openLabelsForCheckins([id], true, { layout: printerMode(), autoClose: false });
    });
  }
  if (el.kidsCheckinResultNewScanBtn) {
    el.kidsCheckinResultNewScanBtn.addEventListener("click", function () {
      closeCheckinResultModal();
      handleError(function () {
        return openQrScanner({
          onResult: function (raw) {
            if (el.kidsQuickQrPayload) el.kidsQuickQrPayload.value = String(raw || "").trim();
            suggestRoomFromQrPayload(raw);
            setMessage("QR lido com sucesso.", false);
            if (el.kidsOpsContextName && !String(el.kidsOpsContextName.value || "").trim()) {
              setOpsContextName(lastContextName());
            }
            if (el.kidsQuickQrForm && typeof el.kidsQuickQrForm.requestSubmit === "function") {
              el.kidsQuickQrForm.requestSubmit();
            }
          },
        });
      }, "Falha ao abrir leitor de QR.");
    });
  }

  async function confirmCheckoutFromModal() {
    try {
      const checkinId = Number(checkoutModalState.checkinId || 0);
      if (!checkinId) throw new Error("Check-in nao selecionado.");
      const tokenRaw = el.kidsCheckoutToken ? String(el.kidsCheckoutToken.value || "").trim() : "";
      if (!tokenRaw) throw new Error("Informe o codigo ou leia o QR da pulseira.");
      if (tokenRaw.startsWith("KIDS:")) {
        throw new Error('Este QR e da carteirinha (entrada). Para retirada, use o QR da pulseira/etiqueta.');
      }
      const guardianId = el.kidsCheckoutGuardianSelect && el.kidsCheckoutGuardianSelect.value
        ? Number(el.kidsCheckoutGuardianSelect.value)
        : null;
      const pickupName = el.kidsCheckoutPickupName ? String(el.kidsCheckoutPickupName.value || "").trim() : "";

      const isQrToken = tokenRaw.length >= 20;
      const body = {
        security_code: isQrToken ? null : tokenRaw,
        qr_token: isQrToken ? tokenRaw : null,
        pickup_guardian_id: guardianId && guardianId > 0 ? guardianId : null,
        pickup_person_name: pickupName || null,
      };
      if (el.kidsCheckoutConfirmBtn) el.kidsCheckoutConfirmBtn.disabled = true;
      await api(`/checkins/${checkinId}/checkout`, { method: "POST", body: JSON.stringify(body) });
      await Promise.all([loadSummary(), loadActiveCheckins()]);
      closeCheckoutModal();
      setMessage("Check-out realizado com sucesso.", false);
    } catch (error) {
      const msg = error instanceof Error ? error.message : "Falha ao realizar check-out.";
      setCheckoutMessage(msg, true);
    } finally {
      if (el.kidsCheckoutConfirmBtn) el.kidsCheckoutConfirmBtn.disabled = false;
    }
  }

  if (el.kidsCheckoutCloseBtn) el.kidsCheckoutCloseBtn.addEventListener("click", closeCheckoutModal);
  if (el.kidsCheckoutCancelBtn) el.kidsCheckoutCancelBtn.addEventListener("click", closeCheckoutModal);
  if (el.kidsCheckoutConfirmBtn) el.kidsCheckoutConfirmBtn.addEventListener("click", function () { confirmCheckoutFromModal(); });
  if (el.kidsCheckoutScanBtn) {
    el.kidsCheckoutScanBtn.addEventListener("click", function () {
      handleError(function () {
        return openQrScanner({
          onResult: function (raw) {
            if (el.kidsCheckoutToken) el.kidsCheckoutToken.value = String(raw || "").trim();
            // Auto-select the first authorized guardian if none is selected.
            if (el.kidsCheckoutGuardianSelect && !String(el.kidsCheckoutGuardianSelect.value || "").trim()) {
              const first = Array.from(el.kidsCheckoutGuardianSelect.options || []).find((opt) => opt && String(opt.value || "").trim());
              if (first) el.kidsCheckoutGuardianSelect.value = String(first.value);
            }
            if (el.kidsCheckoutPickupName && !String(el.kidsCheckoutPickupName.value || "").trim()) {
              const selected = el.kidsCheckoutGuardianSelect
                ? el.kidsCheckoutGuardianSelect.options[el.kidsCheckoutGuardianSelect.selectedIndex]
                : null;
              const name = selected && selected.textContent ? String(selected.textContent).trim() : "";
              if (name && name.toLowerCase() !== "selecione") el.kidsCheckoutPickupName.value = name;
            }
            setCheckoutMessage("QR lido. Confirmando retirada...", false);
            // 1-tap flow: auto-confirm after reading the wristband QR.
            confirmCheckoutFromModal();
          },
        });
      }, "Falha ao abrir leitor de QR.");
    });
  }

  if (el.kidsMonitorForm) {
    el.kidsMonitorForm.addEventListener("submit", function (event) {
      event.preventDefault();
      handleError(async function () {
        await loadRoomMonitoring();
        setMessage("Monitoramento atualizado.", false);
      }, "Falha ao carregar monitoramento da sala.");
    });
  }

  if (el.kidsVirtualCardSearchForm) {
    el.kidsVirtualCardSearchForm.addEventListener("submit", function (event) {
      event.preventDefault();
      handleError(async function () {
        await searchVirtualCards();
        setMessage("Carteirinha virtual localizada.", false);
      }, "Falha ao consultar carteirinha virtual.");
    });
  }

  if (el.kidsFamilyForm) {
    el.kidsFamilyForm.addEventListener("submit", function (event) {
      event.preventDefault();
      handleError(async function () {
        await api("/families", {
          method: "POST",
          body: JSON.stringify({
            family_name: el.kidsFamilyName ? el.kidsFamilyName.value.trim() : "",
            primary_responsible_name: el.kidsFamilyResponsible ? el.kidsFamilyResponsible.value.trim() || null : null,
            phone_primary: el.kidsFamilyPhone ? el.kidsFamilyPhone.value.trim() || null : null,
            email: el.kidsFamilyEmail ? el.kidsFamilyEmail.value.trim() || null : null,
            notes: el.kidsFamilyNotes ? el.kidsFamilyNotes.value.trim() || null : null,
          }),
        });
        if (el.kidsFamilyForm) el.kidsFamilyForm.reset();
        await loadFamilies();
        setMessage("Familia cadastrada com sucesso.", false);
      }, "Falha ao cadastrar família.");
    });
  }

  if (el.kidsChildForm) {
    el.kidsChildForm.addEventListener("submit", function (event) {
      event.preventDefault();
      handleError(async function () {
        await api("/children", {
          method: "POST",
          body: JSON.stringify({
            family_id: Number(el.kidsChildFamilyId ? el.kidsChildFamilyId.value : 0),
            full_name: el.kidsChildName ? el.kidsChildName.value.trim() : "",
            birth_date: el.kidsChildBirthDate && el.kidsChildBirthDate.value ? el.kidsChildBirthDate.value : null,
            age_group: el.kidsChildAgeGroup ? el.kidsChildAgeGroup.value.trim() || null : null,
            room_name: el.kidsChildRoom ? el.kidsChildRoom.value.trim() || null : null,
            gender: el.kidsChildGender ? el.kidsChildGender.value || null : null,
            photo_url: el.kidsChildPhotoUrl ? el.kidsChildPhotoUrl.value.trim() || null : null,
            allergies: el.kidsChildAllergies ? el.kidsChildAllergies.value.trim() || null : null,
            medical_restrictions: el.kidsChildMedical ? el.kidsChildMedical.value.trim() || null : null,
            special_needs: el.kidsChildSpecial ? el.kidsChildSpecial.value.trim() || null : null,
            behavioral_notes: el.kidsChildBehavior ? el.kidsChildBehavior.value.trim() || null : null,
            notes: null,
          }),
        });
        if (el.kidsChildForm) el.kidsChildForm.reset();
        await loadChildren();
        await loadSummary();
        setMessage("Crianca cadastrada com sucesso.", false);
      }, "Falha ao cadastrar crianca.");
    });
  }

  if (el.kidsGuardianForm) {
    el.kidsGuardianForm.addEventListener("submit", function (event) {
      event.preventDefault();
      handleError(async function () {
        await api("/guardians", {
          method: "POST",
          body: JSON.stringify({
            family_id: Number(el.kidsGuardianFamilyId ? el.kidsGuardianFamilyId.value : 0),
            full_name: el.kidsGuardianName ? el.kidsGuardianName.value.trim() : "",
            relationship: el.kidsGuardianRelationship ? el.kidsGuardianRelationship.value.trim() || null : null,
            phone: el.kidsGuardianPhone ? el.kidsGuardianPhone.value.trim() || null : null,
            photo_url: el.kidsGuardianPhotoUrl ? el.kidsGuardianPhotoUrl.value.trim() || null : null,
            is_authorized: el.kidsGuardianAuthorized ? el.kidsGuardianAuthorized.value === "true" : true,
            notes: null,
          }),
        });
        if (el.kidsGuardianForm) el.kidsGuardianForm.reset();
        setMessage("Responsavel cadastrado com sucesso.", false);
      }, "Falha ao cadastrar responsavel.");
    });
  }

  if (el.kidsCheckinForm) {
    el.kidsCheckinForm.addEventListener("submit", function (event) {
      event.preventDefault();
      handleError(async function () {
        const selectedChildIds = Array.from(el.kidsCheckinChildrenList ? el.kidsCheckinChildrenList.querySelectorAll(".kids-checkin-child:checked") : [])
          .map((checkbox) => Number(checkbox.value || 0))
          .filter((value) => value > 0);

        const created = await api("/checkins", {
          method: "POST",
          body: JSON.stringify({
            family_id: Number(el.kidsCheckinFamilyId ? el.kidsCheckinFamilyId.value : 0),
            child_ids: selectedChildIds,
            context_type: el.kidsCheckinContextType ? el.kidsCheckinContextType.value : "culto",
            context_name: el.kidsCheckinContextName ? el.kidsCheckinContextName.value.trim() : "",
            room_name: el.kidsCheckinRoomName ? el.kidsCheckinRoomName.value.trim() : "",
            accompanied_by_name: el.kidsCheckinAccompaniedBy ? el.kidsCheckinAccompaniedBy.value.trim() || null : null,
          }),
        });

        await Promise.all([loadSummary(), loadActiveCheckins()]);
        if (el.kidsCheckinForm) el.kidsCheckinForm.reset();
        renderCheckinChildrenList();
        openLabelsForCheckins(Array.isArray(created) ? created.map((row) => row.id) : [], true);
        setMessage("Check-in realizado com sucesso.", false);
      }, "Falha ao realizar check-in.");
    });
  }


  if (el.kidsVisitorForm) {
    el.kidsVisitorForm.addEventListener("submit", function (event) {
      event.preventDefault();
      handleError(async function () {
        await api("/visitors/quick-checkin", {
          method: "POST",
          body: JSON.stringify({
            child_name: el.kidsVisitorChildName ? el.kidsVisitorChildName.value.trim() : "",
            child_age: el.kidsVisitorAge && el.kidsVisitorAge.value ? Number(el.kidsVisitorAge.value) : null,
            responsible_name: el.kidsVisitorResponsible ? el.kidsVisitorResponsible.value.trim() : "",
            phone: el.kidsVisitorPhone ? el.kidsVisitorPhone.value.trim() : "",
            room_name: el.kidsVisitorRoom ? el.kidsVisitorRoom.value.trim() : "",
            context_name: el.kidsVisitorContext ? el.kidsVisitorContext.value.trim() : "",
            context_type: "culto",
            important_notes: el.kidsVisitorNotes ? el.kidsVisitorNotes.value.trim() || null : null,
          }),
        });

        if (el.kidsVisitorForm) el.kidsVisitorForm.reset();
        await refreshAll();
        setMessage("Visitante registrado e check-in realizado.", false);
      }, "Falha no check-in do visitante.");
    });
  }

  if (el.kidsQuickVisitorForm) {
    el.kidsQuickVisitorForm.addEventListener("submit", function (event) {
      event.preventDefault();
      handleError(async function () {
        if (el.kidsOpsContextName) {
          const name = String(el.kidsOpsContextName.value || "").trim();
          if (name) localStorage.setItem("kidsLastContextName", name);
          else el.kidsOpsContextName.value = lastContextName();
        }
        await api("/visitors/quick-checkin", {
          method: "POST",
          body: JSON.stringify({
            child_name: el.kidsQuickVisitorChildName ? el.kidsQuickVisitorChildName.value.trim() : "",
            child_age: null,
            responsible_name: el.kidsQuickVisitorResponsible ? el.kidsQuickVisitorResponsible.value.trim() : "",
            phone: el.kidsQuickVisitorPhone ? el.kidsQuickVisitorPhone.value.trim() : "",
            room_name: el.kidsQuickVisitorRoom ? el.kidsQuickVisitorRoom.value.trim() : "",
            context_name: el.kidsOpsContextName ? el.kidsOpsContextName.value.trim() : "",
            context_type: "culto",
            important_notes: null,
          }),
        });

        if (el.kidsQuickVisitorForm) el.kidsQuickVisitorForm.reset();
        await refreshAll();
        setMessage("Visitante registrado e check-in realizado.", false);
      }, "Falha no check-in do visitante.");
    });
  }

  if (el.kidsNotifyForm) {
    el.kidsNotifyForm.addEventListener("submit", function (event) {
      event.preventDefault();
      handleError(async function () {
        await api("/notifications", {
          method: "POST",
          body: JSON.stringify({
            family_id: el.kidsNotifyFamilyId && el.kidsNotifyFamilyId.value ? Number(el.kidsNotifyFamilyId.value) : null,
            child_id: el.kidsNotifyChildId && el.kidsNotifyChildId.value ? Number(el.kidsNotifyChildId.value) : null,
            channel: el.kidsNotifyChannel ? el.kidsNotifyChannel.value : "email",
            message_type: el.kidsNotifyType ? el.kidsNotifyType.value : "checkin_confirmation",
            message: el.kidsNotifyMessage ? el.kidsNotifyMessage.value.trim() : "",
          }),
        });
        if (el.kidsNotifyForm) el.kidsNotifyForm.reset();
        await loadNotifications();
        setMessage("Notificacao registrada com sucesso.", false);
      }, "Falha ao enviar notificacao.");
    });
  }

  function bindCheckoutTable(tableBody) {
    if (!tableBody) return;
    tableBody.addEventListener("click", function (event) {
      const target = event.target;
      if (!(target instanceof HTMLElement)) return;
      if (target.classList.contains("kids-label-btn")) {
        const checkinId = Number(target.getAttribute("data-checkin-id") || 0);
        if (!checkinId) return;
        openLabelsForCheckins([checkinId], false, { layout: "label" });
        return;
      }
      if (target.classList.contains("kids-band-btn")) {
        const checkinId = Number(target.getAttribute("data-checkin-id") || 0);
        if (!checkinId) return;
        openLabelsForCheckins([checkinId], false, { layout: "band" });
        return;
      }
      if (!target.classList.contains("kids-checkout-btn")) return;

      const checkinId = Number(target.getAttribute("data-checkin-id") || 0);
      const suggestedCode = String(target.getAttribute("data-security-code") || "");
      if (!checkinId) return;

      handleError(async function () {
        await performCheckout(checkinId, suggestedCode);
      }, "Falha ao realizar check-out.");
    });
  }

  bindCheckoutTable(el.kidsActiveCheckinsBody);
  bindCheckoutTable(el.kidsActiveCheckinsQuickBody);
  bindCheckoutTable(el.kidsActiveCheckinsAdminBody);
})();
