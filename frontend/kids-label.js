(function () {
  const el = {
    grid: document.getElementById("kidsLabelGrid"),
    bandGrid: document.getElementById("kidsBandGrid"),
    labelSection: document.getElementById("kidsLabelSectionLabel"),
    bandSection: document.getElementById("kidsLabelSectionBand"),
    message: document.getElementById("kidsLabelMessage"),
    hint: document.getElementById("kidsLabelHint"),
    printBtn: document.getElementById("kidsLabelPrintBtn"),
  };

  function setMessage(text, isError) {
    if (!el.message) return;
    el.message.textContent = text || "";
    el.message.style.color = isError ? "#b42318" : "#5f6b6d";
  }

  function escapeHtml(value) {
    return String(value == null ? "" : value)
      .replaceAll("&", "&amp;")
      .replaceAll("<", "&lt;")
      .replaceAll(">", "&gt;")
      .replaceAll('"', "&quot;")
      .replaceAll("'", "&#39;");
  }

  function token() {
    return String(localStorage.getItem("accessToken") || "");
  }

  function parseIds() {
    const params = new URLSearchParams(window.location.search || "");
    const raw = params.get("checkins") || params.get("ids") || params.get("checkin") || "";
    return raw
      .split(",")
      .map((value) => Number(String(value || "").trim()))
      .filter((value) => Number.isFinite(value) && value > 0);
  }

  function wantsAutoPrint() {
    const params = new URLSearchParams(window.location.search || "");
    const raw = (params.get("autoprint") || "").trim();
    return raw === "1" || raw.toLowerCase() === "true" || raw.toLowerCase() === "yes";
  }

  function wantsAutoClose() {
    const params = new URLSearchParams(window.location.search || "");
    const raw = (params.get("autoclose") || "").trim();
    return raw === "1" || raw.toLowerCase() === "true" || raw.toLowerCase() === "yes";
  }

  function layoutMode() {
    const params = new URLSearchParams(window.location.search || "");
    const raw = String(params.get("layout") || "").trim().toLowerCase();
    if (raw === "band" || raw === "label" || raw === "both") return raw;
    return "both";
  }

  function applyLayout() {
    const mode = layoutMode();
    document.body.classList.remove("kids-layout-band", "kids-layout-label", "kids-layout-both");
    document.body.classList.add(`kids-layout-${mode}`);

    if (el.labelSection) el.labelSection.style.display = mode === "band" ? "none" : "";
    if (el.bandSection) el.bandSection.style.display = mode === "label" ? "none" : "";
  }

  function formatDateTime(value) {
    try {
      if (!value) return "-";
      const date = new Date(String(value));
      if (Number.isNaN(date.getTime())) return String(value);
      return date.toLocaleString("pt-BR");
    } catch (_error) {
      return String(value || "-");
    }
  }

  async function api(path, options) {
    const auth = token();
    if (!auth) throw new Error("Sessao nao autenticada. Entre no sistema e tente novamente.");

    const requestOptions = options || {};
    const headers = Object.assign({}, requestOptions.headers || {}, { Authorization: `Bearer ${auth}` });
    const response = await fetch(path, {
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

    return response;
  }

  async function fetchLabelPayload(checkinId) {
    const response = await api(`/api/v1/child-checkin/checkins/${checkinId}/label`);
    return response.json();
  }

  async function fetchQrBlobUrl(checkinId) {
    const response = await api(`/api/v1/child-checkin/checkins/${checkinId}/label/qr.png`);
    const blob = await response.blob();
    return URL.createObjectURL(blob);
  }

  function renderLabelCard(payload, qrSrc) {
    const qrImage = qrSrc
      ? `<img class="kids-label-qr" alt="QR de retirada" src="${escapeHtml(qrSrc)}">`
      : `<div class="kids-label-qr-placeholder">Sem QR</div>`;

    return `<article class="kids-label-card">
      <div class="kids-label-top">
        <div class="kids-label-title">
          <strong>${escapeHtml(payload.child_name || "Crianca")}</strong>
          <div class="kids-label-meta">
            <span>${escapeHtml(payload.room_name || "-")}</span>
            <span>${escapeHtml(payload.context_name || "-")}</span>
            <span>${escapeHtml(formatDateTime(payload.checkin_at))}</span>
          </div>
        </div>
        ${qrImage}
      </div>

      <div class="kids-label-code">
        <span>Codigo de seguranca</span>
        <strong>${escapeHtml(payload.security_code || "-")}</strong>
      </div>

      <div class="kids-label-footer">
        <span>${escapeHtml(payload.family_name || "-")}</span>
        <span class="kids-label-token">${escapeHtml(payload.qr_token || "")}</span>
      </div>
    </article>`;
  }

  function renderWristband(payload, qrSrc) {
    const qrImage = qrSrc
      ? `<img class="kids-band-qr" alt="QR de retirada" src="${escapeHtml(qrSrc)}">`
      : `<div class="kids-band-qr kids-band-qr--placeholder">Sem QR</div>`;

    return `<article class="kids-band">
      ${qrImage}
      <div class="kids-band-main">
        <strong>${escapeHtml(payload.child_name || "Crianca")}</strong>
        <div class="kids-band-meta">
          <span>${escapeHtml(payload.room_name || "-")}</span>
          <span>${escapeHtml(payload.context_name || "-")}</span>
        </div>
      </div>
      <div class="kids-band-code">
        <span>Codigo</span>
        <strong>${escapeHtml(payload.security_code || "-")}</strong>
      </div>
      <div class="kids-band-note">Retirar somente com responsavel + codigo</div>
    </article>`;
  }

  async function load() {
    if (!el.grid) return;
    applyLayout();

    const ids = parseIds();
    if (!ids.length) {
      if (el.hint) el.hint.textContent = "Nenhum check-in informado na URL.";
      el.grid.innerHTML = "";
      setMessage("Informe o parametro ?checkins=ID,ID para carregar as etiquetas.", true);
      return;
    }

    if (el.hint) el.hint.textContent = `Carregando ${ids.length} etiqueta(s)...`;
    setMessage("", false);
    el.grid.innerHTML = '<div class="tiny">Carregando...</div>';

    const payloads = await Promise.all(ids.map((id) => fetchLabelPayload(id)));

    const qrUrls = await Promise.all(
      ids.map(async (id) => {
        try {
          return await fetchQrBlobUrl(id);
        } catch (_error) {
          return "";
        }
      }),
    );

    el.grid.innerHTML = payloads
      .map((payload, idx) => renderLabelCard(payload, qrUrls[idx] || ""))
      .join("");
    if (el.bandGrid) {
      el.bandGrid.innerHTML = payloads
        .map((payload, idx) => renderWristband(payload, qrUrls[idx] || ""))
        .join("");
    }

    if (el.hint) el.hint.textContent = `Pronto: ${ids.length} etiqueta(s).`;
  }

  if (el.printBtn) {
    el.printBtn.addEventListener("click", function () {
      window.print();
    });
  }

  load()
    .then(function () {
      if (!wantsAutoPrint()) return;
      const shouldClose = wantsAutoClose();
      if (shouldClose) {
        window.addEventListener("afterprint", function () {
          try {
            window.close();
          } catch (_error) {
          }
        }, { once: true });
      }
      window.setTimeout(function () {
        window.print();
        if (shouldClose) {
          // Fallback: some browsers don't fire afterprint reliably.
          window.setTimeout(function () {
            try {
              window.close();
            } catch (_error) {
            }
          }, 1800);
        }
      }, 450);
    })
    .catch(function (error) {
      const message = error instanceof Error ? error.message : "Falha ao carregar etiquetas.";
      setMessage(message, true);
      if (el.hint) el.hint.textContent = "Falha ao carregar etiquetas.";
      if (el.grid) el.grid.innerHTML = "";
    });
})();
