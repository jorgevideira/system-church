(function () {
  const el = {
    message: document.getElementById("kidsPublicMessage"),

    startView: document.getElementById("kidsPublicStartView"),
    startRegisterBtn: document.getElementById("kidsPublicStartRegisterBtn"),
    startLoginBtn: document.getElementById("kidsPublicStartLoginBtn"),

    registerPanel: document.getElementById("kidsPublicRegisterPanel"),
    backFromRegisterBtn: document.getElementById("kidsPublicBackFromRegisterBtn"),

    loginPanel: document.getElementById("kidsPublicLoginPanel"),
    backFromLoginBtn: document.getElementById("kidsPublicBackFromLoginBtn"),
    loginTitle: document.getElementById("kidsPublicLoginTitle"),
    loginHint: document.getElementById("kidsPublicLoginHint"),

    preRegisterForm: document.getElementById("kidsPublicPreRegisterForm"),
    tenantSlug: document.getElementById("kidsPublicTenantSlug"),
    tenantSlugLabel: document.getElementById("kidsPublicTenantSlugLabel"),
    responsible: document.getElementById("kidsPublicResponsible"),
    responsiblePhotoPreview: document.getElementById("kidsPublicResponsiblePhotoPreview"),
    responsiblePhotoBtn: document.getElementById("kidsPublicResponsiblePhotoBtn"),
    responsiblePhotoClearBtn: document.getElementById("kidsPublicResponsiblePhotoClearBtn"),
    responsiblePhotoStatus: document.getElementById("kidsPublicResponsiblePhotoStatus"),
    phone: document.getElementById("kidsPublicPhone"),
    email: document.getElementById("kidsPublicEmail"),
    pin: document.getElementById("kidsPublicPin"),
    childrenCount: document.getElementById("kidsPublicChildrenCount"),
    childrenWrap: document.getElementById("kidsPublicChildrenWrap"),
    guardianName: document.getElementById("kidsPublicGuardianName"),
    guardianPhone: document.getElementById("kidsPublicGuardianPhone"),
    guardianPhotoPreview: document.getElementById("kidsPublicGuardianPhotoPreview"),
    guardianPhotoBtn: document.getElementById("kidsPublicGuardianPhotoBtn"),
    guardianPhotoClearBtn: document.getElementById("kidsPublicGuardianPhotoClearBtn"),
    guardianPhotoStatus: document.getElementById("kidsPublicGuardianPhotoStatus"),
    preRegisterSubmitBtn: document.getElementById("kidsPublicPreRegisterSubmitBtn"),

    loginForm: document.getElementById("kidsPublicLoginForm"),
    loginTenantSlug: document.getElementById("kidsPublicLoginTenantSlug"),
    loginTenantSlugLabel: document.getElementById("kidsPublicLoginTenantSlugLabel"),
    loginEmail: document.getElementById("kidsPublicLoginEmail"),
    loginPin: document.getElementById("kidsPublicLoginPin"),
    accountPanel: document.getElementById("kidsPublicAccountPanel"),
    accountFamilyCode: document.getElementById("kidsPublicAccountFamilyCode"),
    accountLists: document.getElementById("kidsPublicAccountLists"),
    logoutBtn: document.getElementById("kidsPublicLogoutBtn"),
    addChildForm: document.getElementById("kidsPublicAddChildForm"),
    addChildName: document.getElementById("kidsPublicAddChildName"),
    addChildBirthDate: document.getElementById("kidsPublicAddChildBirthDate"),
    addChildAllergies: document.getElementById("kidsPublicAddChildAllergies"),
    addChildPhotoBtn: document.getElementById("kidsPublicAddChildPhotoBtn"),
    addChildPhotoClearBtn: document.getElementById("kidsPublicAddChildPhotoClearBtn"),
    addChildPhotoPreview: document.getElementById("kidsPublicAddChildPhotoPreview"),
    addChildPhotoStatus: document.getElementById("kidsPublicAddChildPhotoStatus"),
    addGuardianForm: document.getElementById("kidsPublicAddGuardianForm"),
    addGuardianName: document.getElementById("kidsPublicAddGuardianName"),
    addGuardianPhone: document.getElementById("kidsPublicAddGuardianPhone"),
    addGuardianAuthorized: document.getElementById("kidsPublicAddGuardianAuthorized"),
    registerCardsResult: document.getElementById("kidsPublicRegisterCardsResult"),
    loginCardsResult: document.getElementById("kidsPublicLoginCardsResult"),
    lookupCardsResult: null,

    photoModal: document.getElementById("kidsPhotoCaptureModal"),
    photoTitle: document.getElementById("kidsPhotoCaptureTitle"),
    photoCloseBtn: document.getElementById("kidsPhotoCaptureCloseBtn"),
    photoVideo: document.getElementById("kidsPhotoCaptureVideo"),
    photoCanvas: document.getElementById("kidsPhotoCaptureCanvas"),
    photoStatus: document.getElementById("kidsPhotoCaptureStatus"),
    photoSnapBtn: document.getElementById("kidsPhotoCaptureSnapBtn"),
    photoUseBtn: document.getElementById("kidsPhotoCaptureUseBtn"),
    photoRetakeBtn: document.getElementById("kidsPhotoCaptureRetakeBtn"),

    forgotToggleBtn: document.getElementById("kidsPublicForgotToggleBtn"),
    forgotWrap: document.getElementById("kidsPublicForgotWrap"),
    recoverStep1: document.getElementById("kidsPublicRecoverStep1"),
    recoverStep2: document.getElementById("kidsPublicRecoverStep2"),
    recoverStep3: document.getElementById("kidsPublicRecoverStep3"),
    recoverEmail: document.getElementById("kidsPublicRecoverEmail"),
    recoverRequestBtn: document.getElementById("kidsPublicRecoverRequestBtn"),
    recoverCode: document.getElementById("kidsPublicRecoverCode"),
    recoverVerifyBtn: document.getElementById("kidsPublicRecoverVerifyBtn"),
    recoverNewPin: document.getElementById("kidsPublicRecoverNewPin"),
    recoverConfirmBtn: document.getElementById("kidsPublicRecoverConfirmBtn"),

    editChildModal: document.getElementById("kidsPublicEditChildModal"),
    editChildCloseBtn: document.getElementById("kidsPublicEditChildCloseBtn"),
    editChildCancelBtn: document.getElementById("kidsPublicEditChildCancelBtn"),
    editChildForm: document.getElementById("kidsPublicEditChildForm"),
    editChildSaveBtn: document.getElementById("kidsPublicEditChildSaveBtn"),
    editChildMessage: document.getElementById("kidsPublicEditChildMessage"),
    editChildName: document.getElementById("kidsPublicEditChildName"),
    editChildBirthDate: document.getElementById("kidsPublicEditChildBirthDate"),
    editChildAllergies: document.getElementById("kidsPublicEditChildAllergies"),
    editChildPhotoBtn: document.getElementById("kidsPublicEditChildPhotoBtn"),
    editChildPhotoClearBtn: document.getElementById("kidsPublicEditChildPhotoClearBtn"),
    editChildPhotoPreview: document.getElementById("kidsPublicEditChildPhotoPreview"),
    editChildPhotoStatus: document.getElementById("kidsPublicEditChildPhotoStatus"),
  };

  function setMessage(text, isError) {
    if (!el.message) return;
    el.message.textContent = text || "";
    el.message.style.color = isError ? "#b42318" : "#5f6b6d";
  }

  function showView(name) {
    const view = String(name || "start").trim() || "start";
    if (el.startView) el.startView.classList.toggle("hide", view !== "start");
    if (el.registerPanel) el.registerPanel.classList.toggle("hide", view !== "register");
    if (el.loginPanel) el.loginPanel.classList.toggle("hide", view !== "login");
    window.scrollTo({ top: 0, behavior: "smooth" });
  }

  function escapeHtml(value) {
    return String(value == null ? "" : value)
      .replaceAll("&", "&amp;")
      .replaceAll("<", "&lt;")
      .replaceAll(">", "&gt;")
      .replaceAll('"', "&quot;")
      .replaceAll("'", "&#39;");
  }

  function normalizeSlug(value) {
    return String(value || "")
      .normalize("NFD")
      .replace(/[\u0300-\u036f]/g, "")
      .trim()
      .toLowerCase()
      .replace(/[^a-z0-9\s-]/g, "")
      .replace(/\s+/g, "-")
      .replace(/-+/g, "-");
  }

  function effectiveTenantSlug(rawValue) {
    const direct = String(rawValue || "").trim();
    if (!direct) return "";
    if (/^[a-z0-9-]+$/i.test(direct)) return direct.toLowerCase();
    return normalizeSlug(direct);
  }

  function q(name) {
    const params = new URLSearchParams(window.location.search || "");
    return String(params.get(name) || "").trim();
  }

  function sanitizePhoneDigits(value) {
    let digits = String(value || "").replace(/\D+/g, "");
    // Normalize common input like +55 (country code).
    if (digits.length > 11 && digits.startsWith("55")) digits = digits.slice(2);
    if (digits.length > 11) digits = digits.slice(-11);
    return digits;
  }

  function formatBrazilPhone(value) {
    const digits = sanitizePhoneDigits(value);
    const ddd = digits.slice(0, 2);
    const rest = digits.slice(2);
    if (!ddd) return "";
    if (!rest) return `(${ddd})`;

    if (rest.length <= 4) return `(${ddd}) ${rest}`;
    if (rest.length <= 8) return `(${ddd}) ${rest.slice(0, 4)}-${rest.slice(4)}`;
    return `(${ddd}) ${rest.slice(0, 5)}-${rest.slice(5, 9)}`;
  }

  function bindPhoneMask(input) {
    if (!input) return;
    input.addEventListener("input", function () {
      const formatted = formatBrazilPhone(input.value);
      if (formatted) input.value = formatted;
    });
    input.addEventListener("blur", function () {
      const formatted = formatBrazilPhone(input.value);
      if (formatted) input.value = formatted;
    });
  }

  function guessFamilyNameFromResponsible(fullName) {
    const parts = String(fullName || "")
      .trim()
      .split(/\s+/)
      .filter(Boolean);
    if (!parts.length) return "Familia";
    const last = parts.length >= 2 ? parts[parts.length - 1] : parts[0];
    return `Familia ${last}`.trim();
  }

  async function publicApi(path, options) {
    const requestOptions = options || {};
    const headers = Object.assign({}, requestOptions.headers || {});
    if (requestOptions.body && !headers["Content-Type"]) {
      headers["Content-Type"] = "application/json";
    }

    const response = await fetch(`/api/v1/child-checkin/public${path}`, {
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
      if (response.status === 404) {
        detail = "Igreja nao encontrada. Confira o slug (ex: igreja-de-vencedores).";
      }
      throw new Error(detail);
    }

    if (response.status === 204) return null;
    return response.json();
  }

  function renderCardsInto(targetEl, payload) {
    if (!targetEl) return;
    const cards = Array.isArray(payload && payload.cards) ? payload.cards : [];
    if (!cards.length) {
      targetEl.innerHTML = '<p class="tiny">Nenhuma carteirinha encontrada.</p>';
      return;
    }

    const tenantSlug = String(payload && payload.tenant_slug || "").trim();
    const familyCode = String(payload && payload.family_code || "").trim();
    const printLink = tenantSlug && familyCode
      ? `/kids-pass.html?tenant=${encodeURIComponent(tenantSlug)}&code=${encodeURIComponent(familyCode)}`
      : "";
    const printButton = printLink
      ? `<a class="btn ghost" href="${escapeHtml(printLink)}" target="_blank" rel="noopener">Imprimir carteirinha</a>`
      : "";

    targetEl.innerHTML = cards
      .map((card) => {
        const guardians = Array.isArray(card.guardians) ? card.guardians : [];
        const guardiansHtml = guardians
          .map((guardian) => `${escapeHtml(guardian.full_name || "-")} - ${guardian.is_authorized ? "autorizado" : "nao autorizado"}`)
          .join("<br>");

        const photoSrc = card.child_photo_url ? String(card.child_photo_url) : "";
        const photo = `<div class="kids-photo-frame kids-photo-frame--xs">
          ${photoSrc ? `<img src="${escapeHtml(photoSrc)}" alt="Foto da crianca" onerror="this.classList.add('hide')">` : ""}
          <div class="kids-photo-fallback">Sem foto</div>
        </div>`;

        const qrUrl = tenantSlug && familyCode && card.child_id
          ? `/api/v1/child-checkin/public/tenants/${encodeURIComponent(tenantSlug)}/families/${encodeURIComponent(familyCode)}/children/${encodeURIComponent(String(card.child_id))}/qr.png`
          : "";
        const qrImg = qrUrl
          ? `<img src="${escapeHtml(qrUrl)}" alt="QR Code" style="width:92px;height:92px;border-radius:12px;border:1px solid var(--line);background:#fff;object-fit:contain;">`
          : "";

        return `<article class="panel" style="margin-bottom:0.6rem;">
          <div style="display:flex; gap:0.8rem; align-items:center; justify-content:space-between; flex-wrap:wrap;">
            <div style="display:flex; gap:0.8rem; align-items:center;">
            ${photo}
            <div>
              <strong>${escapeHtml(card.child_name || "Crianca")}</strong>
              <div class="tiny">Familia: ${escapeHtml(card.family_name || "-")}</div>
              <div class="tiny">Codigo: ${escapeHtml(card.family_code || "-")}</div>
              <div class="tiny">Sala: ${escapeHtml(card.room_name || "-")}</div>
              <div class="tiny">QR payload: ${escapeHtml(card.qr_payload || "-")}</div>
            </div>
            </div>
            <div style="display:grid; gap:0.35rem; justify-items:end;">
              ${qrImg}
              ${printButton}
            </div>
          </div>
          <div class="tiny" style="margin-top:0.5rem;">Responsaveis:<br>${guardiansHtml || "-"}</div>
        </article>`;
      })
      .join("");
  }

  function renderCards(payload) {
    renderCardsInto(el.registerCardsResult, payload);
    renderCardsInto(el.loginCardsResult, payload);
  }

  let photoStream = null;
  let currentCaptureKind = "";
  let currentCaptureChildIndex = 0;
  let pendingPhotoBlob = null;
  let childPhotoBlobs = [];
  let guardianPhotoBlob = null;
  let responsiblePhotoBlob = null;
  let pendingUploadInfo = null;
  let submitting = false;
  let lastMe = null;
  let accountTenantSlug = "";
  let accountFamilyCode = "";
  let addChildPhotoBlob = null;
  let editChildPhotoBlob = null;
  let editingChildId = 0;

  function accountCtxOrThrow() {
    const tenantSlug = effectiveTenantSlug(accountTenantSlug || (el.loginTenantSlug && el.loginTenantSlug.value) || (el.tenantSlug && el.tenantSlug.value));
    if (!tenantSlug) throw new Error("Slug da igreja ausente.");
    if (!accountFamilyCode) throw new Error("Codigo da familia ausente.");
    return { tenantSlug, familyCode: accountFamilyCode };
  }

  function setImgPreview(imgEl, blob) {
    if (!imgEl) return;
    if (!blob) {
      imgEl.src = "";
      imgEl.classList.add("hide");
      return;
    }
    imgEl.src = URL.createObjectURL(blob);
    imgEl.classList.remove("hide");
  }

  function setPhotoStatus(node, ok) {
    if (!node) return;
    node.classList.toggle("is-ok", !!ok);
    node.classList.toggle("is-missing", !ok);
    const label = ok ? "Ok" : "Falta";
    node.setAttribute("aria-label", label);
    node.setAttribute("title", label);
  }

  function clampChildrenCount(value) {
    const v = Number.parseInt(String(value || ""), 10);
    if (!Number.isFinite(v) || v < 1) return 1;
    if (v > 5) return 5;
    return v;
  }

  function desiredChildrenCount() {
    return clampChildrenCount(el.childrenCount && el.childrenCount.value);
  }

  function ensureChildPhotoArray(count) {
    const normalized = clampChildrenCount(count);
    if (!Array.isArray(childPhotoBlobs)) childPhotoBlobs = [];
    if (childPhotoBlobs.length > normalized) childPhotoBlobs = childPhotoBlobs.slice(0, normalized);
    while (childPhotoBlobs.length < normalized) childPhotoBlobs.push(null);
  }

  function childBlock(idx) {
    if (!el.childrenWrap) return null;
    return el.childrenWrap.querySelector(`[data-child-block][data-child-idx="${idx}"]`);
  }

  function childDom(idx) {
    const block = childBlock(idx);
    if (!block) return null;
    return {
      block,
      name: block.querySelector("[data-child-name]"),
      birth: block.querySelector("[data-child-birth]"),
      allergies: block.querySelector("[data-child-allergies]"),
      preview: block.querySelector("[data-child-photo-preview]"),
      status: block.querySelector("[data-child-photo-status]"),
    };
  }

  function readChildrenDraft() {
    const count = desiredChildrenCount();
    const drafts = [];
    for (let i = 0; i < count; i += 1) {
      const dom = childDom(i);
      drafts.push({
        full_name: dom && dom.name ? String(dom.name.value || "").trim() : "",
        birth_date: dom && dom.birth ? String(dom.birth.value || "").trim() : "",
        allergies: dom && dom.allergies ? String(dom.allergies.value || "").trim() : "",
      });
    }
    return drafts;
  }

  function renderChildrenBlocks(count, drafts) {
    if (!el.childrenWrap) return;
    const desired = clampChildrenCount(count);
    ensureChildPhotoArray(desired);
    const keep = Array.isArray(drafts) ? drafts : [];

    const statusSvg = `
      <svg class="kids-photo-status-svg kids-photo-status-svg--ok" viewBox="0 0 20 20" aria-hidden="true">
        <path d="M4 10.5l3.2 3.2L16 4.9" fill="none" stroke="currentColor" stroke-width="2.4" stroke-linecap="round" stroke-linejoin="round"></path>
      </svg>
      <svg class="kids-photo-status-svg kids-photo-status-svg--x" viewBox="0 0 20 20" aria-hidden="true">
        <path d="M5.5 5.5l9 9M14.5 5.5l-9 9" fill="none" stroke="currentColor" stroke-width="2.4" stroke-linecap="round"></path>
      </svg>
    `;

    el.childrenWrap.innerHTML = Array.from({ length: desired }).map((_, i) => {
      const draft = keep[i] || {};
      const name = escapeHtml(draft.full_name || "");
      const birth = escapeHtml(draft.birth_date || "");
      const allergies = escapeHtml(draft.allergies || "");
      return `
        <section class="panel" data-child-block data-child-idx="${i}" style="margin:0 0 0.85rem 0; padding:0.85rem;">
          <div style="display:flex; align-items:flex-start; justify-content:space-between; gap:0.6rem; flex-wrap:wrap;">
            <strong>Crianca ${i + 1}</strong>
            <span class="tiny" style="color:#5a6f86;">Sala automatica por idade</span>
          </div>
          <div class="grid-form cells-form" style="margin:0.65rem 0 0;">
            <label>Nome
              <input type="text" data-child-name value="${name}" required>
            </label>
            <label>Data de nascimento
              <input type="date" data-child-birth value="${birth}" required>
              <span class="input-hint">A sala sera escolhida automaticamente com base na idade e nas regras da igreja.</span>
            </label>
            <label>Alergias (opcional)
              <input type="text" data-child-allergies value="${allergies}" placeholder="Opcional">
            </label>
            <label>
              <span class="kids-label-head">Foto da crianca
                <span class="kids-photo-status is-missing" data-child-photo-status aria-label="Falta" title="Falta">${statusSvg}</span>
              </span>
              <div class="inline-field-group">
                <button class="btn ghost btn-inline" type="button" data-child-photo-btn data-child-idx="${i}">Abrir camera</button>
                <button class="btn ghost btn-inline" type="button" data-child-photo-clear-btn data-child-idx="${i}">Remover</button>
              </div>
              <img data-child-photo-preview alt="Foto da crianca" class="hide" style="width:92px;height:92px;object-fit:cover;border-radius:16px;border:1px solid var(--line);">
              <span class="input-hint">Obrigatorio. A foto e capturada pela camera e compactada automaticamente.</span>
            </label>
          </div>
        </section>
      `;
    }).join("");

    // Restore photo previews after re-render.
    for (let i = 0; i < desired; i += 1) {
      const dom = childDom(i);
      if (!dom) continue;
      setImgPreview(dom.preview, childPhotoBlobs[i]);
    }
  }

  function isRegisterFormReady() {
    const tenantSlug = effectiveTenantSlug(el.tenantSlug && el.tenantSlug.value);
    const responsibleName = (el.responsible && el.responsible.value || "").trim();
    const guardianName = (el.guardianName && el.guardianName.value || "").trim();
    const phonePrimary = sanitizePhoneDigits((el.phone && el.phone.value || "").trim());
    const email = (el.email && el.email.value || "").trim();

    if (!tenantSlug || !responsibleName || !guardianName || !phonePrimary || !email) return false;
    const count = desiredChildrenCount();
    if (!count) return false;
    ensureChildPhotoArray(count);
    for (let i = 0; i < count; i += 1) {
      const dom = childDom(i);
      const name = dom && dom.name ? String(dom.name.value || "").trim() : "";
      const birth = dom && dom.birth ? String(dom.birth.value || "").trim() : "";
      if (!name || !birth) return false;
      if (!pendingUploadInfo && !childPhotoBlobs[i]) return false;
    }
    // If we have a pending upload, allow the user to press submit again to retry.
    if (!pendingUploadInfo && (!responsiblePhotoBlob || !guardianPhotoBlob)) return false;
    if (submitting) return false;
    return true;
  }

  function syncRegisterUiState() {
    setPhotoStatus(el.responsiblePhotoStatus, !!responsiblePhotoBlob);
    setPhotoStatus(el.guardianPhotoStatus, !!guardianPhotoBlob);
    const count = desiredChildrenCount();
    ensureChildPhotoArray(count);
    for (let i = 0; i < count; i += 1) {
      const dom = childDom(i);
      setPhotoStatus(dom && dom.status, !!childPhotoBlobs[i]);
    }

    if (el.preRegisterSubmitBtn) {
      el.preRegisterSubmitBtn.disabled = !isRegisterFormReady();
      el.preRegisterSubmitBtn.textContent = submitting ? "Enviando..." : "Gerar cadastro e carteirinha";
    }
  }

  function syncAccountPhotoUi() {
    setPhotoStatus(el.addChildPhotoStatus, !!addChildPhotoBlob);
    // Edit photo status: show ok when either existing preview URL or new blob is present.
    const editHasPhoto = !!editChildPhotoBlob || (!!el.editChildPhotoPreview && !el.editChildPhotoPreview.classList.contains("hide"));
    setPhotoStatus(el.editChildPhotoStatus, editHasPhoto);
  }

  function clearPhoto(target, index) {
    if (target === "guardian") {
      guardianPhotoBlob = null;
      setImgPreview(el.guardianPhotoPreview, null);
      syncRegisterUiState();
      return;
    }
    if (target === "responsible") {
      responsiblePhotoBlob = null;
      setImgPreview(el.responsiblePhotoPreview, null);
      syncRegisterUiState();
      return;
    }
    const idx = Number.isFinite(Number(index)) ? Number(index) : 0;
    ensureChildPhotoArray(desiredChildrenCount());
    if (idx >= 0 && idx < childPhotoBlobs.length) childPhotoBlobs[idx] = null;
    const dom = childDom(idx);
    if (dom) setImgPreview(dom.preview, null);
    syncRegisterUiState();
  }

  function closePhotoModal() {
    pendingPhotoBlob = null;
    currentCaptureKind = "";
    currentCaptureChildIndex = 0;
    if (el.photoModal) {
      el.photoModal.classList.add("hide");
      el.photoModal.setAttribute("aria-hidden", "true");
    }
    if (el.photoCanvas) el.photoCanvas.classList.add("hide");
    if (el.photoVideo) {
      el.photoVideo.pause();
      el.photoVideo.srcObject = null;
      el.photoVideo.classList.remove("hide");
    }
    if (photoStream) {
      const tracks = photoStream.getTracks ? photoStream.getTracks() : [];
      tracks.forEach((track) => track.stop());
    }
    photoStream = null;
    if (el.photoUseBtn) el.photoUseBtn.classList.add("hide");
    if (el.photoRetakeBtn) el.photoRetakeBtn.classList.add("hide");
    if (el.photoSnapBtn) el.photoSnapBtn.classList.remove("hide");
    if (el.photoStatus) el.photoStatus.textContent = "Ajuste a camera e toque em Capturar.";
  }

  async function openPhotoModal(kind, childIndex) {
    if (!el.photoModal || !el.photoVideo) return;
    if (!("mediaDevices" in navigator) || typeof navigator.mediaDevices.getUserMedia !== "function") {
      setMessage("Este navegador nao suporta camera. Tente outro dispositivo.", true);
      return;
    }

    const normalizedKind =
      kind === "guardian" || kind === "responsible" || kind === "account_child_add" || kind === "account_child_edit"
        ? kind
        : "child";
    currentCaptureKind = normalizedKind;
    currentCaptureChildIndex = normalizedKind === "child" ? clampChildrenCount(childIndex) - 1 : 0;
    if (normalizedKind === "child") {
      const count = desiredChildrenCount();
      ensureChildPhotoArray(count);
      const idx = Number.isFinite(Number(childIndex)) ? Number(childIndex) : 0;
      currentCaptureChildIndex = Math.min(Math.max(0, idx), Math.max(0, count - 1));
    }
    pendingPhotoBlob = null;

    if (el.photoTitle) {
      el.photoTitle.textContent =
        currentCaptureKind === "guardian" ? "Foto do responsavel da retirada" :
        currentCaptureKind === "responsible" ? "Foto do responsavel principal" :
        currentCaptureKind === "account_child_add" ? "Foto da crianca (Minha conta)" :
        currentCaptureKind === "account_child_edit" ? "Nova foto da crianca" :
        "Foto da crianca";
    }
    if (el.photoStatus) el.photoStatus.textContent = "Abrindo camera...";

    el.photoModal.classList.remove("hide");
    el.photoModal.setAttribute("aria-hidden", "false");
    if (el.photoCanvas) el.photoCanvas.classList.add("hide");
    el.photoVideo.classList.remove("hide");

    photoStream = await navigator.mediaDevices.getUserMedia({
      video: { facingMode: (currentCaptureKind === "guardian" || currentCaptureKind === "responsible") ? "user" : "environment" },
      audio: false,
    });
    el.photoVideo.srcObject = photoStream;
    if (el.photoUseBtn) el.photoUseBtn.classList.add("hide");
    if (el.photoRetakeBtn) el.photoRetakeBtn.classList.add("hide");
    if (el.photoSnapBtn) el.photoSnapBtn.classList.remove("hide");
    if (el.photoStatus) el.photoStatus.textContent = "Ajuste a camera e toque em Capturar.";
  }

  function clampPositiveInt(value, fallback) {
    const v = Number(value);
    if (!Number.isFinite(v) || v <= 0) return fallback;
    return Math.round(v);
  }

  async function captureAndCompressFromVideo(videoEl, canvasEl, options) {
    const maxSide = clampPositiveInt(options && options.maxSide, 720);
    const quality = typeof (options && options.quality) === "number" ? options.quality : 0.76;
    const mime = "image/jpeg";

    const vw = clampPositiveInt(videoEl.videoWidth, 0);
    const vh = clampPositiveInt(videoEl.videoHeight, 0);
    if (!vw || !vh) throw new Error("Camera ainda nao esta pronta. Aguarde e tente novamente.");

    const scale = Math.min(1, maxSide / Math.max(vw, vh));
    const tw = Math.max(1, Math.round(vw * scale));
    const th = Math.max(1, Math.round(vh * scale));

    canvasEl.width = tw;
    canvasEl.height = th;
    const ctx = canvasEl.getContext("2d", { alpha: false });
    if (!ctx) throw new Error("Falha ao processar imagem.");
    ctx.drawImage(videoEl, 0, 0, tw, th);

    const blob = await new Promise((resolve) => {
      canvasEl.toBlob((b) => resolve(b), mime, quality);
    });
    if (!blob) throw new Error("Falha ao gerar imagem.");
    return blob;
  }

  async function snapPhoto() {
    if (!el.photoVideo || !el.photoCanvas) return;
    if (el.photoStatus) el.photoStatus.textContent = "Processando e compactando...";
    const blob = await captureAndCompressFromVideo(el.photoVideo, el.photoCanvas, { maxSide: 640, quality: 0.7 });
    pendingPhotoBlob = blob;

    el.photoCanvas.classList.remove("hide");
    el.photoVideo.classList.add("hide");
    if (el.photoSnapBtn) el.photoSnapBtn.classList.add("hide");
    if (el.photoUseBtn) el.photoUseBtn.classList.remove("hide");
    if (el.photoRetakeBtn) el.photoRetakeBtn.classList.remove("hide");
    if (el.photoStatus) el.photoStatus.textContent = `Pronto: ${(blob.size / 1024).toFixed(0)} KB (JPEG).`;
  }

  function retakePhoto() {
    pendingPhotoBlob = null;
    if (el.photoCanvas) el.photoCanvas.classList.add("hide");
    if (el.photoVideo) el.photoVideo.classList.remove("hide");
    if (el.photoUseBtn) el.photoUseBtn.classList.add("hide");
    if (el.photoRetakeBtn) el.photoRetakeBtn.classList.add("hide");
    if (el.photoSnapBtn) el.photoSnapBtn.classList.remove("hide");
    if (el.photoStatus) el.photoStatus.textContent = "Ajuste a camera e toque em Capturar.";
  }

  function usePhoto() {
    if (!pendingPhotoBlob) return;
    if (currentCaptureKind === "guardian") {
      guardianPhotoBlob = pendingPhotoBlob;
      setImgPreview(el.guardianPhotoPreview, guardianPhotoBlob);
    } else if (currentCaptureKind === "responsible") {
      responsiblePhotoBlob = pendingPhotoBlob;
      setImgPreview(el.responsiblePhotoPreview, responsiblePhotoBlob);
    } else if (currentCaptureKind === "account_child_add") {
      addChildPhotoBlob = pendingPhotoBlob;
      setImgPreview(el.addChildPhotoPreview, addChildPhotoBlob);
      syncAccountPhotoUi();
    } else if (currentCaptureKind === "account_child_edit") {
      editChildPhotoBlob = pendingPhotoBlob;
      setImgPreview(el.editChildPhotoPreview, editChildPhotoBlob);
      syncAccountPhotoUi();
    } else {
      ensureChildPhotoArray(desiredChildrenCount());
      childPhotoBlobs[currentCaptureChildIndex] = pendingPhotoBlob;
      const dom = childDom(currentCaptureChildIndex);
      if (dom) setImgPreview(dom.preview, childPhotoBlobs[currentCaptureChildIndex]);
    }
    closePhotoModal();
    syncRegisterUiState();
  }

  async function uploadPhoto(url, blob) {
    if (!blob) return null;
    const form = new FormData();
    form.append("file", blob, "photo.jpg");
    const response = await fetch(url, { method: "POST", body: form });
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

  async function uploadRequiredPhotos(info) {
    if (!info) throw new Error("Nada para enviar.");
    const tenantSlug = String(info.tenantSlug || "").trim();
    const familyCode = String(info.familyCode || "").trim();
    const childIdsRaw = Array.isArray(info.childIds) ? info.childIds : (info.childId ? [info.childId] : []);
    const childIds = childIdsRaw.map((v) => Number(v || 0)).filter((v) => Number.isFinite(v) && v > 0);
    const responsibleGuardianId = Number(info.responsibleGuardianId || 0);
    const pickupGuardianId = Number(info.pickupGuardianId || 0);

    if (!tenantSlug || !familyCode || !childIds.length || !responsibleGuardianId || !pickupGuardianId) {
      throw new Error("Falha interna: IDs ausentes para envio de fotos.");
    }
    ensureChildPhotoArray(childIds.length);
    for (let i = 0; i < childIds.length; i += 1) {
      if (!childPhotoBlobs[i]) throw new Error(`Foto da crianca ${i + 1} obrigatoria.`);
    }
    if (!responsiblePhotoBlob) throw new Error("Foto do responsavel principal obrigatoria.");
    if (!guardianPhotoBlob) throw new Error("Foto do responsavel da retirada obrigatoria.");

    for (let i = 0; i < childIds.length; i += 1) {
      await uploadPhoto(
        `/api/v1/child-checkin/public/tenants/${encodeURIComponent(tenantSlug)}/families/${encodeURIComponent(familyCode)}/children/${encodeURIComponent(String(childIds[i]))}/photo`,
        childPhotoBlobs[i],
      );
    }
    await uploadPhoto(
      `/api/v1/child-checkin/public/tenants/${encodeURIComponent(tenantSlug)}/families/${encodeURIComponent(familyCode)}/guardians/${encodeURIComponent(String(responsibleGuardianId))}/photo`,
      responsiblePhotoBlob,
    );
    await uploadPhoto(
      `/api/v1/child-checkin/public/tenants/${encodeURIComponent(tenantSlug)}/families/${encodeURIComponent(familyCode)}/guardians/${encodeURIComponent(String(pickupGuardianId))}/photo`,
      guardianPhotoBlob,
    );

    const updated = await publicApi(
      `/tenants/${encodeURIComponent(tenantSlug)}/virtual-cards?family_code=${encodeURIComponent(familyCode)}`,
    );
    renderCards(updated);
    return updated;
  }

  async function handlePreRegister(event) {
    event.preventDefault();
    try {
      submitting = true;
      syncRegisterUiState();

      // If we already created the family but photo upload failed, re-attempt the upload.
      if (pendingUploadInfo) {
        await uploadRequiredPhotos(pendingUploadInfo);
        pendingUploadInfo = null;
        setMessage("Fotos enviadas com sucesso.", false);
        for (let i = 0; i < (Array.isArray(childPhotoBlobs) ? childPhotoBlobs.length : 0); i += 1) clearPhoto("child", i);
        clearPhoto("responsible");
        clearPhoto("guardian");
        showView("register");
        return;
      }

      const tenantSlug = effectiveTenantSlug(el.tenantSlug && el.tenantSlug.value);
      const responsibleName = (el.responsible && el.responsible.value || "").trim();
      const guardianName = (el.guardianName && el.guardianName.value || "").trim();
      const guardianPhone = (el.guardianPhone && el.guardianPhone.value || "").trim();
      const email = (el.email && el.email.value || "").trim();

      if (!tenantSlug) throw new Error("Informe o slug da igreja.");
      if (!responsibleName) throw new Error("Informe o responsavel principal.");
      if (!guardianName) throw new Error("Informe o responsavel da retirada.");
      if (!email) throw new Error("Informe o e-mail.");

      const phonePrimary = sanitizePhoneDigits((el.phone && el.phone.value || "").trim());
      if (!phonePrimary) throw new Error("Informe o telefone principal.");
      const pickupPhone = sanitizePhoneDigits(guardianPhone);

      // Mandatory photos for card/wristband.
      if (!responsiblePhotoBlob) throw new Error("Tire a foto do responsavel principal.");
      if (!guardianPhotoBlob) throw new Error("Tire a foto do responsavel da retirada.");
      const count = desiredChildrenCount();
      ensureChildPhotoArray(count);
      const children = [];
      for (let i = 0; i < count; i += 1) {
        const dom = childDom(i);
        const name = dom && dom.name ? String(dom.name.value || "").trim() : "";
        const birth = dom && dom.birth ? String(dom.birth.value || "").trim() : "";
        const allergies = dom && dom.allergies ? String(dom.allergies.value || "").trim() : "";
        if (!name) throw new Error(`Informe o nome da crianca ${i + 1}.`);
        if (!birth) throw new Error(`Informe a data de nascimento da crianca ${i + 1}.`);
        if (!childPhotoBlobs[i]) throw new Error(`Tire a foto da crianca ${i + 1}.`);
        children.push({
          full_name: name,
          birth_date: birth || null,
          allergies: allergies || null,
        });
      }

      const payload = {
        family_name: guessFamilyNameFromResponsible(responsibleName),
        primary_responsible_name: responsibleName,
        phone_primary: phonePrimary,
        phone_secondary: null,
        email: email,
        notes: null,
        public_pin: (el.pin && el.pin.value || "").trim() || null,
        children: children,
        guardians: [
          {
            full_name: responsibleName,
            relationship: "Responsavel principal",
            phone: phonePrimary || null,
            is_authorized: true,
          },
          {
            full_name: guardianName,
            relationship: "Retirada",
            phone: pickupPhone || null,
            is_authorized: true,
          },
        ],
      };

      const response = await publicApi(`/tenants/${encodeURIComponent(tenantSlug)}/pre-register`, {
        method: "POST",
        body: JSON.stringify(payload),
      });

      // Upload required photos after we have the family_code and IDs.
      const familyCode = String(response && response.family_code || "").trim();
      const cards = response && Array.isArray(response.cards) ? response.cards : [];
      const firstCard = cards[0] || null;
      const cardGuardians = firstCard && Array.isArray(firstCard.guardians) ? firstCard.guardians : [];
      const findGuardianId = function (fullName) {
        const needle = String(fullName || "").trim().toLowerCase();
        if (!needle) return 0;
        const hit = cardGuardians.find((g) => g && String(g.full_name || "").trim().toLowerCase() === needle);
        return hit && hit.guardian_id ? Number(hit.guardian_id) : 0;
      };
      const responsibleGuardianId = findGuardianId(responsibleName);
      const pickupGuardianId = findGuardianId(guardianName);

      const usedCardIdx = new Set();
      const normalizeName = (value) => String(value || "").trim().toLowerCase();
      const childIds = children.map((c) => {
        const desiredName = normalizeName(c.full_name);
        let foundIdx = -1;
        for (let i = 0; i < cards.length; i += 1) {
          if (usedCardIdx.has(i)) continue;
          if (normalizeName(cards[i] && cards[i].child_name) === desiredName) {
            foundIdx = i;
            break;
          }
        }
        if (foundIdx < 0) {
          for (let i = 0; i < cards.length; i += 1) {
            if (usedCardIdx.has(i)) continue;
            foundIdx = i;
            break;
          }
        }
        if (foundIdx >= 0) usedCardIdx.add(foundIdx);
        const id = foundIdx >= 0 && cards[foundIdx] && cards[foundIdx].child_id ? Number(cards[foundIdx].child_id) : 0;
        return id;
      });

      if (childIds.some((id) => !Number.isFinite(Number(id)) || Number(id) <= 0)) {
        throw new Error("Falha interna: nao foi possivel identificar as criancas cadastradas para envio das fotos.");
      }

      pendingUploadInfo = {
        tenantSlug,
        familyCode,
        childIds,
        responsibleGuardianId,
        pickupGuardianId,
      };

      await uploadRequiredPhotos(pendingUploadInfo);
      pendingUploadInfo = null;

      const emailHint =
        response && response.email_sent
          ? " Enviamos a carteirinha (e os QR Codes) no seu e-mail."
          : response && response.email_error
            ? " Nao foi possivel enviar o e-mail agora (a igreja pode estar sem SMTP configurado)."
            : "";
      setMessage(`Cadastro concluido. Codigo da familia: ${response.family_code}.${emailHint}`, false);

      // If the family created a PIN, the backend returns a token: auto-enter "Minha conta".
      if (response && response.token) {
        setAuthToken(response.token);
        await loadMe(tenantSlug);
      }

      if (el.preRegisterForm) el.preRegisterForm.reset();
      // Keep tenant slug filled even after reset (usually comes from ?tenant=...).
      if (el.tenantSlug) el.tenantSlug.value = tenantSlug;
      // Reset children UI to 1 child after submit.
      if (el.childrenCount) el.childrenCount.value = "1";
      childPhotoBlobs = [];
      ensureChildPhotoArray(1);
      renderChildrenBlocks(1, []);
      for (let i = 0; i < desiredChildrenCount(); i += 1) clearPhoto("child", i);
      clearPhoto("responsible");
      clearPhoto("guardian");
      showView("register");
    } catch (error) {
      const msg = error instanceof Error ? error.message : "Falha no cadastro publico.";
      // If we already created the family but failed sending photos, keep pendingUploadInfo
      // and let the user press "Gerar cadastro..." again to retry the upload.
      if (pendingUploadInfo) setMessage(`${msg} Toque em "Gerar cadastro e carteirinha" novamente para tentar enviar as fotos.`, true);
      else setMessage(msg, true);
    } finally {
      submitting = false;
      syncRegisterUiState();
    }
  }

  function authToken() {
    return String(localStorage.getItem("kidsPublicToken") || "").trim();
  }

  function setAuthToken(token) {
    const normalized = String(token || "").trim();
    if (!normalized) localStorage.removeItem("kidsPublicToken");
    else localStorage.setItem("kidsPublicToken", normalized);
  }

  function authHeaders() {
    const token = authToken();
    return token ? { Authorization: `Bearer ${token}` } : {};
  }

  function showAccountPanel(show) {
    if (!el.accountPanel) return;
    el.accountPanel.classList.toggle("hide", !show);
  }

  function setLoggedInUi(isLoggedIn) {
    const loggedIn = Boolean(isLoggedIn);
    if (el.loginForm) el.loginForm.classList.toggle("hide", loggedIn);
    if (el.loginHint) el.loginHint.classList.toggle("hide", loggedIn);
    if (el.forgotToggleBtn) el.forgotToggleBtn.classList.toggle("hide", loggedIn);
    if (loggedIn && el.forgotWrap) el.forgotWrap.classList.add("hide");
    if (el.loginTitle) el.loginTitle.textContent = loggedIn ? "Minha conta" : "Entrar";
  }

  function renderAccount(me) {
    if (el.accountFamilyCode) {
      el.accountFamilyCode.textContent = me && me.family && me.family.family_code ? String(me.family.family_code) : "-";
    }
    if (!el.accountLists) return;
    const children = Array.isArray(me && me.children) ? me.children : [];
    const guardians = Array.isArray(me && me.guardians) ? me.guardians : [];
    const childLines = children.length
      ? children
          .map((c) => {
            const childId = c && c.id ? Number(c.id) : 0;
            const room = escapeHtml(c && c.room_name ? c.room_name : "sem sala");
            const photoFlag = c && c.photo_url ? "com foto" : "sem foto";
            return `<div style="display:flex; gap:0.6rem; align-items:center; justify-content:space-between; flex-wrap:wrap;">
              <div>- ${escapeHtml(c && c.full_name ? c.full_name : "-")} (${room}) <span class="tiny">(${photoFlag})</span></div>
              ${childId ? `<button class="btn ghost btn-mini" type="button" data-edit-child-id="${childId}">Editar</button>` : ""}
            </div>`;
          })
          .join("")
      : "<div>-</div>";
    const guardianLines = guardians.length
      ? guardians.map((g) => `- ${escapeHtml(g.full_name || "-")} ${g.is_authorized ? "(autorizado)" : "(nao autorizado)"}`).join("<br>")
      : "-";
    el.accountLists.innerHTML = `<div><strong>Criancas</strong><div style="margin-top:0.35rem; display:grid; gap:0.35rem;">${childLines}</div></div><div style="margin-top:0.8rem;"><strong>Responsaveis</strong><br>${guardianLines}</div>`;
  }

  async function loadMe(tenantSlug) {
    const response = await publicApi("/me", { method: "GET", headers: authHeaders() });
    lastMe = response;
    accountTenantSlug = effectiveTenantSlug(tenantSlug);
    renderAccount(response);
    showAccountPanel(true);
    // Refresh the cards area using the family code.
    const familyCode = response && response.family && response.family.family_code ? String(response.family.family_code) : "";
    accountFamilyCode = familyCode;
    if (familyCode) {
      const cards = await publicApi(`/tenants/${encodeURIComponent(tenantSlug)}/virtual-cards?family_code=${encodeURIComponent(familyCode)}`);
      renderCards(cards);
    }
    syncAccountPhotoUi();
  }

  async function handleLogin(event) {
    event.preventDefault();
    try {
      const tenantSlug = effectiveTenantSlug(el.loginTenantSlug && el.loginTenantSlug.value);
      const email = (el.loginEmail && el.loginEmail.value || "").trim();
      const pin = (el.loginPin && el.loginPin.value || "").trim();
      if (!tenantSlug) throw new Error("Informe o slug da igreja.");
      if (!email) throw new Error("Informe o e-mail.");
      if (!pin) throw new Error("Informe o PIN.");
      const response = await publicApi(`/tenants/${encodeURIComponent(tenantSlug)}/login`, {
        method: "POST",
        body: JSON.stringify({ email, pin }),
      });
      setAuthToken(response && response.token);
      await loadMe(tenantSlug);
      showView("login");
      setLoggedInUi(true);
      if (el.forgotWrap) el.forgotWrap.classList.add("hide");
      setMessage("Acesso liberado. Voce pode reaproveitar seu cadastro.", false);
    } catch (error) {
      setAuthToken("");
      showAccountPanel(false);
      setLoggedInUi(false);
      setMessage(error instanceof Error ? error.message : "Falha ao entrar.", true);
    }
  }

  function toggleForgot() {
    if (!el.forgotWrap) return;
    const willShow = el.forgotWrap.classList.contains("hide");
    el.forgotWrap.classList.toggle("hide", !willShow);
    if (willShow) {
      const current = (el.loginEmail && el.loginEmail.value || "").trim();
      if (current && el.recoverEmail) el.recoverEmail.value = current;
      resetRecoverSteps({ keepEmail: true });
      window.scrollTo({ top: document.body.scrollHeight, behavior: "smooth" });
    }
  }

  function resetRecoverSteps(options) {
    const keepEmail = Boolean(options && options.keepEmail);
    if (el.recoverStep2) el.recoverStep2.classList.add("hide");
    if (el.recoverStep3) el.recoverStep3.classList.add("hide");
    if (!keepEmail && el.recoverEmail) el.recoverEmail.value = "";
    if (el.recoverCode) el.recoverCode.value = "";
    if (el.recoverNewPin) el.recoverNewPin.value = "";
    if (el.recoverRequestBtn) el.recoverRequestBtn.disabled = false;
    if (el.recoverVerifyBtn) el.recoverVerifyBtn.disabled = false;
    if (el.recoverConfirmBtn) el.recoverConfirmBtn.disabled = false;
  }

  async function handleRecoverRequest() {
    try {
      const tenantSlug = effectiveTenantSlug((el.loginTenantSlug && el.loginTenantSlug.value) || (el.tenantSlug && el.tenantSlug.value));
      if (!tenantSlug) throw new Error("Slug da igreja ausente.");
      const email = (el.recoverEmail && el.recoverEmail.value || (el.loginEmail && el.loginEmail.value) || "").trim();
      if (!email) throw new Error("Informe o e-mail.");
      if (el.recoverEmail) el.recoverEmail.value = email;
      if (el.recoverRequestBtn) el.recoverRequestBtn.disabled = true;

      await publicApi(`/tenants/${encodeURIComponent(tenantSlug)}/recover/request`, {
        method: "POST",
        body: JSON.stringify({ email }),
      });

      // Do not leak whether an account exists.
      setMessage("Se existir cadastro para este e-mail, enviamos um codigo. Confira sua caixa de entrada e spam.", false);
      if (el.recoverStep2) el.recoverStep2.classList.remove("hide");
      if (el.recoverCode) el.recoverCode.focus();
    } catch (error) {
      setMessage(error instanceof Error ? error.message : "Falha ao solicitar recuperacao.", true);
    } finally {
      if (el.recoverRequestBtn) el.recoverRequestBtn.disabled = false;
    }
  }

  async function handleRecoverVerify() {
    try {
      const tenantSlug = effectiveTenantSlug((el.loginTenantSlug && el.loginTenantSlug.value) || (el.tenantSlug && el.tenantSlug.value));
      if (!tenantSlug) throw new Error("Slug da igreja ausente.");
      const email = (el.recoverEmail && el.recoverEmail.value || (el.loginEmail && el.loginEmail.value) || "").trim();
      const code = (el.recoverCode && el.recoverCode.value || "").trim();
      if (!email) throw new Error("Informe o e-mail.");
      if (!code) throw new Error("Informe o codigo.");
      if (el.recoverVerifyBtn) el.recoverVerifyBtn.disabled = true;

      await publicApi(`/tenants/${encodeURIComponent(tenantSlug)}/recover/verify`, {
        method: "POST",
        body: JSON.stringify({ email, code }),
      });

      if (el.recoverStep3) el.recoverStep3.classList.remove("hide");
      if (el.recoverNewPin) el.recoverNewPin.focus();
      setMessage("Codigo validado. Agora crie um novo PIN.", false);
    } catch (error) {
      setMessage(error instanceof Error ? error.message : "Falha ao validar codigo.", true);
    } finally {
      if (el.recoverVerifyBtn) el.recoverVerifyBtn.disabled = false;
    }
  }

  async function handleRecoverConfirm() {
    try {
      const tenantSlug = effectiveTenantSlug((el.loginTenantSlug && el.loginTenantSlug.value) || (el.tenantSlug && el.tenantSlug.value));
      if (!tenantSlug) throw new Error("Slug da igreja ausente.");
      const email = (el.recoverEmail && el.recoverEmail.value || (el.loginEmail && el.loginEmail.value) || "").trim();
      const code = (el.recoverCode && el.recoverCode.value || "").trim();
      const newPin = (el.recoverNewPin && el.recoverNewPin.value || "").trim();
      if (!email) throw new Error("Informe o e-mail.");
      if (!code) throw new Error("Informe o codigo.");
      if (!newPin) throw new Error("Informe o novo PIN.");
      if (el.recoverConfirmBtn) el.recoverConfirmBtn.disabled = true;

      const response = await publicApi(`/tenants/${encodeURIComponent(tenantSlug)}/recover/confirm`, {
        method: "POST",
        body: JSON.stringify({ email, code, new_pin: newPin }),
      });
      setAuthToken(response && response.token);
      if (el.forgotWrap) el.forgotWrap.classList.add("hide");
      resetRecoverSteps({ keepEmail: false });
      await loadMe(tenantSlug);
      showView("login");
      setLoggedInUi(true);
      setMessage("PIN atualizado. Voce ja esta logado.", false);
    } catch (error) {
      setMessage(error instanceof Error ? error.message : "Falha ao confirmar recuperacao.", true);
    } finally {
      if (el.recoverConfirmBtn) el.recoverConfirmBtn.disabled = false;
    }
  }

  async function handleLogout() {
    setAuthToken("");
    showAccountPanel(false);
    setLoggedInUi(false);
    if (el.accountLists) el.accountLists.innerHTML = "";
    if (el.accountFamilyCode) el.accountFamilyCode.textContent = "-";
    if (el.loginCardsResult) el.loginCardsResult.innerHTML = "";
    if (el.registerCardsResult) el.registerCardsResult.innerHTML = "";
    if (el.forgotWrap) el.forgotWrap.classList.add("hide");
    resetRecoverSteps({ keepEmail: false });
    lastMe = null;
    accountTenantSlug = "";
    accountFamilyCode = "";
    addChildPhotoBlob = null;
    editChildPhotoBlob = null;
    editingChildId = 0;
    closeEditChildModal();
    setImgPreview(el.addChildPhotoPreview, null);
    syncAccountPhotoUi();
    showView("start");
    setMessage("Sessao encerrada.", false);
  }

  async function handleAddChild(event) {
    event.preventDefault();
    try {
      const token = authToken();
      if (!token) throw new Error("Faca login antes.");
      const name = (el.addChildName && el.addChildName.value || "").trim();
      const birth = (el.addChildBirthDate && el.addChildBirthDate.value || "").trim();
      const allergies = (el.addChildAllergies && el.addChildAllergies.value || "").trim();
      if (!name) throw new Error("Informe o nome.");
      if (!birth) throw new Error("Informe a data de nascimento.");
      if (!addChildPhotoBlob) throw new Error("Tire a foto da crianca.");

      // Best-effort: infer slug from the login/register inputs.
      const ctx = accountCtxOrThrow();

      const created = await publicApi("/me/children", {
        method: "POST",
        headers: Object.assign({ "Content-Type": "application/json" }, authHeaders()),
        body: JSON.stringify({
          full_name: name,
          birth_date: birth,
          allergies: allergies || null,
        }),
      });
      if (!created || !created.id) throw new Error("Falha ao criar crianca.");

      await uploadPhoto(
        `/api/v1/child-checkin/public/tenants/${encodeURIComponent(ctx.tenantSlug)}/families/${encodeURIComponent(ctx.familyCode)}/children/${encodeURIComponent(String(created.id))}/photo`,
        addChildPhotoBlob,
      );
      addChildPhotoBlob = null;
      setImgPreview(el.addChildPhotoPreview, null);
      syncAccountPhotoUi();
      if (el.addChildForm) el.addChildForm.reset();
      await loadMe(ctx.tenantSlug);
      setMessage("Crianca adicionada com sucesso.", false);
    } catch (error) {
      setMessage(error instanceof Error ? error.message : "Falha ao adicionar crianca.", true);
    }
  }

  async function handleAddGuardian(event) {
    event.preventDefault();
    try {
      const token = authToken();
      if (!token) throw new Error("Faca login antes.");
      const name = (el.addGuardianName && el.addGuardianName.value || "").trim();
      const phone = sanitizePhoneDigits((el.addGuardianPhone && el.addGuardianPhone.value || "").trim());
      const authorized = Boolean(el.addGuardianAuthorized && el.addGuardianAuthorized.checked);
      if (!name) throw new Error("Informe o nome.");

      const tenantSlug = effectiveTenantSlug((el.loginTenantSlug && el.loginTenantSlug.value) || (el.tenantSlug && el.tenantSlug.value));
      if (!tenantSlug) throw new Error("Slug da igreja ausente.");

      await publicApi("/me/guardians", {
        method: "POST",
        headers: Object.assign({ "Content-Type": "application/json" }, authHeaders()),
        body: JSON.stringify({
          full_name: name,
          relationship: "Responsavel",
          phone: phone || null,
          is_authorized: authorized,
        }),
      });
      if (el.addGuardianForm) el.addGuardianForm.reset();
      await loadMe(tenantSlug);
      setMessage("Responsavel adicionado com sucesso.", false);
    } catch (error) {
      setMessage(error instanceof Error ? error.message : "Falha ao adicionar responsavel.", true);
    }
  }

  function openEditChildModal(childId) {
    const id = Number(childId || 0);
    if (!id || !el.editChildModal || !lastMe) return;
    const children = Array.isArray(lastMe.children) ? lastMe.children : [];
    const child = children.find((c) => c && Number(c.id) === id);
    if (!child) return;
    editingChildId = id;
    editChildPhotoBlob = null;
    if (el.editChildMessage) el.editChildMessage.textContent = "";
    if (el.editChildName) el.editChildName.value = String(child.full_name || "");
    if (el.editChildBirthDate) el.editChildBirthDate.value = child.birth_date ? String(child.birth_date).slice(0, 10) : "";
    if (el.editChildAllergies) el.editChildAllergies.value = String(child.allergies || "");

    // Show current photo (if any). If user captures a new one, it will replace.
    if (el.editChildPhotoPreview) {
      const src = child.photo_url ? String(child.photo_url) : "";
      if (src) {
        el.editChildPhotoPreview.src = src;
        el.editChildPhotoPreview.classList.remove("hide");
      } else {
        el.editChildPhotoPreview.src = "";
        el.editChildPhotoPreview.classList.add("hide");
      }
    }
    syncAccountPhotoUi();
    el.editChildModal.classList.remove("hide");
    el.editChildModal.setAttribute("aria-hidden", "false");
  }

  function closeEditChildModal() {
    editingChildId = 0;
    editChildPhotoBlob = null;
    if (el.editChildModal) {
      el.editChildModal.classList.add("hide");
      el.editChildModal.setAttribute("aria-hidden", "true");
    }
    if (el.editChildForm) el.editChildForm.reset();
    if (el.editChildPhotoPreview) {
      el.editChildPhotoPreview.src = "";
      el.editChildPhotoPreview.classList.add("hide");
    }
    syncAccountPhotoUi();
  }

  async function handleEditChildSave(event) {
    event.preventDefault();
    try {
      const token = authToken();
      if (!token) throw new Error("Faca login antes.");
      const childId = Number(editingChildId || 0);
      if (!childId) throw new Error("Crianca nao selecionada.");
      const name = (el.editChildName && el.editChildName.value || "").trim();
      const birth = (el.editChildBirthDate && el.editChildBirthDate.value || "").trim();
      const allergies = (el.editChildAllergies && el.editChildAllergies.value || "").trim();
      if (!name) throw new Error("Informe o nome.");
      if (!birth) throw new Error("Informe a data de nascimento.");
      const ctx = accountCtxOrThrow();
      if (el.editChildSaveBtn) el.editChildSaveBtn.disabled = true;

      await publicApi(`/me/children/${encodeURIComponent(String(childId))}`, {
        method: "PATCH",
        headers: Object.assign({ "Content-Type": "application/json" }, authHeaders()),
        body: JSON.stringify({
          full_name: name,
          birth_date: birth,
          allergies: allergies || null,
        }),
      });

      if (editChildPhotoBlob) {
        await uploadPhoto(
          `/api/v1/child-checkin/public/tenants/${encodeURIComponent(ctx.tenantSlug)}/families/${encodeURIComponent(ctx.familyCode)}/children/${encodeURIComponent(String(childId))}/photo`,
          editChildPhotoBlob,
        );
      }

      await loadMe(ctx.tenantSlug);
      closeEditChildModal();
      setMessage("Crianca atualizada com sucesso.", false);
    } catch (error) {
      const msg = error instanceof Error ? error.message : "Falha ao salvar crianca.";
      if (el.editChildMessage) {
        el.editChildMessage.textContent = msg;
        el.editChildMessage.style.color = "#b42318";
      }
      setMessage(msg, true);
    } finally {
      if (el.editChildSaveBtn) el.editChildSaveBtn.disabled = false;
    }
  }

  function prefillSlugFromQuery() {
    const params = new URLSearchParams(window.location.search);
    const slugFromQuery = String(params.get("tenant") || "").trim();
    const slugFromStorage = String(localStorage.getItem("activeTenantSlug") || "").trim();
    const slug = effectiveTenantSlug(slugFromQuery || slugFromStorage);
    if (!slug) return;
    if (el.tenantSlug) el.tenantSlug.value = slug;
    if (el.loginTenantSlug) el.loginTenantSlug.value = slug;

    // Hide slug inputs when we already know the church.
    if (el.tenantSlugLabel) el.tenantSlugLabel.classList.add("hide");
    if (el.loginTenantSlugLabel) el.loginTenantSlugLabel.classList.add("hide");
  }

  if (el.preRegisterForm) el.preRegisterForm.addEventListener("submit", handlePreRegister);
  if (el.loginForm) el.loginForm.addEventListener("submit", handleLogin);
  if (el.logoutBtn) el.logoutBtn.addEventListener("click", handleLogout);
  if (el.addChildForm) el.addChildForm.addEventListener("submit", handleAddChild);
  if (el.addGuardianForm) el.addGuardianForm.addEventListener("submit", handleAddGuardian);
  if (el.forgotToggleBtn) el.forgotToggleBtn.addEventListener("click", toggleForgot);
  if (el.recoverRequestBtn) el.recoverRequestBtn.addEventListener("click", handleRecoverRequest);
  if (el.recoverVerifyBtn) el.recoverVerifyBtn.addEventListener("click", handleRecoverVerify);
  if (el.recoverConfirmBtn) el.recoverConfirmBtn.addEventListener("click", handleRecoverConfirm);
  prefillSlugFromQuery();

  // Start screen navigation
  if (el.startRegisterBtn) el.startRegisterBtn.addEventListener("click", function () { showView("register"); });
  if (el.startLoginBtn) el.startLoginBtn.addEventListener("click", function () {
    showView("login");
    setLoggedInUi(Boolean(authToken()));
  });
  if (el.backFromRegisterBtn) el.backFromRegisterBtn.addEventListener("click", function () { showView("start"); });
  if (el.backFromLoginBtn) el.backFromLoginBtn.addEventListener("click", function () {
    showView("start");
    setLoggedInUi(false);
  });

  // Default view
  showView("start");

  // If we already have a token, try to resume "Minha conta".
  if (authToken()) {
    const tenantSlug = effectiveTenantSlug((el.loginTenantSlug && el.loginTenantSlug.value) || (el.tenantSlug && el.tenantSlug.value));
    if (tenantSlug) {
      loadMe(tenantSlug)
        .then(() => {
          showView("login");
          setLoggedInUi(true);
          setMessage("", false);
        })
        .catch(() => {
          setAuthToken("");
          showAccountPanel(false);
          setLoggedInUi(false);
          showView("start");
        });
    }
  }

  // Children blocks (dynamic: 1..5)
  if (el.childrenCount) {
    ensureChildPhotoArray(desiredChildrenCount());
    renderChildrenBlocks(desiredChildrenCount(), []);
    el.childrenCount.addEventListener("change", function () {
      if (pendingUploadInfo) {
        const locked = pendingUploadInfo && Array.isArray(pendingUploadInfo.childIds) && pendingUploadInfo.childIds.length
          ? pendingUploadInfo.childIds.length
          : (Array.isArray(childPhotoBlobs) && childPhotoBlobs.length ? childPhotoBlobs.length : 1);
        el.childrenCount.value = String(clampChildrenCount(locked));
        setMessage("Finalize o envio das fotos antes de alterar a quantidade de criancas.", true);
        return;
      }
      const drafts = readChildrenDraft();
      renderChildrenBlocks(desiredChildrenCount(), drafts);
      syncRegisterUiState();
    });
  }
  if (el.childrenWrap) {
    el.childrenWrap.addEventListener("input", syncRegisterUiState);
    el.childrenWrap.addEventListener("change", syncRegisterUiState);
    el.childrenWrap.addEventListener("click", function (event) {
      const btnPhoto = event.target && event.target.closest ? event.target.closest("[data-child-photo-btn]") : null;
      if (btnPhoto) {
        const idx = Number(btnPhoto.getAttribute("data-child-idx") || 0);
        openPhotoModal("child", idx).catch((error) => {
          setMessage(error instanceof Error ? error.message : "Falha ao abrir camera.", true);
        });
        return;
      }
      const btnClear = event.target && event.target.closest ? event.target.closest("[data-child-photo-clear-btn]") : null;
      if (btnClear) {
        const idx = Number(btnClear.getAttribute("data-child-idx") || 0);
        clearPhoto("child", idx);
      }
    });
  }
  // Add-child photo capture (Minha conta)
  if (el.addChildPhotoBtn) {
    el.addChildPhotoBtn.addEventListener("click", function () {
      openPhotoModal("account_child_add", 0).catch((error) => {
        setMessage(error instanceof Error ? error.message : "Falha ao abrir camera.", true);
      });
    });
  }
  if (el.addChildPhotoClearBtn) {
    el.addChildPhotoClearBtn.addEventListener("click", function () {
      addChildPhotoBlob = null;
      setImgPreview(el.addChildPhotoPreview, null);
      syncAccountPhotoUi();
    });
  }

  // Edit child modal
  if (el.accountLists) {
    el.accountLists.addEventListener("click", function (event) {
      const btn = event.target && event.target.closest ? event.target.closest("[data-edit-child-id]") : null;
      if (!btn) return;
      const id = Number(btn.getAttribute("data-edit-child-id") || 0);
      if (id) openEditChildModal(id);
    });
  }
  if (el.editChildCloseBtn) el.editChildCloseBtn.addEventListener("click", closeEditChildModal);
  if (el.editChildCancelBtn) el.editChildCancelBtn.addEventListener("click", closeEditChildModal);
  if (el.editChildForm) el.editChildForm.addEventListener("submit", handleEditChildSave);
  if (el.editChildPhotoBtn) {
    el.editChildPhotoBtn.addEventListener("click", function () {
      openPhotoModal("account_child_edit", 0).catch((error) => {
        setMessage(error instanceof Error ? error.message : "Falha ao abrir camera.", true);
      });
    });
  }
  if (el.editChildPhotoClearBtn) {
    el.editChildPhotoClearBtn.addEventListener("click", function () {
      editChildPhotoBlob = null;
      if (el.editChildPhotoPreview) {
        el.editChildPhotoPreview.src = "";
        el.editChildPhotoPreview.classList.add("hide");
      }
      syncAccountPhotoUi();
    });
  }
  if (el.guardianPhotoBtn) {
    el.guardianPhotoBtn.addEventListener("click", function () {
      openPhotoModal("guardian").catch((error) => {
        setMessage(error instanceof Error ? error.message : "Falha ao abrir camera.", true);
      });
    });
  }
  if (el.responsiblePhotoBtn) {
    el.responsiblePhotoBtn.addEventListener("click", function () {
      openPhotoModal("responsible").catch((error) => {
        setMessage(error instanceof Error ? error.message : "Falha ao abrir camera.", true);
      });
    });
  }
  if (el.guardianPhotoClearBtn) {
    el.guardianPhotoClearBtn.addEventListener("click", function () {
      clearPhoto("guardian");
    });
  }
  if (el.responsiblePhotoClearBtn) {
    el.responsiblePhotoClearBtn.addEventListener("click", function () {
      clearPhoto("responsible");
    });
  }

  // Brazilian phone mask
  bindPhoneMask(el.phone);
  bindPhoneMask(el.guardianPhone);
  bindPhoneMask(el.addGuardianPhone);

  // Keep submit disabled/enabled in sync with inputs.
  const registerInputs = [el.tenantSlug, el.responsible, el.phone, el.email, el.pin, el.childrenCount, el.guardianName, el.guardianPhone];
  registerInputs.forEach((input) => {
    if (!input) return;
    input.addEventListener("input", syncRegisterUiState);
    input.addEventListener("change", syncRegisterUiState);
  });
  syncRegisterUiState();

  if (el.photoCloseBtn) el.photoCloseBtn.addEventListener("click", closePhotoModal);
  if (el.photoSnapBtn) {
    el.photoSnapBtn.addEventListener("click", function () {
      snapPhoto().catch((error) => {
        setMessage(error instanceof Error ? error.message : "Falha ao capturar foto.", true);
      });
    });
  }
  if (el.photoRetakeBtn) el.photoRetakeBtn.addEventListener("click", retakePhoto);
  if (el.photoUseBtn) el.photoUseBtn.addEventListener("click", usePhoto);
})();
