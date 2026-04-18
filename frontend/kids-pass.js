(function () {
  const el = {
    grid: document.getElementById("kidsPassGrid"),
    message: document.getElementById("kidsPassMessage"),
    hint: document.getElementById("kidsPassHint"),
    printBtn: document.getElementById("kidsPassPrintBtn"),
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

  function q(name) {
    const params = new URLSearchParams(window.location.search || "");
    return String(params.get(name) || "").trim();
  }

  function effectiveTenantSlug(rawValue) {
    const direct = String(rawValue || "").trim();
    if (!direct) return "";
    return direct.toLowerCase();
  }

  async function publicApi(path) {
    const response = await fetch(`/api/v1/child-checkin/public${path}`, { method: "GET" });
    if (!response.ok) {
      let detail = `Erro ${response.status}`;
      try {
        const body = await response.json();
        if (body && typeof body.detail === "string") detail = body.detail;
      } catch (_error) {
      }
      throw new Error(detail);
    }
    return response.json();
  }

  function cardQrUrl(tenantSlug, familyCode, childId) {
    return `/api/v1/child-checkin/public/tenants/${encodeURIComponent(tenantSlug)}/families/${encodeURIComponent(familyCode)}/children/${encodeURIComponent(String(childId))}/qr.png`;
  }

  function renderCard(tenantSlug, familyCode, card) {
    const guardians = Array.isArray(card.guardians) ? card.guardians : [];
    const norm = (value) => String(value || "").trim().toLowerCase();
    const isPickup = (g) => {
      const rel = norm(g && g.relationship);
      return rel.includes("retirada") || rel.includes("saida") || rel.includes("pickup");
    };
    const responsibleGuardian =
      guardians.find((g) => g && norm(g.relationship).includes("principal")) ||
      guardians.find((g) => g && norm(g.relationship).includes("responsavel")) ||
      guardians[0] ||
      null;
    const pickupGuardian =
      guardians.find((g) => g && isPickup(g)) ||
      guardians.find((g) => g && g !== responsibleGuardian && g.is_authorized) ||
      null;

    const childPhotoSrc = card.child_photo_url ? String(card.child_photo_url) : "";
    const responsiblePhotoSrc = responsibleGuardian && responsibleGuardian.photo_url ? String(responsibleGuardian.photo_url) : "";
    const pickupPhotoSrc = pickupGuardian && pickupGuardian.photo_url ? String(pickupGuardian.photo_url) : "";

    const childPhoto = `<div class="kids-photo-frame kids-photo-frame--lg">
      ${
        childPhotoSrc
          ? `<img src="${escapeHtml(childPhotoSrc)}" alt="Foto da crianca" onerror="this.classList.add('hide')">`
          : ""
      }
      <div class="kids-photo-fallback">Sem foto</div>
    </div>`;

    const responsiblePhoto = `<div class="kids-photo-frame kids-photo-frame--sm">
      ${
        responsiblePhotoSrc
          ? `<img src="${escapeHtml(responsiblePhotoSrc)}" alt="Foto do responsavel" onerror="this.classList.add('hide')">`
          : ""
      }
      <div class="kids-photo-fallback">Sem foto</div>
    </div>`;

    const pickupPhoto = `<div class="kids-photo-frame kids-photo-frame--sm">
      ${
        pickupPhotoSrc
          ? `<img src="${escapeHtml(pickupPhotoSrc)}" alt="Foto do responsavel da retirada" onerror="this.classList.add('hide')">`
          : ""
      }
      <div class="kids-photo-fallback">Sem foto</div>
    </div>`;

    const qr = cardQrUrl(tenantSlug, familyCode, card.child_id);

    return `<section class="kids-pass-card">
      <div class="kids-pass-card-top">
        <div class="kids-pass-card-main">
          <div class="kids-pass-hero">
            ${childPhoto}
            <div class="kids-pass-hero-text">
              <div class="kids-pass-hero-kicker">Crianca</div>
              <div class="kids-pass-hero-name">${escapeHtml(card.child_name || "Crianca")}</div>
              <div class="kids-pass-hero-meta">
                <div>Familia: ${escapeHtml(card.family_name || "-")}</div>
                <div>Sala: ${escapeHtml(card.room_name || "-")}</div>
              </div>
            </div>
          </div>

          <div class="kids-pass-card-photos">
            <div class="kids-pass-photo-block">
              <span class="kids-pass-photo-label">Responsavel</span>
              ${responsiblePhoto}
              <div class="kids-pass-card-photo-meta">
                <div>${escapeHtml(responsibleGuardian && responsibleGuardian.full_name ? responsibleGuardian.full_name : "-")}</div>
                <div class="tiny">${escapeHtml(responsibleGuardian ? (responsibleGuardian.is_authorized ? "Autorizado" : "Nao autorizado") : "")}</div>
              </div>
            </div>
            <div class="kids-pass-photo-block">
              <span class="kids-pass-photo-label">Retirada</span>
              ${pickupPhoto}
              <div class="kids-pass-card-photo-meta">
                <div>${escapeHtml(pickupGuardian && pickupGuardian.full_name ? pickupGuardian.full_name : "-")}</div>
                <div class="tiny">${escapeHtml(pickupGuardian ? (pickupGuardian.is_authorized ? "Autorizado" : "Nao autorizado") : "")}</div>
              </div>
            </div>
          </div>

          <div class="kids-pass-card-guardians">
            <span class="tiny">Responsaveis cadastrados</span>
            <div class="kids-pass-card-guardians-list">
              ${guardians.length ? guardians.map((g) => `<div>${escapeHtml(g.full_name || "-")} <span class="tiny">(${g.is_authorized ? "autorizado" : "nao autorizado"})</span></div>`).join("") : "<div>-</div>"}
            </div>
          </div>
        </div>
        <div class="kids-pass-card-qr">
          <img src="${escapeHtml(qr)}" alt="QR Code da carteirinha">
          <div class="kids-pass-card-code">${escapeHtml(card.family_code || familyCode || "-")}</div>
        </div>
      </div>
    </section>`;
  }

  async function load() {
    if (!el.grid) return;
    const tenantSlug = effectiveTenantSlug(q("tenant"));
    const familyCode = q("code");
    if (!tenantSlug || !familyCode) {
      if (el.hint) el.hint.textContent = "Parametros ausentes.";
      setMessage("Use a URL com ?tenant=SLUG&code=FAM-XXXXXX", true);
      return;
    }

    if (el.hint) el.hint.textContent = "Buscando carteirinha...";
    const payload = await publicApi(`/tenants/${encodeURIComponent(tenantSlug)}/virtual-cards?family_code=${encodeURIComponent(familyCode)}`);
    const cards = Array.isArray(payload && payload.cards) ? payload.cards : [];
    if (!cards.length) {
      if (el.hint) el.hint.textContent = "Nenhuma carteirinha encontrada.";
      el.grid.innerHTML = "";
      return;
    }

    el.grid.innerHTML = cards.map((card) => renderCard(tenantSlug, familyCode, card)).join("");
    if (el.hint) el.hint.textContent = `Pronto: ${cards.length} carteirinha(s).`;
  }

  if (el.printBtn) {
    el.printBtn.addEventListener("click", function () {
      window.print();
    });
  }

  load().catch(function (error) {
    const message = error instanceof Error ? error.message : "Falha ao carregar carteirinha.";
    setMessage(message, true);
    if (el.hint) el.hint.textContent = "Falha ao carregar.";
    if (el.grid) el.grid.innerHTML = "";
  });
})();
