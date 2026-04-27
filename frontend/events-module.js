(function () {
  const apiPrefix = "/api/v1";
  const eventsEndpoint = `${apiPrefix}/events`;
  const paymentAccountsEndpoint = `${apiPrefix}/payment-accounts/`;
  const permissionStorageKey = "currentUserPermissions";
  const isAdminStorageKey = "currentUserIsAdmin";

  const VIEW_PERMISSIONS = {
    agenda: "events_events_view",
    registrations: "events_registrations_view",
    payments: "events_payments_view",
    analytics: "events_analytics_view",
    notifications: "events_notifications_view",
  };

  let eventsBound = false;

  const el = {
    kidsBtn: document.getElementById("moduleKidsBtn"),
    kidsModule: document.getElementById("kidsModule"),
    eventsBtn: document.getElementById("moduleEventsBtn"),
    eventsModule: document.getElementById("eventsModule"),
    eventsMessage: document.getElementById("eventsMessage"),
    eventsNavEventsBtn: document.getElementById("eventsNavEventsBtn"),
    eventsNavRegistrationsBtn: document.getElementById("eventsNavRegistrationsBtn"),
    eventsNavPaymentsBtn: document.getElementById("eventsNavPaymentsBtn"),
    eventsNavAnalyticsBtn: document.getElementById("eventsNavAnalyticsBtn"),
    eventsNavNotificationsBtn: document.getElementById("eventsNavNotificationsBtn"),
    eventsNavCheckinBtn: document.getElementById("eventsNavCheckinBtn"),
    eventsAgendaView: document.getElementById("eventsAgendaView"),
    eventsRegistrationsView: document.getElementById("eventsRegistrationsView"),
    eventsPaymentsView: document.getElementById("eventsPaymentsView"),
    eventsAnalyticsView: document.getElementById("eventsAnalyticsView"),
    eventsNotificationsView: document.getElementById("eventsNotificationsView"),
    eventsCheckinView: document.getElementById("eventsCheckinView"),
    eventsRefreshBtn: document.getElementById("eventsRefreshBtn"),
    eventsSearchInput: document.getElementById("eventsSearchInput"),
    eventsStatusFilter: document.getElementById("eventsStatusFilter"),
    eventsVisibilityFilter: document.getElementById("eventsVisibilityFilter"),
    eventsResultCount: document.getElementById("eventsResultCount"),
    eventsClearFiltersBtn: document.getElementById("eventsClearFiltersBtn"),
    eventsTotalCount: document.getElementById("eventsTotalCount"),
    eventsPublishedCount: document.getElementById("eventsPublishedCount"),
    eventsPublicCount: document.getElementById("eventsPublicCount"),
    eventsPaidCount: document.getElementById("eventsPaidCount"),
    eventsCalendarPrevBtn: document.getElementById("eventsCalendarPrevBtn"),
    eventsCalendarNextBtn: document.getElementById("eventsCalendarNextBtn"),
    eventsCalendarMonthLabel: document.getElementById("eventsCalendarMonthLabel"),
    eventsCalendarGrid: document.getElementById("eventsCalendarGrid"),
    eventsForm: document.getElementById("eventsForm"),
    eventsFormTitle: document.getElementById("eventsFormTitle"),
    openEventsFormModalBtn: document.getElementById("openEventsFormModalBtn"),
    eventsFormId: document.getElementById("eventsFormId"),
    eventsTitle: document.getElementById("eventsTitle"),
    eventsSlug: document.getElementById("eventsSlug"),
    eventsSummary: document.getElementById("eventsSummary"),
    eventsDescription: document.getElementById("eventsDescription"),
    eventsLocation: document.getElementById("eventsLocation"),
    eventsPaymentAccountId: document.getElementById("eventsPaymentAccountId"),
    eventsStartAt: document.getElementById("eventsStartAt"),
    eventsEndAt: document.getElementById("eventsEndAt"),
    eventsRegistrationOpensAt: document.getElementById("eventsRegistrationOpensAt"),
    eventsRegistrationClosesAt: document.getElementById("eventsRegistrationClosesAt"),
    eventsVisibility: document.getElementById("eventsVisibility"),
    eventsStatus: document.getElementById("eventsStatus"),
    eventsCapacity: document.getElementById("eventsCapacity"),
    eventsMaxRegistrationsPerOrder: document.getElementById("eventsMaxRegistrationsPerOrder"),
    eventsPricePerRegistration: document.getElementById("eventsPricePerRegistration"),
    eventsCurrency: document.getElementById("eventsCurrency"),
    eventsAllowPublicRegistration: document.getElementById("eventsAllowPublicRegistration"),
    eventsRequirePayment: document.getElementById("eventsRequirePayment"),
    eventsIsActive: document.getElementById("eventsIsActive"),
    eventsFormResetBtn: document.getElementById("eventsFormResetBtn"),
    eventsDeleteBtn: document.getElementById("eventsDeleteBtn"),
    eventsCards: document.getElementById("eventsCards"),
    eventsSelectedBadge: document.getElementById("eventsSelectedBadge"),
    eventsRegistrationsRefreshBtn: document.getElementById("eventsRegistrationsRefreshBtn"),
    eventsRegistrationsHint: document.getElementById("eventsRegistrationsHint"),
    eventsRegistrationsEventFilter: document.getElementById("eventsRegistrationsEventFilter"),
    eventsRegistrationsSearchInput: document.getElementById("eventsRegistrationsSearchInput"),
    eventsRegistrationsStatusFilter: document.getElementById("eventsRegistrationsStatusFilter"),
    eventsRegistrationsPaymentFilter: document.getElementById("eventsRegistrationsPaymentFilter"),
    eventsRegistrationsResultCount: document.getElementById("eventsRegistrationsResultCount"),
    eventsRegistrationsBody: document.getElementById("eventsRegistrationsBody"),
    eventsRegistrationsPageSize: document.getElementById("eventsRegistrationsPageSize"),
    eventsRegistrationsPrevBtn: document.getElementById("eventsRegistrationsPrevBtn"),
    eventsRegistrationsPageInfo: document.getElementById("eventsRegistrationsPageInfo"),
    eventsRegistrationsNextBtn: document.getElementById("eventsRegistrationsNextBtn"),
    eventsPaymentsRefreshBtn: document.getElementById("eventsPaymentsRefreshBtn"),
    eventsPaymentsHint: document.getElementById("eventsPaymentsHint"),
    eventsPaymentsEventFilter: document.getElementById("eventsPaymentsEventFilter"),
    eventsPaymentsSearchInput: document.getElementById("eventsPaymentsSearchInput"),
    eventsPaymentsStatusFilter: document.getElementById("eventsPaymentsStatusFilter"),
    eventsPaymentsMethodFilter: document.getElementById("eventsPaymentsMethodFilter"),
    eventsPaymentsResultCount: document.getElementById("eventsPaymentsResultCount"),
    eventsPaymentsBody: document.getElementById("eventsPaymentsBody"),
    eventsPaymentsPageSize: document.getElementById("eventsPaymentsPageSize"),
    eventsPaymentsPrevBtn: document.getElementById("eventsPaymentsPrevBtn"),
    eventsPaymentsPageInfo: document.getElementById("eventsPaymentsPageInfo"),
    eventsPaymentsNextBtn: document.getElementById("eventsPaymentsNextBtn"),
    eventsAnalyticsRefreshBtn: document.getElementById("eventsAnalyticsRefreshBtn"),
    eventsAnalyticsHint: document.getElementById("eventsAnalyticsHint"),
    eventsAnalyticsEventSelect: document.getElementById("eventsAnalyticsEventSelect"),
    eventsReservedSlots: document.getElementById("eventsReservedSlots"),
    eventsConfirmedRegistrations: document.getElementById("eventsConfirmedRegistrations"),
    eventsConfirmedParticipants: document.getElementById("eventsConfirmedParticipants"),
    eventsPendingRegistrations: document.getElementById("eventsPendingRegistrations"),
    eventsRevenueConfirmed: document.getElementById("eventsRevenueConfirmed"),
    eventsRevenuePending: document.getElementById("eventsRevenuePending"),
    eventsCapacityValue: document.getElementById("eventsCapacityValue"),
    eventsPaymentStatusChart: document.getElementById("eventsPaymentStatusChart"),
    eventsPaymentMethodChart: document.getElementById("eventsPaymentMethodChart"),
    eventsRegistrationsTimelineChart: document.getElementById("eventsRegistrationsTimelineChart"),
    eventsNotificationsRefreshBtn: document.getElementById("eventsNotificationsRefreshBtn"),
    eventsNotificationsHint: document.getElementById("eventsNotificationsHint"),
    eventsNotificationsSearchInput: document.getElementById("eventsNotificationsSearchInput"),
    eventsNotificationsChannelFilter: document.getElementById("eventsNotificationsChannelFilter"),
    eventsNotificationsStatusFilter: document.getElementById("eventsNotificationsStatusFilter"),
    eventsNotificationsBody: document.getElementById("eventsNotificationsBody"),
    eventsCheckinRefreshBtn: document.getElementById("eventsCheckinRefreshBtn"),
    eventsCheckinHint: document.getElementById("eventsCheckinHint"),
    eventsCheckinTokenInput: document.getElementById("eventsCheckinTokenInput"),
    eventsCheckinScanBtn: document.getElementById("eventsCheckinScanBtn"),
    eventsCheckinSubmitBtn: document.getElementById("eventsCheckinSubmitBtn"),
    eventsCheckinClearBtn: document.getElementById("eventsCheckinClearBtn"),
    eventsCheckinResult: document.getElementById("eventsCheckinResult"),
    eventsCheckinBody: document.getElementById("eventsCheckinBody"),

    eventsQrScannerModal: document.getElementById("eventsQrScannerModal"),
    eventsQrScannerCloseBtn: document.getElementById("eventsQrScannerCloseBtn"),
    eventsQrScannerVideo: document.getElementById("eventsQrScannerVideo"),
    eventsQrScannerStatus: document.getElementById("eventsQrScannerStatus"),
    eventsQrScannerPhotoBtn: document.getElementById("eventsQrScannerPhotoBtn"),
    eventsQrScannerFile: document.getElementById("eventsQrScannerFile"),
    eventsRegistrationDetailModal: document.getElementById("eventsRegistrationDetailModal"),
    eventsRegistrationDetailCloseBtn: document.getElementById("eventsRegistrationDetailCloseBtn"),
    eventsRegistrationDetailTitle: document.getElementById("eventsRegistrationDetailTitle"),
    eventsRegistrationDetailBody: document.getElementById("eventsRegistrationDetailBody"),
  };

  const state = {
    events: [],
    registrations: [],
    payments: [],
    notifications: [],
    checkins: [],
    analytics: null,
    paymentAccounts: [],
    permissionSet: new Set(),
    isAdmin: false,
    currentView: "agenda",
    selectedEventId: null,
    charts: {
      paymentStatus: null,
      paymentMethod: null,
      registrationsTimeline: null,
    },
    filters: {
      eventsSearch: "",
      eventsStatus: "",
      eventsVisibility: "",
      registrationsEventId: "",
      registrationsSearch: "",
      registrationsStatus: "",
      registrationsPayment: "",
      paymentsEventId: "",
      paymentsSearch: "",
      paymentsStatus: "",
      paymentsMethod: "",
      notificationsSearch: "",
      notificationsChannel: "",
      notificationsStatus: "",
    },
    calendarCursor: new Date(),
    pagination: {
      registrations: {
        page: 1,
        size: 25,
        total: 0,
        pages: 1,
      },
      payments: {
        page: 1,
        size: 25,
        total: 0,
        pages: 1,
      },
    },
    scopedFiltersSeeded: false,
  };

  function getToken() {
    return localStorage.getItem("accessToken") || "";
  }

  function loadPermissionState() {
    try {
      const raw = localStorage.getItem(permissionStorageKey);
      const parsed = raw ? JSON.parse(raw) : [];
      state.permissionSet = new Set(Array.isArray(parsed) ? parsed.filter((item) => typeof item === "string") : []);
    } catch (_error) {
      state.permissionSet = new Set();
    }
    state.isAdmin = localStorage.getItem(isAdminStorageKey) === "true";
  }

  function hasPermission(permissionName) {
    if (!permissionName) return false;
    if (state.isAdmin) return true;
    return state.permissionSet.has(permissionName);
  }

  function canManageCheckin() {
    return hasPermission("events_events_create")
      || hasPermission("events_events_edit")
      || hasPermission("events_events_delete")
      || hasPermission("events_payments_manage");
  }

  function toggleActionByPermission(node, allowed) {
    if (!node) return;
    node.classList.toggle("hide", !allowed);
    node.disabled = !allowed;
  }

  function hasEventsModuleAccess() {
    if (state.isAdmin) return true;
    for (const permissionName of state.permissionSet) {
      if (permissionName.indexOf("events_") === 0) return true;
    }
    return false;
  }

  function getFirstAllowedView() {
    if (hasPermission(VIEW_PERMISSIONS.agenda)) return "agenda";
    if (hasPermission(VIEW_PERMISSIONS.registrations)) return "registrations";
    if (hasPermission(VIEW_PERMISSIONS.payments)) return "payments";
    if (hasPermission(VIEW_PERMISSIONS.analytics)) return "analytics";
    if (hasPermission(VIEW_PERMISSIONS.notifications)) return "notifications";
    if (canManageCheckin()) return "checkin";
    return null;
  }

  function buildHeaders(includeJson = false) {
    const headers = new Headers();
    const token = getToken();
    if (token) headers.set("Authorization", `Bearer ${token}`);
    if (includeJson) headers.set("Content-Type", "application/json");
    return headers;
  }

  async function parseError(response, fallbackMessage) {
    let detail = fallbackMessage;
    try {
      const body = await response.json();
      if (body && typeof body === "object") {
        if (typeof body.detail === "string") detail = body.detail;
        if (typeof body.msg === "string") detail = body.msg;
      }
    } catch (_error) {
      // no-op
    }
    if (response.status === 401) return "Sessao expirada. Faca login novamente.";
    return detail;
  }

  async function fetchJson(url, options = {}, fallbackMessage = "Falha na requisicao.") {
    const response = await fetch(url, options);
    if (!response.ok) {
      throw new Error(await parseError(response, fallbackMessage));
    }
    if (response.status === 204) return null;
    return response.json();
  }

  function setMessage(message, isError = false) {
    if (!el.eventsMessage) return;
    el.eventsMessage.textContent = message || "";
    el.eventsMessage.style.color = isError ? "#b42318" : "#5f6b6d";
    if (message && window.showUiAlert) {
      window.showUiAlert(message, isError ? "error" : "success");
    }
  }

  function openEventsFormModal(title = "Novo evento") {
    if (!window.openSharedFormModal || !el.eventsForm) return;
    window.openSharedFormModal({
      form: el.eventsForm,
      messageNode: el.eventsMessage,
      title,
      eyebrow: "Eventos",
      hint: "Configure agenda, inscrições e conta de recebimento em um só fluxo.",
    });
  }

  function escapeHtml(value) {
    return String(value ?? "")
      .replace(/&/g, "&amp;")
      .replace(/</g, "&lt;")
      .replace(/>/g, "&gt;")
      .replace(/"/g, "&quot;")
      .replace(/'/g, "&#39;");
  }

  function formatDateTime(value) {
    if (!value) return "-";
    const date = new Date(value);
    if (Number.isNaN(date.getTime())) return String(value);
    return date.toLocaleString("pt-BR");
  }

  function formatMoney(value, currency = "BRL") {
    const amount = Number(value || 0);
    return new Intl.NumberFormat("pt-BR", { style: "currency", currency }).format(amount);
  }

  function formatRegistrationAddress(registration) {
    const streetLine = [
      registration.address_street,
      registration.address_number,
    ].filter(Boolean).map(escapeHtml).join(", ");
    const cityLine = [
      registration.address_neighborhood,
      registration.address_city,
      registration.address_state,
    ].filter(Boolean).map(escapeHtml).join(" - ");
    const countryLine = [
      registration.address_zip_code,
      registration.address_country,
    ].filter(Boolean).map(escapeHtml).join(" · ");
    return [streetLine, cityLine, countryLine].filter(Boolean).join("<br>");
  }

  function formatRegistrationAddressText(registration) {
    const streetLine = [
      registration.address_street,
      registration.address_number,
    ].filter(Boolean).join(", ");
    const cityLine = [
      registration.address_neighborhood,
      registration.address_city,
      registration.address_state,
    ].filter(Boolean).join(" - ");
    const countryLine = [
      registration.address_zip_code,
      registration.address_country,
    ].filter(Boolean).join(" · ");
    return [streetLine, cityLine, countryLine].filter(Boolean).join("\n") || "-";
  }

  function findRegistrationById(registrationId) {
    const id = Number(registrationId || 0);
    if (!id) return null;
    return state.registrations.find((registration) => Number(registration.id) === id) || null;
  }

  function findRegistrationAttendee(registration, attendeeIndex) {
    const index = Number(attendeeIndex || 1) || 1;
    const attendees = Array.isArray(registration && registration.attendees) ? registration.attendees : [];
    return attendees.find((attendee) => Number(attendee && attendee.attendee_index) === index) || null;
  }

  function detailField(label, value) {
    const normalized = String(value ?? "").trim();
    return `
      <div class="event-registration-detail-field">
        <span>${escapeHtml(label)}</span>
        <strong>${escapeHtml(normalized || "-")}</strong>
      </div>
    `;
  }

  function openRegistrationDetail(registrationId, attendeeIndex) {
    const registration = findRegistrationById(registrationId);
    if (!registration || !el.eventsRegistrationDetailModal || !el.eventsRegistrationDetailBody) return;

    const attendee = findRegistrationAttendee(registration, attendeeIndex);
    const attendeeName = attendee && attendee.attendee_name ? attendee.attendee_name : registration.attendee_name;
    const attendees = Array.isArray(registration.attendees) && registration.attendees.length
      ? registration.attendees
      : [{ attendee_index: 1, attendee_name: registration.attendee_name }];
    const attendeeList = attendees
      .map((item) => `<li>${escapeHtml(Number(item.attendee_index || 1))}. ${escapeHtml(item.attendee_name || registration.attendee_name || "-")}</li>`)
      .join("");
    const fallbackEvent = getEventById(registration.event_id);
    const eventTitle = registration.event_title || (fallbackEvent ? fallbackEvent.title : "-");
    const address = formatRegistrationAddressText(registration);
    const consentText = registration.lgpd_data_sharing_consent
      ? `Aceito em ${formatDateTime(registration.lgpd_data_sharing_consented_at)}`
      : "Não informado";

    if (el.eventsRegistrationDetailTitle) {
      el.eventsRegistrationDetailTitle.textContent = attendeeName || "Participante";
    }
    el.eventsRegistrationDetailBody.innerHTML = `
      <div class="event-registration-detail-grid">
        ${detailField("Evento", eventTitle)}
        ${detailField("Código", registration.registration_code)}
        ${detailField("Nome", attendeeName)}
        ${detailField("E-mail", registration.attendee_email)}
        ${detailField("Telefone", registration.attendee_phone)}
        ${detailField("Ingresso", `${Number(attendeeIndex || 1) || 1}/${Number(registration.quantity || attendees.length || 1) || 1}`)}
        ${detailField("Status da inscrição", statusLabel(registration.status))}
        ${detailField("Status do pagamento", statusLabel(registration.payment_status))}
        ${detailField("Valor total", formatMoney(registration.total_amount, registration.currency || "BRL"))}
        ${detailField("Criada em", formatDateTime(registration.created_at))}
        ${detailField("Endereço", address)}
        ${detailField("LGPD", consentText)}
        ${detailField("Observações", registration.notes)}
      </div>
      <div class="event-registration-detail-section">
        <h4>Participantes desta inscrição</h4>
        <ul>${attendeeList}</ul>
      </div>
    `;
    el.eventsRegistrationDetailModal.classList.remove("hide");
    el.eventsRegistrationDetailModal.setAttribute("aria-hidden", "false");
  }

  function closeRegistrationDetail() {
    if (!el.eventsRegistrationDetailModal) return;
    el.eventsRegistrationDetailModal.classList.add("hide");
    el.eventsRegistrationDetailModal.setAttribute("aria-hidden", "true");
  }

  function formatMonthLabel(date) {
    return date.toLocaleDateString("pt-BR", { month: "long", year: "numeric" });
  }

  function includesText(value, query) {
    return String(value || "").toLowerCase().includes(String(query || "").toLowerCase().trim());
  }

  function buildQuery(params) {
    const searchParams = new URLSearchParams();
    Object.entries(params || {}).forEach(([key, value]) => {
      if (value === null || value === undefined) return;
      const normalized = String(value).trim();
      if (!normalized) return;
      searchParams.set(key, normalized);
    });
    return searchParams.toString();
  }

  function statusLabel(value) {
    const map = {
      draft: "Rascunho",
      published: "Publicado",
      cancelled: "Cancelado",
      completed: "Concluido",
      pending_payment: "Pendente",
      confirmed: "Confirmada",
      pending: "Pendente",
      paid: "Pago",
      failed: "Falhou",
      expired: "Expirou",
      refunded: "Reembolsado",
      not_required: "Nao exigido",
      queued: "Na fila",
      sent: "Enviado",
    };
    return map[String(value || "").toLowerCase()] || String(value || "-");
  }

  function toInputDateTime(value) {
    if (!value) return "";
    const date = new Date(value);
    if (Number.isNaN(date.getTime())) return "";
    const pad = (item) => String(item).padStart(2, "0");
    return `${date.getFullYear()}-${pad(date.getMonth() + 1)}-${pad(date.getDate())}T${pad(date.getHours())}:${pad(date.getMinutes())}`;
  }

  function toIsoDateTime(value) {
    if (!value) return null;
    const date = new Date(value);
    if (Number.isNaN(date.getTime())) return null;
    return date.toISOString();
  }

  function applyModuleVisibility() {
    const canOpen = hasEventsModuleAccess();
    if (el.eventsBtn) {
      el.eventsBtn.classList.toggle("hide", !canOpen);
      el.eventsBtn.disabled = !canOpen;
    }
    if (el.eventsNavEventsBtn) el.eventsNavEventsBtn.classList.toggle("hide", !hasPermission(VIEW_PERMISSIONS.agenda));
    if (el.eventsNavRegistrationsBtn) el.eventsNavRegistrationsBtn.classList.toggle("hide", !hasPermission(VIEW_PERMISSIONS.registrations));
    if (el.eventsNavPaymentsBtn) el.eventsNavPaymentsBtn.classList.toggle("hide", !hasPermission(VIEW_PERMISSIONS.payments));
    if (el.eventsNavAnalyticsBtn) el.eventsNavAnalyticsBtn.classList.toggle("hide", !hasPermission(VIEW_PERMISSIONS.analytics));
    if (el.eventsNavNotificationsBtn) el.eventsNavNotificationsBtn.classList.toggle("hide", !hasPermission(VIEW_PERMISSIONS.notifications));
    if (el.eventsNavCheckinBtn) el.eventsNavCheckinBtn.classList.toggle("hide", !canManageCheckin());
    if (el.eventsDeleteBtn) el.eventsDeleteBtn.classList.toggle("hide", !(state.selectedEventId && hasPermission("events_events_delete")));
    toggleActionByPermission(el.openEventsFormModalBtn, hasPermission("events_events_create"));
    toggleActionByPermission(el.eventsCheckinSubmitBtn, canManageCheckin());
    toggleActionByPermission(el.eventsCheckinScanBtn, canManageCheckin());
    if (el.eventsCheckinTokenInput) el.eventsCheckinTokenInput.disabled = !canManageCheckin();
  }

  function setActiveModule(moduleName) {
    if (window.setTopModule) {
      window.setTopModule(moduleName);
      return;
    }
    const isKids = moduleName === "kids";
    if (el.kidsBtn) el.kidsBtn.classList.toggle("active", isKids);
    if (el.kidsModule) el.kidsModule.classList.toggle("hide", !isKids);
    if (el.eventsModule) {
      el.eventsModule.classList.toggle("hide", moduleName !== "events");
    }
  }

  function setView(viewName) {
    if (viewName === "checkin" && !canManageCheckin()) {
      setMessage("Acesso negado: sua role nao permite realizar check-in.", true);
      const fallbackView = getFirstAllowedView();
      if (!fallbackView || fallbackView === viewName) return;
      viewName = fallbackView;
    }

    const requiredPermission = VIEW_PERMISSIONS[viewName];
    if (requiredPermission && !hasPermission(requiredPermission)) {
      setMessage("Acesso negado: sua role nao permite esta tela.", true);
      const fallbackView = getFirstAllowedView();
      if (!fallbackView || fallbackView === viewName) return;
      viewName = fallbackView;
    }

    state.currentView = viewName;
    if (el.eventsNavEventsBtn) el.eventsNavEventsBtn.classList.toggle("active", viewName === "agenda");
    if (el.eventsNavRegistrationsBtn) el.eventsNavRegistrationsBtn.classList.toggle("active", viewName === "registrations");
    if (el.eventsNavPaymentsBtn) el.eventsNavPaymentsBtn.classList.toggle("active", viewName === "payments");
    if (el.eventsNavAnalyticsBtn) el.eventsNavAnalyticsBtn.classList.toggle("active", viewName === "analytics");
    if (el.eventsNavNotificationsBtn) el.eventsNavNotificationsBtn.classList.toggle("active", viewName === "notifications");
    if (el.eventsNavCheckinBtn) el.eventsNavCheckinBtn.classList.toggle("active", viewName === "checkin");

    if (el.eventsAgendaView) el.eventsAgendaView.classList.toggle("hide", viewName !== "agenda");
    if (el.eventsRegistrationsView) el.eventsRegistrationsView.classList.toggle("hide", viewName !== "registrations");
    if (el.eventsPaymentsView) el.eventsPaymentsView.classList.toggle("hide", viewName !== "payments");
    if (el.eventsAnalyticsView) el.eventsAnalyticsView.classList.toggle("hide", viewName !== "analytics");
    if (el.eventsNotificationsView) el.eventsNotificationsView.classList.toggle("hide", viewName !== "notifications");
    if (el.eventsCheckinView) el.eventsCheckinView.classList.toggle("hide", viewName !== "checkin");
  }

  function resetEventForm() {
    if (!el.eventsForm) return;
    el.eventsForm.reset();
    el.eventsFormId.value = "";
    if (el.eventsPaymentAccountId) el.eventsPaymentAccountId.value = "";
    el.eventsMaxRegistrationsPerOrder.value = "1";
    el.eventsPricePerRegistration.value = "0";
    el.eventsCurrency.value = "BRL";
    el.eventsAllowPublicRegistration.checked = true;
    el.eventsIsActive.checked = true;
    if (el.eventsFormTitle) el.eventsFormTitle.textContent = "Novo evento";
    if (el.eventsDeleteBtn) el.eventsDeleteBtn.classList.add("hide");
  }

  function selectedEvent() {
    return state.events.find((item) => item.id === state.selectedEventId) || null;
  }

  function getEventById(eventId) {
    const targetId = Number(eventId || 0);
    if (!targetId) return null;
    return state.events.find((item) => item.id === targetId) || null;
  }

  function renderScopedEventFilter(node, selectedValue) {
    if (!node) return;
    const options = ['<option value="">Todos os eventos</option>'];
    const sorted = [...state.events].sort((a, b) => {
      const aTime = new Date(a.start_at || a.created_at || 0).getTime();
      const bTime = new Date(b.start_at || b.created_at || 0).getTime();
      return bTime - aTime;
    });
    sorted.forEach((event) => {
      options.push(`<option value="${event.id}">${escapeHtml(buildEventSelectLabel(event))}</option>`);
    });
    node.innerHTML = options.join("");
    node.value = selectedValue || "";
  }

  function renderScopedEventFilters() {
    renderScopedEventFilter(el.eventsRegistrationsEventFilter, state.filters.registrationsEventId);
    renderScopedEventFilter(el.eventsPaymentsEventFilter, state.filters.paymentsEventId);
  }

  function updatePagedControls(kind) {
    const pagination = state.pagination[kind];
    const infoNode = kind === "registrations" ? el.eventsRegistrationsPageInfo : el.eventsPaymentsPageInfo;
    const prevNode = kind === "registrations" ? el.eventsRegistrationsPrevBtn : el.eventsPaymentsPrevBtn;
    const nextNode = kind === "registrations" ? el.eventsRegistrationsNextBtn : el.eventsPaymentsNextBtn;
    if (infoNode) {
      infoNode.textContent = `Pagina ${pagination.page} de ${pagination.pages} · ${pagination.total} registro(s)`;
    }
    if (prevNode) prevNode.disabled = pagination.page <= 1;
    if (nextNode) nextNode.disabled = pagination.page >= pagination.pages;
  }

  function updateSelectedBadge() {
    const event = selectedEvent();
    const registrationsEvent = getEventById(state.filters.registrationsEventId);
    const paymentsEvent = getEventById(state.filters.paymentsEventId);
    if (el.eventsSelectedBadge) {
      el.eventsSelectedBadge.textContent = event ? `Selecionado: ${event.title}` : "Nenhum evento selecionado";
    }
    if (el.eventsAnalyticsEventSelect) {
      const desired = event ? String(event.id) : "";
      if (el.eventsAnalyticsEventSelect.value !== desired) {
        el.eventsAnalyticsEventSelect.value = desired;
      }
    }
    if (el.eventsRegistrationsHint) {
      el.eventsRegistrationsHint.textContent = registrationsEvent
        ? `Inscrições filtradas por ${registrationsEvent.title}.`
        : "Visualizando inscrições de todos os eventos. Use o filtro para focar em um evento.";
    }
    if (el.eventsPaymentsHint) {
      el.eventsPaymentsHint.textContent = paymentsEvent
        ? `Pagamentos filtrados por ${paymentsEvent.title}.`
        : "Visualizando pagamentos de todos os eventos. Use o filtro para focar em um evento.";
    }
    if (el.eventsAnalyticsHint && state.currentView !== "analytics") {
      el.eventsAnalyticsHint.textContent = event
        ? `Analytics prontos para ${event.title}.`
        : "Selecione um evento na agenda para ver ocupacao, receita e conversao.";
    }
    if (el.eventsCheckinHint) {
      el.eventsCheckinHint.textContent = event
        ? `Check-in de ${event.title}.`
        : "Selecione um evento na agenda e leia o QR Code para registrar a entrada.";
    }
    renderCalendar();
    applyModuleVisibility();
  }

  function pickDefaultEventId() {
    if (!state.events.length) return null;
    const now = Date.now();
    const sorted = [...state.events].sort((a, b) => {
      const aTime = new Date(a.start_at || a.created_at || 0).getTime();
      const bTime = new Date(b.start_at || b.created_at || 0).getTime();
      const aFuture = aTime >= now ? 0 : 1;
      const bFuture = bTime >= now ? 0 : 1;
      if (aFuture !== bFuture) return aFuture - bFuture;
      return aTime - bTime;
    });
    return sorted[0] ? sorted[0].id : null;
  }

  function buildEventSelectLabel(event) {
    const dt = new Date(event.start_at || event.created_at || 0);
    const dateStr = Number.isNaN(dt.getTime()) ? "" : dt.toLocaleString("pt-BR", { day: "2-digit", month: "2-digit", year: "numeric", hour: "2-digit", minute: "2-digit" });
    const head = dateStr ? `${dateStr} · ` : "";
    return `${head}${event.title || "Evento"}`;
  }

  function renderAnalyticsEventSelect() {
    if (!el.eventsAnalyticsEventSelect) return;
    const now = Date.now();
    const sorted = [...state.events].sort((a, b) => {
      const aTime = new Date(a.start_at || a.created_at || 0).getTime();
      const bTime = new Date(b.start_at || b.created_at || 0).getTime();
      const aPast = aTime && aTime < now ? 1 : 0;
      const bPast = bTime && bTime < now ? 1 : 0;
      if (aPast !== bPast) return aPast - bPast; // upcoming first
      return bTime - aTime; // newest first inside bucket
    });

    const options = ['<option value="">Selecione um evento</option>'];
    sorted.forEach((event) => {
      options.push(`<option value="${event.id}">${escapeHtml(buildEventSelectLabel(event))}</option>`);
    });
    el.eventsAnalyticsEventSelect.innerHTML = options.join("");
    if (state.selectedEventId) el.eventsAnalyticsEventSelect.value = String(state.selectedEventId);
  }

  function ensureSelectedEvent() {
    if (state.selectedEventId && state.events.some((item) => item.id === state.selectedEventId)) {
      return;
    }
    const fallbackId = pickDefaultEventId();
    state.selectedEventId = fallbackId ? Number(fallbackId) : null;
    const event = selectedEvent();
    if (event) {
      const eventDate = new Date(event.start_at || event.created_at || Date.now());
      if (!Number.isNaN(eventDate.getTime())) {
        state.calendarCursor = new Date(eventDate.getFullYear(), eventDate.getMonth(), 1);
      }
    }
  }

  function renderCalendar() {
    if (!el.eventsCalendarGrid || !el.eventsCalendarMonthLabel) return;
    const cursor = new Date(state.calendarCursor);
    cursor.setDate(1);
    cursor.setHours(0, 0, 0, 0);
    el.eventsCalendarMonthLabel.textContent = formatMonthLabel(cursor);

    const weekdays = ["Dom", "Seg", "Ter", "Qua", "Qui", "Sex", "Sab"];
    const monthStart = new Date(cursor);
    const gridStart = new Date(monthStart);
    gridStart.setDate(monthStart.getDate() - monthStart.getDay());

    const today = new Date();
    today.setHours(0, 0, 0, 0);

    const chunks = weekdays.map((label) => `<div class="events-calendar-weekday">${escapeHtml(label)}</div>`);
    for (let index = 0; index < 42; index += 1) {
      const day = new Date(gridStart);
      day.setDate(gridStart.getDate() + index);
      const dayKey = day.toISOString().slice(0, 10);
      const dayEvents = state.events
        .filter((event) => {
          const eventDate = new Date(event.start_at || event.created_at || 0);
          return !Number.isNaN(eventDate.getTime()) && eventDate.toISOString().slice(0, 10) === dayKey;
        })
        .sort((a, b) => new Date(a.start_at || 0).getTime() - new Date(b.start_at || 0).getTime());
      const classes = [
        "events-calendar-day",
        day.getMonth() !== cursor.getMonth() ? "is-other-month" : "",
        day.getTime() === today.getTime() ? "is-today" : "",
      ].filter(Boolean).join(" ");
      const items = dayEvents.length
        ? `<div class="events-calendar-items">${dayEvents.map((event) => `
            <button class="events-calendar-item${event.id === state.selectedEventId ? " active" : ""}" type="button" data-event-select="${event.id}">
              <span class="events-calendar-item-time">${escapeHtml(formatDateTime(event.start_at).split(" ")[1] || "")}</span>
              <span>${escapeHtml(event.title)}</span>
            </button>
          `).join("")}</div>`
        : `<div class="events-calendar-empty">Sem eventos</div>`;
      chunks.push(`
        <div class="${classes}">
          <div class="events-calendar-day-head">
            <span class="events-calendar-day-number">${day.getDate()}</span>
            <span class="events-calendar-day-count">${dayEvents.length ? `${dayEvents.length} evento(s)` : ""}</span>
          </div>
          ${items}
        </div>
      `);
    }
    el.eventsCalendarGrid.innerHTML = chunks.join("");
  }

  function fillEventForm(event) {
    if (!hasPermission("events_events_edit")) {
      setMessage("Acesso negado para editar eventos.", true);
      return;
    }

    el.eventsFormId.value = String(event.id);
    if (el.eventsPaymentAccountId) el.eventsPaymentAccountId.value = event.payment_account_id != null ? String(event.payment_account_id) : "";
    el.eventsTitle.value = event.title || "";
    el.eventsSlug.value = event.slug || "";
    el.eventsSummary.value = event.summary || "";
    el.eventsDescription.value = event.description || "";
    el.eventsLocation.value = event.location || "";
    el.eventsStartAt.value = toInputDateTime(event.start_at);
    el.eventsEndAt.value = toInputDateTime(event.end_at);
    el.eventsRegistrationOpensAt.value = toInputDateTime(event.registration_opens_at);
    el.eventsRegistrationClosesAt.value = toInputDateTime(event.registration_closes_at);
    el.eventsVisibility.value = event.visibility || "public";
    el.eventsStatus.value = event.status || "draft";
    el.eventsCapacity.value = event.capacity || "";
    el.eventsMaxRegistrationsPerOrder.value = String(event.max_registrations_per_order || 1);
    el.eventsPricePerRegistration.value = String(event.price_per_registration || 0);
    el.eventsCurrency.value = event.currency || "BRL";
    el.eventsAllowPublicRegistration.checked = Boolean(event.allow_public_registration);
    el.eventsRequirePayment.checked = Boolean(event.require_payment);
    el.eventsIsActive.checked = Boolean(event.is_active);
    if (el.eventsFormTitle) el.eventsFormTitle.textContent = `Editar evento: ${event.title}`;
    if (el.eventsDeleteBtn) el.eventsDeleteBtn.classList.toggle("hide", !hasPermission("events_events_delete"));
    openEventsFormModal(`Editar evento`);
  }

  function renderEvents() {
    if (!el.eventsCards) return;

    const filteredEvents = state.events.filter((event) => {
      if (state.filters.eventsSearch) {
        const haystack = `${event.title || ""} ${event.location || ""} ${event.slug || ""}`;
        if (!includesText(haystack, state.filters.eventsSearch)) return false;
      }
      if (state.filters.eventsStatus && event.status !== state.filters.eventsStatus) return false;
      if (state.filters.eventsVisibility && event.visibility !== state.filters.eventsVisibility) return false;
      return true;
    });

    if (el.eventsResultCount) {
      el.eventsResultCount.textContent = `${filteredEvents.length} de ${state.events.length} evento(s)`;
    }
    if (el.eventsTotalCount) el.eventsTotalCount.textContent = String(state.events.length);
    if (el.eventsPublishedCount) el.eventsPublishedCount.textContent = String(state.events.filter((item) => item.status === "published").length);
    if (el.eventsPublicCount) el.eventsPublicCount.textContent = String(state.events.filter((item) => item.visibility === "public").length);
    if (el.eventsPaidCount) el.eventsPaidCount.textContent = String(state.events.filter((item) => Number(item.price_per_registration || 0) > 0 || item.require_payment).length);

    if (!filteredEvents.length) {
      el.eventsCards.innerHTML = "<article class='event-admin-card'><h4>Sem eventos</h4><p class='tiny'>Crie seu primeiro evento para comecar a vender inscricoes.</p></article>";
      updateSelectedBadge();
      return;
    }

    const tenantSlug = localStorage.getItem("activeTenantSlug") || "default";
    el.eventsCards.innerHTML = filteredEvents.map((event) => {
      const isSelected = event.id === state.selectedEventId;
      const publicUrl = `/events/${encodeURIComponent(tenantSlug)}/${encodeURIComponent(event.slug)}`;
      const showPublicLink = event.visibility === "public";
      return `
        <article class="event-admin-card${isSelected ? " active" : ""}">
          <div class="event-admin-card-head">
            <div>
              <h4>${escapeHtml(event.title)}</h4>
              <p>${escapeHtml(event.summary || event.description || "Sem resumo cadastrado.")}</p>
            </div>
            <span class="event-admin-chip">${escapeHtml(statusLabel(event.status))}</span>
          </div>
          <div class="event-admin-card-meta">
            <span class="event-admin-chip">${escapeHtml(formatDateTime(event.start_at))}</span>
            <span class="event-admin-chip">${escapeHtml(event.location || "Local a definir")}</span>
            <span class="event-admin-chip">${escapeHtml(formatMoney(event.price_per_registration || 0, event.currency || "BRL"))}</span>
            ${event.payment_account_label ? `<span class="event-admin-chip">${escapeHtml(event.payment_account_label)} · ${escapeHtml(event.payment_account_provider || "conta")}</span>` : ""}
          </div>
          <div class="event-admin-card-actions">
            <button class="btn btn-mini" type="button" data-event-select="${event.id}">Selecionar</button>
            ${hasPermission("events_events_edit") ? `<button class="btn ghost btn-mini" type="button" data-event-edit="${event.id}">Editar</button>` : ""}
            ${showPublicLink ? `<a class="btn ghost btn-mini" href="${publicUrl}" target="_blank" rel="noreferrer">Pagina publica</a>` : ""}
          </div>
        </article>
      `;
    }).join("");
    updateSelectedBadge();
  }

  async function loadEvents() {
    setMessage("Carregando eventos...");
    state.events = await fetchJson(`${eventsEndpoint}/?include_inactive=true`, { headers: buildHeaders(false) }, "Falha ao carregar eventos.");
    if (state.selectedEventId && !state.events.some((item) => item.id === state.selectedEventId)) {
      state.selectedEventId = null;
      resetEventForm();
    }
    if (state.filters.registrationsEventId && !getEventById(state.filters.registrationsEventId)) {
      state.filters.registrationsEventId = "";
    }
    if (state.filters.paymentsEventId && !getEventById(state.filters.paymentsEventId)) {
      state.filters.paymentsEventId = "";
    }
    ensureSelectedEvent();
    if (!state.scopedFiltersSeeded && state.selectedEventId) {
      state.filters.registrationsEventId = String(state.selectedEventId);
      state.filters.paymentsEventId = String(state.selectedEventId);
      state.scopedFiltersSeeded = true;
    }
    renderEvents();
    renderCalendar();
    renderAnalyticsEventSelect();
    renderScopedEventFilters();
    setMessage("");
  }

function populatePaymentAccountOptions() {
    if (!el.eventsPaymentAccountId) return;
    const options = ['<option value="">Configuração padrão da igreja</option>'];
    state.paymentAccounts.forEach((account) => {
      const environment = account.environment === "sandbox" ? "sandbox" : "produção";
      const readiness = account.live_ready ? "pronta" : "pendente";
      options.push(
        `<option value="${account.id}">${escapeHtml(account.label)} (${escapeHtml(account.provider)} · ${escapeHtml(environment)} · ${escapeHtml(readiness)})</option>`
      );
    });
    el.eventsPaymentAccountId.innerHTML = options.join("");
  }

  async function loadPaymentAccounts() {
    try {
      state.paymentAccounts = await fetchJson(paymentAccountsEndpoint, { headers: buildHeaders(false) }, "Falha ao carregar contas de pagamento.");
    } catch (_error) {
      state.paymentAccounts = [];
    }
    populatePaymentAccountOptions();
  }

  async function loadRegistrations() {
    const query = buildQuery({
      event_id: state.filters.registrationsEventId,
      search: state.filters.registrationsSearch,
      status: state.filters.registrationsStatus,
      payment_status: state.filters.registrationsPayment,
      page: state.pagination.registrations.page,
      size: state.pagination.registrations.size,
    });
    const payload = await fetchJson(
      `${eventsEndpoint}/registrations${query ? `?${query}` : ""}`,
      { headers: buildHeaders(false) },
      "Falha ao carregar inscricoes."
    );
    state.registrations = Array.isArray(payload && payload.items) ? payload.items : [];
    state.pagination.registrations.total = Number(payload && payload.total ? payload.total : 0) || 0;
    state.pagination.registrations.pages = Number(payload && payload.pages ? payload.pages : 1) || 1;
    state.pagination.registrations.page = Number(payload && payload.page ? payload.page : state.pagination.registrations.page) || 1;
    updatePagedControls("registrations");

    if (el.eventsRegistrationsResultCount) {
      el.eventsRegistrationsResultCount.textContent = `${state.registrations.length} item(ns) na pagina atual`;
    }

    if (!state.registrations.length) {
      el.eventsRegistrationsBody.innerHTML = "<tr><td colspan='9'>Nenhuma inscricao encontrada para os filtros atuais.</td></tr>";
      return;
    }

    const rows = [];
    state.registrations.forEach((registration) => {
      const fallbackEvent = getEventById(registration.event_id);
      const eventTitle = registration.event_title || (fallbackEvent ? fallbackEvent.title : "-");
      const attendees = Array.isArray(registration.attendees) && registration.attendees.length
        ? registration.attendees
        : [{ attendee_index: 1, attendee_name: registration.attendee_name }];
      const qty = Number(registration.quantity || attendees.length || 1) || 1;
      const perTicket = qty > 0 ? Number(registration.total_amount || 0) / qty : Number(registration.total_amount || 0);
      attendees.forEach((attendee) => {
        const idx = Number(attendee && attendee.attendee_index ? attendee.attendee_index : 1) || 1;
        const badge = `${idx}/${qty}`;
        const address = formatRegistrationAddress(registration) || "-";
        rows.push(`
          <tr>
            <td>${escapeHtml(eventTitle)}</td>
            <td>${escapeHtml(registration.registration_code)}</td>
            <td><button class="event-registration-name-btn" type="button" data-registration-detail-id="${escapeHtml(registration.id)}" data-registration-attendee-index="${escapeHtml(idx)}">${escapeHtml(attendee && attendee.attendee_name ? attendee.attendee_name : registration.attendee_name)}</button><br><span class="tiny">${escapeHtml(registration.attendee_email)}</span></td>
            <td>${address}</td>
            <td>${escapeHtml(badge)}</td>
            <td>${escapeHtml(statusLabel(registration.status))}</td>
            <td>${escapeHtml(statusLabel(registration.payment_status))}</td>
            <td>${escapeHtml(formatMoney(perTicket, registration.currency || "BRL"))}</td>
            <td>${escapeHtml(formatDateTime(registration.created_at))}</td>
          </tr>
        `);
      });
    });
    el.eventsRegistrationsBody.innerHTML = rows.join("");
  }

  async function loadPayments() {
    const query = buildQuery({
      event_id: state.filters.paymentsEventId,
      search: state.filters.paymentsSearch,
      status: state.filters.paymentsStatus,
      payment_method: state.filters.paymentsMethod,
      page: state.pagination.payments.page,
      size: state.pagination.payments.size,
    });
    const payload = await fetchJson(
      `${eventsEndpoint}/payments${query ? `?${query}` : ""}`,
      { headers: buildHeaders(false) },
      "Falha ao carregar pagamentos."
    );
    state.payments = Array.isArray(payload && payload.items) ? payload.items : [];
    state.pagination.payments.total = Number(payload && payload.total ? payload.total : 0) || 0;
    state.pagination.payments.pages = Number(payload && payload.pages ? payload.pages : 1) || 1;
    state.pagination.payments.page = Number(payload && payload.page ? payload.page : state.pagination.payments.page) || 1;
    updatePagedControls("payments");

    if (el.eventsPaymentsResultCount) {
      el.eventsPaymentsResultCount.textContent = `${state.payments.length} item(ns) na pagina atual`;
    }

    if (!state.payments.length) {
      el.eventsPaymentsBody.innerHTML = "<tr><td colspan='7'>Nenhum pagamento encontrado para os filtros atuais.</td></tr>";
      return;
    }

    el.eventsPaymentsBody.innerHTML = state.payments.map((payment) => {
      const fallbackEvent = getEventById(payment.event_id);
      const eventTitle = payment.event_title || (fallbackEvent ? fallbackEvent.title : "-");
      return `
      <tr>
        <td>${escapeHtml(eventTitle)}</td>
        <td>${escapeHtml(payment.checkout_reference)}</td>
        <td>${escapeHtml(String(payment.payment_method || "-").toUpperCase())}</td>
        <td>${escapeHtml(statusLabel(payment.status))}</td>
        <td>${escapeHtml(formatMoney(payment.amount, payment.currency || "BRL"))}</td>
        <td>${payment.checkout_url ? `<a href="${escapeHtml(payment.checkout_url)}" target="_blank" rel="noreferrer">Abrir</a>` : "-"}</td>
        <td>
          ${payment.status !== "paid" && hasPermission("events_payments_manage")
            ? `<button class="btn ghost btn-mini" type="button" data-payment-confirm="${payment.id}">Confirmar</button>`
            : payment.can_refund && hasPermission("events_payments_manage")
              ? `<button class="btn ghost btn-mini" type="button" data-payment-refund="${payment.id}">Extornar</button>`
            : "<span class='tiny'>Sem acao</span>"}
        </td>
      </tr>
    `;
    }).join("");
  }

  function destroyChart(chart) {
    if (chart && typeof chart.destroy === "function") {
      chart.destroy();
    }
  }

  function buildChart(canvas, existingChart, type, labels, data, label, color) {
    if (!canvas || !window.Chart) return null;
    destroyChart(existingChart);
    return new window.Chart(canvas, {
      type,
      data: {
        labels,
        datasets: [{
          label,
          data,
          backgroundColor: color,
          borderColor: Array.isArray(color) ? color[0] : color,
          borderWidth: 2,
          fill: type === "line",
          tension: 0.28,
        }],
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
          legend: {
            display: type !== "bar" && type !== "line",
          },
        },
        scales: type === "doughnut" ? {} : {
          y: {
            beginAtZero: true,
          },
        },
      },
    });
  }

  async function loadAnalytics() {
    renderAnalyticsEventSelect();
    if (!state.selectedEventId) {
      if (el.eventsAnalyticsHint) el.eventsAnalyticsHint.textContent = "Selecione um evento no filtro acima para ver ocupacao, receita e conversao.";
      return;
    }
    state.analytics = await fetchJson(`${eventsEndpoint}/${state.selectedEventId}/analytics`, { headers: buildHeaders(false) }, "Falha ao carregar analytics do evento.");
    const analytics = state.analytics;
    el.eventsAnalyticsHint.textContent = `Analytics atualizados para ${analytics.title}.`;
    el.eventsReservedSlots.textContent = String(analytics.reserved_slots || 0);
    el.eventsConfirmedRegistrations.textContent = String(analytics.confirmed_registrations || 0);
    el.eventsConfirmedParticipants.textContent = String(analytics.confirmed_participants || 0);
    el.eventsPendingRegistrations.textContent = String(analytics.pending_registrations || 0);
    el.eventsRevenueConfirmed.textContent = formatMoney(analytics.total_revenue_confirmed || 0);
    el.eventsRevenuePending.textContent = formatMoney(analytics.total_revenue_pending || 0);
    el.eventsCapacityValue.textContent = analytics.capacity ? String(analytics.capacity) : "Ilimitada";

    const paymentStatusRows = Array.isArray(analytics.payment_status_breakdown) ? analytics.payment_status_breakdown : [];
    const paymentMethodRows = Array.isArray(analytics.payment_method_breakdown) ? analytics.payment_method_breakdown : [];
    const timelineRows = Array.isArray(analytics.registrations_by_day) ? analytics.registrations_by_day : [];

    state.charts.paymentStatus = buildChart(
      el.eventsPaymentStatusChart,
      state.charts.paymentStatus,
      "doughnut",
      paymentStatusRows.map((row) => statusLabel(row.status)),
      paymentStatusRows.map((row) => Number(row.count || 0)),
      "Pagamentos",
      ["#2b6cb0", "#38a169", "#f6ad55", "#e53e3e", "#718096", "#805ad5"],
    );

    state.charts.paymentMethod = buildChart(
      el.eventsPaymentMethodChart,
      state.charts.paymentMethod,
      "bar",
      paymentMethodRows.map((row) => String(row.payment_method || "-").toUpperCase()),
      paymentMethodRows.map((row) => Number(row.count || 0)),
      "Metodo",
      "#2f855a",
    );

    state.charts.registrationsTimeline = buildChart(
      el.eventsRegistrationsTimelineChart,
      state.charts.registrationsTimeline,
      "line",
      timelineRows.map((row) => row.day || row.date || "-"),
      timelineRows.map((row) => Number(row.count || 0)),
      "Inscricoes",
      "#c05621",
    );
  }

  async function loadNotifications() {
    if (!state.selectedEventId) {
      el.eventsNotificationsBody.innerHTML = "<tr><td colspan='7'>Selecione um evento.</td></tr>";
      return;
    }
    state.notifications = await fetchJson(`${eventsEndpoint}/${state.selectedEventId}/notifications`, { headers: buildHeaders(false) }, "Falha ao carregar notificacoes.");
    const filteredNotifications = state.notifications.filter((notification) => {
      if (state.filters.notificationsSearch && !includesText(notification.recipient, state.filters.notificationsSearch)) return false;
      if (state.filters.notificationsChannel && notification.channel !== state.filters.notificationsChannel) return false;
      if (state.filters.notificationsStatus && notification.status !== state.filters.notificationsStatus) return false;
      return true;
    });

    if (!filteredNotifications.length) {
      el.eventsNotificationsBody.innerHTML = "<tr><td colspan='7'>Nenhuma notificacao registrada.</td></tr>";
      return;
    }
    el.eventsNotificationsBody.innerHTML = filteredNotifications.map((notification) => `
      <tr>
        <td>${escapeHtml(String(notification.channel || "-").toUpperCase())}</td>
        <td>${escapeHtml(notification.recipient || "-")}</td>
        <td>${escapeHtml(notification.template_key || "-")}</td>
        <td>${escapeHtml(statusLabel(notification.status))}</td>
        <td>${escapeHtml(notification.error_message || "-")}</td>
        <td>${escapeHtml(formatDateTime(notification.sent_at || notification.created_at))}</td>
        <td>${notification.status === "failed"
          ? `<button class="btn ghost btn-mini" type="button" data-notification-retry="${Number(notification.id || 0)}">Reenviar</button>`
          : '<span class="tiny">-</span>'}
        </td>
      </tr>
    `).join("");
  }

  async function retryNotification(notificationId) {
    if (!state.selectedEventId) {
      setMessage("Selecione um evento para reenviar a notificacao.", true);
      return;
    }
    const target = state.notifications.find((notification) => Number(notification.id) === Number(notificationId));
    if (!target) {
      setMessage("Notificacao nao encontrada na lista atual.", true);
      return;
    }
    if (target.status !== "failed") {
      setMessage("Somente notificacoes com falha podem ser reenviadas.", true);
      return;
    }

    const response = await fetchJson(
      `${eventsEndpoint}/${state.selectedEventId}/notifications/${Number(notificationId)}/retry`,
      {
        method: "POST",
        headers: buildHeaders(false),
      },
      "Falha ao reenviar notificacao.",
    );
    const queuedStatus = String(response && response.status ? response.status : "queued");
    setMessage(`Notificacao reenfileirada com status ${queuedStatus}.`, false);
    await loadNotifications();
  }

  function setCheckinResult(message, isError = false) {
    if (!el.eventsCheckinResult) return;
    el.eventsCheckinResult.textContent = message || "";
    el.eventsCheckinResult.style.color = isError ? "#b42318" : "#0f766e";
    if (message && window.showUiAlert) {
      window.showUiAlert(message, isError ? "error" : "success");
    }
  }

  function renderCheckins() {
    if (!el.eventsCheckinBody) return;
    if (!state.selectedEventId) {
      el.eventsCheckinBody.innerHTML = "<tr><td colspan='4'>Selecione um evento.</td></tr>";
      return;
    }
    if (!state.checkins.length) {
      el.eventsCheckinBody.innerHTML = "<tr><td colspan='4'>Nenhum check-in registrado ainda.</td></tr>";
      return;
    }
    el.eventsCheckinBody.innerHTML = state.checkins.map((row) => `
      <tr>
        <td>${escapeHtml(row.attendee_name || "-")}</td>
        <td>${escapeHtml(row.attendee_email || "-")}</td>
        <td>${escapeHtml(formatDateTime(row.checked_in_at))}</td>
        <td>${escapeHtml(row.checked_in_by_user_id ? String(row.checked_in_by_user_id) : "-")}</td>
      </tr>
    `).join("");
  }

  async function loadCheckins() {
    if (!el.eventsCheckinBody) return;
    if (!state.selectedEventId) {
      renderCheckins();
      return;
    }
    state.checkins = await fetchJson(
      `${eventsEndpoint}/${state.selectedEventId}/checkins`,
      { headers: buildHeaders(false) },
      "Falha ao carregar check-ins."
    );
    renderCheckins();
  }

  async function submitCheckinToken() {
    if (!canManageCheckin()) {
      setCheckinResult("Acesso negado para realizar check-in.", true);
      return;
    }
    if (!el.eventsCheckinTokenInput) return;
    const token = String(el.eventsCheckinTokenInput.value || "").trim();
    if (!token) {
      setCheckinResult("Informe o token do QR Code.", true);
      return;
    }
    try {
      const result = await fetchJson(
        `${eventsEndpoint}/checkin`,
        { method: "POST", headers: buildHeaders(true), body: JSON.stringify({ token }) },
        "Falha ao realizar check-in."
      );
      const statusKey = String(result.status || "").toLowerCase();
      if (statusKey === "success") setCheckinResult(`Check-in confirmado: ${result.attendee_name || ""}`.trim(), false);
      else if (statusKey === "duplicate") setCheckinResult(`Check-in duplicado: ${result.attendee_name || ""}`.trim(), true);
      else if (statusKey === "not_paid") setCheckinResult(`Pagamento pendente: ${result.attendee_name || ""}`.trim(), true);
      else setCheckinResult(result.message || "QR Code invalido.", true);
      el.eventsCheckinTokenInput.value = "";
      await loadCheckins();
    } catch (error) {
      setCheckinResult(error && error.message ? error.message : "Falha ao realizar check-in.", true);
    }
  }

  let eventsQrStream = null;
  let eventsQrActive = false;
  let eventsQrDetector = null;
  let eventsQrMode = "";
  let eventsQrCanvas = null;
  let eventsQrCtx = null;
  let eventsQrLastScanAt = 0;

  function eventsHasJsQr() {
    return typeof window.jsQR === "function";
  }

  function eventsEnsureQrCanvas() {
    if (eventsQrCanvas && eventsQrCtx) return;
    eventsQrCanvas = document.createElement("canvas");
    eventsQrCtx = eventsQrCanvas.getContext("2d", { willReadFrequently: true });
  }

  function eventsCanUseLiveCamera() {
    // Most browsers require a secure context (HTTPS) for getUserMedia.
    if (!window.isSecureContext) return false;
    if (!("mediaDevices" in navigator)) return false;
    return typeof navigator.mediaDevices.getUserMedia === "function";
  }

  function eventsSetQrVideoVisible(visible) {
    if (!el.eventsQrScannerVideo) return;
    el.eventsQrScannerVideo.style.display = visible ? "block" : "none";
  }

  async function eventsDecodeQrFromFile(file) {
    if (!file || !eventsHasJsQr()) return "";
    eventsEnsureQrCanvas();
    if (!eventsQrCanvas || !eventsQrCtx) return "";

    const maxSide = 1024;
    const tryBitmap = typeof window.createImageBitmap === "function";
    if (tryBitmap) {
      try {
        const bitmap = await window.createImageBitmap(file);
        const w = bitmap.width || 0;
        const h = bitmap.height || 0;
        if (!w || !h) return "";
        const scale = Math.min(1, maxSide / Math.max(w, h));
        const tw = Math.max(1, Math.round(w * scale));
        const th = Math.max(1, Math.round(h * scale));
        eventsQrCanvas.width = tw;
        eventsQrCanvas.height = th;
        eventsQrCtx.drawImage(bitmap, 0, 0, tw, th);
        const imageData = eventsQrCtx.getImageData(0, 0, tw, th);
        const code = window.jsQR(imageData.data, imageData.width, imageData.height, { inversionAttempts: "attemptBoth" });
        return code && code.data ? String(code.data).trim() : "";
      } catch (_error) {
        // fall through to <img> decode
      }
    }

    return await new Promise((resolve) => {
      const url = URL.createObjectURL(file);
      const img = new Image();
      img.onload = () => {
        try {
          const w = img.naturalWidth || 0;
          const h = img.naturalHeight || 0;
          if (!w || !h) {
            resolve("");
            return;
          }
          const scale = Math.min(1, maxSide / Math.max(w, h));
          const tw = Math.max(1, Math.round(w * scale));
          const th = Math.max(1, Math.round(h * scale));
          eventsQrCanvas.width = tw;
          eventsQrCanvas.height = th;
          eventsQrCtx.drawImage(img, 0, 0, tw, th);
          const imageData = eventsQrCtx.getImageData(0, 0, tw, th);
          const code = window.jsQR(imageData.data, imageData.width, imageData.height, { inversionAttempts: "attemptBoth" });
          resolve(code && code.data ? String(code.data).trim() : "");
        } catch (_err) {
          resolve("");
        } finally {
          URL.revokeObjectURL(url);
        }
      };
      img.onerror = () => {
        URL.revokeObjectURL(url);
        resolve("");
      };
      img.src = url;
    });
  }

  async function openEventsQrScanner() {
    if (!canManageCheckin()) {
      setCheckinResult("Acesso negado para realizar check-in.", true);
      return;
    }
    if (!el.eventsQrScannerModal) return;

    el.eventsQrScannerModal.classList.remove("hide");
    el.eventsQrScannerModal.setAttribute("aria-hidden", "false");
    if (el.eventsQrScannerStatus) el.eventsQrScannerStatus.textContent = "Preparando leitor...";
    eventsSetQrVideoVisible(true);

    eventsQrDetector = null;
    eventsQrMode = "";
    if ("BarcodeDetector" in window) {
      try {
        eventsQrDetector = new window.BarcodeDetector({ formats: ["qr_code"] });
        eventsQrMode = "native";
      } catch (_error) {
        eventsQrDetector = null;
        eventsQrMode = "";
      }
    }
    if (!eventsQrMode && eventsHasJsQr()) {
      eventsEnsureQrCanvas();
      eventsQrMode = "jsqr";
    }
    if (!eventsQrMode && !eventsHasJsQr()) {
      setCheckinResult("Leitor de QR indisponivel neste navegador. Cole o token manualmente.", true);
      if (el.eventsQrScannerStatus) el.eventsQrScannerStatus.textContent = "Leitor indisponivel. Cole o token manualmente.";
      eventsSetQrVideoVisible(false);
      return;
    }

    if (!eventsCanUseLiveCamera()) {
      // Still keep the modal open: users can use the "Ler por foto" fallback.
      if (el.eventsQrScannerStatus) el.eventsQrScannerStatus.textContent = "Camera ao vivo indisponivel. Use 'Ler por foto' ou cole o token.";
      eventsSetQrVideoVisible(false);
      return;
    }

    if (el.eventsQrScannerStatus) el.eventsQrScannerStatus.textContent = "Abrindo camera...";

    try {
      eventsQrStream = await navigator.mediaDevices.getUserMedia({ video: { facingMode: "environment" }, audio: false });
    } catch (error) {
      const name = error && typeof error === "object" && "name" in error ? String(error.name) : "";
      const hint =
        name === "NotAllowedError" ? "Permissao negada para camera." :
        name === "NotFoundError" ? "Camera nao encontrada." :
        "Falha ao abrir camera.";
      setCheckinResult(`${hint} Use 'Ler por foto' ou cole o token.`, true);
      if (el.eventsQrScannerStatus) el.eventsQrScannerStatus.textContent = `${hint} Use 'Ler por foto'.`;
      eventsSetQrVideoVisible(false);
      return;
    }

    el.eventsQrScannerVideo.srcObject = eventsQrStream;
    eventsQrActive = true;
    eventsQrLastScanAt = 0;
    if (el.eventsQrScannerStatus) {
      el.eventsQrScannerStatus.textContent = "Aponte para o QR Code.";
    }
    requestAnimationFrame(scanEventsQrFrame);
  }

  function closeEventsQrScanner() {
    eventsQrActive = false;
    if (el.eventsQrScannerModal) {
      el.eventsQrScannerModal.classList.add("hide");
      el.eventsQrScannerModal.setAttribute("aria-hidden", "true");
    }
    if (el.eventsQrScannerVideo) {
      el.eventsQrScannerVideo.pause();
      el.eventsQrScannerVideo.srcObject = null;
      el.eventsQrScannerVideo.style.display = "block";
    }
    if (eventsQrStream) {
      const tracks = eventsQrStream.getTracks ? eventsQrStream.getTracks() : [];
      tracks.forEach((track) => track.stop());
    }
    eventsQrStream = null;
    eventsQrDetector = null;
    eventsQrMode = "";
    if (el.eventsQrScannerStatus) el.eventsQrScannerStatus.textContent = "Aponte a camera para o QR da inscrição.";
  }

  async function scanEventsQrFrame() {
    if (!eventsQrActive || !el.eventsQrScannerVideo) return;
    try {
      const now = Date.now();
      if (eventsQrLastScanAt && now - eventsQrLastScanAt < 120) {
        requestAnimationFrame(scanEventsQrFrame);
        return;
      }
      eventsQrLastScanAt = now;

      let raw = "";
      if (eventsQrMode === "native" && eventsQrDetector) {
        const barcodes = await eventsQrDetector.detect(el.eventsQrScannerVideo);
        if (Array.isArray(barcodes) && barcodes.length) raw = String(barcodes[0] && barcodes[0].rawValue || "").trim();
      } else if (eventsQrMode === "jsqr" && eventsHasJsQr() && eventsQrCtx && eventsQrCanvas) {
        const vw = Number(el.eventsQrScannerVideo.videoWidth || 0);
        const vh = Number(el.eventsQrScannerVideo.videoHeight || 0);
        if (vw > 0 && vh > 0) {
          const maxSide = 720;
          const scale = Math.min(1, maxSide / Math.max(vw, vh));
          const tw = Math.max(1, Math.round(vw * scale));
          const th = Math.max(1, Math.round(vh * scale));
          eventsQrCanvas.width = tw;
          eventsQrCanvas.height = th;
          eventsQrCtx.drawImage(el.eventsQrScannerVideo, 0, 0, tw, th);
          const imageData = eventsQrCtx.getImageData(0, 0, tw, th);
          const code = window.jsQR(imageData.data, imageData.width, imageData.height, { inversionAttempts: "attemptBoth" });
          if (code && code.data) raw = String(code.data).trim();
        }
      }

      if (raw) {
        closeEventsQrScanner();
        if (el.eventsCheckinTokenInput) el.eventsCheckinTokenInput.value = raw;
        await submitCheckinToken();
        return;
      }
    } catch (_error) {
      if (el.eventsQrScannerStatus) el.eventsQrScannerStatus.textContent = "Falha ao ler. Tente aproximar o QR.";
    }
    requestAnimationFrame(scanEventsQrFrame);
  }

  async function handleEventsQrFilePicked() {
    if (!el.eventsQrScannerFile) return;
    const files = el.eventsQrScannerFile.files;
    const file = files && files.length ? files[0] : null;
    // Reset so picking the same photo twice still triggers change.
    el.eventsQrScannerFile.value = "";
    if (!file) return;

    if (el.eventsQrScannerStatus) el.eventsQrScannerStatus.textContent = "Lendo foto do QR...";
    const raw = await eventsDecodeQrFromFile(file);
    if (!raw) {
      setCheckinResult("Nao foi possivel ler o QR nesta foto. Tente aproximar e focar.", true);
      if (el.eventsQrScannerStatus) el.eventsQrScannerStatus.textContent = "Nao consegui ler. Tente outra foto.";
      return;
    }
    closeEventsQrScanner();
    if (el.eventsCheckinTokenInput) el.eventsCheckinTokenInput.value = raw;
    await submitCheckinToken();
  }

  async function refreshCurrentView() {
    if (state.currentView === "agenda") {
      await loadEvents();
      return;
    }
    if (state.currentView === "registrations") {
      await loadRegistrations();
      return;
    }
    if (state.currentView === "payments") {
      await loadPayments();
      return;
    }
    if (state.currentView === "analytics") {
      await loadAnalytics();
      return;
    }
    if (state.currentView === "notifications") {
      await loadNotifications();
      return;
    }
    if (state.currentView === "checkin") {
      await loadCheckins();
    }
  }

  async function selectEvent(eventId, openForm = false) {
    state.selectedEventId = Number(eventId);
    if (state.selectedEventId) {
      state.filters.registrationsEventId = String(state.selectedEventId);
      state.filters.paymentsEventId = String(state.selectedEventId);
      state.pagination.registrations.page = 1;
      state.pagination.payments.page = 1;
    }
    const event = selectedEvent();
    if (event) {
      const eventDate = new Date(event.start_at || event.created_at || Date.now());
      if (!Number.isNaN(eventDate.getTime())) {
        state.calendarCursor = new Date(eventDate.getFullYear(), eventDate.getMonth(), 1);
      }
    }
    if (event && openForm) {
      fillEventForm(event);
    }
    renderScopedEventFilters();
    renderEvents();
    if (state.currentView !== "agenda") {
      await refreshCurrentView();
    }
  }

  function readFormPayload() {
    return {
      payment_account_id: el.eventsPaymentAccountId && el.eventsPaymentAccountId.value ? Number(el.eventsPaymentAccountId.value) : null,
      title: el.eventsTitle.value.trim(),
      slug: el.eventsSlug.value.trim() || null,
      summary: el.eventsSummary.value.trim() || null,
      description: el.eventsDescription.value.trim() || null,
      location: el.eventsLocation.value.trim() || null,
      timezone_name: "America/Sao_Paulo",
      visibility: el.eventsVisibility.value,
      status: el.eventsStatus.value,
      start_at: toIsoDateTime(el.eventsStartAt.value),
      end_at: toIsoDateTime(el.eventsEndAt.value),
      registration_opens_at: toIsoDateTime(el.eventsRegistrationOpensAt.value),
      registration_closes_at: toIsoDateTime(el.eventsRegistrationClosesAt.value),
      capacity: el.eventsCapacity.value ? Number(el.eventsCapacity.value) : null,
      max_registrations_per_order: Number(el.eventsMaxRegistrationsPerOrder.value || 1),
      price_per_registration: Number(el.eventsPricePerRegistration.value || 0),
      currency: (el.eventsCurrency.value || "BRL").trim().toUpperCase(),
      allow_public_registration: el.eventsAllowPublicRegistration.checked,
      require_payment: el.eventsRequirePayment.checked,
      is_active: el.eventsIsActive.checked,
    };
  }

  async function submitEventForm(event) {
    event.preventDefault();
    if (!hasPermission("events_events_create") && !hasPermission("events_events_edit")) {
      setMessage("Acesso negado para salvar eventos.", true);
      return;
    }
    const payload = readFormPayload();
    const editingId = Number(el.eventsFormId.value || 0);
    const isEditing = editingId > 0;

    if (isEditing && !hasPermission("events_events_edit")) {
      setMessage("Acesso negado para editar eventos.", true);
      return;
    }
    if (!isEditing && !hasPermission("events_events_create")) {
      setMessage("Acesso negado para criar eventos.", true);
      return;
    }

    try {
      const response = await fetchJson(
        isEditing ? `${eventsEndpoint}/${editingId}` : `${eventsEndpoint}/`,
        {
          method: isEditing ? "PUT" : "POST",
          headers: buildHeaders(true),
          body: JSON.stringify(payload),
        },
        isEditing ? "Falha ao atualizar evento." : "Falha ao criar evento.",
      );
      state.selectedEventId = response.id;
      await loadEvents();
      setMessage(isEditing ? "Evento atualizado com sucesso." : "Evento criado com sucesso.");
      if (isEditing || hasPermission("events_events_edit")) {
        fillEventForm(response);
      }
      if (window.closeSharedFormModal) window.closeSharedFormModal();
    } catch (error) {
      setMessage(error.message, true);
    }
  }

  async function deleteSelectedEvent() {
    if (!state.selectedEventId) return;
    if (!hasPermission("events_events_delete")) {
      setMessage("Acesso negado para excluir eventos.", true);
      return;
    }
    const confirmed = window.openUiConfirm
      ? await window.openUiConfirm("Deseja realmente excluir este evento?", "Excluir evento")
      : window.confirm("Deseja realmente excluir este evento?");
    if (!confirmed) return;

    try {
      await fetchJson(`${eventsEndpoint}/${state.selectedEventId}`, { method: "DELETE", headers: buildHeaders(false) }, "Falha ao excluir evento.");
      state.selectedEventId = null;
      resetEventForm();
      if (window.closeSharedFormModal) window.closeSharedFormModal();
      await loadEvents();
      await refreshCurrentView();
      setMessage("Evento excluido com sucesso.");
    } catch (error) {
      setMessage(error.message, true);
    }
  }

  async function confirmPayment(paymentId) {
    if (!hasPermission("events_payments_manage")) {
      setMessage("Acesso negado para confirmar pagamentos.", true);
      return;
    }
    try {
      await fetchJson(`${eventsEndpoint}/payments/${paymentId}/confirm`, { method: "POST", headers: buildHeaders(false) }, "Falha ao confirmar pagamento.");
      await Promise.all([loadPayments(), loadRegistrations(), loadAnalytics(), loadNotifications()]);
      setMessage("Pagamento confirmado e refletido no evento.");
    } catch (error) {
      setMessage(error.message, true);
    }
  }

  async function refundPayment(paymentId) {
    if (!hasPermission("events_payments_manage")) {
      setMessage("Acesso negado para extornar pagamentos.", true);
      return;
    }
    const confirmed = window.openUiConfirm
      ? await window.openUiConfirm("Deseja realmente extornar este pagamento?", "Extornar pagamento")
      : window.confirm("Deseja realmente extornar este pagamento?");
    if (!confirmed) return;
    try {
      await fetchJson(`${eventsEndpoint}/payments/${paymentId}/refund`, { method: "POST", headers: buildHeaders(false) }, "Falha ao extornar pagamento.");
      await Promise.all([loadPayments(), loadRegistrations(), loadAnalytics(), loadNotifications()]);
      setMessage("Pagamento extornado e refletido nas inscricoes.");
    } catch (error) {
      setMessage(error.message, true);
    }
  }

  async function openEventsModule() {
    loadPermissionState();
    applyModuleVisibility();

    if (!hasEventsModuleAccess()) {
      throw new Error("Acesso negado ao modulo Eventos.");
    }

    const fallbackView = getFirstAllowedView();
    if (!fallbackView) {
      throw new Error("Sua role nao possui permissao de visualizacao no modulo Eventos.");
    }

    setActiveModule("events");
    setView(fallbackView);
    await loadPaymentAccounts();
    await loadEvents();
    ensureSelectedEvent();
    if (state.selectedEventId || state.currentView !== "agenda") {
      await refreshCurrentView();
    }
  }

  function bindFilterInput(node, stateKey, onChange) {
    if (!node) return;
    const eventName = node.tagName === "SELECT" ? "change" : "input";
    node.addEventListener(eventName, () => {
      state.filters[stateKey] = node.value || "";
      onChange().catch((error) => setMessage(error.message, true));
    });
  }

  function bindEvents() {
    if (eventsBound) return;
    eventsBound = true;

    loadPermissionState();
    applyModuleVisibility();

    if (el.eventsBtn) {
      el.eventsBtn.addEventListener("click", () => {
        openEventsModule().catch((error) => setMessage(error.message, true));
      });
    }
    if (el.eventsNavEventsBtn) el.eventsNavEventsBtn.addEventListener("click", () => setView("agenda"));
    if (el.eventsNavRegistrationsBtn) {
      el.eventsNavRegistrationsBtn.addEventListener("click", () => {
        ensureSelectedEvent();
        setView("registrations");
        loadRegistrations().catch((error) => setMessage(error.message, true));
      });
    }
    if (el.eventsNavPaymentsBtn) {
      el.eventsNavPaymentsBtn.addEventListener("click", () => {
        ensureSelectedEvent();
        setView("payments");
        loadPayments().catch((error) => setMessage(error.message, true));
      });
    }
    if (el.eventsNavAnalyticsBtn) {
      el.eventsNavAnalyticsBtn.addEventListener("click", () => {
        ensureSelectedEvent();
        setView("analytics");
        renderAnalyticsEventSelect();
        loadAnalytics().catch((error) => setMessage(error.message, true));
      });
    }
    if (el.eventsNavNotificationsBtn) {
      el.eventsNavNotificationsBtn.addEventListener("click", () => {
        ensureSelectedEvent();
        setView("notifications");
        loadNotifications().catch((error) => setMessage(error.message, true));
      });
    }
    if (el.eventsNavCheckinBtn) {
      el.eventsNavCheckinBtn.addEventListener("click", () => {
        ensureSelectedEvent();
        setView("checkin");
        loadCheckins().catch((error) => setMessage(error.message, true));
      });
    }
    if (el.eventsRefreshBtn) el.eventsRefreshBtn.addEventListener("click", () => loadEvents().catch((error) => setMessage(error.message, true)));
    if (el.eventsCalendarPrevBtn) {
      el.eventsCalendarPrevBtn.addEventListener("click", () => {
        state.calendarCursor = new Date(state.calendarCursor.getFullYear(), state.calendarCursor.getMonth() - 1, 1);
        renderCalendar();
      });
    }
    if (el.eventsCalendarNextBtn) {
      el.eventsCalendarNextBtn.addEventListener("click", () => {
        state.calendarCursor = new Date(state.calendarCursor.getFullYear(), state.calendarCursor.getMonth() + 1, 1);
        renderCalendar();
      });
    }
    if (el.eventsClearFiltersBtn) {
      el.eventsClearFiltersBtn.addEventListener("click", () => {
        state.filters.eventsSearch = "";
        state.filters.eventsStatus = "";
        state.filters.eventsVisibility = "";
        if (el.eventsSearchInput) el.eventsSearchInput.value = "";
        if (el.eventsStatusFilter) el.eventsStatusFilter.value = "";
        if (el.eventsVisibilityFilter) el.eventsVisibilityFilter.value = "";
        renderEvents();
      });
    }
    if (el.eventsRegistrationsRefreshBtn) el.eventsRegistrationsRefreshBtn.addEventListener("click", () => loadRegistrations().catch((error) => setMessage(error.message, true)));
    if (el.eventsPaymentsRefreshBtn) el.eventsPaymentsRefreshBtn.addEventListener("click", () => loadPayments().catch((error) => setMessage(error.message, true)));
    if (el.eventsAnalyticsRefreshBtn) el.eventsAnalyticsRefreshBtn.addEventListener("click", () => loadAnalytics().catch((error) => setMessage(error.message, true)));
    if (el.eventsAnalyticsEventSelect) {
      el.eventsAnalyticsEventSelect.addEventListener("change", () => {
        const raw = String(el.eventsAnalyticsEventSelect.value || "").trim();
        const id = raw ? Number(raw) : 0;
        if (!id) {
          state.selectedEventId = null;
          updateSelectedBadge();
          if (el.eventsAnalyticsHint) el.eventsAnalyticsHint.textContent = "Selecione um evento no filtro acima para ver ocupacao, receita e conversao.";
          return;
        }
        selectEvent(id).catch((error) => setMessage(error.message, true));
      });
    }
    if (el.eventsNotificationsRefreshBtn) el.eventsNotificationsRefreshBtn.addEventListener("click", () => loadNotifications().catch((error) => setMessage(error.message, true)));
    if (el.eventsNotificationsBody) {
      el.eventsNotificationsBody.addEventListener("click", (event) => {
        const button = event.target.closest("[data-notification-retry]");
        if (!button) return;
        const notificationId = Number(button.getAttribute("data-notification-retry") || 0);
        if (!notificationId) return;
        retryNotification(notificationId).catch((error) => setMessage(error.message, true));
      });
    }
    if (el.eventsCheckinRefreshBtn) el.eventsCheckinRefreshBtn.addEventListener("click", () => loadCheckins().catch((error) => setMessage(error.message, true)));
    if (el.eventsCheckinSubmitBtn) el.eventsCheckinSubmitBtn.addEventListener("click", () => submitCheckinToken().catch((error) => setMessage(error.message, true)));
    if (el.eventsCheckinScanBtn) el.eventsCheckinScanBtn.addEventListener("click", () => openEventsQrScanner().catch((error) => setMessage(error.message, true)));
    if (el.eventsCheckinTokenInput) {
      el.eventsCheckinTokenInput.addEventListener("keydown", (event) => {
        if (event.key === "Enter") {
          event.preventDefault();
          submitCheckinToken().catch((error) => setMessage(error.message, true));
        }
      });
    }
    if (el.eventsQrScannerCloseBtn) el.eventsQrScannerCloseBtn.addEventListener("click", closeEventsQrScanner);
    if (el.eventsRegistrationDetailCloseBtn) el.eventsRegistrationDetailCloseBtn.addEventListener("click", closeRegistrationDetail);
    if (el.eventsRegistrationDetailModal) {
      el.eventsRegistrationDetailModal.addEventListener("click", (event) => {
        if (event.target === el.eventsRegistrationDetailModal) closeRegistrationDetail();
      });
    }
    if (el.eventsQrScannerPhotoBtn && el.eventsQrScannerFile) {
      el.eventsQrScannerPhotoBtn.addEventListener("click", () => {
        el.eventsQrScannerFile.click();
      });
      el.eventsQrScannerFile.addEventListener("change", () => {
        handleEventsQrFilePicked().catch((error) => setMessage(error.message, true));
      });
    }
    if (el.eventsCheckinClearBtn && el.eventsCheckinTokenInput) {
      el.eventsCheckinClearBtn.addEventListener("click", () => {
        el.eventsCheckinTokenInput.value = "";
        setCheckinResult("", false);
      });
    }
    if (el.eventsForm) el.eventsForm.addEventListener("submit", submitEventForm);
    const handleOpenEventForm = () => {
      if (!hasPermission("events_events_create")) {
        setMessage("Acesso negado para criar eventos.", true);
        return;
      }
      resetEventForm();
      openEventsFormModal("Novo evento");
    };
    if (el.openEventsFormModalBtn) el.openEventsFormModalBtn.addEventListener("click", handleOpenEventForm);
    document.querySelectorAll("[data-open-events-form='true']").forEach((button) => {
      button.addEventListener("click", handleOpenEventForm);
    });
    if (el.eventsFormResetBtn) el.eventsFormResetBtn.addEventListener("click", () => {
      resetEventForm();
      if (window.closeSharedFormModal) window.closeSharedFormModal();
    });
    if (el.eventsDeleteBtn) el.eventsDeleteBtn.addEventListener("click", () => deleteSelectedEvent().catch((error) => setMessage(error.message, true)));

    bindFilterInput(el.eventsSearchInput, "eventsSearch", async () => renderEvents());
    bindFilterInput(el.eventsStatusFilter, "eventsStatus", async () => renderEvents());
    bindFilterInput(el.eventsVisibilityFilter, "eventsVisibility", async () => renderEvents());
    bindFilterInput(el.eventsNotificationsSearchInput, "notificationsSearch", loadNotifications);
    bindFilterInput(el.eventsNotificationsChannelFilter, "notificationsChannel", loadNotifications);
    bindFilterInput(el.eventsNotificationsStatusFilter, "notificationsStatus", loadNotifications);

    const bindPagedFilter = (node, applyValue) => {
      if (!node) return;
      const eventName = node.tagName === "SELECT" ? "change" : "input";
      node.addEventListener(eventName, () => {
        applyValue(node.value || "");
      });
    };

    bindPagedFilter(el.eventsRegistrationsEventFilter, (value) => {
      state.filters.registrationsEventId = value;
      state.pagination.registrations.page = 1;
      if (value) state.selectedEventId = Number(value);
      renderScopedEventFilters();
      renderEvents();
      updateSelectedBadge();
      loadRegistrations().catch((error) => setMessage(error.message, true));
    });
    bindPagedFilter(el.eventsRegistrationsSearchInput, (value) => {
      state.filters.registrationsSearch = value;
      state.pagination.registrations.page = 1;
      loadRegistrations().catch((error) => setMessage(error.message, true));
    });
    bindPagedFilter(el.eventsRegistrationsStatusFilter, (value) => {
      state.filters.registrationsStatus = value;
      state.pagination.registrations.page = 1;
      loadRegistrations().catch((error) => setMessage(error.message, true));
    });
    bindPagedFilter(el.eventsRegistrationsPaymentFilter, (value) => {
      state.filters.registrationsPayment = value;
      state.pagination.registrations.page = 1;
      loadRegistrations().catch((error) => setMessage(error.message, true));
    });
    bindPagedFilter(el.eventsPaymentsEventFilter, (value) => {
      state.filters.paymentsEventId = value;
      state.pagination.payments.page = 1;
      if (value) state.selectedEventId = Number(value);
      renderScopedEventFilters();
      renderEvents();
      updateSelectedBadge();
      loadPayments().catch((error) => setMessage(error.message, true));
    });
    bindPagedFilter(el.eventsPaymentsSearchInput, (value) => {
      state.filters.paymentsSearch = value;
      state.pagination.payments.page = 1;
      loadPayments().catch((error) => setMessage(error.message, true));
    });
    bindPagedFilter(el.eventsPaymentsStatusFilter, (value) => {
      state.filters.paymentsStatus = value;
      state.pagination.payments.page = 1;
      loadPayments().catch((error) => setMessage(error.message, true));
    });
    bindPagedFilter(el.eventsPaymentsMethodFilter, (value) => {
      state.filters.paymentsMethod = value;
      state.pagination.payments.page = 1;
      loadPayments().catch((error) => setMessage(error.message, true));
    });
    bindPagedFilter(el.eventsRegistrationsPageSize, (value) => {
      state.pagination.registrations.size = Number(value || 25) || 25;
      state.pagination.registrations.page = 1;
      loadRegistrations().catch((error) => setMessage(error.message, true));
    });
    bindPagedFilter(el.eventsPaymentsPageSize, (value) => {
      state.pagination.payments.size = Number(value || 25) || 25;
      state.pagination.payments.page = 1;
      loadPayments().catch((error) => setMessage(error.message, true));
    });
    if (el.eventsRegistrationsPrevBtn) {
      el.eventsRegistrationsPrevBtn.addEventListener("click", () => {
        if (state.pagination.registrations.page <= 1) return;
        state.pagination.registrations.page -= 1;
        loadRegistrations().catch((error) => setMessage(error.message, true));
      });
    }
    if (el.eventsRegistrationsNextBtn) {
      el.eventsRegistrationsNextBtn.addEventListener("click", () => {
        if (state.pagination.registrations.page >= state.pagination.registrations.pages) return;
        state.pagination.registrations.page += 1;
        loadRegistrations().catch((error) => setMessage(error.message, true));
      });
    }
    if (el.eventsPaymentsPrevBtn) {
      el.eventsPaymentsPrevBtn.addEventListener("click", () => {
        if (state.pagination.payments.page <= 1) return;
        state.pagination.payments.page -= 1;
        loadPayments().catch((error) => setMessage(error.message, true));
      });
    }
    if (el.eventsPaymentsNextBtn) {
      el.eventsPaymentsNextBtn.addEventListener("click", () => {
        if (state.pagination.payments.page >= state.pagination.payments.pages) return;
        state.pagination.payments.page += 1;
        loadPayments().catch((error) => setMessage(error.message, true));
      });
    }

    document.addEventListener("click", (event) => {
      const registrationDetailButton = event.target.closest && event.target.closest("[data-registration-detail-id]");
      if (registrationDetailButton) {
        openRegistrationDetail(
          registrationDetailButton.getAttribute("data-registration-detail-id"),
          registrationDetailButton.getAttribute("data-registration-attendee-index"),
        );
        return;
      }

      const selectButton = event.target.closest && event.target.closest("[data-event-select]");
      if (selectButton) {
        selectEvent(Number(selectButton.getAttribute("data-event-select"))).catch((error) => setMessage(error.message, true));
        return;
      }

      const editButton = event.target.closest && event.target.closest("[data-event-edit]");
      if (editButton) {
        selectEvent(Number(editButton.getAttribute("data-event-edit")), true).catch((error) => setMessage(error.message, true));
        return;
      }

      const paymentButton = event.target.closest && event.target.closest("[data-payment-confirm]");
      if (paymentButton) {
        confirmPayment(Number(paymentButton.getAttribute("data-payment-confirm"))).catch((error) => setMessage(error.message, true));
        return;
      }

      const refundButton = event.target.closest && event.target.closest("[data-payment-refund]");
      if (refundButton) {
        refundPayment(Number(refundButton.getAttribute("data-payment-refund"))).catch((error) => setMessage(error.message, true));
      }
    });
  }

  window.openEventsModule = () => openEventsModule().catch((error) => setMessage(error.message, true));

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", bindEvents);
  } else {
    bindEvents();
  }
})();
