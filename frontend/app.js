const API_PREFIX = "/api/v1";
const TX_FILTERS_STORAGE_KEY = "txFiltersV1";
const TX_PAGINATION_STORAGE_KEY = "txPaginationV1";
const DASH_BUDGETS_STORAGE_KEY = "dashBudgetsV1";
const CURRENT_USER_PERMISSIONS_STORAGE_KEY = "currentUserPermissions";
const CURRENT_USER_IS_ADMIN_STORAGE_KEY = "currentUserIsAdmin";

const state = {
  accessToken: localStorage.getItem("accessToken") || "",
  refreshToken: localStorage.getItem("refreshToken") || "",
  publicPaymentPollTimer: null,
  categories: [],
  ministries: [],
  transactionsRaw: [],
  payables: [],
  payableAlertsSummary: {
    overdue: 0,
    due_today: 0,
    due_in_3_days: 0,
    due_in_7_days: 0,
    pending_total: 0,
  },
  receivables: [],
  receivableAlertsSummary: {
    overdue: 0,
    due_today: 0,
    due_in_3_days: 0,
    due_in_7_days: 0,
    pending_total: 0,
  },
  txFilters: {
    search: "",
    startDate: "",
    endDate: "",
    type: "",
    categoryId: "",
    ministryId: "",
    attachment: "",
    sort: "date_desc",
  },
  dashboardFilters: {
    startDate: "",
    endDate: "",
    type: "",
    categoryId: "",
    ministryId: "",
    bank: "",
  },
  budgetTargets: [],
  budgetHealthMetrics: [],
  cashFlowForecast: null,
  dashboardTrendRows: [],
  txPagination: {
    page: 1,
    pageSize: 25,
  },
  payableFilters: {
    search: "",
    status: "",
    startDate: "",
    endDate: "",
  },
  receivableFilters: {
    search: "",
    status: "",
    startDate: "",
    endDate: "",
  },
  editingTransactionId: null,
  editingPayableId: null,
  editingReceivableId: null,
  editingCategoryId: null,
  editingMinistryId: null,
  currentUserRole: "",
  currentUserPermissions: [],
  currentUserPermissionSet: new Set(),
  currentUserIsAdmin: false,
  previewAttachmentUrl: "",
};

const el = {
  loginScreen: document.getElementById("loginScreen"),
  publicCatalogScreen: document.getElementById("publicCatalogScreen"),
  publicEventDetailScreen: document.getElementById("publicEventDetailScreen"),
  publicEventScreen: document.getElementById("publicEventScreen"),
  appShell: document.getElementById("appShell"),
  publicCatalogTitle: document.getElementById("publicCatalogTitle"),
  publicCatalogSummary: document.getElementById("publicCatalogSummary"),
  publicCatalogGrid: document.getElementById("publicCatalogGrid"),
  publicDetailTitle: document.getElementById("publicDetailTitle"),
  publicDetailSummary: document.getElementById("publicDetailSummary"),
  publicDetailMetaDate: document.getElementById("publicDetailMetaDate"),
  publicDetailMetaLocation: document.getElementById("publicDetailMetaLocation"),
  publicDetailMetaSlots: document.getElementById("publicDetailMetaSlots"),
  publicDetailMessage: document.getElementById("publicDetailMessage"),
  publicEventRegistrationForm: document.getElementById("publicEventRegistrationForm"),
  publicDetailName: document.getElementById("publicDetailName"),
  publicDetailEmail: document.getElementById("publicDetailEmail"),
  publicDetailPhone: document.getElementById("publicDetailPhone"),
  publicDetailQuantity: document.getElementById("publicDetailQuantity"),
  publicDetailPaymentMethod: document.getElementById("publicDetailPaymentMethod"),
  publicDetailNotes: document.getElementById("publicDetailNotes"),
  publicDetailSubmitBtn: document.getElementById("publicDetailSubmitBtn"),
  publicEventTitle: document.getElementById("publicEventTitle"),
  publicEventSummary: document.getElementById("publicEventSummary"),
  publicEventMetaDate: document.getElementById("publicEventMetaDate"),
  publicEventMetaLocation: document.getElementById("publicEventMetaLocation"),
  publicEventMetaCode: document.getElementById("publicEventMetaCode"),
  publicPaymentBadge: document.getElementById("publicPaymentBadge"),
  publicPaymentHeadline: document.getElementById("publicPaymentHeadline"),
  publicPaymentMessage: document.getElementById("publicPaymentMessage"),
  publicRegistrationName: document.getElementById("publicRegistrationName"),
  publicPaymentAmount: document.getElementById("publicPaymentAmount"),
  publicPaymentMethod: document.getElementById("publicPaymentMethod"),
  publicRegistrationStatus: document.getElementById("publicRegistrationStatus"),
  publicPixBlock: document.getElementById("publicPixBlock"),
  publicPixCode: document.getElementById("publicPixCode"),
  publicCopyPixBtn: document.getElementById("publicCopyPixBtn"),
  publicCheckoutBlock: document.getElementById("publicCheckoutBlock"),
  publicCheckoutLink: document.getElementById("publicCheckoutLink"),
  publicRefreshStatusBtn: document.getElementById("publicRefreshStatusBtn"),
  dashboardView: document.getElementById("dashboardView"),
  transactionsView: document.getElementById("transactionsView"),
  payablesView: document.getElementById("payablesView"),
  receivablesView: document.getElementById("receivablesView"),
  categoriesView: document.getElementById("categoriesView"),
  ministriesView: document.getElementById("ministriesView"),
  uploadView: document.getElementById("uploadView"),
  reportsView: document.getElementById("reportsView"),
  navButtons: document.querySelectorAll(".nav-btn"),
  sessionUser: document.getElementById("sessionUser"),
  authMessage: document.getElementById("authMessage"),
  dashboardMessage: document.getElementById("dashboardMessage"),
  txMessage: document.getElementById("txMessage"),
  payableMessage: document.getElementById("payableMessage"),
  receivableMessage: document.getElementById("receivableMessage"),
  categoryMessage: document.getElementById("categoryMessage"),
  ministryMessage: document.getElementById("ministryMessage"),
  uploadMessage: document.getElementById("uploadMessage"),
  reportMessage: document.getElementById("reportMessage"),
  moduleFinanceBtn: document.getElementById("moduleFinanceBtn"),
  moduleCellsBtn: document.getElementById("moduleCellsBtn"),
  moduleBibleSchoolBtn: document.getElementById("moduleBibleSchoolBtn"),
  moduleEventsBtn: document.getElementById("moduleEventsBtn"),
  moduleUsersBtn: document.getElementById("moduleUsersBtn"),
  loginForm: document.getElementById("loginForm"),
  logoutBtn: document.getElementById("logoutBtn"),
  refreshBtn: document.getElementById("refreshBtn"),
  dashStartDate: document.getElementById("dashStartDate"),
  dashEndDate: document.getElementById("dashEndDate"),
  dashTypeFilter: document.getElementById("dashTypeFilter"),
  dashCategoryFilter: document.getElementById("dashCategoryFilter"),
  dashMinistryFilter: document.getElementById("dashMinistryFilter"),
  dashBankFilter: document.getElementById("dashBankFilter"),
  dashBudgetForm: document.getElementById("dashBudgetForm"),
  dashBudgetType: document.getElementById("dashBudgetType"),
  dashBudgetRef: document.getElementById("dashBudgetRef"),
  dashBudgetAmount: document.getElementById("dashBudgetAmount"),
  dashBudgetMessage: document.getElementById("dashBudgetMessage"),
  dashBudgetList: document.getElementById("dashBudgetList"),
  dashAlertsList: document.getElementById("dashAlertsList"),
  dashResetFiltersBtn: document.getElementById("dashResetFiltersBtn"),
  dashResultCount: document.getElementById("dashResultCount"),
  dashIncomeBar: document.getElementById("dashIncomeBar"),
  dashExpenseBar: document.getElementById("dashExpenseBar"),
  dashIncomePercent: document.getElementById("dashIncomePercent"),
  dashExpensePercent: document.getElementById("dashExpensePercent"),
  dashEfficiencyNote: document.getElementById("dashEfficiencyNote"),
  dashBankBars: document.getElementById("dashBankBars"),
  dashTopCategories: document.getElementById("dashTopCategories"),
  dashLineMetric: document.getElementById("dashLineMetric"),
  dashTopMinistries: document.getElementById("dashTopMinistries"),
  dashLineChart: document.getElementById("dashLineChart"),
  dashLineTooltip: document.getElementById("dashLineTooltip"),
  dashExpensePie: document.getElementById("dashExpensePie"),
  dashExpensePieCenter: document.getElementById("dashExpensePieCenter"),
  dashExpensePieLegend: document.getElementById("dashExpensePieLegend"),
  dashPieTooltip: document.getElementById("dashPieTooltip"),
  dashMonthlyTrend: document.getElementById("dashMonthlyTrend"),
  dashMonthlyBars: document.getElementById("dashMonthlyBars"),
  dashProjectedIncome: document.getElementById("dashProjectedIncome"),
  dashProjectedExpense: document.getElementById("dashProjectedExpense"),
  dashProjectedBalance: document.getElementById("dashProjectedBalance"),
  dashProjectionNote: document.getElementById("dashProjectionNote"),
  dashSixMonthComparison: document.getElementById("dashSixMonthComparison"),
  transactionForm: document.getElementById("transactionForm"),
  uploadForm: document.getElementById("uploadForm"),
  txTableBody: document.getElementById("txTableBody"),
  txDescription: document.getElementById("txDescription"),
  txFilterSearch: document.getElementById("txFilterSearch"),
  txFilterStartDate: document.getElementById("txFilterStartDate"),
  txFilterEndDate: document.getElementById("txFilterEndDate"),
  txFilterType: document.getElementById("txFilterType"),
  txFilterCategory: document.getElementById("txFilterCategory"),
  txFilterMinistry: document.getElementById("txFilterMinistry"),
  txFilterAttachment: document.getElementById("txFilterAttachment"),
  txFilterSort: document.getElementById("txFilterSort"),
  txFilterResetBtn: document.getElementById("txFilterResetBtn"),
  txFilterChips: document.getElementById("txFilterChips"),
  txFilterResultCount: document.getElementById("txFilterResultCount"),
  txPageSize: document.getElementById("txPageSize"),
  txPagePrevBtn: document.getElementById("txPagePrevBtn"),
  txPageInfo: document.getElementById("txPageInfo"),
  txPageNextBtn: document.getElementById("txPageNextBtn"),
  txHeaderDateSort: document.getElementById("txHeaderDateSort"),
  txHeaderAmountSort: document.getElementById("txHeaderAmountSort"),
  txType: document.getElementById("txType"),
  txBankName: document.getElementById("txBankName"),
  payableForm: document.getElementById("payableForm"),
  payableDescription: document.getElementById("payableDescription"),
  payableAmount: document.getElementById("payableAmount"),
  payableDueDate: document.getElementById("payableDueDate"),
  payableCategory: document.getElementById("payableCategory"),
  payableMinistry: document.getElementById("payableMinistry"),
  payableBankName: document.getElementById("payableBankName"),
  payableExpenseProfile: document.getElementById("payableExpenseProfile"),
  payableAttachmentFile: document.getElementById("payableAttachmentFile"),
  payableRecurringType: document.getElementById("payableRecurringType"),
  payableNotes: document.getElementById("payableNotes"),
  payableSaveBtn: document.getElementById("payableSaveBtn"),
  payableCancelEditBtn: document.getElementById("payableCancelEditBtn"),
  payableFilterSearch: document.getElementById("payableFilterSearch"),
  payableFilterStatus: document.getElementById("payableFilterStatus"),
  payableFilterStartDate: document.getElementById("payableFilterStartDate"),
  payableFilterEndDate: document.getElementById("payableFilterEndDate"),
  payableFilterResultCount: document.getElementById("payableFilterResultCount"),
  payableFilterResetBtn: document.getElementById("payableFilterResetBtn"),
  payableTableBody: document.getElementById("payableTableBody"),
  editPayableModal: document.getElementById("editPayableModal"),
  editPayableForm: document.getElementById("editPayableForm"),
  editPayableCloseBtn: document.getElementById("editPayableCloseBtn"),
  editPayableCancelBtn: document.getElementById("editPayableCancelBtn"),
  editPayableDescription: document.getElementById("editPayableDescription"),
  editPayableAmount: document.getElementById("editPayableAmount"),
  editPayableDueDate: document.getElementById("editPayableDueDate"),
  editPayableCategory: document.getElementById("editPayableCategory"),
  editPayableMinistry: document.getElementById("editPayableMinistry"),
  editPayableBankName: document.getElementById("editPayableBankName"),
  editPayableExpenseProfile: document.getElementById("editPayableExpenseProfile"),
  editPayableRecurringType: document.getElementById("editPayableRecurringType"),
  editPayableAttachmentFile: document.getElementById("editPayableAttachmentFile"),
  editPayableNotes: document.getElementById("editPayableNotes"),
  editPayableAttachmentBlockCurrent: document.getElementById("editPayableAttachmentBlockCurrent"),
  editPayableAttachmentCurrentName: document.getElementById("editPayableAttachmentCurrentName"),
  editPayableRemoveCurrentAttachmentBtn: document.getElementById("editPayableRemoveCurrentAttachmentBtn"),
  receivableForm: document.getElementById("receivableForm"),
  receivableDescription: document.getElementById("receivableDescription"),
  receivableAmount: document.getElementById("receivableAmount"),
  receivableDueDate: document.getElementById("receivableDueDate"),
  receivableCategory: document.getElementById("receivableCategory"),
  receivableMinistry: document.getElementById("receivableMinistry"),
  receivableBankName: document.getElementById("receivableBankName"),
  receivableRecurringType: document.getElementById("receivableRecurringType"),
  receivableNotes: document.getElementById("receivableNotes"),
  receivableSaveBtn: document.getElementById("receivableSaveBtn"),
  receivableCancelEditBtn: document.getElementById("receivableCancelEditBtn"),
  receivableFilterSearch: document.getElementById("receivableFilterSearch"),
  receivableFilterStatus: document.getElementById("receivableFilterStatus"),
  receivableFilterStartDate: document.getElementById("receivableFilterStartDate"),
  receivableFilterEndDate: document.getElementById("receivableFilterEndDate"),
  receivableFilterResultCount: document.getElementById("receivableFilterResultCount"),
  receivableFilterResetBtn: document.getElementById("receivableFilterResetBtn"),
  receivableTableBody: document.getElementById("receivableTableBody"),
  txCategoryInput: document.getElementById("txCategoryInput"),
  txCategoryId: document.getElementById("txCategoryId"),
  txCategoryOptions: document.getElementById("txCategoryOptions"),
  txAddTypedCategoryBtn: document.getElementById("txAddTypedCategoryBtn"),
  txExpenseProfile: document.getElementById("txExpenseProfile"),
  txMinistry: document.getElementById("txMinistry"),
  categoryForm: document.getElementById("categoryForm"),
  categoryName: document.getElementById("categoryName"),
  categoryType: document.getElementById("categoryType"),
  categoryDescription: document.getElementById("categoryDescription"),
  categoryCancelEditBtn: document.getElementById("categoryCancelEditBtn"),
  categoryTableBody: document.getElementById("categoryTableBody"),
  ministryForm: document.getElementById("ministryForm"),
  ministryName: document.getElementById("ministryName"),
  ministryDescription: document.getElementById("ministryDescription"),
  ministryCancelEditBtn: document.getElementById("ministryCancelEditBtn"),
  ministryTableBody: document.getElementById("ministryTableBody"),
  deleteCategoryModal: document.getElementById("deleteCategoryModal"),
  deleteCategoryText: document.getElementById("deleteCategoryText"),
  deleteCategoryCloseBtn: document.getElementById("deleteCategoryCloseBtn"),
  deleteCategoryCancelBtn: document.getElementById("deleteCategoryCancelBtn"),
  deleteCategoryConfirmBtn: document.getElementById("deleteCategoryConfirmBtn"),
  categoryReport: document.getElementById("categoryReport"),
  monthlyReport: document.getElementById("monthlyReport"),
  reportYear: document.getElementById("reportYear"),
  kpiIncome: document.getElementById("kpiIncome"),
  kpiExpense: document.getElementById("kpiExpense"),
  kpiBalance: document.getElementById("kpiBalance"),
  kpiPayablesPending: document.getElementById("kpiPayablesPending"),
  kpiPayablesCard: document.querySelector(".kpi.payables"),
  kpiPayablesOverdue: document.getElementById("kpiPayablesOverdue"),
  kpiPayablesOverdueCard: document.querySelector(".kpi.payables-overdue"),
  kpiReceivablesPending: document.getElementById("kpiReceivablesPending"),
  kpiReceivablesAlert: document.getElementById("kpiReceivablesAlert"),
  kpiReceivablesCard: document.querySelector(".kpi.receivables"),
  kpiReceivablesOverdue: document.getElementById("kpiReceivablesOverdue"),
  kpiReceivablesOverdueCard: document.querySelector(".kpi.receivables-overdue"),
  uploadResultModal: document.getElementById("uploadResultModal"),
  modalTitle: document.getElementById("modalTitle"),
  modalBody: document.getElementById("modalBody"),
  modalDuplicatesList: document.getElementById("modalDuplicatesList"),
  modalKeepBothBtn: document.getElementById("modalKeepBothBtn"),
  modalDiscardBtn: document.getElementById("modalDiscardBtn"),
  modalChooseOneBtn: document.getElementById("modalChooseOneBtn"),
  modalApplySelectionBtn: document.getElementById("modalApplySelectionBtn"),
  modalCloseBtn: document.getElementById("modalCloseBtn"),
  modalOkBtn: document.getElementById("modalOkBtn"),
  editTransactionModal: document.getElementById("editTransactionModal"),
  editTransactionForm: document.getElementById("editTransactionForm"),
  editModalCloseBtn: document.getElementById("editModalCloseBtn"),
  editModalCancelBtn: document.getElementById("editModalCancelBtn"),
  editTxDescription: document.getElementById("editTxDescription"),
  editTxAmount: document.getElementById("editTxAmount"),
  editTxType: document.getElementById("editTxType"),
  editTxDate: document.getElementById("editTxDate"),
  editTxCategory: document.getElementById("editTxCategory"),
  editTxExpenseProfile: document.getElementById("editTxExpenseProfile"),
  editTxMinistry: document.getElementById("editTxMinistry"),
  editTxBankName: document.getElementById("editTxBankName"),
  editTxAttachmentFile: document.getElementById("editTxAttachmentFile"),
  editTxUploadAttachmentBtn: document.getElementById("editTxUploadAttachmentBtn"),
  editTxAttachmentsList: document.getElementById("editTxAttachmentsList"),
  attachmentPreviewModal: document.getElementById("attachmentPreviewModal"),
  attachmentPreviewTitle: document.getElementById("attachmentPreviewTitle"),
  attachmentPreviewCloseBtn: document.getElementById("attachmentPreviewCloseBtn"),
  attachmentPreviewImage: document.getElementById("attachmentPreviewImage"),
  attachmentPreviewPdf: document.getElementById("attachmentPreviewPdf"),
  payablePaidAtModal: document.getElementById("payablePaidAtModal"),
  payablePaidAtInput: document.getElementById("payablePaidAtInput"),
  payablePaidMethodInput: document.getElementById("payablePaidMethodInput"),
  payablePaidAtCloseBtn: document.getElementById("payablePaidAtCloseBtn"),
  payablePaidAtCancelBtn: document.getElementById("payablePaidAtCancelBtn"),
  payablePaidAtConfirmBtn: document.getElementById("payablePaidAtConfirmBtn"),
};

let payablePaidAtResolver = null;
let confirmModalResolver = null;

function brl(value) {
  return new Intl.NumberFormat("pt-BR", { style: "currency", currency: "BRL" }).format(Number(value || 0));
}

function toInputAmount(value) {
  return Number(value || 0).toFixed(2);
}

function normalizeText(value) {
  return String(value || "")
    .toLowerCase()
    .normalize("NFD")
    .replace(/[\u0300-\u036f]/g, "")
    .trim();
}

function debounce(fn, wait = 300) {
  let timeoutId;
  return (...args) => {
    clearTimeout(timeoutId);
    timeoutId = setTimeout(() => fn(...args), wait);
  };
}

function positionTooltipInContainer(tooltipNode, containerNode, anchorX, anchorY, offsetX = 12, offsetY = -18) {
  const pad = 8;
  const containerRect = containerNode.getBoundingClientRect();

  const rawLeft = anchorX - containerRect.left + offsetX;
  const rawTop = anchorY - containerRect.top + offsetY;

  const width = tooltipNode.offsetWidth || 180;
  const height = tooltipNode.offsetHeight || 36;

  const maxLeft = Math.max(pad, containerRect.width - width - pad);
  const maxTop = Math.max(pad, containerRect.height - height - pad);

  const left = Math.max(pad, Math.min(rawLeft, maxLeft));
  const top = Math.max(pad, Math.min(rawTop, maxTop));

  tooltipNode.style.left = `${left}px`;
  tooltipNode.style.top = `${top}px`;
}

function errorDetailToText(detail, fallback = "Erro inesperado") {
  if (detail == null) {
    return fallback;
  }
  if (typeof detail === "string") {
    return detail;
  }
  if (Array.isArray(detail)) {
    return detail
      .map((item) => {
        if (typeof item === "string") {
          return item;
        }
        if (item && typeof item === "object") {
          const loc = Array.isArray(item.loc) ? item.loc.join(".") : "campo";
          const msg = item.msg || JSON.stringify(item);
          return `${loc}: ${msg}`;
        }
        return String(item);
      })
      .join("; ");
  }
  if (typeof detail === "object") {
    if (typeof detail.msg === "string") {
      return detail.msg;
    }
    return JSON.stringify(detail);
  }
  return String(detail);
}

function clearAttachmentPreview() {
  if (state.previewAttachmentUrl) {
    URL.revokeObjectURL(state.previewAttachmentUrl);
    state.previewAttachmentUrl = "";
  }
  el.attachmentPreviewImage.src = "";
  el.attachmentPreviewPdf.src = "";
  el.attachmentPreviewImage.classList.add("hide");
  el.attachmentPreviewPdf.classList.add("hide");
}

function closeAttachmentPreviewModal() {
  clearAttachmentPreview();
  el.attachmentPreviewModal.classList.add("hide");
}

async function previewTransactionAttachment(transactionId, attachment) {
  const headers = new Headers();
  if (state.accessToken) {
    headers.set("Authorization", `Bearer ${state.accessToken}`);
  }

  const response = await fetch(
    `${API_PREFIX}/transactions/${transactionId}/attachments/${attachment.id}/download`,
    { method: "GET", headers },
  );
  if (!response.ok) {
    throw new Error("Falha ao carregar preview do anexo.");
  }

  const blob = await response.blob();
  clearAttachmentPreview();
  state.previewAttachmentUrl = URL.createObjectURL(blob);
  el.attachmentPreviewTitle.textContent = attachment.original_filename;

  if ((attachment.mime_type || "").startsWith("image/")) {
    el.attachmentPreviewImage.src = state.previewAttachmentUrl;
    el.attachmentPreviewImage.classList.remove("hide");
  } else if (attachment.mime_type === "application/pdf") {
    el.attachmentPreviewPdf.src = state.previewAttachmentUrl;
    el.attachmentPreviewPdf.classList.remove("hide");
  } else {
    throw new Error("Preview nao suportado para este tipo de arquivo.");
  }

  el.attachmentPreviewModal.classList.remove("hide");
}

async function previewPayableAttachment(payableId) {
  const payable = state.payables.find((item) => item.id === payableId);
  if (!payable || !payable.attachment_original_filename) {
    throw new Error("Boleto nao encontrado.");
  }

  const headers = new Headers();
  if (state.accessToken) {
    headers.set("Authorization", `Bearer ${state.accessToken}`);
  }

  const response = await fetch(`${API_PREFIX}/payables/${payableId}/attachment/download`, {
    method: "GET",
    headers,
  });
  if (!response.ok) {
    throw new Error("Falha ao carregar boleto.");
  }

  const blob = await response.blob();
  const mimeType = payable.attachment_mime_type || "application/octet-stream";

  if ((mimeType || "").startsWith("image/")) {
    // Para imagens, mostrar em modal preview
    clearAttachmentPreview();
    state.previewAttachmentUrl = URL.createObjectURL(blob);
    el.attachmentPreviewTitle.textContent = payable.attachment_original_filename;
    el.attachmentPreviewImage.src = state.previewAttachmentUrl;
    el.attachmentPreviewImage.classList.remove("hide");
    el.attachmentPreviewModal.classList.remove("hide");
  } else if (mimeType === "application/pdf") {
    // Para PDF, abrir em nova aba
    const url = URL.createObjectURL(blob);
    window.open(url, "_blank");
    setTimeout(() => URL.revokeObjectURL(url), 100);
  } else {
    throw new Error("Preview nao suportado para este tipo de arquivo.");
  }
}

function setMessage(node, text, isError = false) {
  node.textContent = text;
  node.style.color = isError ? "#b42318" : "#5f6b6d";
}

function showApp(isAuthed) {
  el.loginScreen.classList.toggle("hide", isAuthed);
  el.publicCatalogScreen.classList.add("hide");
  el.publicEventDetailScreen.classList.add("hide");
  el.publicEventScreen.classList.add("hide");
  el.appShell.classList.toggle("hide", !isAuthed);
}

function showPublicEventApp() {
  el.loginScreen.classList.add("hide");
  el.publicCatalogScreen.classList.add("hide");
  el.publicEventDetailScreen.classList.add("hide");
  el.appShell.classList.add("hide");
  el.publicEventScreen.classList.remove("hide");
}

function showPublicCatalogApp() {
  el.loginScreen.classList.add("hide");
  el.publicEventDetailScreen.classList.add("hide");
  el.publicEventScreen.classList.add("hide");
  el.appShell.classList.add("hide");
  el.publicCatalogScreen.classList.remove("hide");
}

function showPublicEventDetailApp() {
  el.loginScreen.classList.add("hide");
  el.publicCatalogScreen.classList.add("hide");
  el.publicEventScreen.classList.add("hide");
  el.appShell.classList.add("hide");
  el.publicEventDetailScreen.classList.remove("hide");
}

function isPublicRegistrationRoute() {
  const match = window.location.pathname.match(/\/events\/registration\/([^/?#]+)/);
  return Boolean(match);
}

function isPublicCatalogRoute() {
  return Boolean(window.location.pathname.match(/^\/events\/([^/]+)\/?$/));
}

function isPublicEventDetailRoute() {
  return Boolean(window.location.pathname.match(/^\/events\/([^/]+)\/([^/]+)\/?$/));
}

function getCheckoutReferenceFromRoute() {
  const match = window.location.pathname.match(/\/events\/registration\/([^/?#]+)/);
  return match ? decodeURIComponent(match[1]) : "";
}

function getPublicCatalogTenantSlug() {
  const match = window.location.pathname.match(/^\/events\/([^/]+)\/?$/);
  return match ? decodeURIComponent(match[1]) : "default";
}

function getPublicEventRouteParams() {
  const match = window.location.pathname.match(/^\/events\/([^/]+)\/([^/]+)\/?$/);
  if (!match) {
    return { tenantSlug: "default", eventSlug: "" };
  }
  return {
    tenantSlug: decodeURIComponent(match[1]),
    eventSlug: decodeURIComponent(match[2]),
  };
}

function formatCurrency(value) {
  const amount = Number(value || 0);
  return amount.toLocaleString("pt-BR", { style: "currency", currency: "BRL" });
}

function formatDateTime(value) {
  if (!value) {
    return "-";
  }
  const date = new Date(value);
  return date.toLocaleString("pt-BR", {
    dateStyle: "medium",
    timeStyle: "short",
  });
}

function formatPublicStatusLabel(value) {
  const map = {
    pending: "Pagamento pendente",
    paid: "Pagamento aprovado",
    failed: "Pagamento recusado",
    expired: "Pagamento expirado",
    cancelled: "Pagamento cancelado",
    refunded: "Pagamento estornado",
    pending_payment: "Aguardando pagamento",
    confirmed: "Inscricao confirmada",
    card: "Cartao",
    pix: "PIX",
  };
  return map[value] || String(value || "-");
}

function escapeHtml(value) {
  return String(value || "")
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;")
    .replaceAll("'", "&#039;");
}

function clearPublicPaymentPolling() {
  if (state.publicPaymentPollTimer) {
    clearTimeout(state.publicPaymentPollTimer);
    state.publicPaymentPollTimer = null;
  }
}

function schedulePublicPaymentPolling(checkoutReference) {
  clearPublicPaymentPolling();
  state.publicPaymentPollTimer = window.setTimeout(() => {
    loadPublicPaymentStatus(checkoutReference, { silent: true }).catch(() => {});
  }, 10000);
}

function renderPublicPaymentStatus(payload) {
  const { event, registration, payment } = payload;
  document.title = `${event.title} | Inscricao`;
  el.publicEventTitle.textContent = event.title;
  el.publicEventSummary.textContent = event.summary || event.description || "Acompanhe sua inscricao e o status do pagamento.";
  el.publicEventMetaDate.textContent = `Data: ${formatDateTime(event.start_at)}`;
  el.publicEventMetaLocation.textContent = `Local: ${event.location || "A definir"}`;
  el.publicEventMetaCode.textContent = `Codigo: ${registration.registration_code}`;
  el.publicRegistrationName.textContent = registration.attendee_name;
  el.publicPaymentAmount.textContent = formatCurrency(payment.amount);
  el.publicPaymentMethod.textContent = formatPublicStatusLabel(payment.payment_method);
  el.publicRegistrationStatus.textContent = formatPublicStatusLabel(registration.status);

  const paymentStatus = String(payment.status || "").toLowerCase();
  el.publicPaymentBadge.textContent = formatPublicStatusLabel(paymentStatus);
  el.publicPaymentBadge.className = `public-event-status-badge ${paymentStatus}`;

  if (paymentStatus === "paid") {
    el.publicPaymentHeadline.textContent = "Pagamento confirmado";
    el.publicPaymentMessage.textContent = "Sua inscricao esta confirmada. Guarde este codigo para apresentar no evento.";
  } else if (paymentStatus === "pending") {
    el.publicPaymentHeadline.textContent = "Pagamento em andamento";
    el.publicPaymentMessage.textContent = "Conclua o pagamento para confirmar sua inscricao. O status sera atualizado automaticamente.";
  } else {
    el.publicPaymentHeadline.textContent = "Pagamento requer atencao";
    el.publicPaymentMessage.textContent = "Seu pagamento ainda nao foi concluido. Revise os dados e tente novamente se necessario.";
  }

  const hasPix = Boolean(payment.pix_copy_paste);
  el.publicPixBlock.classList.toggle("hide", !hasPix);
  el.publicPixCode.value = hasPix ? payment.pix_copy_paste : "";

  const hasCheckoutUrl = Boolean(payment.checkout_url);
  el.publicCheckoutBlock.classList.toggle("hide", !hasCheckoutUrl);
  if (hasCheckoutUrl) {
    el.publicCheckoutLink.href = payment.checkout_url;
  }

  if (paymentStatus === "pending") {
    schedulePublicPaymentPolling(payment.checkout_reference);
  } else {
    clearPublicPaymentPolling();
  }
}

async function loadPublicPaymentStatus(checkoutReference, options = {}) {
  const response = await fetch(`${API_PREFIX}/events/public/payments/${encodeURIComponent(checkoutReference)}`);
  if (!response.ok) {
    const body = await response.json().catch(() => ({}));
    const detail = errorDetailToText(body.detail ?? body, "Falha ao carregar status da inscricao");
    if (!options.silent) {
      el.publicPaymentMessage.textContent = detail;
    }
    throw new Error(detail);
  }
  const payload = await response.json();
  renderPublicPaymentStatus(payload);
  return payload;
}

async function initializePublicEventApp() {
  showPublicEventApp();
  const checkoutReference = getCheckoutReferenceFromRoute();
  if (!checkoutReference) {
    el.publicPaymentMessage.textContent = "Referencia de pagamento nao encontrada na URL.";
    return;
  }

  const searchParams = new URLSearchParams(window.location.search);
  const returnStatus = searchParams.get("status");
  if (returnStatus === "success") {
    el.publicPaymentMessage.textContent = "Retorno recebido. Estamos atualizando a confirmacao do pagamento.";
  }

  try {
    await loadPublicPaymentStatus(checkoutReference);
  } catch (error) {
    el.publicPaymentMessage.textContent = error.message;
  }
}

function renderPublicCatalog(events, tenantSlug) {
  document.title = "Eventos | Inscricao Online";
  el.publicCatalogTitle.textContent = "Eventos disponíveis";
  el.publicCatalogSummary.textContent = "Escolha um evento público, faça sua inscrição e acompanhe o pagamento online.";

  if (!events.length) {
    el.publicCatalogGrid.innerHTML = "<article class='public-event-card-link'><h3>Nenhum evento disponível</h3><p class='tiny'>Publique um evento para começar a receber inscrições.</p></article>";
    return;
  }

  el.publicCatalogGrid.innerHTML = events.map((event) => `
    <a class="public-event-card-link" href="/events/${encodeURIComponent(tenantSlug)}/${encodeURIComponent(event.slug)}">
      <div>
        <p class="eyebrow">Evento Público</p>
        <h3>${escapeHtml(event.title)}</h3>
      </div>
      <p>${escapeHtml(event.summary || event.description || "Inscrições abertas online.")}</p>
      <div class="public-event-card-meta">
        <span>${escapeHtml(formatDateTime(event.start_at))}</span>
        <span>${escapeHtml(event.location || "Local a definir")}</span>
        <span>${escapeHtml(formatCurrency(event.price_per_registration || 0))}</span>
      </div>
    </a>
  `).join("");
}

async function initializePublicCatalogApp() {
  showPublicCatalogApp();
  const tenantSlug = getPublicCatalogTenantSlug();
  const response = await fetch(`${API_PREFIX}/events/public/tenants/${encodeURIComponent(tenantSlug)}/events`);
  if (!response.ok) {
    el.publicCatalogGrid.innerHTML = "<article class='public-event-card-link'><h3>Falha ao carregar eventos</h3><p class='tiny'>Tente novamente em instantes.</p></article>";
    return;
  }
  const events = await response.json();
  renderPublicCatalog(events, tenantSlug);
}

function renderPublicEventDetail(payload) {
  const { tenant_slug: tenantSlug, event, available_slots: availableSlots } = payload;
  document.title = `${event.title} | Inscricao`;
  el.publicDetailTitle.textContent = event.title;
  el.publicDetailSummary.textContent = event.summary || event.description || "Preencha seus dados para gerar a inscrição.";
  el.publicDetailMetaDate.textContent = `Data: ${formatDateTime(event.start_at)}`;
  el.publicDetailMetaLocation.textContent = `Local: ${event.location || "A definir"}`;
  el.publicDetailMetaSlots.textContent = `Vagas: ${availableSlots == null ? "Ilimitadas" : availableSlots}`;
  el.publicDetailMessage.textContent = `Valor por inscrição: ${formatCurrency(event.price_per_registration || 0)}`;
  el.publicEventRegistrationForm.dataset.tenantSlug = tenantSlug;
  el.publicEventRegistrationForm.dataset.eventSlug = event.slug;
  el.publicDetailQuantity.max = String(event.max_registrations_per_order || 1);
}

async function initializePublicEventDetailApp() {
  showPublicEventDetailApp();
  const { tenantSlug, eventSlug } = getPublicEventRouteParams();
  if (!eventSlug) {
    el.publicDetailMessage.textContent = "Evento não encontrado.";
    return;
  }
  const response = await fetch(`${API_PREFIX}/events/public/${encodeURIComponent(tenantSlug)}/${encodeURIComponent(eventSlug)}`);
  if (!response.ok) {
    el.publicDetailMessage.textContent = "Falha ao carregar detalhes do evento.";
    return;
  }
  const payload = await response.json();
  renderPublicEventDetail(payload);
}

function setActiveView(viewId) {
  const viewPermissionById = {
    dashboardView: "finance_dashboard_view",
    transactionsView: "finance_transactions_view",
    payablesView: "finance_payables_view",
    receivablesView: "finance_receivables_view",
    categoriesView: "finance_categories_view",
    ministriesView: "finance_ministries_view",
    uploadView: "finance_upload_manage",
    reportsView: "finance_reports_view",
  };

  const requiredPermission = viewPermissionById[viewId];
  if (requiredPermission && !hasPermission(requiredPermission)) {
    setMessage(el.dashboardMessage, "Acesso negado: sua role nao permite esta tela.", true);
    const fallbackView = getFirstFinanceAllowedView();
    if (!fallbackView || fallbackView === viewId) {
      return;
    }
    viewId = fallbackView;
  }

  const views = [
    el.dashboardView,
    el.transactionsView,
    el.payablesView,
    el.receivablesView,
    el.categoriesView,
    el.ministriesView,
    el.uploadView,
    el.reportsView,
  ];
  for (const view of views) {
    view.classList.toggle("hide", view.id !== viewId);
  }
  for (const btn of el.navButtons) {
    btn.classList.toggle("active", btn.dataset.view === viewId);
  }
}

function getPermissionsFromStorage() {
  try {
    const raw = localStorage.getItem(CURRENT_USER_PERMISSIONS_STORAGE_KEY);
    const parsed = raw ? JSON.parse(raw) : [];
    return Array.isArray(parsed) ? parsed.filter((item) => typeof item === "string") : [];
  } catch (_error) {
    return [];
  }
}

function syncPermissionStateFromStorage() {
  state.currentUserPermissions = getPermissionsFromStorage();
  state.currentUserPermissionSet = new Set(state.currentUserPermissions);
  state.currentUserIsAdmin = localStorage.getItem(CURRENT_USER_IS_ADMIN_STORAGE_KEY) === "true";
  if (!state.currentUserRole) {
    state.currentUserRole = String(localStorage.getItem("currentUserRole") || "").toLowerCase();
  }
}

function hasPermission(permissionName) {
  if (!permissionName) return false;
  if (state.currentUserIsAdmin || state.currentUserRole === "admin") return true;
  if (!state.currentUserPermissionSet || !state.currentUserPermissionSet.size) {
    syncPermissionStateFromStorage();
  }
  return state.currentUserPermissionSet.has(permissionName);
}

function hasModuleAccess(moduleName) {
  if (state.currentUserIsAdmin || state.currentUserRole === "admin") return true;
  if (!state.currentUserPermissionSet || !state.currentUserPermissionSet.size) {
    syncPermissionStateFromStorage();
  }
  const prefix = `${moduleName}_`;
  for (const permissionName of state.currentUserPermissionSet) {
    if (permissionName.startsWith(prefix)) {
      return true;
    }
  }
  return false;
}

function getFirstAccessibleModule() {
  const orderedModules = ["finance", "cells", "school", "events", "users"];
  for (const moduleName of orderedModules) {
    if (hasModuleAccess(moduleName)) {
      return moduleName;
    }
  }
  return null;
}

function openFirstAccessibleModule() {
  const moduleName = getFirstAccessibleModule();
  if (!moduleName) return false;

  if (moduleName === "finance") {
    const firstFinanceView = getFirstFinanceAllowedView();
    if (firstFinanceView) {
      setActiveView(firstFinanceView);
      return true;
    }
    return false;
  }

  const clickMap = {
    cells: el.moduleCellsBtn,
    school: el.moduleBibleSchoolBtn,
    events: el.moduleEventsBtn,
    users: el.moduleUsersBtn,
  };
  const targetBtn = clickMap[moduleName];
  if (targetBtn && !targetBtn.disabled) {
    targetBtn.click();
    return true;
  }

  return false;
}

function getFirstFinanceAllowedView() {
  const orderedViewPermissions = [
    ["dashboardView", "finance_dashboard_view"],
    ["transactionsView", "finance_transactions_view"],
    ["payablesView", "finance_payables_view"],
    ["receivablesView", "finance_receivables_view"],
    ["categoriesView", "finance_categories_view"],
    ["ministriesView", "finance_ministries_view"],
    ["uploadView", "finance_upload_manage"],
    ["reportsView", "finance_reports_view"],
  ];

  for (const [viewId, permissionName] of orderedViewPermissions) {
    if (hasPermission(permissionName)) {
      return viewId;
    }
  }
  return null;
}

function applyTopModulePermissions() {
  const modules = [
    [el.moduleFinanceBtn, "finance"],
    [el.moduleCellsBtn, "cells"],
    [el.moduleBibleSchoolBtn, "school"],
    [el.moduleEventsBtn, "events"],
    [el.moduleUsersBtn, "users"],
  ];

  modules.forEach(([button, moduleName]) => {
    if (!button) return;
    const allowed = hasModuleAccess(moduleName);
    button.classList.toggle("hide", !allowed);
    button.disabled = !allowed;
  });
}

function setTransactionSort(sortValue) {
  state.txFilters.sort = sortValue;
  el.txFilterSort.value = sortValue;
  state.txPagination.page = 1;
  saveTransactionFilterState();
}

function toggleTransactionSort(base) {
  const current = state.txFilters.sort;
  if (base === "date") {
    setTransactionSort(current === "date_desc" ? "date_asc" : "date_desc");
  } else if (base === "amount") {
    setTransactionSort(current === "amount_desc" ? "amount_asc" : "amount_desc");
  }
  renderTransactions();
}

function updateTransactionSortHeaderLabels() {
  el.txHeaderDateSort.textContent = "Data";
  el.txHeaderAmountSort.textContent = "Valor";
  if (state.txFilters.sort === "date_desc") {
    el.txHeaderDateSort.textContent = "Data ↓";
  }
  if (state.txFilters.sort === "date_asc") {
    el.txHeaderDateSort.textContent = "Data ↑";
  }
  if (state.txFilters.sort === "amount_desc") {
    el.txHeaderAmountSort.textContent = "Valor ↓";
  }
  if (state.txFilters.sort === "amount_asc") {
    el.txHeaderAmountSort.textContent = "Valor ↑";
  }
}

function populateTransactionFilterOptions() {
  const selectedCategory = state.txFilters.categoryId;
  const selectedMinistry = state.txFilters.ministryId;

  el.txFilterCategory.innerHTML = "<option value=''>Todas</option>";
  for (const cat of [...state.categories].sort((a, b) => a.name.localeCompare(b.name, "pt-BR"))) {
    const option = document.createElement("option");
    option.value = String(cat.id);
    option.textContent = cat.name;
    el.txFilterCategory.appendChild(option);
  }

  el.txFilterMinistry.innerHTML = "<option value=''>Todos</option>";
  for (const ministry of [...state.ministries].sort((a, b) => a.name.localeCompare(b.name, "pt-BR"))) {
    const option = document.createElement("option");
    option.value = String(ministry.id);
    option.textContent = ministry.name;
    el.txFilterMinistry.appendChild(option);
  }

  el.txFilterCategory.value = selectedCategory || "";
  el.txFilterMinistry.value = selectedMinistry || "";
}

function saveTransactionFilterState() {
  localStorage.setItem(TX_FILTERS_STORAGE_KEY, JSON.stringify(state.txFilters));
  localStorage.setItem(TX_PAGINATION_STORAGE_KEY, JSON.stringify(state.txPagination));
}

function loadTransactionFilterState() {
  try {
    const rawFilters = localStorage.getItem(TX_FILTERS_STORAGE_KEY);
    if (rawFilters) {
      const parsed = JSON.parse(rawFilters);
      state.txFilters = {
        ...state.txFilters,
        ...parsed,
      };
    }

    const rawPagination = localStorage.getItem(TX_PAGINATION_STORAGE_KEY);
    if (rawPagination) {
      const parsedPagination = JSON.parse(rawPagination);
      state.txPagination = {
        ...state.txPagination,
        ...parsedPagination,
      };
    }
  } catch {
    // Ignore malformed storage and keep defaults.
  }

  el.txFilterSearch.value = state.txFilters.search;
  el.txFilterStartDate.value = state.txFilters.startDate;
  el.txFilterEndDate.value = state.txFilters.endDate;
  el.txFilterType.value = state.txFilters.type;
  el.txFilterAttachment.value = state.txFilters.attachment;
  el.txFilterSort.value = state.txFilters.sort;
  el.txPageSize.value = String(state.txPagination.pageSize || 25);
}

async function loadBudgets() {
  const monthLabel = new Date().toISOString().slice(0, 7);
  const rawBudgets = await api(`/budgets/?month=${monthLabel}`);
  state.budgetTargets = rawBudgets;
  
  // Load budget health metrics for the current month
  const rawHealthMetrics = await api(`/budgets/${monthLabel}/health`);
  state.budgetHealthMetrics = rawHealthMetrics;
}

async function saveBudget(budgetData) {
  const response = await api("/budgets/", {
    method: "POST",
    body: JSON.stringify(budgetData),
  });
  return response;
}

async function deleteBudget(budgetId) {
  await api(`/budgets/${budgetId}`, {
    method: "DELETE",
  });
}

async function loadCashFlowForecast() {
  state.cashFlowForecast = await api("/reports/cash-flow?months_history=6&months_forecast=1");
}

function populateDashboardFilterOptions() {
  const selectedCategory = state.dashboardFilters.categoryId;
  const selectedMinistry = state.dashboardFilters.ministryId;

  el.dashCategoryFilter.innerHTML = "<option value=''>Todas</option>";
  for (const cat of [...state.categories].sort((a, b) => a.name.localeCompare(b.name, "pt-BR"))) {
    const option = document.createElement("option");
    option.value = String(cat.id);
    option.textContent = cat.name;
    el.dashCategoryFilter.appendChild(option);
  }

  el.dashMinistryFilter.innerHTML = "<option value=''>Todos</option>";
  for (const ministry of [...state.ministries].sort((a, b) => a.name.localeCompare(b.name, "pt-BR"))) {
    const option = document.createElement("option");
    option.value = String(ministry.id);
    option.textContent = ministry.name;
    el.dashMinistryFilter.appendChild(option);
  }

  el.dashCategoryFilter.value = selectedCategory || "";
  el.dashMinistryFilter.value = selectedMinistry || "";
}

function ensureSelectHasOption(selectNode, value) {
  if (!value) {
    return;
  }
  const exists = Array.from(selectNode.options).some((opt) => opt.value === value);
  if (!exists) {
    const option = document.createElement("option");
    option.value = value;
    option.textContent = value;
    selectNode.appendChild(option);
  }
}

function populateBankDropdowns() {
  const selectedTx = el.txBankName.value;
  const selectedEdit = el.editTxBankName.value;
  const selectedDash = state.dashboardFilters.bank || el.dashBankFilter.value;
  const banks = new Set();

  for (const tx of state.transactionsRaw) {
    const bank = String(tx.source_bank || tx.source_bank_name || "").trim();
    if (bank) {
      banks.add(bank);
    }
  }

  el.txBankName.innerHTML = "<option value=''>Nao informado</option>";
  el.editTxBankName.innerHTML = "<option value=''>Nao informado</option>";
  el.dashBankFilter.innerHTML = "<option value=''>Todos</option>";

  for (const bank of [...banks].sort((a, b) => a.localeCompare(b, "pt-BR"))) {
    const optionTx = document.createElement("option");
    optionTx.value = bank;
    optionTx.textContent = bank;
    el.txBankName.appendChild(optionTx);

    const optionEdit = document.createElement("option");
    optionEdit.value = bank;
    optionEdit.textContent = bank;
    el.editTxBankName.appendChild(optionEdit);

    const optionDash = document.createElement("option");
    optionDash.value = bank;
    optionDash.textContent = bank;
    el.dashBankFilter.appendChild(optionDash);
  }

  ensureSelectHasOption(el.txBankName, selectedTx);
  ensureSelectHasOption(el.editTxBankName, selectedEdit);
  ensureSelectHasOption(el.dashBankFilter, selectedDash);

  el.txBankName.value = selectedTx || "";
  el.editTxBankName.value = selectedEdit || "";
  el.dashBankFilter.value = selectedDash || "";
}

function populateBudgetReferenceOptions() {
  const currentRef = el.dashBudgetRef.value;
  const type = el.dashBudgetType.value;
  const source = type === "ministry" ? state.ministries : state.categories;

  el.dashBudgetRef.innerHTML = "";
  for (const item of [...source].sort((a, b) => a.name.localeCompare(b.name, "pt-BR"))) {
    if (type === "category" && item.type === "income") {
      continue;
    }
    const option = document.createElement("option");
    option.value = String(item.id);
    option.textContent = item.name;
    el.dashBudgetRef.appendChild(option);
  }

  if (currentRef) {
    el.dashBudgetRef.value = currentRef;
  }
}

function syncDashboardFiltersFromUi() {
  state.dashboardFilters.startDate = el.dashStartDate.value;
  state.dashboardFilters.endDate = el.dashEndDate.value;
  state.dashboardFilters.type = el.dashTypeFilter.value;
  state.dashboardFilters.categoryId = el.dashCategoryFilter.value;
  state.dashboardFilters.ministryId = el.dashMinistryFilter.value;
  state.dashboardFilters.bank = el.dashBankFilter.value;
}

function resetDashboardFilters() {
  state.dashboardFilters = {
    startDate: "",
    endDate: "",
    type: "",
    categoryId: "",
    ministryId: "",
    bank: "",
  };

  el.dashStartDate.value = "";
  el.dashEndDate.value = "";
  el.dashTypeFilter.value = "";
  el.dashCategoryFilter.value = "";
  el.dashMinistryFilter.value = "";
  el.dashBankFilter.value = "";
  renderDashboard();
}

function getDashboardFilteredTransactions() {
  const f = state.dashboardFilters;
  const bankSearch = normalizeText(f.bank);

  return state.transactionsRaw.filter((tx) => {
    if (f.startDate && tx.transaction_date < f.startDate) return false;
    if (f.endDate && tx.transaction_date > f.endDate) return false;
    if (f.type && tx.transaction_type !== f.type) return false;
    if (f.categoryId && String(tx.category_id || "") !== String(f.categoryId)) return false;
    if (f.ministryId && String(tx.ministry_id || "") !== String(f.ministryId)) return false;
    if (bankSearch && normalizeText(tx.source_bank || tx.source_bank_name || "") !== bankSearch) return false;
    return true;
  });
}

function renderTopList(targetNode, rows, emptyMessage, labelBuilder) {
  targetNode.innerHTML = "";
  for (const row of rows) {
    const li = document.createElement("li");
    li.textContent = labelBuilder(row);
    targetNode.appendChild(li);
  }
  if (!rows.length) {
    const li = document.createElement("li");
    li.textContent = emptyMessage;
    targetNode.appendChild(li);
  }
}

function renderMonthlyBars(trendRows) {
  el.dashMonthlyBars.innerHTML = "";
  if (!trendRows.length) {
    const empty = document.createElement("div");
    empty.className = "month-bar-label";
    empty.textContent = "Sem dados mensais para exibir grafico.";
    el.dashMonthlyBars.appendChild(empty);
    return;
  }

  const maxValue = Math.max(
    ...trendRows.map((row) => Math.max(Number(row.income || 0), Number(row.expense || 0))),
    1,
  );

  for (const row of trendRows) {
    const incomeWidth = (Number(row.income || 0) / maxValue) * 100;
    const expenseWidth = (Number(row.expense || 0) / maxValue) * 100;
    const wrap = document.createElement("div");
    wrap.className = "month-bar-row";
    wrap.innerHTML = `
      <span class="month-bar-label">${row.month.slice(5)}/${row.month.slice(2, 4)}</span>
      <div>
        <div class="month-bar-track" title="Entrada ${brl(row.income)}">
          <div class="month-bar-income" style="width:${incomeWidth.toFixed(1)}%"></div>
        </div>
        <div class="month-bar-track" style="margin-top:4px" title="Saida ${brl(row.expense)}">
          <div class="month-bar-expense" style="width:${expenseWidth.toFixed(1)}%"></div>
        </div>
      </div>
    `;
    el.dashMonthlyBars.appendChild(wrap);
  }
}

function renderLineChart(trendRows) {
  if (!trendRows.length) {
    el.dashLineChart.innerHTML = "<div class='month-bar-label'>Sem dados para grafico de linha.</div>";
    return;
  }

  const metric = el.dashLineMetric.value || "balance";
  const metricLabel = metric === "income" ? "Entradas" : metric === "expense" ? "Saidas" : "Saldo";
  const points = trendRows.map((row) => ({
    label: row.month,
    value:
      metric === "income"
        ? Number(row.income || 0)
        : metric === "expense"
          ? Number(row.expense || 0)
          : Number(row.income || 0) - Number(row.expense || 0),
  }));

  const minY = Math.min(...points.map((p) => p.value), 0);
  const maxY = Math.max(...points.map((p) => p.value), 0);
  const range = Math.max(maxY - minY, 1);

  const width = 720;
  const height = 240;
  const padX = 44;
  const padY = 24;
  const chartW = width - padX * 2;
  const chartH = height - padY * 2;

  const toX = (idx) => padX + (points.length === 1 ? chartW / 2 : (idx / (points.length - 1)) * chartW);
  const toY = (val) => padY + chartH - ((val - minY) / range) * chartH;

  const path = points.map((p, i) => `${i === 0 ? "M" : "L"}${toX(i).toFixed(1)},${toY(p.value).toFixed(1)}`).join(" ");
  const zeroY = toY(0).toFixed(1);

  const circles = points.map((p, i) => `
    <circle class="line-point" data-idx="${i}" cx="${toX(i).toFixed(1)}" cy="${toY(p.value).toFixed(1)}" r="5" fill="#1565c0" stroke="#fff" stroke-width="2"></circle>
  `).join("");

  const labels = points.map((p, i) => `
    <text x="${toX(i).toFixed(1)}" y="${(height - 6).toFixed(1)}" text-anchor="middle" font-size="11" fill="#5a6f88">${p.label.slice(5)}</text>
  `).join("");

  el.dashLineChart.innerHTML = `
    <svg viewBox="0 0 ${width} ${height}" width="100%" height="250" role="img" aria-label="Evolucao mensal do saldo">
      <line x1="${padX}" y1="${zeroY}" x2="${width - padX}" y2="${zeroY}" stroke="#cbd9ea" stroke-dasharray="4 3"></line>
      <path d="${path}" fill="none" stroke="#1565c0" stroke-width="3" stroke-linecap="round" stroke-linejoin="round"></path>
      ${circles}
      ${labels}
    </svg>
  `;

  const pointNodes = el.dashLineChart.querySelectorAll(".line-point");
  for (const node of pointNodes) {
    const idx = Number(node.getAttribute("data-idx") || 0);
    const point = points[idx];
    node.addEventListener("mousemove", (event) => {
      el.dashLineTooltip.textContent = `${point.label} | ${metricLabel}: ${brl(point.value)}`;
      el.dashLineTooltip.classList.remove("hide");

      const pointRect = event.currentTarget.getBoundingClientRect();
      const anchorX = pointRect.left + pointRect.width / 2;
      const anchorY = pointRect.top + pointRect.height / 2;
      const container = el.dashLineTooltip.parentElement;
      positionTooltipInContainer(el.dashLineTooltip, container, anchorX, anchorY, 12, -24);
    });
    node.addEventListener("mouseleave", () => {
      el.dashLineTooltip.classList.add("hide");
    });
  }
}

function renderExpensePie(categoryTotals) {
  const entries = [...categoryTotals.entries()]
    .sort((a, b) => b[1] - a[1])
    .slice(0, 5);
  const total = entries.reduce((sum, [, value]) => sum + Number(value || 0), 0);

  if (total <= 0) {
    el.dashExpensePie.style.background = "conic-gradient(#dde7f5 0deg 360deg)";
    el.dashExpensePieCenter.textContent = "Sem despesas";
    el.dashExpensePieLegend.innerHTML = "<li>Sem despesas para compor grafico.</li>";
    el.dashPieTooltip.classList.add("hide");
    return;
  }

  const palette = ["#1565c0", "#0a8f72", "#f39c12", "#8e44ad", "#e74c3c"];
  let acc = 0;
  const segments = [];
  const segmentData = [];
  const legendRows = [];

  entries.forEach(([name, value], index) => {
    const pct = (Number(value || 0) / total) * 100;
    const start = acc;
    const end = acc + pct;
    const color = palette[index % palette.length];
    segments.push(`${color} ${(start * 3.6).toFixed(2)}deg ${(end * 3.6).toFixed(2)}deg`);
    segmentData.push({ name, value: Number(value || 0), pct, startDeg: start * 3.6, endDeg: end * 3.6, color });
    legendRows.push(`<li><span style="color:${color}">●</span> ${name}: ${pct.toFixed(1)}%</li>`);
    acc = end;
  });

  el.dashExpensePie.style.background = `conic-gradient(${segments.join(", ")})`;
  el.dashExpensePieCenter.textContent = `Total\n${brl(total)}`;
  el.dashExpensePieLegend.innerHTML = legendRows.join("");

  el.dashExpensePie.onmousemove = (event) => {
    const rect = el.dashExpensePie.getBoundingClientRect();
    const x = event.clientX - rect.left - rect.width / 2;
    const y = event.clientY - rect.top - rect.height / 2;
    const angle = (Math.atan2(y, x) * 180) / Math.PI;
    const deg = (angle + 450) % 360;
    const match = segmentData.find((seg) => deg >= seg.startDeg && deg <= seg.endDeg);
    if (!match) {
      el.dashPieTooltip.classList.add("hide");
      return;
    }
    el.dashPieTooltip.textContent = `${match.name}: ${brl(match.value)} (${match.pct.toFixed(1)}%)`;
    el.dashPieTooltip.classList.remove("hide");

    const midDeg = (match.startDeg + match.endDeg) / 2;
    const rad = ((midDeg - 90) * Math.PI) / 180;
    const radius = rect.width * 0.36;
    const anchorX = rect.left + rect.width / 2 + Math.cos(rad) * radius;
    const anchorY = rect.top + rect.height / 2 + Math.sin(rad) * radius;
    const container = el.dashPieTooltip.parentElement;
    positionTooltipInContainer(el.dashPieTooltip, container, anchorX, anchorY, 14, -10);
  };
  el.dashExpensePie.onmouseleave = () => {
    el.dashPieTooltip.classList.add("hide");
  };
}

function renderBankBars(rows) {
  const bankTotals = new Map();

  for (const tx of rows) {
    const bank = (tx.source_bank || tx.source_bank_name || "Nao informado").trim() || "Nao informado";
    const current = bankTotals.get(bank) || { income: 0, expense: 0 };
    const amount = Number(tx.amount || 0);
    if (tx.transaction_type === "income") {
      current.income += amount;
    } else {
      current.expense += amount;
    }
    bankTotals.set(bank, current);
  }

  const rowsByBank = [...bankTotals.entries()]
    .map(([bank, totals]) => ({ bank, ...totals, volume: totals.income + totals.expense }))
    .sort((a, b) => b.volume - a.volume)
    .slice(0, 8);

  el.dashBankBars.innerHTML = "";
  if (!rowsByBank.length) {
    el.dashBankBars.innerHTML = "<div class='bank-bar-row'>Sem movimentacoes por banco no periodo.</div>";
    return;
  }

  const maxValue = Math.max(...rowsByBank.map((item) => Math.max(item.income, item.expense)), 1);

  for (const item of rowsByBank) {
    const incomeWidth = (item.income / maxValue) * 100;
    const expenseWidth = (item.expense / maxValue) * 100;
    const rowNode = document.createElement("div");
    rowNode.className = "bank-bar-row clickable";
    rowNode.title = `Abrir lancamentos filtrados por banco: ${item.bank}`;
    rowNode.innerHTML = `
      <div class="bank-bar-head">
        <strong>${item.bank}</strong>
        <span>Entrada ${brl(item.income)} | Saida ${brl(item.expense)}</span>
      </div>
      <div class="bank-bar-tracks">
        <div class="bank-bar-track" title="Entrada ${brl(item.income)}">
          <div class="bank-bar-fill-income" style="width:${incomeWidth.toFixed(1)}%"></div>
        </div>
        <div class="bank-bar-track" title="Saida ${brl(item.expense)}">
          <div class="bank-bar-fill-expense" style="width:${expenseWidth.toFixed(1)}%"></div>
        </div>
      </div>
    `;
    rowNode.addEventListener("click", () => {
      openTransactionsWithFilters({
        search: item.bank,
        startDate: state.dashboardFilters.startDate || "",
        endDate: state.dashboardFilters.endDate || "",
      });
      setMessage(el.txMessage, `Filtro aplicado para banco: ${item.bank}`);
    });
    el.dashBankBars.appendChild(rowNode);
  }
}

function buildLastMonthKeys(monthCount = 6) {
  const keys = [];
  const now = new Date();
  for (let i = monthCount - 1; i >= 0; i -= 1) {
    const date = new Date(now.getFullYear(), now.getMonth() - i, 1);
    const key = `${date.getFullYear()}-${String(date.getMonth() + 1).padStart(2, "0")}`;
    keys.push(key);
  }
  return keys;
}

function formatDeltaPercent(current, previous) {
  if (previous === 0 && current === 0) {
    return "0.0%";
  }
  if (previous === 0) {
    return "novo";
  }
  const delta = ((current - previous) / Math.abs(previous)) * 100;
  return `${delta >= 0 ? "+" : ""}${delta.toFixed(1)}%`;
}

function deltaClass(deltaText) {
  if (deltaText === "novo") {
    return "delta-up";
  }
  return deltaText.startsWith("+") ? "delta-up" : "delta-down";
}

function renderSixMonthComparison(series) {
  el.dashSixMonthComparison.innerHTML = "";
  if (!series.length) {
    const li = document.createElement("li");
    li.textContent = "Sem dados para comparar.";
    el.dashSixMonthComparison.appendChild(li);
    return;
  }

  for (let i = 0; i < series.length; i += 1) {
    const current = series[i];
    const previous = i > 0 ? series[i - 1] : null;
    const incomeDelta = previous ? formatDeltaPercent(current.income, previous.income) : "base";
    const expenseDelta = previous ? formatDeltaPercent(current.expense, previous.expense) : "base";
    const balanceDelta = previous
      ? formatDeltaPercent(current.income - current.expense, previous.income - previous.expense)
      : "base";

    const li = document.createElement("li");
    li.className = "comparison-item";
    li.innerHTML = `
      <strong>${current.month}</strong>
      <div class="comparison-metrics">
        <span>Entrada: ${brl(current.income)} <span class="${incomeDelta === "base" ? "" : deltaClass(incomeDelta)}">(${incomeDelta})</span></span>
        <span>Saida: ${brl(current.expense)} <span class="${expenseDelta === "base" ? "" : deltaClass(expenseDelta)}">(${expenseDelta})</span></span>
        <span>Saldo: ${brl(current.income - current.expense)} <span class="${balanceDelta === "base" ? "" : deltaClass(balanceDelta)}">(${balanceDelta})</span></span>
      </div>
    `;
    el.dashSixMonthComparison.appendChild(li);
  }
}

function openTransactionsWithFilters(nextFilters) {
  setActiveView("transactionsView");
  state.txFilters = {
    ...state.txFilters,
    ...nextFilters,
  };
  state.txPagination.page = 1;

  el.txFilterSearch.value = state.txFilters.search || "";
  el.txFilterStartDate.value = state.txFilters.startDate || "";
  el.txFilterEndDate.value = state.txFilters.endDate || "";
  el.txFilterType.value = state.txFilters.type || "";
  el.txFilterCategory.value = state.txFilters.categoryId || "";
  el.txFilterMinistry.value = state.txFilters.ministryId || "";
  el.txFilterAttachment.value = state.txFilters.attachment || "";
  el.txFilterSort.value = state.txFilters.sort || "date_desc";

  saveTransactionFilterState();
  renderTransactions();
}

function openPayablesWithFilters(nextFilters) {
  setActiveView("payablesView");
  state.payableFilters = {
    ...state.payableFilters,
    ...nextFilters,
  };

  el.payableFilterSearch.value = state.payableFilters.search || "";
  el.payableFilterStatus.value = state.payableFilters.status || "";
  el.payableFilterStartDate.value = state.payableFilters.startDate || "";
  el.payableFilterEndDate.value = state.payableFilters.endDate || "";

  renderPayables();
}

function openReceivablesWithFilters(nextFilters) {
  setActiveView("receivablesView");
  state.receivableFilters = {
    ...state.receivableFilters,
    ...nextFilters,
  };

  el.receivableFilterSearch.value = state.receivableFilters.search || "";
  el.receivableFilterStatus.value = state.receivableFilters.status || "";
  el.receivableFilterStartDate.value = state.receivableFilters.startDate || "";
  el.receivableFilterEndDate.value = state.receivableFilters.endDate || "";

  renderReceivables();
}

function renderBudgetAndAlerts(rows, categoryTotals, ministryTotals) {
  el.dashBudgetList.innerHTML = "";

  // Use health metrics from API if available
  if (state.budgetHealthMetrics && state.budgetHealthMetrics.length > 0) {
    for (const health of state.budgetHealthMetrics) {
      const li = document.createElement("li");
      li.className = "comparison-item";
      
      // Color-code based on alert level
      const alertClass = health.alert_level === "critical" ? "alert-high" : 
                        health.alert_level === "warning" ? "alert-medium" : "alert-low";
      li.classList.add(alertClass);
      
      li.innerHTML = `
        <strong>${health.budget_type === "category" ? "Categoria" : "Ministerio"}: ${health.reference_name}</strong>
        <div class="comparison-metrics">
          <span>Meta: ${brl(health.target_amount)} | Realizado: ${brl(health.spent_amount)}</span>
          <span class="${health.percent_spent >= 100 ? "delta-down" : "delta-up"}">${health.percent_spent.toFixed(1)}% consumido</span>
        </div>
      `;

      const removeBtn = document.createElement("button");
      removeBtn.className = "btn ghost btn-mini";
      removeBtn.type = "button";
      removeBtn.textContent = "Remover meta";
      removeBtn.addEventListener("click", async () => {
        try {
          const confirmed = await openConfirmModal("Tem certeza que deseja remover esta meta?", "Remover meta");
          if (!confirmed) {
            return;
          }
          await deleteBudget(health.budget_id);
          setMessage(el.dashBudgetMessage, "Meta removida com sucesso.");
          await loadBudgets();
          renderDashboard();
        } catch (error) {
          setMessage(el.dashBudgetMessage, error.message, true);
        }
      });
      li.appendChild(removeBtn);
      el.dashBudgetList.appendChild(li);
    }
  }

  if (!state.budgetHealthMetrics || state.budgetHealthMetrics.length === 0) {
    el.dashBudgetList.innerHTML = "<li class='comparison-item alert-low'>Nenhuma meta cadastrada para o mes atual.</li>";
  }

  const alerts = [];
  const uncategorized = rows.filter((tx) => tx.transaction_type === "expense" && !tx.category_id).length;
  if (uncategorized > 0) alerts.push({ level: "high", text: `${uncategorized} despesa(s) sem categoria.` });

  const noMinistry = rows.filter((tx) => tx.transaction_type === "expense" && !tx.ministry_id).length;
  if (noMinistry > 0) alerts.push({ level: "medium", text: `${noMinistry} despesa(s) sem ministerio.` });

  const noAttachment = rows.filter((tx) => tx.transaction_type === "expense" && (Number(tx.attachment_count || 0) <= 0 && tx.has_attachments !== true)).length;
  if (noAttachment > 0) alerts.push({ level: "low", text: `${noAttachment} despesa(s) sem anexo.` });

  for (const health of state.budgetHealthMetrics || []) {
    if (health.alert_level === "critical") {
      alerts.push({
        level: "high",
        text: `Meta estourada em ${health.reference_name}: ${brl(health.spent_amount)} de ${brl(health.target_amount)}.`,
      });
    } else if (health.alert_level === "warning") {
      alerts.push({
        level: "medium",
        text: `Meta em alerta em ${health.reference_name}: ${brl(health.spent_amount)} de ${brl(health.target_amount)}.`,
      });
    }
  }

  if (Number(state.payableAlertsSummary.overdue || 0) > 0) {
    alerts.push({ level: "high", text: `${state.payableAlertsSummary.overdue} conta(s) vencida(s) aguardando pagamento.` });
  }
  if (Number(state.payableAlertsSummary.due_today || 0) > 0) {
    alerts.push({ level: "medium", text: `${state.payableAlertsSummary.due_today} conta(s) vencem hoje.` });
  }
  if (Number(state.payableAlertsSummary.due_in_3_days || 0) > 0) {
    alerts.push({ level: "medium", text: `${state.payableAlertsSummary.due_in_3_days} conta(s) vencem em ate 3 dias.` });
  }
  if (Number(state.payableAlertsSummary.due_in_7_days || 0) > 0) {
    alerts.push({ level: "low", text: `${state.payableAlertsSummary.due_in_7_days} conta(s) vencem em ate 7 dias.` });
  }

  if (Number(state.receivableAlertsSummary.overdue || 0) > 0) {
    alerts.push({ level: "medium", text: `${state.receivableAlertsSummary.overdue} conta(s) a receber vencida(s).` });
  }
  if (Number(state.receivableAlertsSummary.due_today || 0) > 0) {
    alerts.push({ level: "low", text: `${state.receivableAlertsSummary.due_today} conta(s) a receber vencem hoje.` });
  }
  if (Number(state.receivableAlertsSummary.due_in_3_days || 0) > 0) {
    alerts.push({ level: "low", text: `${state.receivableAlertsSummary.due_in_3_days} conta(s) a receber em ate 3 dias.` });
  }

  el.dashAlertsList.innerHTML = "";
  if (!alerts.length) {
    el.dashAlertsList.innerHTML = "<li class='comparison-item alert-low'>Sem alertas criticos no periodo atual.</li>";
    return;
  }

  for (const alert of alerts) {
    const li = document.createElement("li");
    li.className = `comparison-item alert-${alert.level}`;
    li.textContent = alert.text;
    el.dashAlertsList.appendChild(li);
  }
}

function renderPayablesKpi() {
  const summary = state.payableAlertsSummary || {
    overdue: 0,
    due_today: 0,
    due_in_3_days: 0,
    due_in_7_days: 0,
    pending_total: 0,
  };

  const pendingCount = Number(summary.pending_total || 0);
  const overdueCount = Number(summary.overdue || 0);

  el.kpiPayablesPending.textContent = String(pendingCount);
  el.kpiPayablesOverdue.textContent = String(overdueCount);
}

function renderDashboard() {
  const rows = getDashboardFilteredTransactions();

  let income = 0;
  let expense = 0;
  let fixedExpense = 0;
  let withAttachment = 0;
  const categoryTotals = new Map();
  const ministryTotals = new Map();
  const monthlyTotals = new Map();

  for (const tx of rows) {
    const amount = Number(tx.amount || 0);
    if (tx.transaction_type === "income") {
      income += amount;
    } else {
      expense += amount;
      if (tx.expense_profile === "fixed") {
        fixedExpense += amount;
      }
    }

    const hasAttachment = Number(tx.attachment_count || 0) > 0 || tx.has_attachments === true;
    if (hasAttachment) {
      withAttachment += 1;
    }

    if (tx.transaction_type === "expense") {
      const categoryName = tx.category?.name || "Sem categoria";
      categoryTotals.set(categoryName, (categoryTotals.get(categoryName) || 0) + amount);
    }

    if (tx.transaction_type === "expense" && tx.ministry?.name) {
      const ministryName = tx.ministry.name;
      ministryTotals.set(ministryName, (ministryTotals.get(ministryName) || 0) + amount);
    }

    const monthKey = String(tx.transaction_date || "").slice(0, 7);
    if (monthKey.length === 7) {
      const current = monthlyTotals.get(monthKey) || { income: 0, expense: 0 };
      if (tx.transaction_type === "income") {
        current.income += amount;
      } else {
        current.expense += amount;
      }
      monthlyTotals.set(monthKey, current);
    }
  }

  const balance = income - expense;
  const volume = income + expense;
  const incomePct = volume > 0 ? (income / volume) * 100 : 0;
  const expensePct = volume > 0 ? (expense / volume) * 100 : 0;
  const fixedPct = expense > 0 ? (fixedExpense / expense) * 100 : 0;
  const attachmentPct = rows.length > 0 ? (withAttachment / rows.length) * 100 : 0;

  el.kpiIncome.textContent = brl(income);
  el.kpiExpense.textContent = brl(expense);
  el.kpiBalance.textContent = brl(balance);
  el.dashIncomeBar.style.width = `${incomePct.toFixed(1)}%`;
  el.dashExpenseBar.style.width = `${expensePct.toFixed(1)}%`;
  el.dashIncomePercent.textContent = `${incomePct.toFixed(1)}%`;
  el.dashExpensePercent.textContent = `${expensePct.toFixed(1)}%`;
  el.dashResultCount.textContent = `Base: ${rows.length} lancamento(s)`;
  el.dashEfficiencyNote.textContent = `Despesas fixas: ${fixedPct.toFixed(1)}% das saidas | Com anexo: ${attachmentPct.toFixed(1)}%`;

  const topCategories = [...categoryTotals.entries()]
    .sort((a, b) => b[1] - a[1])
    .slice(0, 5)
    .map(([name, total]) => ({ name, total }));
  el.dashTopCategories.innerHTML = "";
  for (const row of topCategories) {
    const li = document.createElement("li");
    const cat = state.categories.find((item) => item.name === row.name);
    const btn = document.createElement("button");
    btn.type = "button";
    btn.textContent = `${row.name}: ${brl(row.total)}`;
    btn.addEventListener("click", () => {
      openTransactionsWithFilters({
        type: "expense",
        categoryId: cat ? String(cat.id) : "",
      });
    });
    li.appendChild(btn);
    el.dashTopCategories.appendChild(li);
  }
  if (!topCategories.length) {
    el.dashTopCategories.innerHTML = "<li>Sem despesas por categoria no periodo.</li>";
  }

  const topMinistries = [...ministryTotals.entries()]
    .sort((a, b) => b[1] - a[1])
    .slice(0, 5)
    .map(([name, total]) => ({ name, total }));
  el.dashTopMinistries.innerHTML = "";
  for (const row of topMinistries) {
    const li = document.createElement("li");
    const ministry = state.ministries.find((item) => item.name === row.name);
    const btn = document.createElement("button");
    btn.type = "button";
    btn.textContent = `${row.name}: ${brl(row.total)}`;
    btn.addEventListener("click", () => {
      openTransactionsWithFilters({
        type: "expense",
        ministryId: ministry ? String(ministry.id) : "",
      });
    });
    li.appendChild(btn);
    el.dashTopMinistries.appendChild(li);
  }
  if (!topMinistries.length) {
    el.dashTopMinistries.innerHTML = "<li>Sem despesas por ministerio no periodo.</li>";
  }

  const lastMonthKeys = buildLastMonthKeys(6);
  const trendRows = lastMonthKeys.map((month) => {
    const totals = monthlyTotals.get(month) || { income: 0, expense: 0 };
    return { month, income: totals.income, expense: totals.expense };
  });
  
  // Store for use in metric change listener
  state.dashboardTrendRows = trendRows;
  
  renderLineChart(trendRows);
  renderMonthlyBars(trendRows);
  el.dashMonthlyTrend.innerHTML = "";
  for (const row of trendRows) {
    const li = document.createElement("li");
    const btn = document.createElement("button");
    btn.type = "button";
    btn.textContent = `${row.month}: Entrada ${brl(row.income)} | Saida ${brl(row.expense)} | Saldo ${brl(row.income - row.expense)}`;
    btn.addEventListener("click", () => {
      openTransactionsWithFilters({
        startDate: `${row.month}-01`,
        endDate: `${row.month}-31`,
      });
    });
    li.appendChild(btn);
    el.dashMonthlyTrend.appendChild(li);
  }
  if (!trendRows.length) {
    el.dashMonthlyTrend.innerHTML = "<li>Sem dados mensais no periodo.</li>";
  }
  renderSixMonthComparison(trendRows);
  renderExpensePie(categoryTotals);
  renderBankBars(rows);
  renderBudgetAndAlerts(rows, categoryTotals, ministryTotals);
  renderPayablesKpi();
  renderReceivablesKpi();

  const now = new Date();
  const dayOfMonth = now.getDate();
  const currentMonth = now.toISOString().slice(0, 7);
  const cashFlow = state.cashFlowForecast;
  const currentFromApi = cashFlow?.current_month?.month === currentMonth ? cashFlow.current_month : null;
  const nextForecast = Array.isArray(cashFlow?.forecast) && cashFlow.forecast.length ? cashFlow.forecast[0] : null;

  if (currentFromApi && nextForecast) {
    const projectedIncome = Number(currentFromApi.income || 0) + Math.max(Number(nextForecast.projected_net || 0), 0);
    const projectedExpense = Number(currentFromApi.expense || 0) + Math.max(-Number(nextForecast.projected_net || 0), 0);
    const projectedBalance = projectedIncome - projectedExpense;

    el.dashProjectedIncome.textContent = brl(projectedIncome);
    el.dashProjectedExpense.textContent = brl(projectedExpense);
    el.dashProjectedBalance.textContent = brl(projectedBalance);
    el.dashProjectionNote.textContent = `Base ate ${String(dayOfMonth).padStart(2, "0")}/${String(now.getMonth() + 1).padStart(2, "0")} + tendencia media: ${brl(Number(cashFlow.average_net_last_months || 0))}.`;
  } else {
    let currentIncome = 0;
    let currentExpense = 0;
    for (const tx of rows) {
      if (String(tx.transaction_date || "").startsWith(currentMonth)) {
        const amount = Number(tx.amount || 0);
        if (tx.transaction_type === "income") {
          currentIncome += amount;
        } else {
          currentExpense += amount;
        }
      }
    }

    const daysInMonth = new Date(now.getFullYear(), now.getMonth() + 1, 0).getDate();
    const elapsedRatio = Math.max(1 / daysInMonth, dayOfMonth / daysInMonth);
    const projectedIncome = currentIncome / elapsedRatio;
    const projectedExpense = currentExpense / elapsedRatio;
    const projectedBalance = projectedIncome - projectedExpense;

    el.dashProjectedIncome.textContent = brl(projectedIncome);
    el.dashProjectedExpense.textContent = brl(projectedExpense);
    el.dashProjectedBalance.textContent = brl(projectedBalance);

    if (currentIncome === 0 && currentExpense === 0) {
      el.dashProjectionNote.textContent = "Sem dados do mes atual dentro dos filtros para projetar fechamento.";
    } else {
      el.dashProjectionNote.textContent = `Base ate ${String(dayOfMonth).padStart(2, "0")}/${String(now.getMonth() + 1).padStart(2, "0")}: Entrada ${brl(currentIncome)} | Saida ${brl(currentExpense)}.`;
    }
  }

  setMessage(el.dashboardMessage, "Dashboard gerencial atualizado.");
}

function syncTransactionFiltersFromUi() {
  state.txFilters.search = el.txFilterSearch.value.trim();
  state.txFilters.startDate = el.txFilterStartDate.value;
  state.txFilters.endDate = el.txFilterEndDate.value;
  state.txFilters.type = el.txFilterType.value;
  state.txFilters.categoryId = el.txFilterCategory.value;
  state.txFilters.ministryId = el.txFilterMinistry.value;
  state.txFilters.attachment = el.txFilterAttachment.value;
  state.txFilters.sort = el.txFilterSort.value;
  state.txPagination.page = 1;
  saveTransactionFilterState();
}

function resetTransactionFilters() {
  state.txFilters = {
    search: "",
    startDate: "",
    endDate: "",
    type: "",
    categoryId: "",
    ministryId: "",
    attachment: "",
    sort: "date_desc",
  };
  state.txPagination = {
    page: 1,
    pageSize: Number(el.txPageSize.value || 25),
  };

  el.txFilterSearch.value = "";
  el.txFilterStartDate.value = "";
  el.txFilterEndDate.value = "";
  el.txFilterType.value = "";
  el.txFilterCategory.value = "";
  el.txFilterMinistry.value = "";
  el.txFilterAttachment.value = "";
  el.txFilterSort.value = "date_desc";

  saveTransactionFilterState();
  renderTransactions();
}

function renderTransactionFilterChips(filteredCount) {
  const chips = [];
  const f = state.txFilters;
  if (f.search) chips.push(`Busca: ${f.search}`);
  if (f.startDate) chips.push(`De: ${f.startDate}`);
  if (f.endDate) chips.push(`Ate: ${f.endDate}`);
  if (f.type) chips.push(`Tipo: ${f.type === "income" ? "Entrada" : "Saida"}`);
  if (f.categoryId) {
    const cat = state.categories.find((c) => String(c.id) === String(f.categoryId));
    if (cat) chips.push(`Categoria: ${cat.name}`);
  }
  if (f.ministryId) {
    const ministry = state.ministries.find((m) => String(m.id) === String(f.ministryId));
    if (ministry) chips.push(`Ministerio: ${ministry.name}`);
  }
  if (f.attachment === "with") chips.push("Com anexo");
  if (f.attachment === "without") chips.push("Sem anexo");

  el.txFilterChips.innerHTML = "";
  for (const chipText of chips) {
    const chip = document.createElement("span");
    chip.className = "filter-chip";
    chip.textContent = chipText;
    el.txFilterChips.appendChild(chip);
  }
  el.txFilterResultCount.textContent = `Mostrando ${filteredCount} de ${state.transactionsRaw.length}`;
}

function getFilteredAndSortedTransactions() {
  const f = state.txFilters;
  const search = normalizeText(f.search);

  const filtered = state.transactionsRaw.filter((tx) => {
    if (f.startDate && tx.transaction_date < f.startDate) return false;
    if (f.endDate && tx.transaction_date > f.endDate) return false;
    if (f.type && tx.transaction_type !== f.type) return false;
    if (f.categoryId && String(tx.category_id || "") !== String(f.categoryId)) return false;
    if (f.ministryId && String(tx.ministry_id || "") !== String(f.ministryId)) return false;

    const hasAttachment = Number(tx.attachment_count || 0) > 0 || tx.has_attachments === true;
    if (f.attachment === "with" && !hasAttachment) return false;
    if (f.attachment === "without" && hasAttachment) return false;

    if (search) {
      const haystack = normalizeText([
        tx.description,
        tx.source_bank,
        tx.category?.name,
        tx.ministry?.name,
      ].join(" "));
      if (!haystack.includes(search)) return false;
    }
    return true;
  });

  filtered.sort((a, b) => {
    if (f.sort === "date_asc") {
      return String(a.transaction_date).localeCompare(String(b.transaction_date));
    }
    if (f.sort === "date_desc") {
      return String(b.transaction_date).localeCompare(String(a.transaction_date));
    }
    if (f.sort === "amount_asc") {
      return Number(a.amount) - Number(b.amount);
    }
    if (f.sort === "amount_desc") {
      return Number(b.amount) - Number(a.amount);
    }
    return 0;
  });

  return filtered;
}

function renderTransactions() {
  const filteredRows = getFilteredAndSortedTransactions();
  const pageSize = Number(state.txPagination.pageSize || 25);
  const totalPages = Math.max(1, Math.ceil(filteredRows.length / pageSize));
  if (state.txPagination.page > totalPages) {
    state.txPagination.page = totalPages;
  }
  if (state.txPagination.page < 1) {
    state.txPagination.page = 1;
  }

  const start = (state.txPagination.page - 1) * pageSize;
  const end = start + pageSize;
  const rows = filteredRows.slice(start, end);

  el.txTableBody.innerHTML = "";

  for (const tx of rows) {
    const tr = document.createElement("tr");
    const editBtn = `<button class="btn ghost" type="button" data-edit-tx="${tx.id}">Editar</button>`;
    const deleteBtn = `<button class="btn ghost" type="button" data-delete-tx="${tx.id}">Excluir</button>`;
    const attachmentCount = Number(tx.attachment_count || 0);
    const hasAttachment = attachmentCount > 0 || tx.has_attachments === true;
    const displayAttachmentCount = attachmentCount > 0 ? attachmentCount : 1;
    const attachmentIcon = hasAttachment
      ? `<span class="tx-attachment-badge" title="${displayAttachmentCount} anexo(s)" aria-label="${displayAttachmentCount} anexo(s)">&#128206; ${displayAttachmentCount}</span>`
      : "-";
    tr.innerHTML = `
      <td>${tx.transaction_date}</td>
      <td>${tx.description}</td>
      <td>${tx.transaction_type === "income" ? "Entrada" : "Saida"}</td>
      <td>${tx.source_bank || "-"}</td>
      <td>${tx.category?.name || "-"}</td>
      <td>${tx.transaction_type === "expense" ? (tx.ministry?.name || "-") : "-"}</td>
      <td>${tx.transaction_type === "expense" ? toExpenseProfileLabel(tx.expense_profile) : "-"}</td>
      <td>${brl(tx.amount)}</td>
      <td>${attachmentIcon}</td>
      <td>${editBtn} ${deleteBtn}</td>
    `;
    el.txTableBody.appendChild(tr);
  }

  for (const button of el.txTableBody.querySelectorAll("button[data-edit-tx]")) {
    button.addEventListener("click", async () => {
      await openEditTransactionModal(Number(button.getAttribute("data-edit-tx")));
    });
  }

  for (const button of el.txTableBody.querySelectorAll("button[data-delete-tx]")) {
    button.addEventListener("click", async () => {
      const txId = Number(button.getAttribute("data-delete-tx"));
      if (!txId) {
        return;
      }
      const confirmed = await openConfirmModal("Tem certeza que deseja excluir este lancamento?", "Excluir lancamento");
      if (!confirmed) {
        return;
      }
      try {
        await api(`/transactions/${txId}`, { method: "DELETE" });
        setMessage(el.txMessage, "Lancamento excluido com sucesso.");
        await Promise.all([
          loadTransactions(),
          loadSummary(),
          loadReports(),
          loadPayables(),
          loadPayablesAlertsSummary(),
          loadReceivables(),
          loadReceivablesAlertsSummary(),
        ]);
        renderDashboard();
      } catch (error) {
        const message = String(error?.message || "");
        if (message.includes("403")) {
          setMessage(el.txMessage, "Somente administrador pode excluir lancamentos.", true);
        } else {
          setMessage(el.txMessage, message || "Falha ao excluir lancamento.", true);
        }
      }
    });
  }

  if (!rows.length) {
    const tr = document.createElement("tr");
    tr.innerHTML = "<td colspan='10'>Nenhum resultado para os filtros atuais. <button class='btn ghost btn-mini' type='button' id='txEmptyResetBtn'>Limpar filtros</button></td>";
    el.txTableBody.appendChild(tr);
    const resetEmptyBtn = document.getElementById("txEmptyResetBtn");
    if (resetEmptyBtn) {
      resetEmptyBtn.addEventListener("click", resetTransactionFilters);
    }
  }

  updateTransactionSortHeaderLabels();
  renderTransactionFilterChips(filteredRows.length);
  el.txPageInfo.textContent = `Pag. ${state.txPagination.page}/${totalPages}`;
  el.txPagePrevBtn.disabled = state.txPagination.page <= 1;
  el.txPageNextBtn.disabled = state.txPagination.page >= totalPages;
  saveTransactionFilterState();
}

function isAnyModalOpen() {
  return !el.deleteCategoryModal.classList.contains("hide")
    || !el.attachmentPreviewModal.classList.contains("hide")
    || !el.editTransactionModal.classList.contains("hide")
    || !el.editPayableModal.classList.contains("hide")
    || !el.uploadResultModal.classList.contains("hide")
    || !el.payablePaidAtModal.classList.contains("hide");
}

function closePayablePaidAtModal(selectedPayload = null) {
  el.payablePaidAtModal.classList.add("hide");
  if (payablePaidAtResolver) {
    const resolver = payablePaidAtResolver;
    payablePaidAtResolver = null;
    resolver(selectedPayload);
  }
}

function openPayablePaidAtModal(defaultDate, defaultPaymentMethod = "") {
  el.payablePaidAtInput.value = defaultDate;
  el.payablePaidMethodInput.value = defaultPaymentMethod || "";
  el.payablePaidAtModal.classList.remove("hide");
  window.setTimeout(() => {
    el.payablePaidAtInput.focus();
    el.payablePaidAtInput.showPicker?.();
  }, 0);

  return new Promise((resolve) => {
    payablePaidAtResolver = resolve;
  });
}

function isTypingTarget(target) {
  if (!(target instanceof Element)) {
    return false;
  }
  return target.closest("input, textarea, select, [contenteditable='true']") !== null;
}

function categoryTypeLabel(value) {
  if (value === "income") {
    return "Receita";
  }
  if (value === "expense") {
    return "Despesa";
  }
  return "Ambos";
}

function findCategoryByName(name) {
  const typed = String(name || "").trim().toLowerCase();
  if (!typed) {
    return null;
  }
  return state.categories.find((cat) => cat.name.trim().toLowerCase() === typed) || null;
}

function clearCategoryForm() {
  state.editingCategoryId = null;
  el.categoryForm.reset();
  el.categoryType.value = "expense";
}

function openConfirmModal(message, confirmLabel = "Confirmar") {
  if (confirmModalResolver) {
    confirmModalResolver(false);
    confirmModalResolver = null;
  }
  el.deleteCategoryText.textContent = message;
  el.deleteCategoryConfirmBtn.textContent = confirmLabel;
  el.deleteCategoryModal.classList.remove("hide");
  return new Promise((resolve) => {
    confirmModalResolver = resolve;
  });
}

function closeConfirmModal(confirmed = false) {
  el.deleteCategoryModal.classList.add("hide");
  el.deleteCategoryText.textContent = "Tem certeza que deseja continuar?";
  el.deleteCategoryConfirmBtn.textContent = "Confirmar";
  if (confirmModalResolver) {
    const resolver = confirmModalResolver;
    confirmModalResolver = null;
    resolver(confirmed);
  }
}

function renderCategoryTable() {
  el.categoryTableBody.innerHTML = "";
  const ordered = [...state.categories].sort((a, b) => a.name.localeCompare(b.name, "pt-BR"));

  for (const cat of ordered) {
    const tr = document.createElement("tr");
    const deleteDisabled = cat.is_system ? "disabled" : "";
    const deleteTitle = cat.is_system ? "Categorias de sistema nao podem ser excluidas" : "Excluir categoria";
    tr.innerHTML = `
      <td>${cat.name}</td>
      <td>${categoryTypeLabel(cat.type)}</td>
      <td>${cat.description || "-"}</td>
      <td>${cat.is_system ? "Sim" : "Nao"}</td>
      <td>${cat.is_active ? "Sim" : "Nao"}</td>
      <td>
        <button class="btn ghost btn-mini" type="button" data-edit-category="${cat.id}">Editar</button>
        <button class="btn ghost btn-mini" type="button" data-delete-category="${cat.id}" ${deleteDisabled} title="${deleteTitle}">Excluir</button>
      </td>
    `;
    el.categoryTableBody.appendChild(tr);
  }

  if (!ordered.length) {
    const tr = document.createElement("tr");
    tr.innerHTML = "<td colspan='6'>Nenhuma categoria cadastrada.</td>";
    el.categoryTableBody.appendChild(tr);
  }
}

function renderTransactionCategoryOptions() {
  el.txCategoryOptions.innerHTML = "";
  const ordered = [...state.categories].sort((a, b) => a.name.localeCompare(b.name, "pt-BR"));
  for (const cat of ordered) {
    const option = document.createElement("option");
    option.value = cat.name;
    option.setAttribute("data-id", String(cat.id));
    el.txCategoryOptions.appendChild(option);
  }
}

function syncTransactionCategoryFromInput() {
  const match = findCategoryByName(el.txCategoryInput.value);
  el.txCategoryId.value = match ? String(match.id) : "";
}

async function createCategoryFromTransactionInput() {
  const name = el.txCategoryInput.value.trim();
  if (!name) {
    throw new Error("Digite o nome da categoria para adicionar.");
  }

  const alreadyExists = findCategoryByName(name);
  if (alreadyExists) {
    el.txCategoryId.value = String(alreadyExists.id);
    el.txCategoryInput.value = alreadyExists.name;
    return { category: alreadyExists, created: false };
  }

  const created = await api("/categories/", {
    method: "POST",
    body: JSON.stringify({
      name,
      type: el.txType.value === "income" ? "income" : "expense",
    }),
  });
  await loadCategories();
  el.txCategoryId.value = String(created.id);
  el.txCategoryInput.value = created.name;
  return { category: created, created: true };
}

function toExpenseProfileLabel(value) {
  if (value === "fixed") {
    return "Fixa";
  }
  if (value === "variable") {
    return "Variavel";
  }
  return "-";
}

function syncExpenseProfileField(typeSelect, expenseProfileSelect) {
  const isExpense = typeSelect.value === "expense";
  expenseProfileSelect.disabled = !isExpense;
  if (!isExpense) {
    expenseProfileSelect.value = "";
  }
}

function syncMinistryField(typeSelect, ministrySelect) {
  const isExpense = typeSelect.value === "expense";
  ministrySelect.disabled = !isExpense;
  if (!isExpense) {
    ministrySelect.value = "";
  }
}

function clearMinistryForm() {
  state.editingMinistryId = null;
  el.ministryForm.reset();
}

function renderMinistryTable() {
  el.ministryTableBody.innerHTML = "";
  const ordered = [...state.ministries].sort((a, b) => a.name.localeCompare(b.name, "pt-BR"));

  for (const ministry of ordered) {
    const tr = document.createElement("tr");
    tr.innerHTML = `
      <td>${ministry.name}</td>
      <td>${ministry.description || "-"}</td>
      <td>${ministry.is_active ? "Sim" : "Nao"}</td>
      <td>
        <button class="btn ghost btn-mini" type="button" data-edit-ministry="${ministry.id}">Editar</button>
        <button class="btn ghost btn-mini" type="button" data-delete-ministry="${ministry.id}">Excluir</button>
      </td>
    `;
    el.ministryTableBody.appendChild(tr);
  }

  if (!ordered.length) {
    const tr = document.createElement("tr");
    tr.innerHTML = "<td colspan='4'>Nenhum ministerio cadastrado.</td>";
    el.ministryTableBody.appendChild(tr);
  }
}

function populateMinistrySelects() {
  el.txMinistry.innerHTML = "<option value=''>Nao se aplica</option>";
  el.editTxMinistry.innerHTML = "<option value=''>Nao se aplica</option>";

  const ordered = [...state.ministries].sort((a, b) => a.name.localeCompare(b.name, "pt-BR"));
  for (const ministry of ordered) {
    const txOption = document.createElement("option");
    txOption.value = ministry.id;
    txOption.textContent = ministry.name;
    el.txMinistry.appendChild(txOption);

    const editOption = document.createElement("option");
    editOption.value = ministry.id;
    editOption.textContent = ministry.name;
    el.editTxMinistry.appendChild(editOption);
  }
}

function payableStatusLabel(value) {
  if (value === "paid") {
    return "Paga";
  }
  if (value === "overdue") {
    return "Vencida";
  }
  return "Pendente";
}

function payableRecurringLabel(value) {
  if (value === "weekly") {
    return "Semanal";
  }
  if (value === "monthly") {
    return "Mensal";
  }
  if (value === "yearly") {
    return "Anual";
  }
  return "Nao";
}

function payableExpenseProfileLabel(value) {
  if (value === "fixed") {
    return "Fixa";
  }
  if (value === "variable") {
    return "Variavel";
  }
  return "-";
}

function payablePaymentMethodLabel(value) {
  if (value === "pix") {
    return "PIX";
  }
  if (value === "boleto") {
    return "Boleto";
  }
  if (value === "cash") {
    return "Dinheiro";
  }
  return "-";
}

function clearPayableForm() {
  state.editingPayableId = null;
  el.payableForm.reset();
  el.payableCategory.value = "";
  el.payableMinistry.value = "";
  el.payableBankName.value = "";
  el.payableExpenseProfile.value = "";
  el.payableAttachmentFile.value = "";
  el.payableRecurringType.value = "";
  el.payableDueDate.value = new Date().toISOString().slice(0, 10);
  el.payableSaveBtn.textContent = "Salvar conta";
}

function closeEditPayableModal() {
  state.editingPayableId = null;
  el.editPayableForm.reset();
  el.editPayableCategory.value = "";
  el.editPayableMinistry.value = "";
  el.editPayableBankName.value = "";
  el.editPayableExpenseProfile.value = "";
  el.editPayableRecurringType.value = "";
  el.editPayableAttachmentFile.value = "";
  el.editPayableModal.classList.add("hide");
}

function populateEditPayableFormOptions() {
  const selectedCategory = el.editPayableCategory.value;
  const selectedMinistry = el.editPayableMinistry.value;
  const selectedBank = el.editPayableBankName.value;

  el.editPayableCategory.innerHTML = "<option value=''>Sem categoria</option>";
  for (const cat of [...state.categories].sort((a, b) => a.name.localeCompare(b.name, "pt-BR"))) {
    const option = document.createElement("option");
    option.value = String(cat.id);
    option.textContent = cat.name;
    el.editPayableCategory.appendChild(option);
  }
  if (selectedCategory) {
    el.editPayableCategory.value = selectedCategory;
  }

  el.editPayableMinistry.innerHTML = "<option value=''>Nao se aplica</option>";
  for (const ministry of [...state.ministries].sort((a, b) => a.name.localeCompare(b.name, "pt-BR"))) {
    const option = document.createElement("option");
    option.value = String(ministry.id);
    option.textContent = ministry.name;
    el.editPayableMinistry.appendChild(option);
  }
  if (selectedMinistry) {
    el.editPayableMinistry.value = selectedMinistry;
  }

  el.editPayableBankName.innerHTML = "<option value=''>Nao informado</option>";
  const banks = new Set();
  for (const tx of state.transactionsRaw) {
    const name = String(tx.source_bank || tx.source_bank_name || "").trim();
    if (name) {
      banks.add(name);
    }
  }
  for (const payable of state.payables) {
    const name = String(payable.source_bank_name || "").trim();
    if (name) {
      banks.add(name);
    }
  }
  for (const bank of [...banks].sort((a, b) => a.localeCompare(b, "pt-BR"))) {
    const option = document.createElement("option");
    option.value = bank;
    option.textContent = bank;
    el.editPayableBankName.appendChild(option);
  }
  if (selectedBank) {
    ensureSelectHasOption(el.editPayableBankName, selectedBank);
    el.editPayableBankName.value = selectedBank;
  }
}

function populatePayableFormOptions() {
  const selectedCategory = el.payableCategory.value;
  const selectedMinistry = el.payableMinistry.value;
  const selectedBank = el.payableBankName.value;

  el.payableCategory.innerHTML = "<option value=''>Sem categoria</option>";
  for (const cat of [...state.categories].sort((a, b) => a.name.localeCompare(b.name, "pt-BR"))) {
    const option = document.createElement("option");
    option.value = String(cat.id);
    option.textContent = cat.name;
    el.payableCategory.appendChild(option);
  }
  if (selectedCategory) {
    el.payableCategory.value = selectedCategory;
  }

  el.payableMinistry.innerHTML = "<option value=''>Nao se aplica</option>";
  for (const ministry of [...state.ministries].sort((a, b) => a.name.localeCompare(b.name, "pt-BR"))) {
    const option = document.createElement("option");
    option.value = String(ministry.id);
    option.textContent = ministry.name;
    el.payableMinistry.appendChild(option);
  }
  if (selectedMinistry) {
    el.payableMinistry.value = selectedMinistry;
  }

  el.payableBankName.innerHTML = "<option value=''>Nao informado</option>";
  const banks = new Set();
  for (const tx of state.transactionsRaw) {
    const name = String(tx.source_bank || tx.source_bank_name || "").trim();
    if (name) {
      banks.add(name);
    }
  }
  for (const payable of state.payables) {
    const name = String(payable.source_bank_name || "").trim();
    if (name) {
      banks.add(name);
    }
  }
  for (const bank of [...banks].sort((a, b) => a.localeCompare(b, "pt-BR"))) {
    const option = document.createElement("option");
    option.value = bank;
    option.textContent = bank;
    el.payableBankName.appendChild(option);
  }
  if (selectedBank) {
    ensureSelectHasOption(el.payableBankName, selectedBank);
    el.payableBankName.value = selectedBank;
  }
}

function syncPayableFiltersFromUi() {
  state.payableFilters.search = el.payableFilterSearch.value.trim();
  state.payableFilters.status = el.payableFilterStatus.value;
  state.payableFilters.startDate = el.payableFilterStartDate.value;
  state.payableFilters.endDate = el.payableFilterEndDate.value;
}

function resetPayableFilters() {
  state.payableFilters = {
    search: "",
    status: "",
    startDate: "",
    endDate: "",
  };
  el.payableFilterSearch.value = "";
  el.payableFilterStatus.value = "";
  el.payableFilterStartDate.value = "";
  el.payableFilterEndDate.value = "";
  renderPayables();
}

function getFilteredPayables() {
  const f = state.payableFilters;
  const search = normalizeText(f.search);

  return state.payables.filter((payable) => {
    if (f.status && payable.status !== f.status) return false;
    if (f.startDate && payable.due_date < f.startDate) return false;
    if (f.endDate && payable.due_date > f.endDate) return false;

    if (search) {
      const haystack = normalizeText([
        payable.description,
        payable.source_bank_name,
        payable.category?.name,
        payable.ministry?.name,
      ].join(" "));
      if (!haystack.includes(search)) return false;
    }

    return true;
  }).sort((a, b) => String(a.due_date).localeCompare(String(b.due_date)));
}

function renderPayables() {
  const rows = getFilteredPayables();
  el.payableTableBody.innerHTML = "";

  for (const payable of rows) {
    const tr = document.createElement("tr");
    tr.innerHTML = `
      <td>${payable.due_date}</td>
      <td>${payable.paid_at || "-"}</td>
      <td>${payable.description}</td>
      <td><span class="payable-status ${payable.status}">${payableStatusLabel(payable.status)}</span></td>
      <td>${payablePaymentMethodLabel(payable.payment_method)}</td>
      <td>${payable.category?.name || "-"}</td>
      <td>${payable.ministry?.name || "-"}</td>
      <td>${payable.source_bank_name || "-"}</td>
      <td>${payableExpenseProfileLabel(payable.expense_profile)}</td>
      <td>${payable.attachment_original_filename ? "Sim" : "-"}</td>
      <td>${brl(payable.amount)}</td>
      <td>${payableRecurringLabel(payable.recurrence_type)}</td>
      <td>
        <div class="payable-actions">
          <button class="btn ghost btn-mini" type="button" data-edit-payable="${payable.id}">Editar</button>
          ${payable.status !== "paid" ? `<button class="btn btn-mini" type="button" data-mark-payable-paid="${payable.id}">Marcar paga</button>` : ""}
          ${payable.attachment_original_filename ? `<button class="btn ghost btn-mini" type="button" data-preview-payable-attachment="${payable.id}">Boleto</button>` : ""}
          ${payable.attachment_original_filename ? `<button class="btn ghost btn-mini" type="button" data-delete-payable-attachment="${payable.id}">Remover boleto</button>` : ""}
          <button class="btn ghost btn-mini" type="button" data-delete-payable="${payable.id}">Excluir</button>
        </div>
      </td>
    `;
    el.payableTableBody.appendChild(tr);
  }

  if (!rows.length) {
    const tr = document.createElement("tr");
    tr.innerHTML = "<td colspan='13'>Nenhuma conta encontrada para os filtros atuais.</td>";
    el.payableTableBody.appendChild(tr);
  }

  el.payableFilterResultCount.textContent = `Mostrando ${rows.length} de ${state.payables.length}`;
}

function openEditPayable(payable) {
  populateEditPayableFormOptions();
  state.editingPayableId = payable.id;
  el.editPayableDescription.value = payable.description || "";
  el.editPayableAmount.value = toInputAmount(payable.amount);
  el.editPayableDueDate.value = payable.due_date || "";
  el.editPayableCategory.value = payable.category_id ? String(payable.category_id) : "";
  el.editPayableMinistry.value = payable.ministry_id ? String(payable.ministry_id) : "";
  ensureSelectHasOption(el.editPayableBankName, payable.source_bank_name || "");
  el.editPayableBankName.value = payable.source_bank_name || "";
  el.editPayableExpenseProfile.value = payable.expense_profile || "";
  el.editPayableRecurringType.value = payable.recurrence_type || "";
  el.editPayableNotes.value = payable.notes || "";
  el.editPayableAttachmentFile.value = "";
  
  if (payable.attachment_original_filename) {
    el.editPayableAttachmentCurrentName.textContent = payable.attachment_original_filename;
    el.editPayableAttachmentBlockCurrent.classList.remove("hide");
  } else {
    el.editPayableAttachmentBlockCurrent.classList.add("hide");
  }
  
  el.editPayableModal.classList.remove("hide");
  window.setTimeout(() => {
    el.editPayableDescription.focus();
    el.editPayableDescription.select();
  }, 0);
}

function receivableStatusLabel(value) {
  if (value === "received") {
    return "Recebida";
  }
  if (value === "overdue") {
    return "Vencida";
  }
  return "Pendente";
}

function receivableRecurringLabel(value) {
  if (value === "weekly") {
    return "Semanal";
  }
  if (value === "monthly") {
    return "Mensal";
  }
  if (value === "yearly") {
    return "Anual";
  }
  return "Nao";
}

function clearReceivableForm() {
  state.editingReceivableId = null;
  el.receivableForm.reset();
  el.receivableCategory.value = "";
  el.receivableMinistry.value = "";
  el.receivableBankName.value = "";
  el.receivableRecurringType.value = "";
  el.receivableDueDate.value = new Date().toISOString().slice(0, 10);
  el.receivableSaveBtn.textContent = "Salvar conta";
}

function populateReceivableFormOptions() {
  const selectedCategory = el.receivableCategory.value;
  const selectedMinistry = el.receivableMinistry.value;
  const selectedBank = el.receivableBankName.value;

  el.receivableCategory.innerHTML = "<option value=''>Sem categoria</option>";
  for (const cat of [...state.categories].sort((a, b) => a.name.localeCompare(b.name, "pt-BR"))) {
    const option = document.createElement("option");
    option.value = String(cat.id);
    option.textContent = cat.name;
    el.receivableCategory.appendChild(option);
  }
  if (selectedCategory) {
    el.receivableCategory.value = selectedCategory;
  }

  el.receivableMinistry.innerHTML = "<option value=''>Nao se aplica</option>";
  for (const ministry of [...state.ministries].sort((a, b) => a.name.localeCompare(b.name, "pt-BR"))) {
    const option = document.createElement("option");
    option.value = String(ministry.id);
    option.textContent = ministry.name;
    el.receivableMinistry.appendChild(option);
  }
  if (selectedMinistry) {
    el.receivableMinistry.value = selectedMinistry;
  }

  el.receivableBankName.innerHTML = "<option value=''>Nao informado</option>";
  const banks = new Set();
  for (const tx of state.transactionsRaw) {
    const name = String(tx.source_bank || tx.source_bank_name || "").trim();
    if (name) {
      banks.add(name);
    }
  }
  for (const receivable of state.receivables) {
    const name = String(receivable.source_bank_name || "").trim();
    if (name) {
      banks.add(name);
    }
  }
  for (const bank of [...banks].sort((a, b) => a.localeCompare(b, "pt-BR"))) {
    const option = document.createElement("option");
    option.value = bank;
    option.textContent = bank;
    el.receivableBankName.appendChild(option);
  }
  if (selectedBank) {
    ensureSelectHasOption(el.receivableBankName, selectedBank);
    el.receivableBankName.value = selectedBank;
  }
}

function syncReceivableFiltersFromUi() {
  state.receivableFilters.search = el.receivableFilterSearch.value.trim();
  state.receivableFilters.status = el.receivableFilterStatus.value;
  state.receivableFilters.startDate = el.receivableFilterStartDate.value;
  state.receivableFilters.endDate = el.receivableFilterEndDate.value;
}

function resetReceivableFilters() {
  state.receivableFilters = {
    search: "",
    status: "",
    startDate: "",
    endDate: "",
  };
  el.receivableFilterSearch.value = "";
  el.receivableFilterStatus.value = "";
  el.receivableFilterStartDate.value = "";
  el.receivableFilterEndDate.value = "";
  renderReceivables();
}

function getFilteredReceivables() {
  const f = state.receivableFilters;
  const search = normalizeText(f.search);

  return state.receivables.filter((receivable) => {
    if (f.status && receivable.status !== f.status) return false;
    if (f.startDate && receivable.due_date < f.startDate) return false;
    if (f.endDate && receivable.due_date > f.endDate) return false;

    if (search) {
      const haystack = normalizeText([
        receivable.description,
        receivable.source_bank_name,
        receivable.category?.name,
        receivable.ministry?.name,
      ].join(" "));
      if (!haystack.includes(search)) return false;
    }

    return true;
  }).sort((a, b) => String(a.due_date).localeCompare(String(b.due_date)));
}

function renderReceivables() {
  const rows = getFilteredReceivables();
  el.receivableTableBody.innerHTML = "";

  for (const receivable of rows) {
    const tr = document.createElement("tr");
    tr.innerHTML = `
      <td>${receivable.due_date}</td>
      <td>${receivable.description}</td>
      <td><span class="receivable-status ${receivable.status}">${receivableStatusLabel(receivable.status)}</span></td>
      <td>${receivable.category?.name || "-"}</td>
      <td>${receivable.ministry?.name || "-"}</td>
      <td>${receivable.source_bank_name || "-"}</td>
      <td>${brl(receivable.amount)}</td>
      <td>${receivableRecurringLabel(receivable.recurrence_type)}</td>
      <td>
        <div class="receivable-actions">
          <button class="btn ghost btn-mini" type="button" data-edit-receivable="${receivable.id}">Editar</button>
          ${receivable.status !== "received" ? `<button class="btn btn-mini" type="button" data-mark-receivable-received="${receivable.id}">Marcar recebida</button>` : ""}
          <button class="btn ghost btn-mini" type="button" data-delete-receivable="${receivable.id}">Excluir</button>
        </div>
      </td>
    `;
    el.receivableTableBody.appendChild(tr);
  }

  if (!rows.length) {
    const tr = document.createElement("tr");
    tr.innerHTML = "<td colspan='9'>Nenhuma conta encontrada para os filtros atuais.</td>";
    el.receivableTableBody.appendChild(tr);
  }

  el.receivableFilterResultCount.textContent = `Mostrando ${rows.length} de ${state.receivables.length}`;
}

function openEditReceivable(receivable) {
  state.editingReceivableId = receivable.id;
  el.receivableDescription.value = receivable.description || "";
  el.receivableAmount.value = toInputAmount(receivable.amount);
  el.receivableDueDate.value = receivable.due_date || "";
  el.receivableCategory.value = receivable.category_id ? String(receivable.category_id) : "";
  el.receivableMinistry.value = receivable.ministry_id ? String(receivable.ministry_id) : "";
  ensureSelectHasOption(el.receivableBankName, receivable.source_bank_name || "");
  el.receivableBankName.value = receivable.source_bank_name || "";
  el.receivableRecurringType.value = receivable.recurrence_type || "";
  el.receivableNotes.value = receivable.notes || "";
  el.receivableSaveBtn.textContent = "Salvar alteracoes";
}

function renderReceivablesKpi() {
  const summary = state.receivableAlertsSummary || {
    overdue: 0,
    due_today: 0,
    due_in_3_days: 0,
    due_in_7_days: 0,
    pending_total: 0,
  };

  const pendingCount = Number(summary.pending_total || 0);
  const overdueCount = Number(summary.overdue || 0);

  el.kpiReceivablesPending.textContent = String(pendingCount);
  el.kpiReceivablesOverdue.textContent = String(overdueCount);

  if (overdueCount > 0) {
    el.kpiReceivablesAlert.textContent = `${overdueCount} vencida(s)!`;
    el.kpiReceivablesAlert.style.display = "block";
  } else if (Number(summary.due_today || 0) > 0) {
    el.kpiReceivablesAlert.textContent = `${summary.due_today} vence hoje`;
    el.kpiReceivablesAlert.style.display = "block";
    el.kpiReceivablesAlert.style.color = "#f57c00";
  } else if (Number(summary.due_in_3_days || 0) > 0) {
    el.kpiReceivablesAlert.textContent = `${summary.due_in_3_days} em 3 dias`;
    el.kpiReceivablesAlert.style.display = "block";
    el.kpiReceivablesAlert.style.color = "#f57c00";
  } else {
    el.kpiReceivablesAlert.textContent = "";
    el.kpiReceivablesAlert.style.display = "none";
  }
}

async function api(path, options = {}, isForm = false) {
  const headers = new Headers(options.headers || {});
  if (!isForm) {
    headers.set("Content-Type", "application/json");
  }
  if (state.accessToken) {
    headers.set("Authorization", `Bearer ${state.accessToken}`);
  }

  const response = await fetch(`${API_PREFIX}${path}`, { ...options, headers });
  if (!response.ok) {
    let detail = `Erro ${response.status}`;
    try {
      const body = await response.json();
      detail = errorDetailToText(body.detail ?? body, detail);
    } catch {
      // no-op
    }
    throw new Error(detail);
  }

  if (response.status === 204) {
    return null;
  }
  return response.json();
}

async function login(email, password) {
  const form = new URLSearchParams();
  form.set("username", email);
  form.set("password", password);

  const response = await fetch(`${API_PREFIX}/auth/login`, {
    method: "POST",
    headers: { "Content-Type": "application/x-www-form-urlencoded" },
    body: form,
  });

  if (!response.ok) {
    const body = await response.json().catch(() => ({}));
    throw new Error(errorDetailToText(body.detail ?? body, "Falha no login"));
  }

  const data = await response.json();
  state.accessToken = data.access_token;
  state.refreshToken = data.refresh_token;
  localStorage.setItem("accessToken", data.access_token);
  localStorage.setItem("refreshToken", data.refresh_token);
  if (data.active_tenant_slug) {
    localStorage.setItem("activeTenantSlug", data.active_tenant_slug);
  }
}

function logout() {
  state.accessToken = "";
  state.refreshToken = "";
  state.currentUserRole = "";
  state.currentUserPermissions = [];
  state.currentUserPermissionSet = new Set();
  state.currentUserIsAdmin = false;
  localStorage.removeItem("accessToken");
  localStorage.removeItem("refreshToken");
  localStorage.removeItem("currentUserRole");
  localStorage.removeItem(CURRENT_USER_PERMISSIONS_STORAGE_KEY);
  localStorage.removeItem(CURRENT_USER_IS_ADMIN_STORAGE_KEY);
  localStorage.removeItem("activeTenantSlug");
  document.body.dataset.userRole = "";
  el.sessionUser.textContent = "Nao autenticado";
  setMessage(el.authMessage, "");
  showApp(false);
}

async function loadMe() {
  const me = await api("/auth/me");
  state.currentUserRole = String(me.role || "").toLowerCase();

  const rolePermissions = Array.isArray(me && me.role_obj && me.role_obj.permissions)
    ? me.role_obj.permissions
    : [];
  const permissionNames = rolePermissions
    .filter((permission) => permission && permission.active !== false && typeof permission.name === "string")
    .map((permission) => permission.name);

  state.currentUserPermissions = permissionNames;
  state.currentUserPermissionSet = new Set(permissionNames);
  state.currentUserIsAdmin = Boolean(me && me.role_obj && me.role_obj.is_admin) || state.currentUserRole === "admin";

  localStorage.setItem("currentUserRole", state.currentUserRole);
  localStorage.setItem(CURRENT_USER_PERMISSIONS_STORAGE_KEY, JSON.stringify(permissionNames));
  localStorage.setItem(CURRENT_USER_IS_ADMIN_STORAGE_KEY, String(state.currentUserIsAdmin));
  document.body.dataset.userRole = state.currentUserRole;
  el.sessionUser.textContent = `${me.full_name || me.email} (${me.role})`;

  applyTopModulePermissions();
  return me;
}

async function loadSummary() {
  renderDashboard();
}

async function loadCategories() {
  const categories = await api("/categories/");
  state.categories = categories;

  renderTransactionCategoryOptions();
  syncTransactionCategoryFromInput();

  el.editTxCategory.innerHTML = "<option value=''>Sem categoria</option>";
  for (const cat of categories) {
    const option = document.createElement("option");
    option.value = cat.id;
    option.textContent = cat.name;
    el.editTxCategory.appendChild(option);
  }

  renderCategoryTable();
  populateTransactionFilterOptions();
  populateDashboardFilterOptions();
  populateBudgetReferenceOptions();
  populatePayableFormOptions();
  renderPayables();
}

async function loadMinistries() {
  const ministries = await api("/ministries/");
  state.ministries = ministries;
  populateMinistrySelects();
  renderMinistryTable();
  populateTransactionFilterOptions();
  populateDashboardFilterOptions();
  populateBudgetReferenceOptions();
  populatePayableFormOptions();
  renderPayables();
  syncMinistryField(el.txType, el.txMinistry);
  syncMinistryField(el.editTxType, el.editTxMinistry);
}

async function loadTransactions() {
  const pageSize = 100;
  const maxPages = 20;
  const allItems = [];

  for (let page = 1; page <= maxPages; page += 1) {
    const data = await api(`/transactions/?page=${page}&size=${pageSize}`);
    const items = data.items || [];
    allItems.push(...items);
    if (items.length < pageSize) {
      break;
    }
  }

  state.transactionsRaw = allItems;
  populateBankDropdowns();
  populatePayableFormOptions();
  renderTransactions();
  renderDashboard();
}

async function loadPayables() {
  const payables = await api("/payables/");
  state.payables = payables;
  populatePayableFormOptions();
  renderPayables();
}

async function loadPayablesAlertsSummary() {
  try {
    const summary = await api("/payables/alerts/summary");
    state.payableAlertsSummary = summary;
  } catch {
    state.payableAlertsSummary = {
      overdue: 0,
      due_today: 0,
      due_in_3_days: 0,
      due_in_7_days: 0,
      pending_total: 0,
    };
  }
}

async function loadReceivables() {
  const receivables = await api("/receivables/");
  state.receivables = receivables;
  populateReceivableFormOptions();
  renderReceivables();
}

async function loadReceivablesAlertsSummary() {
  try {
    const summary = await api("/receivables/alerts/summary");
    state.receivableAlertsSummary = summary;
  } catch {
    state.receivableAlertsSummary = {
      overdue: 0,
      due_today: 0,
      due_in_3_days: 0,
      due_in_7_days: 0,
      pending_total: 0,
    };
  }
}

async function openEditTransactionModal(transactionId) {
  const tx = await api(`/transactions/${transactionId}`);
  state.editingTransactionId = tx.id;
  el.editTxDescription.value = tx.description || "";
  el.editTxAmount.value = toInputAmount(tx.amount);
  el.editTxType.value = tx.transaction_type || "expense";
  syncExpenseProfileField(el.editTxType, el.editTxExpenseProfile);
  syncMinistryField(el.editTxType, el.editTxMinistry);
  el.editTxExpenseProfile.value = tx.expense_profile || "";
  el.editTxMinistry.value = tx.ministry_id ? String(tx.ministry_id) : "";
  el.editTxDate.value = tx.transaction_date;
  el.editTxCategory.value = tx.category_id ? String(tx.category_id) : "";
  ensureSelectHasOption(el.editTxBankName, tx.source_bank_name || tx.source_bank || "");
  el.editTxBankName.value = tx.source_bank_name || tx.source_bank || "";
  el.editTransactionModal.classList.remove("hide");
  try {
    await loadTransactionAttachments(tx.id);
  } catch (error) {
    el.editTxAttachmentsList.innerHTML = "<li>Nao foi possivel carregar anexos.</li>";
    setMessage(el.txMessage, error.message, true);
  }
}

function closeEditTransactionModal() {
  state.editingTransactionId = null;
  el.editTransactionForm.reset();
  el.editTxAttachmentsList.innerHTML = "";
  closeAttachmentPreviewModal();
  el.editTransactionModal.classList.add("hide");
}

async function loadTransactionAttachments(transactionId) {
  const attachments = await api(`/transactions/${transactionId}/attachments`);
  el.editTxAttachmentsList.innerHTML = "";

  for (const attachment of attachments) {
    const li = document.createElement("li");
    const nameBtn = document.createElement("button");
    nameBtn.className = "attachment-name-btn";
    nameBtn.type = "button";
    nameBtn.textContent = attachment.original_filename;
    nameBtn.addEventListener("click", async () => {
      try {
        await previewTransactionAttachment(transactionId, attachment);
      } catch (error) {
        setMessage(el.txMessage, error.message, true);
      }
    });

    const downloadBtn = document.createElement("button");
    downloadBtn.className = "btn ghost btn-mini";
    downloadBtn.type = "button";
    downloadBtn.textContent = "Baixar";
    downloadBtn.addEventListener("click", async () => {
      try {
        const headers = new Headers();
        if (state.accessToken) {
          headers.set("Authorization", `Bearer ${state.accessToken}`);
        }
        const response = await fetch(`${API_PREFIX}/transactions/${transactionId}/attachments/${attachment.id}/download`, {
          method: "GET",
          headers,
        });
        if (!response.ok) {
          throw new Error("Falha ao baixar anexo.");
        }
        const blob = await response.blob();
        const url = URL.createObjectURL(blob);
        const anchor = document.createElement("a");
        anchor.href = url;
        anchor.download = attachment.original_filename;
        document.body.appendChild(anchor);
        anchor.click();
        anchor.remove();
        URL.revokeObjectURL(url);
      } catch (error) {
        setMessage(el.txMessage, error.message, true);
      }
    });

    li.appendChild(nameBtn);
    li.appendChild(downloadBtn);
    el.editTxAttachmentsList.appendChild(li);
  }

  if (!attachments.length) {
    const li = document.createElement("li");
    li.textContent = "Nenhum anexo neste lancamento.";
    el.editTxAttachmentsList.appendChild(li);
  }
}

async function uploadAttachmentForEditingTransaction(showSuccessMessage = true) {
  if (!state.editingTransactionId) {
    throw new Error("Selecione um lancamento para anexar arquivos.");
  }

  const file = el.editTxAttachmentFile.files?.[0];
  if (!file) {
    return false;
  }

  const formData = new FormData();
  formData.append("file", file);

  await api(
    `/transactions/${state.editingTransactionId}/attachments`,
    { method: "POST", body: formData },
    true,
  );

  el.editTxAttachmentFile.value = "";
  await loadTransactionAttachments(state.editingTransactionId);
  await loadTransactions();

  if (showSuccessMessage) {
    setMessage(el.txMessage, "Anexo enviado com sucesso. Arquivo armazenado de forma compactada.");
  }
  return true;
}

function openUploadModal() {
  el.uploadResultModal.classList.remove("hide");
}

function closeUploadModal() {
  el.uploadResultModal.classList.add("hide");
}

function extractDuplicateCount(errorMessage) {
  const msg = String(errorMessage || "");
  const match = msg.match(/duplicadas=(\d+)/i);
  return match ? Number(match[1]) : 0;
}

function renderUploadModalStatus(record, fileName) {
  const duplicates = extractDuplicateCount(record.error_message);
  el.modalTitle.textContent = `Resultado do Upload: ${fileName}`;
  el.modalBody.innerHTML = `
    <p>Status: <strong>${record.status}</strong></p>
    <p>Transacoes importadas: <strong>${record.transactions_count || 0}</strong></p>
    <p>${record.error_message || "Processamento concluido sem avisos."}</p>
  `;

  const showDecision = duplicates > 0;
  el.modalKeepBothBtn.classList.toggle("hide", !showDecision);
  el.modalDiscardBtn.classList.toggle("hide", !showDecision);
  el.modalChooseOneBtn.classList.toggle("hide", !showDecision);
  el.modalApplySelectionBtn.classList.add("hide");
  el.modalDuplicatesList.classList.add("hide");
  el.modalDuplicatesList.innerHTML = "";
  el.modalOkBtn.classList.toggle("hide", showDecision);

  return duplicates;
}

function renderDuplicateOptions(duplicates) {
  el.modalDuplicatesList.innerHTML = "";
  for (const dup of duplicates) {
    const row = document.createElement("label");
    row.className = "dup-row";
    const incomingBank = dup.source_bank || "-";
    const existingBank = dup.existing?.source_bank || "-";
    row.innerHTML = `
      <input type="checkbox" data-dup-key="${dup.key}" checked>
      <span>
        <strong>${dup.date} - ${dup.transaction_type === "income" ? "Entrada" : "Saida"} - ${brl(dup.amount)}</strong><br>
        <div class="dup-compare">
          <div class="dup-card incoming">
            <b>Novo</b>
            <div>${dup.description || "Sem descricao"}</div>
            <small>Banco: ${incomingBank} | Ref: ${dup.reference || "-"}</small>
          </div>
          <div class="dup-card existing">
            <b>Existente</b>
            <div>${dup.existing?.description || "-"}</div>
            <small>Banco: ${existingBank} | Ref: ${dup.existing?.reference || "-"}</small>
          </div>
        </div>
      </span>
    `;
    el.modalDuplicatesList.appendChild(row);
  }
  el.modalDuplicatesList.classList.remove("hide");
  el.modalApplySelectionBtn.classList.remove("hide");
}

async function loadDuplicatePreview(fileId) {
  const data = await api(`/upload/${fileId}/duplicates-preview`);
  return data.duplicates || [];
}

function collectSelectedDuplicateKeys() {
  const checked = el.modalDuplicatesList.querySelectorAll("input[type='checkbox']:checked");
  return Array.from(checked).map((node) => node.getAttribute("data-dup-key"));
}

async function waitUploadCompletion(fileId, fileName) {
  let tries = 0;
  while (tries < 90) {
    const rec = await api(`/upload/${fileId}`);
    if (rec.status === "completed" || rec.status === "failed") {
      return renderUploadModalStatus(rec, fileName);
    }
    await new Promise((resolve) => setTimeout(resolve, 2000));
    tries += 1;
  }
  el.modalTitle.textContent = `Upload em processamento: ${fileName}`;
  el.modalBody.innerHTML = "<p>O processamento está demorando mais que o esperado. Voce pode fechar e verificar depois.</p>";
  el.modalKeepBothBtn.classList.add("hide");
  el.modalDiscardBtn.classList.add("hide");
  el.modalOkBtn.classList.remove("hide");
  return 0;
}

async function loadReports() {
  const year = Number(el.reportYear.value) || new Date().getFullYear();
  const [byCategory, monthly, cashFlow] = await Promise.all([
    api("/reports/by-category"),
    api(`/reports/monthly?year=${year}`),
    api("/reports/cash-flow?months_history=6&months_forecast=1"),
  ]);
  state.cashFlowForecast = cashFlow;

  el.categoryReport.innerHTML = "";
  for (const row of byCategory) {
    const li = document.createElement("li");
    li.textContent = `${row.category} (${row.transaction_type}): ${brl(row.total)} em ${row.count} item(ns)`;
    el.categoryReport.appendChild(li);
  }
  if (!byCategory.length) {
    el.categoryReport.innerHTML = "<li>Sem dados por categoria.</li>";
  }

  el.monthlyReport.innerHTML = "";
  for (const row of monthly) {
    const month = String(row.month).padStart(2, "0");
    const li = document.createElement("li");
    li.textContent = `${year}-${month} (${row.transaction_type}): ${brl(row.total)}`;
    el.monthlyReport.appendChild(li);
  }
  if (!monthly.length) {
    el.monthlyReport.innerHTML = "<li>Sem dados mensais.</li>";
  }

  setMessage(el.reportMessage, `Relatorios carregados para ${year}.`);
}

async function initializeApp() {
  if (isPublicRegistrationRoute()) {
    await initializePublicEventApp();
    return;
  }

  if (isPublicEventDetailRoute()) {
    await initializePublicEventDetailApp();
    return;
  }

  if (isPublicCatalogRoute()) {
    await initializePublicCatalogApp();
    return;
  }

  if (!state.accessToken) {
    showApp(false);
    return;
  }

  try {
    showApp(true);
    el.reportYear.value = new Date().getFullYear();
    const me = await loadMe();

    if (!hasModuleAccess("finance")) {
      const opened = openFirstAccessibleModule();
      if (!opened) {
        setMessage(el.dashboardMessage, "Sem acesso a nenhum modulo para esta role.", true);
      }
      return;
    }

    const firstFinanceView = getFirstFinanceAllowedView();
    if (!firstFinanceView) {
      setMessage(el.dashboardMessage, "Sua role nao possui permissoes de visualizacao no modulo Financeiro.", true);
      return;
    }

    setActiveView(firstFinanceView);
    if (String(me.role || "").toLowerCase() === "leader") {
      setMessage(el.dashboardMessage, "Perfil de lider: use o modulo de Celulas para gerenciar sua equipe e frequencia.");
      return;
    }
    await Promise.all([
      loadSummary(),
      loadCategories(),
      loadMinistries(),
      loadTransactions(),
      loadPayables(),
      loadPayablesAlertsSummary(),
      loadReceivables(),
      loadReceivablesAlertsSummary(),
      loadBudgets(),
      loadCashFlowForecast(),
      loadReports(),
    ]);
    renderDashboard();
  } catch (error) {
    logout();
    const msg = error instanceof Error ? error.message : errorDetailToText(error, "Falha ao validar sessao");
    setMessage(el.authMessage, `Sessao invalida: ${msg}`, true);
  }
}

el.loginForm.addEventListener("submit", async (event) => {
  event.preventDefault();
  try {
    const email = document.getElementById("email").value;
    const password = document.getElementById("password").value;
    await login(email, password);
    setMessage(el.authMessage, "Login realizado com sucesso.");
    await initializeApp();
  } catch (error) {
    setMessage(el.authMessage, error.message, true);
  }
});

el.logoutBtn.addEventListener("click", () => {
  logout();
  setMessage(el.authMessage, "Sessao encerrada.");
});

el.publicRefreshStatusBtn.addEventListener("click", async () => {
  try {
    const checkoutReference = getCheckoutReferenceFromRoute();
    if (!checkoutReference) {
      throw new Error("Referencia de pagamento nao encontrada.");
    }
    await loadPublicPaymentStatus(checkoutReference);
  } catch (error) {
    el.publicPaymentMessage.textContent = error.message;
  }
});

el.publicCopyPixBtn.addEventListener("click", async () => {
  try {
    const pixCode = String(el.publicPixCode.value || "").trim();
    if (!pixCode) {
      throw new Error("Nenhum codigo PIX disponivel.");
    }
    await navigator.clipboard.writeText(pixCode);
    el.publicPaymentMessage.textContent = "Codigo PIX copiado com sucesso.";
  } catch (error) {
    el.publicPaymentMessage.textContent = error.message;
  }
});

el.publicEventRegistrationForm.addEventListener("submit", async (event) => {
  event.preventDefault();
  try {
    const tenantSlug = String(el.publicEventRegistrationForm.dataset.tenantSlug || "").trim();
    const eventSlug = String(el.publicEventRegistrationForm.dataset.eventSlug || "").trim();
    if (!tenantSlug || !eventSlug) {
      throw new Error("Evento público não carregado.");
    }

    const payload = {
      attendee_name: el.publicDetailName.value.trim(),
      attendee_email: el.publicDetailEmail.value.trim(),
      attendee_phone: el.publicDetailPhone.value.trim() || null,
      quantity: Number(el.publicDetailQuantity.value || 1),
      payment_method: el.publicDetailPaymentMethod.value,
      notes: el.publicDetailNotes.value.trim() || null,
    };

    const response = await fetch(`${API_PREFIX}/events/public/${encodeURIComponent(tenantSlug)}/${encodeURIComponent(eventSlug)}/registrations`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
    });
    if (!response.ok) {
      const body = await response.json().catch(() => ({}));
      throw new Error(errorDetailToText(body.detail ?? body, "Falha ao criar inscricao"));
    }

    const result = await response.json();
    if (result.payment && result.payment.checkout_url) {
      window.location.href = `/events/registration/${encodeURIComponent(result.payment.checkout_reference)}`;
      return;
    }
    throw new Error("Pagamento nao foi gerado para esta inscrição.");
  } catch (error) {
    el.publicDetailMessage.textContent = error.message;
  }
});

el.refreshBtn.addEventListener("click", async () => {
  try {
    await Promise.all([loadTransactions(), loadPayables(), loadPayablesAlertsSummary(), loadReceivables(), loadReceivablesAlertsSummary(), loadBudgets(), loadReports()]);
    renderDashboard();
  } catch (error) {
    setMessage(el.dashboardMessage, error.message, true);
  }
});

el.kpiPayablesCard.addEventListener("click", () => {
  openPayablesWithFilters({ status: "pending" });
});

el.kpiPayablesOverdueCard.addEventListener("click", () => {
  openPayablesWithFilters({ status: "overdue" });
});

el.kpiReceivablesCard.addEventListener("click", () => {
  openReceivablesWithFilters({ status: "pending" });
});

el.kpiReceivablesAlert.addEventListener("click", (event) => {
  if (el.kpiReceivablesAlert.textContent.toLowerCase().includes("vencida")) {
    openReceivablesWithFilters({ status: "overdue" });
  }
});

el.kpiReceivablesOverdueCard.addEventListener("click", () => {
  openReceivablesWithFilters({ status: "overdue" });
});

for (const node of [
  el.dashStartDate,
  el.dashEndDate,
  el.dashTypeFilter,
  el.dashCategoryFilter,
  el.dashMinistryFilter,
  el.dashBankFilter,
]) {
  node.addEventListener("change", () => {
    syncDashboardFiltersFromUi();
    renderDashboard();
  });
}

el.dashResetFiltersBtn.addEventListener("click", () => {
  resetDashboardFilters();
  setMessage(el.dashboardMessage, "Filtros do dashboard limpos.");
});

el.dashBudgetType.addEventListener("change", populateBudgetReferenceOptions);
el.dashLineMetric.addEventListener("change", () => {
  el.dashLineChart.classList.add("metric-transition");
  renderLineChart(state.dashboardTrendRows);
  window.setTimeout(() => {
    el.dashLineChart.classList.remove("metric-transition");
  }, 360);
});
el.dashBudgetForm.addEventListener("submit", async (event) => {
  event.preventDefault();
  try {
    const month = new Date().toISOString().slice(0, 7);
    const budget_type = el.dashBudgetType.value;
    const reference_id = Number(el.dashBudgetRef.value);
    const target_amount = Number(el.dashBudgetAmount.value || 0);

    if (!reference_id || target_amount <= 0) {
      setMessage(el.dashBudgetMessage, "Informe referencia e valor de meta validos.", true);
      return;
    }

    const budgetData = {
      month,
      budget_type,
      reference_id,
      target_amount,
      alert_threshold_percent: 80, // Default 80%
    };

    await saveBudget(budgetData);
    setMessage(el.dashBudgetMessage, "Meta salva com sucesso.");
    el.dashBudgetAmount.value = "";
    await loadBudgets();
    renderDashboard();
  } catch (error) {
    setMessage(el.dashBudgetMessage, error.message, true);
  }
});

el.payableForm.addEventListener("submit", async (event) => {
  event.preventDefault();
  try {
    const recurrenceType = el.payableRecurringType.value || null;
    const payload = {
      description: el.payableDescription.value.trim(),
      amount: Number(el.payableAmount.value || 0),
      due_date: el.payableDueDate.value,
      category_id: el.payableCategory.value ? Number(el.payableCategory.value) : null,
      ministry_id: el.payableMinistry.value ? Number(el.payableMinistry.value) : null,
      source_bank_name: el.payableBankName.value || null,
      expense_profile: el.payableExpenseProfile.value || null,
      notes: el.payableNotes.value.trim() || null,
      is_recurring: recurrenceType !== null,
      recurrence_type: recurrenceType,
    };

    if (!payload.description) {
      throw new Error("Informe a descricao da conta.");
    }
    if (!payload.due_date) {
      throw new Error("Informe a data de vencimento.");
    }
    if (!Number.isFinite(payload.amount) || payload.amount <= 0) {
      throw new Error("Informe um valor valido maior que zero.");
    }

    const savedPayable = await api("/payables/", {
      method: "POST",
      body: JSON.stringify(payload),
    });
    setMessage(el.payableMessage, "Conta cadastrada com sucesso.");

    const attachment = el.payableAttachmentFile.files?.[0];
    if (attachment && savedPayable?.id) {
      const formData = new FormData();
      formData.append("file", attachment);
      await api(`/payables/${savedPayable.id}/attachment`, { method: "POST", body: formData }, true);
      setMessage(el.payableMessage, "Conta salva e boleto anexado com sucesso.");
    }

    clearPayableForm();
    await Promise.all([loadPayables(), loadPayablesAlertsSummary(), loadTransactions(), loadReports()]);
    renderDashboard();
  } catch (error) {
    setMessage(el.payableMessage, error.message, true);
  }
});

el.payableCancelEditBtn.addEventListener("click", () => {
  clearPayableForm();
  setMessage(el.payableMessage, "");
});

el.editPayableForm.addEventListener("submit", async (event) => {
  event.preventDefault();
  try {
    if (!state.editingPayableId) {
      throw new Error("Nenhuma conta selecionada para edicao.");
    }

    const payload = {
      description: el.editPayableDescription.value.trim(),
      amount: Number(el.editPayableAmount.value || 0),
      due_date: el.editPayableDueDate.value,
      category_id: el.editPayableCategory.value ? Number(el.editPayableCategory.value) : null,
      ministry_id: el.editPayableMinistry.value ? Number(el.editPayableMinistry.value) : null,
      source_bank_name: el.editPayableBankName.value || null,
      expense_profile: el.editPayableExpenseProfile.value || null,
      notes: el.editPayableNotes.value.trim() || null,
      is_recurring: !!el.editPayableRecurringType.value,
      recurrence_type: el.editPayableRecurringType.value || null,
    };

    if (!payload.description) {
      throw new Error("Informe a descricao da conta.");
    }
    if (!payload.due_date) {
      throw new Error("Informe a data de vencimento.");
    }
    if (!Number.isFinite(payload.amount) || payload.amount <= 0) {
      throw new Error("Informe um valor valido maior que zero.");
    }

    const updatedPayable = await api(`/payables/${state.editingPayableId}`, {
      method: "PUT",
      body: JSON.stringify(payload),
    });

    const attachment = el.editPayableAttachmentFile.files?.[0];
    if (attachment && updatedPayable?.id) {
      const formData = new FormData();
      formData.append("file", attachment);
      await api(`/payables/${updatedPayable.id}/attachment`, { method: "POST", body: formData }, true);
    }

    closeEditPayableModal();
    setMessage(el.payableMessage, "Conta atualizada com sucesso.");
    await Promise.all([loadPayables(), loadPayablesAlertsSummary(), loadTransactions(), loadReports()]);
    renderDashboard();
  } catch (error) {
    setMessage(el.payableMessage, error.message, true);
  }
});

const debouncedPayableSearch = debounce(() => {
  syncPayableFiltersFromUi();
  renderPayables();
}, 300);

el.payableFilterSearch.addEventListener("input", debouncedPayableSearch);
for (const node of [el.payableFilterStatus, el.payableFilterStartDate, el.payableFilterEndDate]) {
  node.addEventListener("change", () => {
    syncPayableFiltersFromUi();
    renderPayables();
  });
}
el.payableFilterResetBtn.addEventListener("click", resetPayableFilters);

el.payableTableBody.addEventListener("click", async (event) => {
  const target = event.target;
  if (!(target instanceof HTMLButtonElement)) {
    return;
  }

  const editId = target.getAttribute("data-edit-payable");
  if (editId) {
    const payable = state.payables.find((item) => item.id === Number(editId));
    if (!payable) {
      return;
    }
    openEditPayable(payable);
    setMessage(el.payableMessage, `Editando conta: ${payable.description}`);
    return;
  }

  const markPaidId = target.getAttribute("data-mark-payable-paid");
  if (markPaidId) {
    try {
      const payable = state.payables.find((item) => item.id === Number(markPaidId));
      const defaultPaidAt = new Date().toISOString().slice(0, 10);
      const paidPayload = await openPayablePaidAtModal(defaultPaidAt, payable?.payment_method || "");
      if (!paidPayload) {
        return;
      }
      const paidAt = paidPayload.paid_at;
      const paymentMethod = paidPayload.payment_method;
      if (!/^\d{4}-\d{2}-\d{2}$/.test(paidAt) || Number.isNaN(new Date(paidAt).getTime())) {
        setMessage(el.payableMessage, "Data de pagamento invalida. Use o formato AAAA-MM-DD.", true);
        return;
      }
      if (!paymentMethod) {
        setMessage(el.payableMessage, "Informe a forma de pagamento.", true);
        return;
      }

      await api(`/payables/${Number(markPaidId)}/mark-paid`, {
        method: "POST",
        body: JSON.stringify({ generate_transaction: true, paid_at: paidAt, payment_method: paymentMethod }),
      });
      setMessage(el.payableMessage, `Conta marcada como paga em ${paidAt} via ${payablePaymentMethodLabel(paymentMethod)}.`);
      await Promise.all([loadPayables(), loadPayablesAlertsSummary(), loadTransactions(), loadReports()]);
      renderDashboard();
    } catch (error) {
      setMessage(el.payableMessage, error.message, true);
    }
    return;
  }

  const previewAttachmentId = target.getAttribute("data-preview-payable-attachment");
  if (previewAttachmentId) {
    try {
      const payableId = Number(previewAttachmentId);
      await previewPayableAttachment(payableId);
    } catch (error) {
      setMessage(el.payableMessage, error.message, true);
    }
    return;
  }

  const deleteAttachmentId = target.getAttribute("data-delete-payable-attachment");
  if (deleteAttachmentId) {
    try {
      const payableId = Number(deleteAttachmentId);
      const confirmed = await openConfirmModal("Tem certeza que deseja remover o boleto desta conta?", "Remover boleto");
      if (!confirmed) {
        return;
      }

      await api(`/payables/${payableId}/attachment`, { method: "DELETE" });
      setMessage(el.payableMessage, "Boleto removido com sucesso.");
      await Promise.all([loadPayables(), loadPayablesAlertsSummary(), loadTransactions(), loadReports()]);
      renderDashboard();
    } catch (error) {
      setMessage(el.payableMessage, error.message, true);
    }
    return;
  }

  const deleteId = target.getAttribute("data-delete-payable");
  if (deleteId) {
    try {
      const confirmed = await openConfirmModal("Tem certeza que deseja excluir esta conta a pagar?", "Excluir conta");
      if (!confirmed) {
        return;
      }
      await api(`/payables/${Number(deleteId)}`, { method: "DELETE" });
      setMessage(el.payableMessage, "Conta excluida com sucesso.");
      if (state.editingPayableId === Number(deleteId)) {
        closeEditPayableModal();
      }
      await Promise.all([loadPayables(), loadPayablesAlertsSummary(), loadTransactions(), loadReports()]);
      renderDashboard();
    } catch (error) {
      setMessage(el.payableMessage, error.message, true);
    }
  }
});

el.receivableForm.addEventListener("submit", async (event) => {
  event.preventDefault();
  try {
    const recurrenceType = el.receivableRecurringType.value || null;
    const payload = {
      description: el.receivableDescription.value.trim(),
      amount: Number(el.receivableAmount.value || 0),
      due_date: el.receivableDueDate.value,
      category_id: el.receivableCategory.value ? Number(el.receivableCategory.value) : null,
      ministry_id: el.receivableMinistry.value ? Number(el.receivableMinistry.value) : null,
      source_bank_name: el.receivableBankName.value || null,
      notes: el.receivableNotes.value.trim() || null,
      is_recurring: recurrenceType !== null,
      recurrence_type: recurrenceType,
    };

    if (!payload.description) {
      throw new Error("Informe a descricao da conta.");
    }
    if (!payload.due_date) {
      throw new Error("Informe a data de vencimento.");
    }
    if (!Number.isFinite(payload.amount) || payload.amount <= 0) {
      throw new Error("Informe um valor valido maior que zero.");
    }

    if (state.editingReceivableId) {
      await api(`/receivables/${state.editingReceivableId}`, {
        method: "PUT",
        body: JSON.stringify(payload),
      });
      setMessage(el.receivableMessage, "Conta atualizada com sucesso.");
    } else {
      await api("/receivables/", {
        method: "POST",
        body: JSON.stringify(payload),
      });
      setMessage(el.receivableMessage, "Conta cadastrada com sucesso.");
    }

    clearReceivableForm();
    await Promise.all([loadReceivables(), loadReceivablesAlertsSummary(), loadTransactions(), loadReports()]);
    renderDashboard();
  } catch (error) {
    setMessage(el.receivableMessage, error.message, true);
  }
});

el.receivableCancelEditBtn.addEventListener("click", () => {
  clearReceivableForm();
  setMessage(el.receivableMessage, "");
});

const debouncedReceivableSearch = debounce(() => {
  syncReceivableFiltersFromUi();
  renderReceivables();
}, 300);

el.receivableFilterSearch.addEventListener("input", debouncedReceivableSearch);
for (const node of [el.receivableFilterStatus, el.receivableFilterStartDate, el.receivableFilterEndDate]) {
  node.addEventListener("change", () => {
    syncReceivableFiltersFromUi();
    renderReceivables();
  });
}
el.receivableFilterResetBtn.addEventListener("click", resetReceivableFilters);

el.receivableTableBody.addEventListener("click", async (event) => {
  const target = event.target;
  if (!(target instanceof HTMLButtonElement)) {
    return;
  }

  const editId = target.getAttribute("data-edit-receivable");
  if (editId) {
    const receivable = state.receivables.find((item) => item.id === Number(editId));
    if (!receivable) {
      return;
    }
    openEditReceivable(receivable);
    setMessage(el.receivableMessage, `Editando conta: ${receivable.description}`);
    return;
  }

  const markReceivedId = target.getAttribute("data-mark-receivable-received");
  if (markReceivedId) {
    try {
      await api(`/receivables/${Number(markReceivedId)}/mark-received`, {
        method: "POST",
        body: JSON.stringify({ generate_transaction: true }),
      });
      setMessage(el.receivableMessage, "Conta marcada como recebida e lancamento gerado.");
      await Promise.all([loadReceivables(), loadReceivablesAlertsSummary(), loadTransactions(), loadReports()]);
      renderDashboard();
    } catch (error) {
      setMessage(el.receivableMessage, error.message, true);
    }
    return;
  }

  const deleteId = target.getAttribute("data-delete-receivable");
  if (deleteId) {
    try {
      const confirmed = await openConfirmModal("Tem certeza que deseja excluir esta conta a receber?", "Excluir conta");
      if (!confirmed) {
        return;
      }
      await api(`/receivables/${Number(deleteId)}`, { method: "DELETE" });
      setMessage(el.receivableMessage, "Conta excluida com sucesso.");
      if (state.editingReceivableId === Number(deleteId)) {
        clearReceivableForm();
      }
      await Promise.all([loadReceivables(), loadReceivablesAlertsSummary(), loadTransactions(), loadReports()]);
      renderDashboard();
    } catch (error) {
      setMessage(el.receivableMessage, error.message, true);
    }
  }
});

el.transactionForm.addEventListener("submit", async (event) => {
  event.preventDefault();
  try {
    const payload = {
      description: document.getElementById("txDescription").value,
      amount: Number(document.getElementById("txAmount").value),
      transaction_type: el.txType.value,
      transaction_date: document.getElementById("txDate").value,
      source_bank_name: el.txBankName.value || null,
      expense_profile: el.txType.value === "expense" ? (el.txExpenseProfile.value || null) : null,
      ministry_id: el.txType.value === "expense" && el.txMinistry.value ? Number(el.txMinistry.value) : null,
      notes: null,
      reference: null,
    };

    syncTransactionCategoryFromInput();
    const catId = el.txCategoryId.value;
    if (catId) {
      payload.category_id = Number(catId);
    } else if (el.txCategoryInput.value.trim()) {
      throw new Error("Categoria nao encontrada. Clique em Adicionar para criar.");
    }

    await api("/transactions/", { method: "POST", body: JSON.stringify(payload) });
    setMessage(el.txMessage, "Lancamento criado com sucesso.");
    event.target.reset();
    el.txCategoryId.value = "";
    el.txCategoryInput.value = "";
    syncExpenseProfileField(el.txType, el.txExpenseProfile);
    syncMinistryField(el.txType, el.txMinistry);
    await Promise.all([loadTransactions(), loadSummary(), loadReports()]);
  } catch (error) {
    setMessage(el.txMessage, error.message, true);
  }
});

el.txAddTypedCategoryBtn.addEventListener("click", async () => {
  try {
    const result = await createCategoryFromTransactionInput();
    if (result.created) {
      setMessage(el.txMessage, `Categoria \"${result.category.name}\" criada com sucesso.`);
      return;
    }
    setMessage(el.txMessage, `Categoria \"${result.category.name}\" ja existe e foi selecionada.`);
  } catch (error) {
    setMessage(el.txMessage, error.message, true);
  }
});

el.txCategoryInput.addEventListener("input", syncTransactionCategoryFromInput);
el.txCategoryInput.addEventListener("change", syncTransactionCategoryFromInput);

const debouncedTransactionSearch = debounce(() => {
  syncTransactionFiltersFromUi();
  renderTransactions();
}, 300);

el.txFilterSearch.addEventListener("input", debouncedTransactionSearch);
el.txFilterSearch.addEventListener("keydown", (event) => {
  if (event.key === "Enter") {
    event.preventDefault();
    syncTransactionFiltersFromUi();
    renderTransactions();
  }
});

for (const node of [
  el.txFilterStartDate,
  el.txFilterEndDate,
  el.txFilterType,
  el.txFilterCategory,
  el.txFilterMinistry,
  el.txFilterAttachment,
  el.txFilterSort,
]) {
  node.addEventListener("change", () => {
    syncTransactionFiltersFromUi();
    renderTransactions();
  });
}

el.txFilterResetBtn.addEventListener("click", resetTransactionFilters);
el.txHeaderDateSort.addEventListener("click", () => toggleTransactionSort("date"));
el.txHeaderAmountSort.addEventListener("click", () => toggleTransactionSort("amount"));
el.txPageSize.addEventListener("change", () => {
  state.txPagination.pageSize = Number(el.txPageSize.value || 25);
  state.txPagination.page = 1;
  saveTransactionFilterState();
  renderTransactions();
});
el.txPagePrevBtn.addEventListener("click", () => {
  state.txPagination.page = Math.max(1, state.txPagination.page - 1);
  renderTransactions();
});
el.txPageNextBtn.addEventListener("click", () => {
  state.txPagination.page += 1;
  renderTransactions();
});

el.categoryForm.addEventListener("submit", async (event) => {
  event.preventDefault();
  try {
    const payload = {
      name: el.categoryName.value.trim(),
      type: el.categoryType.value,
      description: el.categoryDescription.value.trim() || null,
    };

    if (!payload.name) {
      throw new Error("Informe o nome da categoria.");
    }

    if (state.editingCategoryId) {
      await api(`/categories/${state.editingCategoryId}`, {
        method: "PUT",
        body: JSON.stringify(payload),
      });
      setMessage(el.categoryMessage, "Categoria atualizada com sucesso.");
    } else {
      await api("/categories/", {
        method: "POST",
        body: JSON.stringify(payload),
      });
      setMessage(el.categoryMessage, "Categoria criada com sucesso.");
    }

    clearCategoryForm();
    await loadCategories();
  } catch (error) {
    setMessage(el.categoryMessage, error.message, true);
  }
});

el.categoryCancelEditBtn.addEventListener("click", () => {
  clearCategoryForm();
  setMessage(el.categoryMessage, "");
});

el.categoryTableBody.addEventListener("click", async (event) => {
  const target = event.target;
  if (!(target instanceof HTMLButtonElement)) {
    return;
  }

  const editId = target.getAttribute("data-edit-category");
  if (editId) {
    const categoryId = Number(editId);
    const cat = state.categories.find((item) => item.id === categoryId);
    if (!cat) {
      return;
    }
    state.editingCategoryId = categoryId;
    el.categoryName.value = cat.name;
    el.categoryType.value = cat.type || "expense";
    el.categoryDescription.value = cat.description || "";
    setMessage(el.categoryMessage, `Editando categoria: ${cat.name}`);
    return;
  }

  const deleteId = target.getAttribute("data-delete-category");
  if (deleteId) {
    try {
      const categoryId = Number(deleteId);
      const cat = state.categories.find((item) => item.id === categoryId);
      if (cat?.is_system) {
        throw new Error("Categorias de sistema nao podem ser excluidas.");
      }
      const categoryName = cat?.name || "categoria";
      const confirmed = await openConfirmModal(`Tem certeza que deseja excluir a categoria \"${categoryName}\"?`, "Excluir categoria");
      if (!confirmed) {
        return;
      }
      await api(`/categories/${categoryId}`, { method: "DELETE" });
      setMessage(el.categoryMessage, "Categoria excluida com sucesso.");
      clearCategoryForm();
      await loadCategories();
    } catch (error) {
      setMessage(el.categoryMessage, error.message, true);
    }
  }
});

el.ministryForm.addEventListener("submit", async (event) => {
  event.preventDefault();
  try {
    const payload = {
      name: el.ministryName.value.trim(),
      description: el.ministryDescription.value.trim() || null,
    };

    if (!payload.name) {
      throw new Error("Informe o nome do ministerio.");
    }

    if (state.editingMinistryId) {
      await api(`/ministries/${state.editingMinistryId}`, {
        method: "PUT",
        body: JSON.stringify(payload),
      });
      setMessage(el.ministryMessage, "Ministerio atualizado com sucesso.");
    } else {
      await api("/ministries/", {
        method: "POST",
        body: JSON.stringify(payload),
      });
      setMessage(el.ministryMessage, "Ministerio criado com sucesso.");
    }

    clearMinistryForm();
    await loadMinistries();
  } catch (error) {
    setMessage(el.ministryMessage, error.message, true);
  }
});

el.ministryCancelEditBtn.addEventListener("click", () => {
  clearMinistryForm();
  setMessage(el.ministryMessage, "");
});

el.ministryTableBody.addEventListener("click", async (event) => {
  const target = event.target;
  if (!(target instanceof HTMLButtonElement)) {
    return;
  }

  const editId = target.getAttribute("data-edit-ministry");
  if (editId) {
    const ministryId = Number(editId);
    const ministry = state.ministries.find((item) => item.id === ministryId);
    if (!ministry) {
      return;
    }
    state.editingMinistryId = ministryId;
    el.ministryName.value = ministry.name;
    el.ministryDescription.value = ministry.description || "";
    setMessage(el.ministryMessage, `Editando ministerio: ${ministry.name}`);
    return;
  }

  const deleteId = target.getAttribute("data-delete-ministry");
  if (deleteId) {
    try {
      const ministryId = Number(deleteId);
      const confirmed = await openConfirmModal("Tem certeza que deseja excluir este ministerio?", "Excluir ministerio");
      if (!confirmed) {
        return;
      }
      await api(`/ministries/${ministryId}`, { method: "DELETE" });
      setMessage(el.ministryMessage, "Ministerio excluido com sucesso.");
      clearMinistryForm();
      await loadMinistries();
    } catch (error) {
      setMessage(el.ministryMessage, error.message, true);
    }
  }
});

el.deleteCategoryCloseBtn.addEventListener("click", () => closeConfirmModal(false));
el.deleteCategoryCancelBtn.addEventListener("click", () => closeConfirmModal(false));
el.attachmentPreviewCloseBtn.addEventListener("click", closeAttachmentPreviewModal);

el.deleteCategoryModal.addEventListener("click", (event) => {
  if (event.target === el.deleteCategoryModal) {
    closeConfirmModal(false);
  }
});

el.uploadResultModal.addEventListener("click", (event) => {
  if (event.target === el.uploadResultModal) {
    closeUploadModal();
  }
});

el.attachmentPreviewModal.addEventListener("click", (event) => {
  if (event.target === el.attachmentPreviewModal) {
    closeAttachmentPreviewModal();
  }
});

el.payablePaidAtModal.addEventListener("click", (event) => {
  if (event.target === el.payablePaidAtModal) {
    closePayablePaidAtModal(null);
  }
});

el.editPayableModal.addEventListener("click", (event) => {
  if (event.target === el.editPayableModal) {
    closeEditPayableModal();
  }
});

el.editTransactionModal.addEventListener("click", (event) => {
  if (event.target === el.editTransactionModal) {
    closeEditTransactionModal();
  }
});

document.addEventListener("keydown", (event) => {
  const key = String(event.key || "").toLowerCase();

  if (
    key === "n"
    && !event.ctrlKey
    && !event.metaKey
    && !event.altKey
    && !isTypingTarget(event.target)
    && !isAnyModalOpen()
    && !el.transactionsView.classList.contains("hide")
  ) {
    event.preventDefault();
    el.txDescription.focus();
    el.txDescription.select();
    return;
  }

  if (
    key === "l"
    && !event.ctrlKey
    && !event.metaKey
    && !event.altKey
    && !isTypingTarget(event.target)
    && !isAnyModalOpen()
    && !el.transactionsView.classList.contains("hide")
  ) {
    event.preventDefault();
    resetTransactionFilters();
    setMessage(el.txMessage, "Filtros limpos.");
    return;
  }

  if (
    event.key === "/"
    && !event.ctrlKey
    && !event.metaKey
    && !event.altKey
    && !isTypingTarget(event.target)
    && !isAnyModalOpen()
    && !el.transactionsView.classList.contains("hide")
  ) {
    event.preventDefault();
    el.txFilterSearch.focus();
    el.txFilterSearch.select();
    return;
  }

  if (event.key !== "Escape") {
    return;
  }

  if (!el.deleteCategoryModal.classList.contains("hide")) {
    closeConfirmModal(false);
    return;
  }

  if (!el.attachmentPreviewModal.classList.contains("hide")) {
    closeAttachmentPreviewModal();
    return;
  }

  if (!el.editTransactionModal.classList.contains("hide")) {
    closeEditTransactionModal();
    return;
  }

  if (!el.editPayableModal.classList.contains("hide")) {
    closeEditPayableModal();
    return;
  }

  if (!el.uploadResultModal.classList.contains("hide")) {
    closeUploadModal();
    return;
  }

  if (!el.payablePaidAtModal.classList.contains("hide")) {
    closePayablePaidAtModal(null);
    return;
  }

  if (!el.transactionsView.classList.contains("hide") && el.txFilterSearch.value) {
    el.txFilterSearch.value = "";
    syncTransactionFiltersFromUi();
    renderTransactions();
  }
});

el.deleteCategoryConfirmBtn.addEventListener("click", () => closeConfirmModal(true));

el.uploadForm.addEventListener("submit", async (event) => {
  event.preventDefault();
  try {
    const file = document.getElementById("fileInput").files[0];
    if (!file) {
      throw new Error("Selecione um arquivo antes de enviar.");
    }

    const formData = new FormData();
    formData.append("file", file);

    const uploaded = await api("/upload/", { method: "POST", body: formData }, true);
    setMessage(el.uploadMessage, "Arquivo enviado. Processando...");
    event.target.reset();

    openUploadModal();
    const duplicates = await waitUploadCompletion(uploaded.id, uploaded.original_filename || file.name);

    el.modalKeepBothBtn.onclick = async () => {
      try {
        await api(`/upload/${uploaded.id}/retry?include_duplicates=true&reset_existing=true`, { method: "POST" });
        el.modalBody.innerHTML += "<p>Reprocessando para manter ambas as transacoes duplicadas...</p>";
        await waitUploadCompletion(uploaded.id, uploaded.original_filename || file.name);
        await Promise.all([loadTransactions(), loadSummary(), loadReports()]);
      } catch (error) {
        setMessage(el.uploadMessage, error.message, true);
      }
    };

    el.modalDiscardBtn.onclick = async () => {
      closeUploadModal();
      setMessage(el.uploadMessage, `Duplicadas desconsideradas (${duplicates}).`);
      await Promise.all([loadTransactions(), loadSummary(), loadReports()]);
    };

    el.modalChooseOneBtn.onclick = async () => {
      try {
        const list = await loadDuplicatePreview(uploaded.id);
        if (!list.length) {
          el.modalBody.innerHTML += "<p>Nao ha duplicatas elegiveis para selecao manual.</p>";
          return;
        }
        renderDuplicateOptions(list);
      } catch (error) {
        setMessage(el.uploadMessage, error.message, true);
      }
    };

    el.modalApplySelectionBtn.onclick = async () => {
      try {
        const selectedKeys = collectSelectedDuplicateKeys();
        await api(`/upload/${uploaded.id}/retry?include_duplicates=true&reset_existing=true`, { method: "POST" });
        await waitUploadCompletion(uploaded.id, uploaded.original_filename || file.name);
        await api(`/upload/${uploaded.id}/duplicate-selection`, {
          method: "POST",
          body: JSON.stringify({ selected_keys: selectedKeys }),
        });
        closeUploadModal();
        setMessage(el.uploadMessage, "Selecao de duplicatas aplicada com sucesso.");
        await Promise.all([loadTransactions(), loadSummary(), loadReports()]);
      } catch (error) {
        setMessage(el.uploadMessage, error.message, true);
      }
    };

    el.modalOkBtn.onclick = async () => {
      closeUploadModal();
      await Promise.all([loadTransactions(), loadSummary(), loadReports()]);
    };
  } catch (error) {
    setMessage(el.uploadMessage, error.message, true);
  }
});

el.modalCloseBtn.addEventListener("click", closeUploadModal);

el.payablePaidAtCloseBtn.addEventListener("click", () => closePayablePaidAtModal(null));
el.payablePaidAtCancelBtn.addEventListener("click", () => closePayablePaidAtModal(null));
el.payablePaidAtConfirmBtn.addEventListener("click", () => {
  const paidAt = String(el.payablePaidAtInput.value || "").trim();
  const paymentMethod = String(el.payablePaidMethodInput.value || "").trim();
  if (!paidAt) {
    setMessage(el.payableMessage, "Informe a data de pagamento.", true);
    return;
  }
  if (!paymentMethod) {
    setMessage(el.payableMessage, "Informe a forma de pagamento.", true);
    return;
  }
  closePayablePaidAtModal({ paid_at: paidAt, payment_method: paymentMethod });
});

el.editModalCloseBtn.addEventListener("click", closeEditTransactionModal);
el.editModalCancelBtn.addEventListener("click", closeEditTransactionModal);
el.editPayableCloseBtn.addEventListener("click", closeEditPayableModal);
el.editPayableCancelBtn.addEventListener("click", closeEditPayableModal);
el.editPayableRemoveCurrentAttachmentBtn.addEventListener("click", async (event) => {
  event.preventDefault();
  if (!state.editingPayableId) {
    return;
  }
  try {
    const confirmed = await openConfirmModal("Tem certeza que deseja remover o boleto desta conta?", "Remover boleto");
    if (!confirmed) {
      return;
    }
    await api(`/payables/${state.editingPayableId}/attachment`, { method: "DELETE" });
    el.editPayableAttachmentBlockCurrent.classList.add("hide");
    setMessage(el.payableMessage, "Boleto removido com sucesso.");
  } catch (error) {
    setMessage(el.payableMessage, error.message, true);
  }
});

el.editTransactionForm.addEventListener("submit", async (event) => {
  event.preventDefault();
  try {
    if (!state.editingTransactionId) {
      throw new Error("Nenhum lancamento selecionado para edicao.");
    }

    const amountValue = Number(el.editTxAmount.value);
    if (!Number.isFinite(amountValue) || amountValue <= 0) {
      throw new Error("Informe um valor valido maior que zero.");
    }

    const payload = {
      description: el.editTxDescription.value.trim(),
      amount: amountValue,
      transaction_type: el.editTxType.value,
      transaction_date: el.editTxDate.value,
      source_bank_name: el.editTxBankName.value || null,
      expense_profile: el.editTxType.value === "expense" ? (el.editTxExpenseProfile.value || null) : null,
      ministry_id: el.editTxType.value === "expense" && el.editTxMinistry.value ? Number(el.editTxMinistry.value) : null,
      category_id: el.editTxCategory.value ? Number(el.editTxCategory.value) : null,
    };

    await api(`/transactions/${state.editingTransactionId}`, {
      method: "PUT",
      body: JSON.stringify(payload),
    });

    const attachmentUploaded = await uploadAttachmentForEditingTransaction(false);

    closeEditTransactionModal();
    setMessage(
      el.txMessage,
      attachmentUploaded
        ? "Lancamento atualizado e anexo enviado com sucesso."
        : "Lancamento atualizado e aprendizado registrado.",
    );
    await Promise.all([loadTransactions(), loadSummary(), loadReports()]);
  } catch (error) {
    setMessage(el.txMessage, error.message, true);
  }
});

el.editTxUploadAttachmentBtn.addEventListener("click", async () => {
  try {
    const sent = await uploadAttachmentForEditingTransaction(true);
    if (!sent) {
      throw new Error("Selecione um arquivo PDF ou imagem para anexar.");
    }
  } catch (error) {
    setMessage(el.txMessage, error.message, true);
  }
});

el.reportYear.addEventListener("change", async () => {
  try {
    await loadReports();
  } catch (error) {
    setMessage(el.reportMessage, error.message, true);
  }
});

for (const btn of el.navButtons) {
  btn.addEventListener("click", async () => {
    setActiveView(btn.dataset.view);
    if (btn.dataset.view === "payablesView") {
      try {
        await loadPayables();
      } catch (error) {
        setMessage(el.payableMessage, error.message, true);
      }
    }
    if (btn.dataset.view === "receivablesView") {
      try {
        await loadReceivables();
      } catch (error) {
        setMessage(el.receivableMessage, error.message, true);
      }
    }
    if (btn.dataset.view === "dashboardView") {
      try {
        await loadPayablesAlertsSummary();
        await loadReceivablesAlertsSummary();
        renderDashboard();
      } catch (error) {
        setMessage(el.dashboardMessage, error.message, true);
      }
    }
  });
}

el.txType.addEventListener("change", () => {
  syncExpenseProfileField(el.txType, el.txExpenseProfile);
  syncMinistryField(el.txType, el.txMinistry);
  syncTransactionCategoryFromInput();
});

el.editTxType.addEventListener("change", () => {
  syncExpenseProfileField(el.editTxType, el.editTxExpenseProfile);
  syncMinistryField(el.editTxType, el.editTxMinistry);
});

document.getElementById("txDate").value = new Date().toISOString().slice(0, 10);
el.payableDueDate.value = new Date().toISOString().slice(0, 10);
el.receivableDueDate.value = new Date().toISOString().slice(0, 10);
loadTransactionFilterState();
populateBudgetReferenceOptions();
syncExpenseProfileField(el.txType, el.txExpenseProfile);
syncExpenseProfileField(el.editTxType, el.editTxExpenseProfile);
syncMinistryField(el.txType, el.txMinistry);
syncMinistryField(el.editTxType, el.editTxMinistry);
clearPayableForm();
clearReceivableForm();
initializeApp();
