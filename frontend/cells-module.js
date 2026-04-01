(function () {
  const apiPrefix = "/api/v1";
  const roleTagsStorageKey = "cellsMemberRoleTags";

  const el = {
    financeBtn: document.getElementById("moduleFinanceBtn"),
    cellsBtn: document.getElementById("moduleCellsBtn"),
    financeModule: document.getElementById("financeModule"),
    cellsModule: document.getElementById("cellsModule"),
    cellsNavDashboardBtn: document.getElementById("cellsNavDashboardBtn"),
    cellsNavCellsBtn: document.getElementById("cellsNavCellsBtn"),
    cellsNavPeopleBtn: document.getElementById("cellsNavPeopleBtn"),
    cellsNavMeetingsBtn: document.getElementById("cellsNavMeetingsBtn"),
    cellsNavLeadersBtn: document.getElementById("cellsNavLeadersBtn"),
    cellsNavDisciplersBtn: document.getElementById("cellsNavDisciplersBtn"),
    cellsNavLostSheepBtn: document.getElementById("cellsNavLostSheepBtn"),
    cellsDashboardView: document.getElementById("cellsDashboardView"),
    cellsListView: document.getElementById("cellsListView"),
    cellsPeopleView: document.getElementById("cellsPeopleView"),
    cellsMeetingsView: document.getElementById("cellsMeetingsView"),
    cellsLeadersView: document.getElementById("cellsLeadersView"),
    cellsDisciplersView: document.getElementById("cellsDisciplersView"),
    cellsLostSheepView: document.getElementById("cellsLostSheepView"),
    cellsPeopleRefreshBtn: document.getElementById("cellsPeopleRefreshBtn"),
    cellsPeopleCellSelect: document.getElementById("cellsPeopleCellSelect"),
    cellsPeopleVisitorForm: document.getElementById("cellsPeopleVisitorForm"),
    cellsPeopleVisitorName: document.getElementById("cellsPeopleVisitorName"),
    cellsPeopleVisitorContact: document.getElementById("cellsPeopleVisitorContact"),
    cellsPeopleVisitorCountStartDate: document.getElementById("cellsPeopleVisitorCountStartDate"),
    cellsPeopleAssiduoForm: document.getElementById("cellsPeopleAssiduoForm"),
    cellsPeopleAssiduoName: document.getElementById("cellsPeopleAssiduoName"),
    cellsPeopleAssiduoContact: document.getElementById("cellsPeopleAssiduoContact"),
    cellsPeopleAssiduoCountStartDate: document.getElementById("cellsPeopleAssiduoCountStartDate"),
    cellsPeopleMemberForm: document.getElementById("cellsPeopleMemberForm"),
    cellsPeopleMemberName: document.getElementById("cellsPeopleMemberName"),
    cellsPeopleMemberContact: document.getElementById("cellsPeopleMemberContact"),
    cellsPeopleMemberCountStartDate: document.getElementById("cellsPeopleMemberCountStartDate"),
    cellsPeopleVisitorsBody: document.getElementById("cellsPeopleVisitorsBody"),
    cellsPeopleAssiduosBody: document.getElementById("cellsPeopleAssiduosBody"),
    cellsPeopleMembersBody: document.getElementById("cellsPeopleMembersBody"),
    cellsMeetingsRefreshBtn: document.getElementById("cellsMeetingsRefreshBtn"),
    cellsMeetingsCellSelect: document.getElementById("cellsMeetingsCellSelect"),
    cellsMeetingsStartDate: document.getElementById("cellsMeetingsStartDate"),
    cellsMeetingsEndDate: document.getElementById("cellsMeetingsEndDate"),
    cellsMeetingsForm: document.getElementById("cellsMeetingsForm"),
    cellsMeetingDate: document.getElementById("cellsMeetingDate"),
    cellsMeetingTheme: document.getElementById("cellsMeetingTheme"),
    cellsMeetingNotes: document.getElementById("cellsMeetingNotes"),
    cellsMeetingsBody: document.getElementById("cellsMeetingsBody"),
    cellsMeetingsPrevBtn: document.getElementById("cellsMeetingsPrevBtn"),
    cellsMeetingsPageInfo: document.getElementById("cellsMeetingsPageInfo"),
    cellsMeetingsNextBtn: document.getElementById("cellsMeetingsNextBtn"),
    cellsAttendanceModal: document.getElementById("cellsAttendanceModal"),
    cellsAttendanceModalTitle: document.getElementById("cellsAttendanceModalTitle"),
    cellsAttendanceModalCloseBtn: document.getElementById("cellsAttendanceModalCloseBtn"),
    cellsAttendanceMeetingId: document.getElementById("cellsAttendanceMeetingId"),
    cellsAttendanceBody: document.getElementById("cellsAttendanceBody"),
    cellsAttendanceModalCancelBtn: document.getElementById("cellsAttendanceModalCancelBtn"),
    cellsAttendanceModalSaveAndPeopleBtn: document.getElementById("cellsAttendanceModalSaveAndPeopleBtn"),
    cellsAttendanceModalSaveBtn: document.getElementById("cellsAttendanceModalSaveBtn"),
    cellsCellsAddBtn: document.getElementById("cellsCellsAddBtn"),
    cellsCellsRefreshBtn: document.getElementById("cellsCellsRefreshBtn"),
    cellsLeadersAddBtn: document.getElementById("cellsLeadersAddBtn"),
    cellsLeadersRefreshBtn: document.getElementById("cellsLeadersRefreshBtn"),
    cellsDisciplersAddBtn: document.getElementById("cellsDisciplersAddBtn"),
    cellsDisciplersRefreshBtn: document.getElementById("cellsDisciplersRefreshBtn"),
    cellsListBody: document.getElementById("cellsListBody"),
    cellsLeadersBody: document.getElementById("cellsLeadersBody"),
    cellsDisciplersBody: document.getElementById("cellsDisciplersBody"),
    cellsCellModal: document.getElementById("cellsCellModal"),
    cellsCellModalTitle: document.getElementById("cellsCellModalTitle"),
    cellsCellModalCloseBtn: document.getElementById("cellsCellModalCloseBtn"),
    cellsCellModalForm: document.getElementById("cellsCellModalForm"),
    cellsCellModalId: document.getElementById("cellsCellModalId"),
    cellsCellModalName: document.getElementById("cellsCellModalName"),
    cellsCellModalWeekday: document.getElementById("cellsCellModalWeekday"),
    cellsCellModalMeetingTime: document.getElementById("cellsCellModalMeetingTime"),
    cellsCellModalAddress: document.getElementById("cellsCellModalAddress"),
    cellsCellModalStatus: document.getElementById("cellsCellModalStatus"),
    cellsCellModalDisciplerId: document.getElementById("cellsCellModalDisciplerId"),
    cellsCellModalLeaderId: document.getElementById("cellsCellModalLeaderId"),
    cellsCellModalDisableBtn: document.getElementById("cellsCellModalDisableBtn"),
    cellsCellModalDeleteBtn: document.getElementById("cellsCellModalDeleteBtn"),
    cellsMemberModal: document.getElementById("cellsMemberModal"),
    cellsMemberModalTitle: document.getElementById("cellsMemberModalTitle"),
    cellsMemberModalCloseBtn: document.getElementById("cellsMemberModalCloseBtn"),
    cellsMemberModalForm: document.getElementById("cellsMemberModalForm"),
    cellsMemberModalId: document.getElementById("cellsMemberModalId"),
    cellsMemberModalRoleTag: document.getElementById("cellsMemberModalRoleTag"),
    cellsMemberModalName: document.getElementById("cellsMemberModalName"),
    cellsMemberModalContact: document.getElementById("cellsMemberModalContact"),
    cellsMemberModalStatus: document.getElementById("cellsMemberModalStatus"),
    cellsMemberModalCountStartDate: document.getElementById("cellsMemberModalCountStartDate"),
    cellsMemberModalCellId: document.getElementById("cellsMemberModalCellId"),
    cellsMemberModalDisableBtn: document.getElementById("cellsMemberModalDisableBtn"),
    cellsMemberModalTransferBtn: document.getElementById("cellsMemberModalTransferBtn"),
    cellsTransferMemberModal: document.getElementById("cellsTransferMemberModal"),
    cellsTransferMemberModalCloseBtn: document.getElementById("cellsTransferMemberModalCloseBtn"),
    cellsTransferMemberModalForm: document.getElementById("cellsTransferMemberModalForm"),
    cellsTransferMemberModalMemberId: document.getElementById("cellsTransferMemberModalMemberId"),
    cellsTransferMemberModalTargetCell: document.getElementById("cellsTransferMemberModalTargetCell"),
    cellsTransferMemberModalReason: document.getElementById("cellsTransferMemberModalReason"),
    cellsTransferMemberModalCancelBtn: document.getElementById("cellsTransferMemberModalCancelBtn"),
    cellsTransferMemberModalSaveBtn: document.getElementById("cellsTransferMemberModalSaveBtn"),
    cellsLostSheepBody: document.getElementById("cellsLostSheepBody"),
    cellsLostSheepRefreshBtn: document.getElementById("cellsLostSheepRefreshBtn"),
    cellsLostSheepModal: document.getElementById("cellsLostSheepModal"),
    cellsLostSheepModalCloseBtn: document.getElementById("cellsLostSheepModalCloseBtn"),
    cellsLostSheepModalForm: document.getElementById("cellsLostSheepModalForm"),
    cellsLostSheepModalMemberId: document.getElementById("cellsLostSheepModalMemberId"),
    cellsLostSheepModalCellId: document.getElementById("cellsLostSheepModalCellId"),
    cellsLostSheepModalMemberName: document.getElementById("cellsLostSheepModalMemberName"),
    cellsLostSheepModalPhone: document.getElementById("cellsLostSheepModalPhone"),
    cellsLostSheepModalObservation: document.getElementById("cellsLostSheepModalObservation"),
    cellsLostSheepModalCancelBtn: document.getElementById("cellsLostSheepModalCancelBtn"),
    cellsLostSheepModalConfirmBtn: document.getElementById("cellsLostSheepModalConfirmBtn"),
    cellsLostSheepVisitModal: document.getElementById("cellsLostSheepVisitModal"),
    cellsLostSheepVisitModalTitle: document.getElementById("cellsLostSheepVisitModalTitle"),
    cellsLostSheepVisitModalCloseBtn: document.getElementById("cellsLostSheepVisitModalCloseBtn"),
    cellsLostSheepVisitModalForm: document.getElementById("cellsLostSheepVisitModalForm"),
    cellsLostSheepVisitModalId: document.getElementById("cellsLostSheepVisitModalId"),
    cellsLostSheepVisitModalObservation: document.getElementById("cellsLostSheepVisitModalObservation"),
    cellsLostSheepVisitModalCancelBtn: document.getElementById("cellsLostSheepVisitModalCancelBtn"),
    cellsLostSheepVisitModalConfirmBtn: document.getElementById("cellsLostSheepVisitModalConfirmBtn"),
    cellsConfirmModal: document.getElementById("cellsConfirmModal"),
    cellsConfirmModalMessage: document.getElementById("cellsConfirmModalMessage"),
    cellsConfirmModalCloseBtn: document.getElementById("cellsConfirmModalCloseBtn"),
    cellsConfirmModalCancelBtn: document.getElementById("cellsConfirmModalCancelBtn"),
    cellsConfirmModalConfirmBtn: document.getElementById("cellsConfirmModalConfirmBtn"),
    cellsCreateCellView: document.getElementById("cellsCreateCellView"),
    cellsCreateDisciplerView: document.getElementById("cellsCreateDisciplerView"),
    cellsCreateLeaderView: document.getElementById("cellsCreateLeaderView"),
    cellsMessage: document.getElementById("cellsMessage"),
    cellsSelect: document.getElementById("cellsSelect"),
    cellsStartDate: document.getElementById("cellsStartDate"),
    cellsEndDate: document.getElementById("cellsEndDate"),
    cellsApplyFiltersBtn: document.getElementById("cellsApplyFiltersBtn"),
    cellsRefreshBtn: document.getElementById("cellsRefreshBtn"),
    cellsKpiActiveStart: document.getElementById("cellsKpiActiveStart"),
    cellsKpiRetained: document.getElementById("cellsKpiRetained"),
    cellsKpiRetentionRate: document.getElementById("cellsKpiRetentionRate"),
    cellsKpiRecurringTotal: document.getElementById("cellsKpiRecurringTotal"),
    cellsKpiVisitorsPeriod: document.getElementById("cellsKpiVisitorsPeriod"),
    cellsKpiMembersFrequency: document.getElementById("cellsKpiMembersFrequency"),
    cellsKpiAssiduousCount: document.getElementById("cellsKpiAssiduousCount"),
    cellsKpiMissingWeeks: document.getElementById("cellsKpiMissingWeeks"),
    cellsKpiLowFrequencyMeetings: document.getElementById("cellsKpiLowFrequencyMeetings"),
    cellsKpiFrequencyTrend: document.getElementById("cellsKpiFrequencyTrend"),
    cellsRecurringBody: document.getElementById("cellsRecurringBody"),
    cellsMissingWeeksBody: document.getElementById("cellsMissingWeeksBody"),
    cellsMissingMembersBody: document.getElementById("cellsMissingMembersBody"),
    cellsRetentionChart: document.getElementById("cellsRetentionChart"),
    cellsVisitorsChart: document.getElementById("cellsVisitorsChart"),
    cellsHistoryChart: document.getElementById("cellsHistoryChart"),
    cellsStageCountsChart: document.getElementById("cellsStageCountsChart"),
    cellsInsightsChart: document.getElementById("cellsInsightsChart"),
    cellsDashboardLostSheepPending: document.getElementById("cellsDashboardLostSheepPending"),
    cellsDashboardLostSheepVisited: document.getElementById("cellsDashboardLostSheepVisited"),
    cellsDashboardLostSheepBody: document.getElementById("cellsDashboardLostSheepBody"),
    cellsCreateCellForm: document.getElementById("cellsCreateCellForm"),
    cellsCreateCellName: document.getElementById("cellsCreateCellName"),
    cellsCreateCellWeekday: document.getElementById("cellsCreateCellWeekday"),
    cellsCreateCellMeetingTime: document.getElementById("cellsCreateCellMeetingTime"),
    cellsCreateCellAddress: document.getElementById("cellsCreateCellAddress"),
    cellsCreateCellDisciplerInput: document.getElementById("cellsCreateCellDisciplerInput"),
    cellsCreateCellDisciplerId: document.getElementById("cellsCreateCellDisciplerId"),
    cellsCreateCellAddDisciplerBtn: document.getElementById("cellsCreateCellAddDisciplerBtn"),
    cellsCreateCellLeaderInput: document.getElementById("cellsCreateCellLeaderInput"),
    cellsCreateCellLeaderId: document.getElementById("cellsCreateCellLeaderId"),
    cellsCreateCellAddLeaderBtn: document.getElementById("cellsCreateCellAddLeaderBtn"),
    cellsCreateDisciplerForm: document.getElementById("cellsCreateDisciplerForm"),
    cellsCreateDisciplerName: document.getElementById("cellsCreateDisciplerName"),
    cellsCreateDisciplerContact: document.getElementById("cellsCreateDisciplerContact"),
    cellsCreateLeaderForm: document.getElementById("cellsCreateLeaderForm"),
    cellsCreateLeaderName: document.getElementById("cellsCreateLeaderName"),
    cellsCreateLeaderContact: document.getElementById("cellsCreateLeaderContact"),
    cellsCellInfoCard: document.getElementById("cellsCellInfoCard"),
    cellsCellInfoName: document.getElementById("cellsCellInfoName"),
    cellsCellInfoMembers: document.getElementById("cellsCellInfoMembers"),
    cellsCellInfoAssiduos: document.getElementById("cellsCellInfoAssiduos"),
    cellsCellInfoVisitors: document.getElementById("cellsCellInfoVisitors"),
    cellsCellInfoLeader: document.getElementById("cellsCellInfoLeader"),
  };

  if (!el.financeBtn || !el.cellsBtn || !el.financeModule || !el.cellsModule) return;

  const state = {
    initialized: false,
    currentUserRole: "",
    retentionChart: null,
    visitorsChart: null,
    historyChart: null,
    stageCountsChart: null,
    insightsChart: null,
    cells: [],
    members: [],
    availableMembersForCellCreation: [],
    memberRoleTags: {},
    leadershipByCellId: {},
    lostSheep: [],
    peopleByStage: {
      visitor: [],
      assiduo: [],
      member: [],
    },
    meetings: [],
    attendanceMembers: [],
    meetingAttendanceSummary: {},
    meetingsExpectedTotal: 0,
    meetingsExpectedTotalByMeeting: {},
    meetingsPagination: {
      page: 1,
      pageSize: 8,
    },
    pendingConfirmAction: null,
    pendingConfirmErrorMessage: "Falha ao executar exclusao.",
    currentView: "dashboard",
  };

  function isLeaderMode() {
    return state.currentUserRole === "leader";
  }

  function applyRoleLayout() {
    if (!isLeaderMode()) return;

    if (el.financeBtn) {
      el.financeBtn.classList.add("hide");
      el.financeBtn.disabled = true;
    }
  }

  async function loadCurrentUserRole() {
    if (state.currentUserRole) return state.currentUserRole;

    const roleFromStorage = valueOr(localStorage.getItem("currentUserRole"), "").toLowerCase();
    if (roleFromStorage) {
      state.currentUserRole = roleFromStorage;
      return state.currentUserRole;
    }

    const me = await api("/auth/me");
    state.currentUserRole = valueOr(me.role, "").toLowerCase();
    return state.currentUserRole;
  }

  function loadRoleTagsFromStorage() {
    try {
      const raw = localStorage.getItem(roleTagsStorageKey);
      if (!raw) return {};
      const parsed = JSON.parse(raw);
      return parsed && typeof parsed === "object" ? parsed : {};
    } catch (_error) {
      return {};
    }
  }

  function saveRoleTagsToStorage() {
    try {
      localStorage.setItem(roleTagsStorageKey, JSON.stringify(state.memberRoleTags));
    } catch (_error) {
    }
  }

  function setMemberRoleTag(memberId, roleTag) {
    if (!memberId || !roleTag) return;
    state.memberRoleTags[String(memberId)] = roleTag;
    saveRoleTagsToStorage();
  }

  function tagMembersFromAssignments(assignmentsByCell) {
    assignmentsByCell.forEach((assignments) => {
      if (!Array.isArray(assignments)) return;
      assignments.forEach((assignment) => {
        const memberId = toNumber(assignment ? assignment.member_id : 0, 0);
        if (!memberId) return;
        if (assignment.role === "co_leader") {
          state.memberRoleTags[String(memberId)] = "discipler";
        }
        if (assignment.role === "leader") {
          state.memberRoleTags[String(memberId)] = "leader";
        }
      });
    });
    saveRoleTagsToStorage();
  }

  function valueOr(value, fallback) {
    if (value === undefined || value === null || value === "") return fallback;
    return value;
  }

  function toNumber(value, fallback) {
    const number = Number(value);
    return Number.isNaN(number) ? fallback : number;
  }

  function escapeHtml(value) {
    return String(value)
      .replaceAll("&", "&amp;")
      .replaceAll("<", "&lt;")
      .replaceAll(">", "&gt;")
      .replaceAll('"', "&quot;")
      .replaceAll("'", "&#39;");
  }

  function setCellsMessage(text, isError) {
    if (!el.cellsMessage) return;
    el.cellsMessage.textContent = valueOr(text, "");
    el.cellsMessage.style.color = isError ? "#b42318" : "#5f6b6d";
  }

  function getToken() {
    return valueOr(localStorage.getItem("accessToken"), "");
  }

  async function api(path, options) {
    const token = getToken();
    if (!token) {
      throw new Error("Sessao nao autenticada. Faca login no Financeiro primeiro.");
    }

    const requestOptions = options || {};
    const headers = Object.assign({}, requestOptions.headers || {}, {
      Authorization: `Bearer ${token}`,
    });

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
        if (body && typeof body === "object") {
          if (typeof body.detail === "string") detail = body.detail;
          if (typeof body.msg === "string") detail = body.msg;
        }
      } catch (_error) {
      }

      if (detail.toLowerCase().includes("could not validate credentials")) {
        localStorage.removeItem("accessToken");
        throw new Error("Sessao expirada. Faca login novamente no Financeiro.");
      }
      throw new Error(detail);
    }

    if (response.status === 204) return null;
    return response.json();
  }

  function setActiveModule(moduleName) {
    const isFinance = moduleName === "finance";
    el.financeBtn.classList.toggle("active", isFinance);
    el.cellsBtn.classList.toggle("active", !isFinance);
    el.financeModule.classList.toggle("hide", !isFinance);
    el.cellsModule.classList.toggle("hide", isFinance);
  }

  function setCellsView(viewName) {
    state.currentView = viewName;

    if (el.cellsDashboardView) el.cellsDashboardView.classList.toggle("hide", viewName !== "dashboard");
    if (el.cellsListView) el.cellsListView.classList.toggle("hide", viewName !== "cells");
    if (el.cellsPeopleView) el.cellsPeopleView.classList.toggle("hide", viewName !== "people");
    if (el.cellsMeetingsView) el.cellsMeetingsView.classList.toggle("hide", viewName !== "meetings");
    if (el.cellsLeadersView) el.cellsLeadersView.classList.toggle("hide", viewName !== "leaders");
    if (el.cellsDisciplersView) el.cellsDisciplersView.classList.toggle("hide", viewName !== "disciplers");
    if (el.cellsLostSheepView) el.cellsLostSheepView.classList.toggle("hide", viewName !== "lost-sheep");
    if (el.cellsCreateCellView) el.cellsCreateCellView.classList.add("hide");
    if (el.cellsCreateDisciplerView) el.cellsCreateDisciplerView.classList.add("hide");
    if (el.cellsCreateLeaderView) el.cellsCreateLeaderView.classList.add("hide");

    if (el.cellsNavDashboardBtn) el.cellsNavDashboardBtn.classList.toggle("active", viewName === "dashboard");
    if (el.cellsNavCellsBtn) el.cellsNavCellsBtn.classList.toggle("active", viewName === "cells");
    if (el.cellsNavPeopleBtn) el.cellsNavPeopleBtn.classList.toggle("active", viewName === "people");
    if (el.cellsNavMeetingsBtn) el.cellsNavMeetingsBtn.classList.toggle("active", viewName === "meetings");
    if (el.cellsNavLeadersBtn) el.cellsNavLeadersBtn.classList.toggle("active", viewName === "leaders");
    if (el.cellsNavDisciplersBtn) el.cellsNavDisciplersBtn.classList.toggle("active", viewName === "disciplers");
    if (el.cellsNavLostSheepBtn) el.cellsNavLostSheepBtn.classList.toggle("active", viewName === "lost-sheep");
  }

  function formatDate(date) {
    return date.toISOString().slice(0, 10);
  }

  function getTodayIsoDate() {
    return new Date().toISOString().slice(0, 10);
  }

  function resetPeopleCountStartDateInputs() {
    const today = getTodayIsoDate();
    if (el.cellsPeopleVisitorCountStartDate) el.cellsPeopleVisitorCountStartDate.value = today;
    if (el.cellsPeopleAssiduoCountStartDate) el.cellsPeopleAssiduoCountStartDate.value = today;
    if (el.cellsPeopleMemberCountStartDate) el.cellsPeopleMemberCountStartDate.value = today;
  }

  function applyPreset(days) {
    const end = new Date();
    const start = new Date();
    start.setDate(end.getDate() - days);
    el.cellsStartDate.value = formatDate(start);
    el.cellsEndDate.value = formatDate(end);
  }

  function createOrUpdateChart(currentChart, canvas, config) {
    if (!canvas) return currentChart;
    if (typeof Chart === "undefined") {
      const host = canvas.parentElement;
      if (host && !host.querySelector(".cells-chart-warning")) {
        const warning = document.createElement("p");
        warning.className = "cells-chart-warning";
        warning.textContent = "Nao foi possivel carregar biblioteca de graficos (Chart.js).";
        host.appendChild(warning);
      }
      return currentChart;
    }

    const host = canvas.parentElement;
    if (host) {
      const warning = host.querySelector(".cells-chart-warning");
      if (warning) warning.remove();
    }

    if (currentChart) currentChart.destroy();

    const baseOptions = {
      responsive: true,
      maintainAspectRatio: false,
      devicePixelRatio: Math.max(window.devicePixelRatio || 1, 1),
    };
    const mergedConfig = {
      ...config,
      options: {
        ...baseOptions,
        ...(config && config.options ? config.options : {}),
      },
    };

    return new Chart(canvas.getContext("2d"), mergedConfig);
  }

  function renderRecurringVisitors(visitors) {
    if (!el.cellsRecurringBody) return;
    if (!visitors.length) {
      el.cellsRecurringBody.innerHTML = '<tr><td colspan="3">Sem visitantes recorrentes no periodo.</td></tr>';
      return;
    }

    el.cellsRecurringBody.innerHTML = visitors
      .slice(0, 12)
      .map((item) => `<tr><td>${escapeHtml(valueOr(item.full_name, "-"))}</td><td>${escapeHtml(valueOr(item.contact, "-"))}</td><td>${toNumber(item.visits_count, 0)}</td></tr>`)
      .join("");
  }

  function renderRetention(retention) {
    if (!retention) return;

    const activeAtStart = toNumber(retention.active_at_start, 0);
    const retainedMembers = toNumber(retention.retained_members, 0);
    const activeAtEnd = toNumber(retention.active_at_end, 0);
    const retentionRatePercent = toNumber(retention.retention_rate_percent, 0);

    el.cellsKpiActiveStart.textContent = String(activeAtStart);
    el.cellsKpiRetained.textContent = String(retainedMembers);
    el.cellsKpiRetentionRate.textContent = `${retentionRatePercent.toFixed(1)}%`;

    state.retentionChart = createOrUpdateChart(state.retentionChart, el.cellsRetentionChart, {
      type: "bar",
      data: {
        labels: ["Ativos no inicio", "Retidos", "Ativos no fim"],
        datasets: [{
          label: "Membros",
          data: [activeAtStart, retainedMembers, activeAtEnd],
          backgroundColor: ["#1565c0", "#0a8f72", "#4f6fbf"],
          borderRadius: 10,
        }],
      },
      options: { responsive: true, maintainAspectRatio: false, plugins: { legend: { display: false } } },
    });
  }

  function renderVisitors(recurring) {
    const visitors = recurring && Array.isArray(recurring.visitors) ? recurring.visitors : [];
    const recurringTotal = toNumber(recurring ? recurring.total_recurring_visitors : 0, 0);
    const topVisitors = visitors.slice(0, 6);

    el.cellsKpiRecurringTotal.textContent = String(recurringTotal);
    renderRecurringVisitors(visitors);

    if (!topVisitors.length) {
      state.visitorsChart = createOrUpdateChart(state.visitorsChart, el.cellsVisitorsChart, {
        type: "bar",
        data: {
          labels: ["Sem dados"],
          datasets: [{ label: "Visitas", data: [0], backgroundColor: "#d8e1ec", borderRadius: 8 }],
        },
        options: { responsive: true, maintainAspectRatio: false, plugins: { legend: { display: false } } },
      });
    }
  }

  function renderHistory(history) {
    const data = Array.isArray(history) ? history : [];

    if (el.cellsKpiFrequencyTrend) {
      let trendText = "→ Estavel";
      let trendClass = "cells-trend-stable";
      if (data.length >= 2) {
        const first = toNumber(data[0].average_frequency_percent, 0);
        const last = toNumber(data[data.length - 1].average_frequency_percent, 0);
        const delta = last - first;
        if (delta >= 3) {
          trendText = `↑ Alta (+${delta.toFixed(1)} p.p.)`;
          trendClass = "cells-trend-up";
        } else if (delta <= -3) {
          trendText = `↓ Queda (${delta.toFixed(1)} p.p.)`;
          trendClass = "cells-trend-down";
        }
      }
      el.cellsKpiFrequencyTrend.textContent = trendText;
      el.cellsKpiFrequencyTrend.classList.remove("cells-trend-up", "cells-trend-down", "cells-trend-stable");
      el.cellsKpiFrequencyTrend.classList.add(trendClass);
    }

  }

  function renderVisitorsByDateChart(points) {
    const data = Array.isArray(points) ? points : [];
    state.retentionChart = createOrUpdateChart(state.retentionChart, el.cellsRetentionChart, {
      type: "line",
      data: {
        labels: data.map((item) => formatDatePtBr(item.date)),
        datasets: [{
          label: "Visitantes",
          data: data.map((item) => toNumber(item.visitors_count, 0)),
          borderColor: "#1565c0",
          backgroundColor: "rgba(21, 101, 192, 0.18)",
          tension: 0.35,
          fill: true,
        }],
      },
      options: { responsive: true, maintainAspectRatio: false },
    });
  }

  function renderWeeklyPresenceChart(points) {
    const data = Array.isArray(points) ? points : [];
    state.visitorsChart = createOrUpdateChart(state.visitorsChart, el.cellsVisitorsChart, {
      type: "bar",
      data: {
        labels: data.map((item) => {
          const start = valueOr(item.week_start, null);
          const end = valueOr(item.week_end, null);
          if (start && end && start === end) return formatDatePtBr(start);
          return `${formatDatePtBr(start)} - ${formatDatePtBr(end)}`;
        }),
        datasets: [
          {
            label: "P (presentes)",
            data: data.map((item) => toNumber(item.present_total, 0)),
            backgroundColor: "#1565c0",
            borderRadius: 8,
            maxBarThickness: 36,
          },
          {
            label: "A (ausentes)",
            data: data.map((item) => toNumber(item.absent_total, 0)),
            backgroundColor: "#f57c00",
            borderRadius: 8,
            maxBarThickness: 36,
          },
          {
            label: "J (justificados)",
            data: data.map((item) => toNumber(item.justified_total, 0)),
            backgroundColor: "#7b8ca2",
            borderRadius: 8,
            maxBarThickness: 36,
          },
          {
            label: "T (total)",
            data: data.map((item) => toNumber(item.expected_total, 0)),
            type: "line",
            borderColor: "#0a8f72",
            backgroundColor: "rgba(10, 143, 114, 0.2)",
            borderWidth: 2,
            pointRadius: 3,
            pointHoverRadius: 4,
            tension: 0.25,
            yAxisID: "y",
          },
        ],
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        scales: {
          x: {
            ticks: {
              maxRotation: 0,
              autoSkip: true,
              maxTicksLimit: 6,
            },
          },
          y: {
            beginAtZero: true,
            ticks: {
              precision: 0,
            },
          },
        },
      },
    });
  }

  function renderVisitorRetentionChart(buckets) {
    const data = Array.isArray(buckets) ? buckets : [];
    state.historyChart = createOrUpdateChart(state.historyChart, el.cellsHistoryChart, {
      type: "bar",
      data: {
        labels: data.map((item) => valueOr(item.bucket_label, "-")),
        datasets: [{
          label: "Qtde visitantes",
          data: data.map((item) => toNumber(item.visitors_count, 0)),
          backgroundColor: ["#90caf9", "#64b5f6", "#42a5f5", "#1e88e5"],
          borderRadius: 8,
        }],
      },
      options: { responsive: true, maintainAspectRatio: false, plugins: { legend: { display: false } } },
    });
  }

  function renderCompositionPieChart(slices) {
    const data = Array.isArray(slices) ? slices : [];
    state.insightsChart = createOrUpdateChart(state.insightsChart, el.cellsInsightsChart, {
      type: "pie",
      data: {
        labels: data.map((item) => `${valueOr(item.label, "-")} (${toNumber(item.percent, 0).toFixed(1)}%)`),
        datasets: [{
          label: "Composicao",
          data: data.map((item) => toNumber(item.count, 0)),
          backgroundColor: ["#f57c00", "#1565c0", "#0a8f72"],
          borderColor: "#ffffff",
          borderWidth: 2,
        }],
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
          legend: { position: "top" },
        },
      },
    });
  }

  function renderStageCountsChart(points) {
    const data = Array.isArray(points) ? points : [];
    state.stageCountsChart = createOrUpdateChart(state.stageCountsChart, el.cellsStageCountsChart, {
      type: "line",
      data: {
        labels: data.map((item) => formatDatePtBr(item.date)),
        datasets: [
          {
            label: "Membros",
            data: data.map((item) => toNumber(item.members_count, 0)),
            borderColor: "#1565c0",
            backgroundColor: "rgba(21, 101, 192, 0.15)",
            pointRadius: 3,
            tension: 0.25,
          },
          {
            label: "Visitantes",
            data: data.map((item) => toNumber(item.visitors_count, 0)),
            borderColor: "#f57c00",
            backgroundColor: "rgba(245, 124, 0, 0.15)",
            pointRadius: 3,
            tension: 0.25,
          },
          {
            label: "Assiduos",
            data: data.map((item) => toNumber(item.assiduous_count, 0)),
            borderColor: "#0a8f72",
            backgroundColor: "rgba(10, 143, 114, 0.15)",
            pointRadius: 3,
            tension: 0.25,
          },
        ],
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        scales: {
          y: {
            beginAtZero: true,
            ticks: {
              precision: 0,
            },
          },
        },
      },
    });
  }

  function renderMissingWeeks(rows) {
    if (!el.cellsMissingWeeksBody) return;
    if (!Array.isArray(rows) || !rows.length) {
      el.cellsMissingWeeksBody.innerHTML = '<tr><td colspan="2">Nenhuma semana sem relatorio no periodo.</td></tr>';
      return;
    }

    // Filter weeks by cell members count_start_date
    const allMembers = state.peopleByStage ? [
      ...(state.peopleByStage.member || []),
      ...(state.peopleByStage.assiduo || []),
      ...(state.peopleByStage.visitor || [])
    ] : [];
    
    const earliestCountDate = allMembers.length > 0
      ? new Date(Math.min(...allMembers.map((m) => new Date(valueOr(m.count_start_date, "1970-01-01")).getTime())))
      : new Date("1970-01-01");

    const filteredRows = rows.filter((week) => {
      const weekStart = new Date(week.week_start);
      return weekStart >= earliestCountDate;
    });

    if (!filteredRows.length) {
      el.cellsMissingWeeksBody.innerHTML = '<tr><td colspan="2">Nenhuma semana sem relatorio no periodo (apos data de cadastro).</td></tr>';
      return;
    }

    el.cellsMissingWeeksBody.innerHTML = filteredRows
      .map((item) => `<tr><td>${escapeHtml(formatDatePtBr(item.week_start))}</td><td>${escapeHtml(formatDatePtBr(item.week_end))}</td></tr>`)
      .join("");
  }

  function renderMissingMembers(meetings) {
    if (!el.cellsMissingMembersBody) return;

    const members = state.peopleByStage ? (state.peopleByStage.member || []) : [];
    const assiduos = state.peopleByStage ? (state.peopleByStage.assiduo || []) : [];
    const allPeople = [...members, ...assiduos];

    if (!Array.isArray(meetings) || meetings.length === 0 || allPeople.length === 0) {
      el.cellsMissingMembersBody.innerHTML = '<tr><td colspan="3">Sem dados ou nenhuma reuniao no periodo.</td></tr>';
      return;
    }

    const meetsCount = meetings.length;
    const peopleWithAbsences = allPeople.map((person) => {
      const absences = meetings.filter((meeting) => {
        const isDueDate = new Date(meeting.meeting_date) >= new Date(valueOr(person.count_start_date, "1970-01-01"));
        if (!isDueDate) return false;
        const attendance = Array.isArray(meeting.attendance) ? meeting.attendance : [];
        return !attendance.some((a) => toNumber(a.member_id, 0) === person.id && valueOr(a.status, "").toLowerCase() !== "absent");
      }).length;
      return { person, absences };
    }).filter((item) => item.absences > 0);

    if (!peopleWithAbsences.length) {
      el.cellsMissingMembersBody.innerHTML = '<tr><td colspan="3">Todos compareceram em todas as reunioes.</td></tr>';
      return;
    }

    el.cellsMissingMembersBody.innerHTML = peopleWithAbsences
      .sort((a, b) => b.absences - a.absences)
      .map((item) => {
        const type = members.some((m) => m.id === item.person.id) ? "Membro" : "Assiduo";
        return `<tr>
          <td>${escapeHtml(valueOr(item.person.full_name, `Pessoa ${item.person.id}`))}</td>
          <td>${escapeHtml(type)}</td>
          <td>${item.absences}</td>
        </tr>`;
      })
      .join("");
  }

  function renderDashboardLostSheep(cellId, lostSheepRows) {
    const rows = (Array.isArray(lostSheepRows) ? lostSheepRows : []).filter(
      (item) => toNumber(item && item.previous_cell_id, 0) === toNumber(cellId, 0)
    );

    const pending = rows.filter((item) => !(item && item.visit_completed)).length;
    const visited = rows.filter((item) => item && item.visit_completed).length;

    if (el.cellsDashboardLostSheepPending) el.cellsDashboardLostSheepPending.textContent = String(pending);
    if (el.cellsDashboardLostSheepVisited) el.cellsDashboardLostSheepVisited.textContent = String(visited);

    if (!el.cellsDashboardLostSheepBody) return;
    if (!rows.length) {
      el.cellsDashboardLostSheepBody.innerHTML = '<tr><td colspan="3">Sem ovelhas perdidas nesta celula.</td></tr>';
      return;
    }

    el.cellsDashboardLostSheepBody.innerHTML = rows
      .slice(0, 8)
      .map((item) => {
        const status = item && item.visit_completed ? "Visitada" : "Pendente";
        return `<tr>
          <td>${escapeHtml(valueOr(item && item.member_name, "-"))}</td>
          <td>${escapeHtml(formatDatePtBr(valueOr(item && item.marked_as_lost_date, "")))}</td>
          <td>${escapeHtml(status)}</td>
        </tr>`;
      })
      .join("");
  }

  function renderInsights(insights) {
    if (!insights) return;

    const totalVisitors = toNumber(insights.total_visitors, 0);
    const membersFrequency = toNumber(insights.member_frequency_percent, 0);
    const assiduousCount = toNumber(insights.assiduous_members_count, 0);
    const missingWeeks = toNumber(insights.weeks_without_reports_count, 0);
    const lowFrequencyMeetings = toNumber(insights.low_frequency_meetings_count, 0);
    const visitorsAverage = toNumber(insights.visitors_average_per_meeting, 0);

    if (el.cellsKpiVisitorsPeriod) el.cellsKpiVisitorsPeriod.textContent = String(totalVisitors);
    if (el.cellsKpiMembersFrequency) el.cellsKpiMembersFrequency.textContent = `${membersFrequency.toFixed(1)}%`;
    if (el.cellsKpiAssiduousCount) el.cellsKpiAssiduousCount.textContent = String(assiduousCount);
    if (el.cellsKpiMissingWeeks) el.cellsKpiMissingWeeks.textContent = String(missingWeeks);
    if (el.cellsKpiLowFrequencyMeetings) el.cellsKpiLowFrequencyMeetings.textContent = String(lowFrequencyMeetings);

    renderMissingWeeks(Array.isArray(insights.weeks_without_reports) ? insights.weeks_without_reports : []);

    if (!el.cellsInsightsChart) return;
  }

  function renderCellInfoCard() {
    const cellId = toNumber(el.cellsSelect ? el.cellsSelect.value : 0, 0);
    if (!cellId) return;

    const cell = state.cells.find((c) => c.id === cellId);
    if (!cell) return;

    const leadership = getCellLeadership(cellId);
    const totalMembers = state.peopleByStage ? (state.peopleByStage.member || []).length : 0;
    const totalAssiduos = state.peopleByStage ? (state.peopleByStage.assiduo || []).length : 0;
    const totalVisitors = state.peopleByStage ? (state.peopleByStage.visitor || []).length : 0;

    if (el.cellsCellInfoName) el.cellsCellInfoName.textContent = valueOr(cell.name, `Celula ${cellId}`);
    if (el.cellsCellInfoMembers) el.cellsCellInfoMembers.textContent = String(totalMembers);
    if (el.cellsCellInfoAssiduos) el.cellsCellInfoAssiduos.textContent = String(totalAssiduos);
    if (el.cellsCellInfoVisitors) el.cellsCellInfoVisitors.textContent = String(totalVisitors);
    if (el.cellsCellInfoLeader) el.cellsCellInfoLeader.textContent = valueOr(leadership.leaderName, "-");
  }

  function fillCellOptions(selectElement, cells, placeholder) {
    if (!selectElement) return;
    const defaultOption = `<option value="">${placeholder}</option>`;
    const options = cells.map((cell) => `<option value="${cell.id}">${escapeHtml(valueOr(cell.name, `Celula ${cell.id}`))}</option>`).join("");
    selectElement.innerHTML = defaultOption + options;
  }

  function normalizeText(value) {
    return String(valueOr(value, "")).trim().toLowerCase();
  }

  function getRoleControls(roleTag) {
    if (roleTag === "discipler") {
      return {
        input: el.cellsCreateCellDisciplerInput,
        hidden: el.cellsCreateCellDisciplerId,
        list: document.getElementById("cellsCreateCellDisciplerList"),
        addBtn: el.cellsCreateCellAddDisciplerBtn,
      };
    }
    return {
      input: el.cellsCreateCellLeaderInput,
      hidden: el.cellsCreateCellLeaderId,
      list: document.getElementById("cellsCreateCellLeaderList"),
      addBtn: el.cellsCreateCellAddLeaderBtn,
    };
  }

  function toggleRoleAddButton(roleTag) {
    const controls = getRoleControls(roleTag);
    if (!controls.addBtn || !controls.input || !controls.hidden) return;
    const hasText = controls.input.value.trim().length > 0;
    const hasSelected = toNumber(controls.hidden.value, 0) > 0;
    controls.addBtn.classList.toggle("hide", !hasText || hasSelected);
  }

  function getRoleCandidates(roleTag, queryText) {
    const sourceMembers = roleTag === "discipler" ? state.members : state.availableMembersForCellCreation;
    const taggedCandidates = sourceMembers
      .filter((member) => state.memberRoleTags[String(member.id)] === roleTag);
    const base = taggedCandidates.length ? taggedCandidates : sourceMembers;

    const selectedDisciplerId = toNumber(el.cellsCreateCellDisciplerId ? el.cellsCreateCellDisciplerId.value : 0, 0);
    const withoutInvalid = roleTag === "leader"
      ? base.filter((member) => member.id !== selectedDisciplerId)
      : base;

    const search = normalizeText(queryText);
    if (!search) return withoutInvalid;
    return withoutInvalid.filter((member) => normalizeText(member.full_name).includes(search));
  }

  function resolveRoleSelection(roleTag) {
    const controls = getRoleControls(roleTag);
    if (!controls.input || !controls.hidden) return;

    const typed = normalizeText(controls.input.value);
    const allCandidates = getRoleCandidates(roleTag, "");
    const exact = allCandidates.find((member) => normalizeText(member.full_name) === typed);
    const selectedId = exact ? exact.id : 0;
    controls.hidden.value = selectedId ? String(selectedId) : "";
    toggleRoleAddButton(roleTag);
  }

  function hideRoleList(roleTag) {
    const controls = getRoleControls(roleTag);
    if (!controls.list) return;
    controls.list.classList.add("hide");
    controls.list.innerHTML = "";
  }

  function renderRoleList(roleTag) {
    const controls = getRoleControls(roleTag);
    if (!controls.input || !controls.hidden || !controls.list) return;

    const query = controls.input.value.trim();
    if (!query) {
      hideRoleList(roleTag);
      return;
    }

    const candidates = getRoleCandidates(roleTag, query).slice(0, 8);
    if (!candidates.length) {
      hideRoleList(roleTag);
      return;
    }

    controls.list.innerHTML = candidates
      .map((member) => `<div class="autocomplete-item" data-role="${roleTag}" data-member-id="${member.id}" data-member-name="${escapeHtml(valueOr(member.full_name, ""))}">${escapeHtml(valueOr(member.full_name, `Membro ${member.id}`))}</div>`)
      .join("");
    controls.list.classList.remove("hide");
  }

  function setRoleInputToMember(roleTag, member) {
    const controls = getRoleControls(roleTag);
    if (!controls.input || !controls.hidden) return;
    controls.input.value = valueOr(member.full_name, `Membro ${member.id}`);
    controls.hidden.value = String(member.id);
    toggleRoleAddButton(roleTag);
  }

  function syncCreateCellRoleOptions() {
    resolveRoleSelection("discipler");
    resolveRoleSelection("leader");
    hideRoleList("discipler");
    hideRoleList("leader");
  }

  async function loadCells() {
    const path = isLeaderMode() ? "/cells/my" : "/cells/";
    const cells = await api(path);
    state.cells = Array.isArray(cells) ? cells : [];

    fillCellOptions(el.cellsSelect, state.cells, "Selecione");

    if (state.cells.length && !el.cellsSelect.value) {
      el.cellsSelect.value = String(state.cells[0].id);
    }
  }

  async function loadMembers() {
    const members = await api("/cells/members/all?status=active");
    state.members = Array.isArray(members) ? members : [];
  }

  async function loadAvailableMembersForCellCreation() {
    if (!state.cells.length || !state.members.length) {
      await Promise.all([loadCells(), loadMembers()]);
    }

    const [linksPerCell, assignmentsByCell] = await Promise.all([
      Promise.all(state.cells.map((cell) => api(`/cells/${cell.id}/members`))),
      Promise.all(state.cells.map((cell) => api(`/cells/${cell.id}/leaders`))),
    ]);

    tagMembersFromAssignments(assignmentsByCell);

    const linkedMemberIds = new Set();
    linksPerCell.forEach((links) => {
      if (!Array.isArray(links)) return;
      links.forEach((link) => {
        if (link && link.active) linkedMemberIds.add(toNumber(link.member_id, 0));
      });
    });

    state.availableMembersForCellCreation = state.members.filter(
      (member) => !linkedMemberIds.has(member.id)
    );

    syncCreateCellRoleOptions();
  }

  function formatWeekday(weekday) {
    const map = {
      monday: "Segunda",
      tuesday: "Terca",
      wednesday: "Quarta",
      thursday: "Quinta",
      friday: "Sexta",
      saturday: "Sabado",
      sunday: "Domingo",
    };
    return valueOr(map[valueOr(weekday, "")], valueOr(weekday, "-"));
  }

  function memberStatusLabel(member) {
    const status = valueOr(member.status, "active");
    return status === "active" ? "Ativo" : status;
  }

  function memberStageLabel(member) {
    const stage = valueOr(member.stage, "member");
    if (stage === "visitor") return "Visitante";
    if (stage === "assiduo") return "Assiduo";
    return "Membro";
  }

  function fillMemberSelect(selectElement, members, selectedId, placeholder, excludedMemberId) {
    if (!selectElement) return;
    const excluded = toNumber(excludedMemberId, 0);
    const selected = toNumber(selectedId, 0);
    const options = members
      .filter((member) => member.id !== excluded)
      .map((member) => `<option value="${member.id}">${escapeHtml(valueOr(member.full_name, `Membro ${member.id}`))}</option>`)
      .join("");
    selectElement.innerHTML = `<option value="">${placeholder}</option>` + options;
    if (selected) {
      selectElement.value = String(selected);
    }
  }

  function getModalRoleCandidates(roleTag, includeMemberId) {
    const includeId = toNumber(includeMemberId, 0);
    const tagged = state.members.filter((member) => state.memberRoleTags[String(member.id)] === roleTag);
    const base = tagged.length ? tagged : state.members;
    return base.filter((member) => member.status === "active" || member.id === includeId);
  }

  function getCellActiveRoleSelections(assignments) {
    const rows = Array.isArray(assignments) ? assignments : [];
    const activeRows = rows.filter((row) => row && row.active);
    const discipler = activeRows.find((row) => row.role === "co_leader");
    const leader = activeRows.find((row) => row.role === "leader");
    return {
      disciplerMemberId: discipler ? toNumber(discipler.member_id, 0) : 0,
      leaderMemberId: leader ? toNumber(leader.member_id, 0) : 0,
    };
  }

  function updateCellModalLeaderOptions() {
    const selectedDiscipler = toNumber(el.cellsCellModalDisciplerId ? el.cellsCellModalDisciplerId.value : 0, 0);
    const selectedLeader = toNumber(el.cellsCellModalLeaderId ? el.cellsCellModalLeaderId.value : 0, 0);
    const leaderCandidates = getModalRoleCandidates("leader", selectedLeader);
    fillMemberSelect(el.cellsCellModalLeaderId, leaderCandidates, selectedLeader, "Selecione", selectedDiscipler);
  }

  function getRoleMembers(roleTag) {
    const tagged = state.members.filter((member) => state.memberRoleTags[String(member.id)] === roleTag);
    return tagged.sort((a, b) => String(valueOr(a.full_name, "")).localeCompare(String(valueOr(b.full_name, ""))));
  }

  function getMemberNameById(memberId) {
    const id = toNumber(memberId, 0);
    if (!id) return "-";
    const member = state.members.find((item) => item.id === id);
    return member ? valueOr(member.full_name, `Membro ${id}`) : `Membro ${id}`;
  }

  function getCellLeadership(cellId) {
    const leadership = state.leadershipByCellId[String(cellId)] || {};
    return {
      disciplerName: getMemberNameById(leadership.disciplerMemberId),
      leaderName: getMemberNameById(leadership.leaderMemberId),
    };
  }

  function renderCellsListTable() {
    if (!el.cellsListBody) return;
    if (!state.cells.length) {
      el.cellsListBody.innerHTML = '<tr><td colspan="7">Sem celulas cadastradas.</td></tr>';
      return;
    }

    el.cellsListBody.innerHTML = state.cells
      .map((cell) => {
        const meetingTime = valueOr(cell.meeting_time, "").slice(0, 5) || "-";
        const leadership = getCellLeadership(cell.id);
        const actions = isLeaderMode()
          ? "-"
          : `<button class="btn ghost btn-inline cells-edit-cell-btn" type="button" data-cell-id="${cell.id}">Editar</button>`;
        return `<tr>
          <td>${escapeHtml(valueOr(cell.name, `Celula ${cell.id}`))}</td>
          <td>${escapeHtml(formatWeekday(cell.weekday))}</td>
          <td>${escapeHtml(meetingTime)}</td>
          <td>${escapeHtml(leadership.disciplerName)}</td>
          <td>${escapeHtml(leadership.leaderName)}</td>
          <td>${escapeHtml(valueOr(cell.status, "-"))}</td>
          <td>${actions}</td>
        </tr>`;
      })
      .join("");
  }

  function renderRoleMembersTable(roleTag, bodyElement) {
    if (!bodyElement) return;
    const members = getRoleMembers(roleTag);
    if (!members.length) {
      bodyElement.innerHTML = '<tr><td colspan="4">Sem registros.</td></tr>';
      return;
    }

    bodyElement.innerHTML = members
      .map((member) => `<tr>
        <td>${escapeHtml(valueOr(member.full_name, `Membro ${member.id}`))}</td>
        <td>${escapeHtml(valueOr(member.contact, "-"))}</td>
        <td>${escapeHtml(memberStatusLabel(member))}</td>
        <td><button class="btn ghost btn-inline cells-edit-member-btn" type="button" data-member-id="${member.id}" data-role-tag="${roleTag}">Editar</button></td>
      </tr>`)
      .join("");
  }

  async function refreshLeadershipByCellMap() {
    if (!state.cells.length) {
      state.leadershipByCellId = {};
      return;
    }

    const assignmentsByCell = await Promise.all(state.cells.map((cell) => api(`/cells/${cell.id}/leaders`)));
    tagMembersFromAssignments(assignmentsByCell);

    state.leadershipByCellId = {};
    state.cells.forEach((cell, index) => {
      const selections = getCellActiveRoleSelections(assignmentsByCell[index]);
      state.leadershipByCellId[String(cell.id)] = selections;
    });
  }

  async function refreshCellsAdminData() {
    await Promise.all([loadCells(), loadMembers()]);
    await refreshLeadershipByCellMap();

    renderCellsListTable();
    renderRoleMembersTable("leader", el.cellsLeadersBody);
    renderRoleMembersTable("discipler", el.cellsDisciplersBody);
  }

  function fillPeopleCellSelect() {
    fillCellOptions(el.cellsPeopleCellSelect, state.cells, "Selecione");
    if (el.cellsPeopleCellSelect && state.cells.length && !el.cellsPeopleCellSelect.value) {
      el.cellsPeopleCellSelect.value = String(state.cells[0].id);
    }
  }

  function renderPeopleTableRows(stage, members) {
    if (!Array.isArray(members) || !members.length) {
      return '<tr><td colspan="4">Sem registros.</td></tr>';
    }

    return members
      .map((member) => {
        const actions = stage === "visitor"
          ? `<button class="btn ghost btn-inline cells-promote-btn" type="button" data-member-id="${member.id}" data-target-stage="assiduo">Promover para assiduo</button>
             <button class="btn ghost btn-inline cells-promote-btn" type="button" data-member-id="${member.id}" data-target-stage="member">Promover para membro</button>`
          : stage === "assiduo"
            ? `<button class="btn ghost btn-inline cells-promote-btn" type="button" data-member-id="${member.id}" data-target-stage="member">Promover para membro</button>`
            : "-";

        return `<tr>
          <td>${escapeHtml(valueOr(member.full_name, `Membro ${member.id}`))}</td>
          <td>${escapeHtml(valueOr(member.contact, "-"))}</td>
          <td>${escapeHtml(formatDatePtBr(valueOr(member.count_start_date, "")))}</td>
          <td>${actions}</td>
        </tr>`;
      })
      .join("");
  }

  function renderPeopleTables() {
    if (el.cellsPeopleVisitorsBody) {
      el.cellsPeopleVisitorsBody.innerHTML = renderPeopleTableRows("visitor", state.peopleByStage.visitor);
    }
    if (el.cellsPeopleAssiduosBody) {
      el.cellsPeopleAssiduosBody.innerHTML = renderPeopleTableRows("assiduo", state.peopleByStage.assiduo);
    }
    if (el.cellsPeopleMembersBody) {
      const members = state.peopleByStage.member;
      el.cellsPeopleMembersBody.innerHTML = members.length
        ? members.map((member) => {
          const cellId = toNumber(el.cellsPeopleCellSelect ? el.cellsPeopleCellSelect.value : 0, 0);
          const actions = `<button class="btn ghost btn-inline cells-edit-member-people-btn" type="button" data-member-id="${member.id}">Editar</button>
                           <button class="btn ghost btn-inline cells-transfer-member-btn" type="button" data-member-id="${member.id}">Transferir</button>
                           <button class="btn ghost btn-inline cells-mark-lost-sheep-btn" type="button" data-member-id="${member.id}" data-cell-id="${cellId}" data-member-name="${escapeHtml(valueOr(member.full_name, ''))}">Ovelha Perdida</button>`;
          return `<tr>
            <td>${escapeHtml(valueOr(member.full_name, `Membro ${member.id}`))}</td>
            <td>${escapeHtml(valueOr(member.contact, "-"))}</td>
            <td>${escapeHtml(memberStageLabel(member))}</td>
            <td>${escapeHtml(formatDatePtBr(valueOr(member.count_start_date, "")))}</td>
            <td>${actions}</td>
          </tr>`;
        }).join("")
        : '<tr><td colspan="5">Sem registros.</td></tr>';
    }
  }

  async function loadPeopleViewData() {
    const cellId = toNumber(el.cellsPeopleCellSelect ? el.cellsPeopleCellSelect.value : 0, 0);
    if (!cellId) {
      state.peopleByStage = { visitor: [], assiduo: [], member: [] };
      renderPeopleTables();
      return;
    }

    const [visitors, assiduos, members] = await Promise.all([
      api(`/cells/${cellId}/people?stage=visitor`),
      api(`/cells/${cellId}/people?stage=assiduo`),
      api(`/cells/${cellId}/people?stage=member`),
    ]);
    state.peopleByStage = {
      visitor: Array.isArray(visitors) ? visitors : [],
      assiduo: Array.isArray(assiduos) ? assiduos : [],
      member: Array.isArray(members) ? members : [],
    };
    renderPeopleTables();
  }

  async function addPersonToSelectedCell(stage, fullName, contact, countStartDate) {
    const cellId = toNumber(el.cellsPeopleCellSelect ? el.cellsPeopleCellSelect.value : 0, 0);
    if (!cellId) throw new Error("Selecione uma celula para cadastrar pessoas.");
    if (!fullName) throw new Error("Informe o nome completo.");
    if (!countStartDate) throw new Error("Informe a data de cadastrado.");

    const member = await api("/cells/members/all", {
      method: "POST",
      body: JSON.stringify({
        full_name: fullName,
        contact: contact || null,
        status: "active",
        stage,
        count_start_date: countStartDate,
      }),
    });

    await api(`/cells/${cellId}/members/${member.id}`, {
      method: "POST",
      body: JSON.stringify({ start_date: countStartDate }),
    });
  }

  async function promotePersonInSelectedCell(memberId, targetStage) {
    const cellId = toNumber(el.cellsPeopleCellSelect ? el.cellsPeopleCellSelect.value : 0, 0);
    if (!cellId) throw new Error("Selecione uma celula para promover pessoas.");
    await api(`/cells/${cellId}/members/${memberId}/promote`, {
      method: "POST",
      body: JSON.stringify({ target_stage: targetStage }),
    });
  }

  async function disableMemberInPeople() {
    const cellId = toNumber(el.cellsMemberModalCellId ? el.cellsMemberModalCellId.value : 0, 0);
    const memberId = toNumber(el.cellsMemberModalId ? el.cellsMemberModalId.value : 0, 0);
    if (!cellId || !memberId) throw new Error("Celula ou membro invalido.");
    await api(`/cells/${cellId}/members/${memberId}`, {
      method: "DELETE",
    });
    closeMemberPeopleModal();
    await loadPeopleViewData();
    setCellsMessage("Membro desativado com sucesso.", false);
  }

  function openTransferMemberModal(memberId) {
    if (el.cellsTransferMemberModalMemberId) el.cellsTransferMemberModalMemberId.value = String(memberId);
    if (el.cellsTransferMemberModalReason) el.cellsTransferMemberModalReason.value = "";
    fillCellOptions(el.cellsTransferMemberModalTargetCell, state.cells, "Selecione");
    if (el.cellsTransferMemberModal) el.cellsTransferMemberModal.classList.remove("hide");
  }

  function closeTransferMemberModal() {
    if (el.cellsTransferMemberModal) el.cellsTransferMemberModal.classList.add("hide");
  }

  async function transferMemberToCell() {
    const memberId = toNumber(el.cellsTransferMemberModalMemberId ? el.cellsTransferMemberModalMemberId.value : 0, 0);
    const targetCellId = toNumber(el.cellsTransferMemberModalTargetCell ? el.cellsTransferMemberModalTargetCell.value : 0, 0);
    const reason = valueOr(el.cellsTransferMemberModalReason ? el.cellsTransferMemberModalReason.value.trim() : "", null);

    if (!memberId) throw new Error("Membro invalido.");
    if (!targetCellId) throw new Error("Selecione uma celula de destino.");

    const currentCellId = toNumber(el.cellsPeopleCellSelect ? el.cellsPeopleCellSelect.value : 0, 0);
    await api(`/cells/${currentCellId}/members/${memberId}/transfer`, {
      method: "POST",
      body: JSON.stringify({ target_cell_id: targetCellId, transfer_reason: reason }),
    });
    closeTransferMemberModal();
    await loadPeopleViewData();
    setCellsMessage("Membro transferido com sucesso.", false);
  }

  function openMemberPeopleModal(memberId) {
    const cellId = toNumber(el.cellsPeopleCellSelect ? el.cellsPeopleCellSelect.value : 0, 0);
    const member = state.peopleByStage.member.find((m) => m.id === memberId);
    if (!member) return;

    if (el.cellsMemberModalId) el.cellsMemberModalId.value = String(memberId);
    if (el.cellsMemberModalCellId) el.cellsMemberModalCellId.value = String(cellId);
    if (el.cellsMemberModalName) el.cellsMemberModalName.value = valueOr(member.full_name, "");
    if (el.cellsMemberModalContact) el.cellsMemberModalContact.value = valueOr(member.contact, "");
    if (el.cellsMemberModalStatus) el.cellsMemberModalStatus.value = valueOr(member.status, "active");
    if (el.cellsMemberModalCountStartDate) {
      el.cellsMemberModalCountStartDate.value = valueOr(member.count_start_date, getTodayIsoDate());
    }
    if (el.cellsMemberModal) el.cellsMemberModal.classList.remove("hide");
  }

  function closeMemberPeopleModal() {
    if (el.cellsMemberModal) el.cellsMemberModal.classList.add("hide");
  }

  async function disableMemberInPeople() {
    const memberId = toNumber(el.cellsMemberModalId ? el.cellsMemberModalId.value : 0, 0);
    if (!memberId) throw new Error("Membro invalido.");
    await api(`/cells/members/${memberId}`, {
      method: "PUT",
      body: JSON.stringify({ status: "inactive" }),
    });
    closeMemberPeopleModal();
    await loadPeopleViewData();
    setCellsMessage("Membro desativado com sucesso.", false);
  }

  function openTransferMemberModal(memberId) {
    if (el.cellsTransferMemberModalMemberId) el.cellsTransferMemberModalMemberId.value = String(memberId);
    if (el.cellsTransferMemberModalReason) el.cellsTransferMemberModalReason.value = "";
    fillCellOptions(el.cellsTransferMemberModalTargetCell, state.cells, "Selecione");
    if (el.cellsTransferMemberModal) el.cellsTransferMemberModal.classList.remove("hide");
  }

  function closeTransferMemberModal() {
    if (el.cellsTransferMemberModal) el.cellsTransferMemberModal.classList.add("hide");
  }

  async function transferMemberToCell() {
    const memberId = toNumber(el.cellsTransferMemberModalMemberId ? el.cellsTransferMemberModalMemberId.value : 0, 0);
    const targetCellId = toNumber(el.cellsTransferMemberModalTargetCell ? el.cellsTransferMemberModalTargetCell.value : 0, 0);
    const reason = valueOr(el.cellsTransferMemberModalReason ? el.cellsTransferMemberModalReason.value.trim() : "", null);

    if (!memberId) throw new Error("Membro invalido.");
    if (!targetCellId) throw new Error("Selecione uma celula de destino.");

    const currentCellId = toNumber(el.cellsPeopleCellSelect ? el.cellsPeopleCellSelect.value : 0, 0);
    await api(`/cells/${currentCellId}/members/${memberId}/transfer`, {
      method: "POST",
      body: JSON.stringify({ target_cell_id: targetCellId, transfer_reason: reason }),
    });
    closeTransferMemberModal();
    await loadPeopleViewData();
    setCellsMessage("Membro transferido com sucesso.", false);
  }

  // Lost Sheep functions
  async function loadLostSheepData() {
    const lostSheep = await api("/lost-sheep");
    state.lostSheep = Array.isArray(lostSheep) ? lostSheep : [];
    renderLostSheepTable();
  }

  function renderLostSheepTable() {
    if (!el.cellsLostSheepBody) return;
    const lostSheep = state.lostSheep || [];

    el.cellsLostSheepBody.innerHTML = lostSheep.length
      ? lostSheep.map((sheep) => {
        const visitedBadge = sheep.visit_completed ? "✓ Visitada" : "Pendente";
        const visitedClass = sheep.visit_completed ? "badge-success" : "badge-warning";
        const actions = `<button class="btn ghost btn-inline cells-lost-sheep-visit-btn" type="button" data-lost-sheep-id="${sheep.id}">Visita</button>`;
        
        return `<tr>
          <td>${escapeHtml(valueOr(sheep.member_name, "Desconhecido"))}</td>
          <td>${escapeHtml(valueOr(sheep.phone_number, "-"))}</td>
          <td>${escapeHtml(valueOr(sheep.previous_cell_name, "Desconhecida"))}</td>
          <td>${formatDatePtBr(sheep.marked_as_lost_date)}</td>
          <td><span class="badge ${visitedClass}">${visitedBadge}</span></td>
          <td>${actions}</td>
        </tr>`;
      }).join("")
      : '<tr><td colspan="6">Sem registros.</td></tr>';
  }

  function openLostSheepModal(memberId, cellId, memberName) {
    if (el.cellsLostSheepModalMemberId) el.cellsLostSheepModalMemberId.value = String(memberId);
    if (el.cellsLostSheepModalCellId) el.cellsLostSheepModalCellId.value = String(cellId);
    if (el.cellsLostSheepModalMemberName) el.cellsLostSheepModalMemberName.value = memberName;
    if (el.cellsLostSheepModalPhone) el.cellsLostSheepModalPhone.value = "";
    if (el.cellsLostSheepModalObservation) el.cellsLostSheepModalObservation.value = "";
    if (el.cellsLostSheepModal) el.cellsLostSheepModal.classList.remove("hide");
  }

  function closeLostSheepModal() {
    if (el.cellsLostSheepModal) el.cellsLostSheepModal.classList.add("hide");
  }

  async function markMemberAsLostSheep() {
    const memberId = toNumber(el.cellsLostSheepModalMemberId ? el.cellsLostSheepModalMemberId.value : 0, 0);
    const cellId = toNumber(el.cellsLostSheepModalCellId ? el.cellsLostSheepModalCellId.value : 0, 0);
    const phone = valueOr(el.cellsLostSheepModalPhone ? el.cellsLostSheepModalPhone.value.trim() : "", null);
    const observation = valueOr(el.cellsLostSheepModalObservation ? el.cellsLostSheepModalObservation.value.trim() : "", null);

    if (!memberId || !cellId) throw new Error("Dados invalidos.");

    await api("/lost-sheep", {
      method: "POST",
      body: JSON.stringify({
        member_id: memberId,
        cell_id: cellId,
        phone_number: phone,
        observation: observation,
      }),
    });

    closeLostSheepModal();
    await loadLostSheepData();
    await loadPeopleViewData();
    setCellsMessage("Pessoa marcada como ovelha perdida com sucesso.", false);
  }

  function openLostSheepVisitModal(lostSheepId) {
    if (el.cellsLostSheepVisitModalId) el.cellsLostSheepVisitModalId.value = String(lostSheepId);
    if (el.cellsLostSheepVisitModalObservation) el.cellsLostSheepVisitModalObservation.value = "";
    const sheep = state.lostSheep.find((s) => s.id === lostSheepId);
    if (sheep && el.cellsLostSheepVisitModalTitle) {
      el.cellsLostSheepVisitModalTitle.textContent = `Visita - ${valueOr(sheep.member?.full_name, "Ovelha Perdida")}`;
    }
    if (el.cellsLostSheepVisitModal) el.cellsLostSheepVisitModal.classList.remove("hide");
  }

  function closeLostSheepVisitModal() {
    if (el.cellsLostSheepVisitModal) el.cellsLostSheepVisitModal.classList.add("hide");
  }

  async function recordLostSheepVisit() {
    const lostSheepId = toNumber(el.cellsLostSheepVisitModalId ? el.cellsLostSheepVisitModalId.value : 0, 0);
    const observation = valueOr(el.cellsLostSheepVisitModalObservation ? el.cellsLostSheepVisitModalObservation.value.trim() : "", null);

    if (!lostSheepId) throw new Error("Registro invalido.");

    await api(`/lost-sheep/${lostSheepId}/visit`, {
      method: "PUT",
      body: JSON.stringify({ visit_observation: observation }),
    });

    closeLostSheepVisitModal();
    await loadLostSheepData();
    setCellsMessage("Visita registrada com sucesso.", false);
  }

  function fillMeetingsCellSelect() {
    fillCellOptions(el.cellsMeetingsCellSelect, state.cells, "Selecione");
    if (el.cellsMeetingsCellSelect && state.cells.length && !el.cellsMeetingsCellSelect.value) {
      el.cellsMeetingsCellSelect.value = String(state.cells[0].id);
    }
  }

  function buildMeetingsQueryParams() {
    const params = new URLSearchParams();
    const startDate = valueOr(el.cellsMeetingsStartDate ? el.cellsMeetingsStartDate.value : "", "");
    const endDate = valueOr(el.cellsMeetingsEndDate ? el.cellsMeetingsEndDate.value : "", "");
    if (startDate) params.set("start_date", startDate);
    if (endDate) params.set("end_date", endDate);
    const query = params.toString();
    return query ? `?${query}` : "";
  }

  function formatDatePtBr(isoDate) {
    if (!isoDate) return "-";
    const value = String(isoDate).slice(0, 10);
    const [year, month, day] = value.split("-");
    if (!year || !month || !day) return value;
    return `${day}/${month}/${year}`;
  }

  function renderMeetingsTable() {
    if (!el.cellsMeetingsBody) return;
    if (!state.meetings.length) {
      el.cellsMeetingsBody.innerHTML = '<tr><td colspan="5">Sem reunioes cadastradas.</td></tr>';
      if (el.cellsMeetingsPageInfo) el.cellsMeetingsPageInfo.textContent = "Pag. 1/1";
      if (el.cellsMeetingsPrevBtn) el.cellsMeetingsPrevBtn.disabled = true;
      if (el.cellsMeetingsNextBtn) el.cellsMeetingsNextBtn.disabled = true;
      return;
    }

    const ordered = [...state.meetings].sort((a, b) => {
      const dateA = String(valueOr(a.meeting_date, ""));
      const dateB = String(valueOr(b.meeting_date, ""));
      if (dateA === dateB) return Number(b.id || 0) - Number(a.id || 0);
      return dateB.localeCompare(dateA);
    });

    const totalPages = Math.max(1, Math.ceil(ordered.length / state.meetingsPagination.pageSize));
    if (state.meetingsPagination.page > totalPages) state.meetingsPagination.page = totalPages;
    if (state.meetingsPagination.page < 1) state.meetingsPagination.page = 1;
    const start = (state.meetingsPagination.page - 1) * state.meetingsPagination.pageSize;
    const end = start + state.meetingsPagination.pageSize;
    const pageRows = ordered.slice(start, end);

    el.cellsMeetingsBody.innerHTML = pageRows
      .map((meeting) => {
        const summary = state.meetingAttendanceSummary[String(meeting.id)] || { present: 0, absent: 0, justified: 0 };
        const expectedTotalForMeeting = toNumber(state.meetingsExpectedTotalByMeeting[String(meeting.id)], 0);
        const rate = expectedTotalForMeeting > 0
          ? (summary.present / expectedTotalForMeeting) * 100
          : 0;
        const summaryClass = rate < 70
          ? "cells-attendance-low"
          : rate < 90
            ? "cells-attendance-medium"
            : "cells-attendance-good";
        return `<tr>
        <td>${escapeHtml(formatDatePtBr(meeting.meeting_date))}</td>
        <td>${escapeHtml(valueOr(meeting.theme, "-"))}</td>
        <td>${escapeHtml(valueOr(meeting.notes, "-"))}</td>
        <td><span class="${summaryClass}">P: ${summary.present} | A: ${summary.absent} | J: ${summary.justified} / T: ${expectedTotalForMeeting}</span></td>
        <td>
          <button
            class="btn ghost btn-inline cells-open-attendance-btn"
            type="button"
            data-meeting-id="${meeting.id}"
            data-meeting-date="${escapeHtml(valueOr(meeting.meeting_date, ""))}"
            data-cell-id="${meeting.cell_id}"
          >Marcar frequencia</button>
        </td>
      </tr>`;
      })
      .join("");

    if (el.cellsMeetingsPageInfo) {
      el.cellsMeetingsPageInfo.textContent = `Pag. ${state.meetingsPagination.page}/${totalPages}`;
    }
    if (el.cellsMeetingsPrevBtn) el.cellsMeetingsPrevBtn.disabled = state.meetingsPagination.page <= 1;
    if (el.cellsMeetingsNextBtn) el.cellsMeetingsNextBtn.disabled = state.meetingsPagination.page >= totalPages;
  }

  function summarizeAttendanceRows(rows) {
    const summary = { present: 0, absent: 0, justified: 0 };
    (Array.isArray(rows) ? rows : []).forEach((row) => {
      const status = valueOr(row.attendance_status, "");
      if (status === "present") summary.present += 1;
      if (status === "absent") summary.absent += 1;
      if (status === "justified") summary.justified += 1;
    });
    return summary;
  }

  async function loadMeetingsViewData() {
    const cellId = toNumber(el.cellsMeetingsCellSelect ? el.cellsMeetingsCellSelect.value : 0, 0);
    if (!cellId) {
      state.meetings = [];
      state.meetingAttendanceSummary = {};
      state.meetingsExpectedTotal = 0;
      state.meetingsExpectedTotalByMeeting = {};
      renderMeetingsTable();
      return;
    }

    const query = buildMeetingsQueryParams();
    const meetings = await api(`/cells/${cellId}/meetings${query}`);
    state.meetings = Array.isArray(meetings) ? meetings : [];
    state.meetingsPagination.page = 1;
    state.meetingAttendanceSummary = {};
    state.meetingsExpectedTotalByMeeting = {};
    if (state.meetings.length) {
      const [attendancesByMeeting, peopleByMeeting] = await Promise.all([
        Promise.all(state.meetings.map((meeting) => api(`/cells/meetings/${meeting.id}/attendances`))),
        Promise.all(state.meetings.map((meeting) => api(`/cells/${cellId}/people?on_date=${meeting.meeting_date}`))),
      ]);

      state.meetings.forEach((meeting, index) => {
        const attendances = Array.isArray(attendancesByMeeting[index]) ? attendancesByMeeting[index] : [];
        state.meetingAttendanceSummary[String(meeting.id)] = summarizeAttendanceRows(attendances);
        const people = peopleByMeeting[index];
        const expected = Math.max(Array.isArray(people) ? people.length : 0, attendances.length);
        state.meetingsExpectedTotalByMeeting[String(meeting.id)] = expected;
      });

      const expectedTotals = Object.values(state.meetingsExpectedTotalByMeeting);
      state.meetingsExpectedTotal = expectedTotals.length
        ? Math.max(...expectedTotals.map((value) => toNumber(value, 0)))
        : 0;
    }
    renderMeetingsTable();
  }

  function closeAttendanceModal() {
    if (!el.cellsAttendanceModal) return;
    el.cellsAttendanceModal.classList.add("hide");
    if (el.cellsAttendanceMeetingId) el.cellsAttendanceMeetingId.value = "";
    state.attendanceMembers = [];
  }

  async function openAttendanceModal(meetingId, cellId, meetingDate) {
    const [people, attendances, allMembers] = await Promise.all([
      api(`/cells/${cellId}/people?on_date=${meetingDate}`),
      api(`/cells/meetings/${meetingId}/attendances`),
      api(`/cells/members/all`),
    ]);

    const attendanceByMemberId = new Map();
    (Array.isArray(attendances) ? attendances : []).forEach((item) => {
      attendanceByMemberId.set(Number(item.member_id), valueOr(item.attendance_status, "present"));
    });

    const allMembersById = new Map();
    (Array.isArray(allMembers) ? allMembers : []).forEach((member) => {
      const memberId = toNumber(member.id, 0);
      if (memberId > 0) allMembersById.set(memberId, member);
    });

    const memberById = new Map();
    (Array.isArray(people) ? people : []).forEach((member) => {
      const memberId = toNumber(member.id, 0);
      if (memberId > 0) memberById.set(memberId, member);
    });

    attendanceByMemberId.forEach((_status, memberId) => {
      if (memberById.has(memberId)) return;
      const knownMember = allMembersById.get(memberId);
      memberById.set(memberId, {
        id: memberId,
        full_name: valueOr(knownMember ? knownMember.full_name : null, `Membro ${memberId}`),
        __historical_only: true,
      });
    });

    state.attendanceMembers = Array.from(memberById.values()).sort((a, b) => {
      const nameA = normalizeText(a.full_name);
      const nameB = normalizeText(b.full_name);
      return nameA.localeCompare(nameB);
    });
    if (el.cellsAttendanceMeetingId) el.cellsAttendanceMeetingId.value = String(meetingId);
    if (el.cellsAttendanceModalTitle) {
      el.cellsAttendanceModalTitle.textContent = `Frequencia - ${formatDatePtBr(meetingDate)}`;
    }

    if (el.cellsAttendanceBody) {
      if (!state.attendanceMembers.length) {
        el.cellsAttendanceBody.innerHTML = '<tr><td colspan="2">Sem membros ativos.</td></tr>';
      } else {
        el.cellsAttendanceBody.innerHTML = state.attendanceMembers
          .map((member) => {
            const status = attendanceByMemberId.get(Number(member.id)) || "present";
            const historicalTag = member && member.__historical_only
              ? ' <small class="input-hint">(historico)</small>'
              : "";
            return `<tr>
              <td>${escapeHtml(valueOr(member.full_name, `Membro ${member.id}`))}${historicalTag}</td>
              <td>
                <select class="cells-attendance-status" data-member-id="${member.id}">
                  <option value="present" ${status === "present" ? "selected" : ""}>Presente</option>
                  <option value="absent" ${status === "absent" ? "selected" : ""}>Ausente</option>
                  <option value="justified" ${status === "justified" ? "selected" : ""}>Justificado</option>
                </select>
              </td>
            </tr>`;
          })
          .join("");
      }
    }

    if (el.cellsAttendanceModal) {
      el.cellsAttendanceModal.classList.remove("hide");
    }
  }

  async function saveAttendanceFromModal(openPeopleAfterSave = false) {
    const meetingId = toNumber(el.cellsAttendanceMeetingId ? el.cellsAttendanceMeetingId.value : 0, 0);
    if (!meetingId) throw new Error("Reuniao invalida para frequencia.");
    const selectedCellId = toNumber(el.cellsMeetingsCellSelect ? el.cellsMeetingsCellSelect.value : 0, 0);

    const rows = el.cellsAttendanceBody ? Array.from(el.cellsAttendanceBody.querySelectorAll("select.cells-attendance-status")) : [];
    const items = rows
      .map((select) => ({
        member_id: toNumber(select.getAttribute("data-member-id"), 0),
        attendance_status: select.value || "present",
      }))
      .filter((item) => item.member_id > 0);

    await api(`/cells/meetings/${meetingId}/attendances/bulk`, {
      method: "POST",
      body: JSON.stringify({ items }),
    });

    closeAttendanceModal();
    await loadMeetingsViewData();
    if (openPeopleAfterSave) {
      setCellsView("people");
      fillPeopleCellSelect();
      if (el.cellsPeopleCellSelect && selectedCellId) {
        el.cellsPeopleCellSelect.value = String(selectedCellId);
      }
      await loadPeopleViewData();
    }
    setCellsMessage("Frequencia salva com sucesso.", false);
  }

  async function openCellModal(cell) {
    if (!el.cellsCellModal || !el.cellsCellModalForm) return;
    const editing = Boolean(cell);
    const cellId = editing ? toNumber(cell.id, 0) : 0;
    let selectedDisciplerId = 0;
    let selectedLeaderId = 0;

    if (editing && cellId) {
      const assignments = await api(`/cells/${cellId}/leaders`);
      const selected = getCellActiveRoleSelections(assignments);
      selectedDisciplerId = selected.disciplerMemberId;
      selectedLeaderId = selected.leaderMemberId;
    }

    if (el.cellsCellModalTitle) {
      el.cellsCellModalTitle.textContent = editing ? "Editar Celula" : "Adicionar Celula";
    }
    if (el.cellsCellModalId) el.cellsCellModalId.value = editing ? String(cell.id) : "";
    if (el.cellsCellModalName) el.cellsCellModalName.value = editing ? valueOr(cell.name, "") : "";
    if (el.cellsCellModalWeekday) el.cellsCellModalWeekday.value = editing ? valueOr(cell.weekday, "monday") : "monday";
    if (el.cellsCellModalMeetingTime) {
      const baseTime = editing ? valueOr(cell.meeting_time, "19:00:00") : "19:00:00";
      el.cellsCellModalMeetingTime.value = baseTime.slice(0, 5);
    }
    if (el.cellsCellModalAddress) el.cellsCellModalAddress.value = editing ? valueOr(cell.address, "") : "";
    if (el.cellsCellModalStatus) el.cellsCellModalStatus.value = editing ? valueOr(cell.status, "active") : "active";

    const disciplerCandidates = getModalRoleCandidates("discipler", selectedDisciplerId);
    fillMemberSelect(el.cellsCellModalDisciplerId, disciplerCandidates, selectedDisciplerId, "Selecione");
    const leaderCandidates = getModalRoleCandidates("leader", selectedLeaderId);
    fillMemberSelect(el.cellsCellModalLeaderId, leaderCandidates, selectedLeaderId, "Selecione", selectedDisciplerId);

    if (el.cellsCellModalDisableBtn) el.cellsCellModalDisableBtn.classList.toggle("hide", !editing);
    if (el.cellsCellModalDeleteBtn) el.cellsCellModalDeleteBtn.classList.toggle("hide", !editing);
    el.cellsCellModal.classList.remove("hide");
  }

  function closeCellModal() {
    if (!el.cellsCellModal) return;
    el.cellsCellModal.classList.add("hide");
  }

  function openMemberModal(roleTag, member) {
    if (!el.cellsMemberModal || !el.cellsMemberModalForm) return;
    const editing = Boolean(member);
    const roleLabel = roleTag === "leader" ? "Lider" : "Discipulador";
    if (el.cellsMemberModalTitle) {
      el.cellsMemberModalTitle.textContent = editing ? `Editar ${roleLabel}` : `Adicionar ${roleLabel}`;
    }
    if (el.cellsMemberModalRoleTag) el.cellsMemberModalRoleTag.value = roleTag;
    if (el.cellsMemberModalId) el.cellsMemberModalId.value = editing ? String(member.id) : "";
    if (el.cellsMemberModalName) el.cellsMemberModalName.value = editing ? valueOr(member.full_name, "") : "";
    if (el.cellsMemberModalContact) el.cellsMemberModalContact.value = editing ? valueOr(member.contact, "") : "";
    if (el.cellsMemberModalStatus) el.cellsMemberModalStatus.value = editing ? valueOr(member.status, "active") : "active";
    if (el.cellsMemberModalCountStartDate) {
      el.cellsMemberModalCountStartDate.value = editing
        ? valueOr(member.count_start_date, getTodayIsoDate())
        : getTodayIsoDate();
    }

    if (el.cellsMemberModalDisableBtn) el.cellsMemberModalDisableBtn.classList.toggle("hide", !editing);
    if (el.cellsMemberModalDeleteBtn) el.cellsMemberModalDeleteBtn.classList.toggle("hide", !editing);
    el.cellsMemberModal.classList.remove("hide");
  }

  function closeMemberModal() {
    if (!el.cellsMemberModal) return;
    el.cellsMemberModal.classList.add("hide");
  }

  function openConfirmModal(message, action, errorMessage) {
    if (!el.cellsConfirmModal || !el.cellsConfirmModalMessage) return;
    el.cellsConfirmModalMessage.textContent = valueOr(message, "Tem certeza que deseja excluir?");
    state.pendingConfirmAction = action;
    state.pendingConfirmErrorMessage = valueOr(errorMessage, "Falha ao executar exclusao.");
    el.cellsConfirmModal.classList.remove("hide");
  }

  function closeConfirmModal() {
    if (!el.cellsConfirmModal) return;
    el.cellsConfirmModal.classList.add("hide");
    state.pendingConfirmAction = null;
    state.pendingConfirmErrorMessage = "Falha ao executar exclusao.";
  }

  async function confirmModalAction() {
    const action = state.pendingConfirmAction;
    const errorMessage = state.pendingConfirmErrorMessage;
    closeConfirmModal();
    if (!action) return;
    await handleLoadError(action, errorMessage);
  }

  async function disableCell(cellId) {
    await api(`/cells/${cellId}/status`, {
      method: "PATCH",
      body: JSON.stringify({ status: "inactive" }),
    });
    await refreshCellsAdminData();
    setCellsMessage("Celula desabilitada.", false);
  }

  async function deleteCell(cellId) {
    await api(`/cells/${cellId}`, { method: "DELETE" });
    await refreshCellsAdminData();
    setCellsMessage("Celula excluida com sucesso.", false);
  }

  async function disableMember(memberId, roleTag, fromDelete) {
    await api(`/cells/members/${memberId}`, {
      method: "PUT",
      body: JSON.stringify({ status: "inactive" }),
    });
    if (fromDelete) {
      delete state.memberRoleTags[String(memberId)];
      saveRoleTagsToStorage();
    }
    if (!fromDelete && roleTag) {
      setMemberRoleTag(memberId, roleTag);
    }
    await refreshCellsAdminData();
    setCellsMessage(fromDelete ? "Registro excluido (desabilitado)." : "Registro desabilitado.", false);
  }

  async function ensureMembersLinkedToCell(cellId, memberIds) {
    const links = await api(`/cells/${cellId}/members`);
    const activeMemberIds = new Set(
      (Array.isArray(links) ? links : [])
        .filter((link) => link && link.active)
        .map((link) => toNumber(link.member_id, 0))
    );

    for (const memberId of memberIds) {
      if (activeMemberIds.has(memberId)) continue;
      await api(`/cells/${cellId}/members/${memberId}`, {
        method: "POST",
        body: JSON.stringify({}),
      });
    }
  }

  async function ensureDisciplerIsSupervisorOnly(cellId, disciplerMemberId, leaderMemberId) {
    const disciplerId = toNumber(disciplerMemberId, 0);
    const leaderId = toNumber(leaderMemberId, 0);
    if (!disciplerId || disciplerId === leaderId) return;

    const links = await api(`/cells/${cellId}/members`);
    const activeDisciplerLink = (Array.isArray(links) ? links : []).some(
      (link) => link && link.active && toNumber(link.member_id, 0) === disciplerId
    );
    if (!activeDisciplerLink) return;

    await api(`/cells/${cellId}/members/${disciplerId}`, {
      method: "DELETE",
    });
  }

  async function syncCellLeadershipAssignments(cellId, disciplerMemberId, leaderMemberId) {
    const assignments = await api(`/cells/${cellId}/leaders`);
    const rows = Array.isArray(assignments) ? assignments : [];

    const activeRows = rows.filter((row) => row && row.active && (row.role === "co_leader" || row.role === "leader"));
    for (const row of activeRows) {
      const keepDiscipler = row.role === "co_leader" && toNumber(row.member_id, 0) === disciplerMemberId;
      const keepLeader = row.role === "leader"
        && toNumber(row.member_id, 0) === leaderMemberId
        && toNumber(row.discipler_member_id, 0) === disciplerMemberId;
      if (keepDiscipler || keepLeader) continue;

      await api(`/cells/${cellId}/leaders/${row.id}`, {
        method: "PATCH",
        body: JSON.stringify({ active: false }),
      });
    }

    const updatedRows = await api(`/cells/${cellId}/leaders`);
    const updated = Array.isArray(updatedRows) ? updatedRows : [];
    const hasDiscipler = updated.some((row) => row && row.active && row.role === "co_leader" && toNumber(row.member_id, 0) === disciplerMemberId);
    if (!hasDiscipler) {
      await api(`/cells/${cellId}/leaders`, {
        method: "POST",
        body: JSON.stringify({ member_id: disciplerMemberId, role: "co_leader", is_primary: false }),
      });
    }

    const hasLeader = updated.some(
      (row) => row
        && row.active
        && row.role === "leader"
        && toNumber(row.member_id, 0) === leaderMemberId
        && toNumber(row.discipler_member_id, 0) === disciplerMemberId
    );
    if (!hasLeader) {
      await api(`/cells/${cellId}/leaders`, {
        method: "POST",
        body: JSON.stringify({
          member_id: leaderMemberId,
          discipler_member_id: disciplerMemberId,
          role: "leader",
          is_primary: false,
        }),
      });
    }
  }

  async function createMemberOnly(fullName, contact) {
    const member = await api("/cells/members/all", {
      method: "POST",
      body: JSON.stringify({ full_name: fullName, contact: contact || null, status: "active" }),
    });
    return member;
  }

  async function loadCellsDashboard() {
    const cellId = toNumber(el.cellsSelect.value, 0);
    if (!cellId) throw new Error("Selecione uma celula.");

    if (!state.leadershipByCellId[String(cellId)]) {
      await refreshLeadershipByCellMap();
    }

    const startDate = el.cellsStartDate.value;
    const endDate = el.cellsEndDate.value;

    if (!startDate || !endDate) throw new Error("Informe data inicial e final.");
    if (new Date(startDate) > new Date(endDate)) throw new Error("Data inicial nao pode ser maior que data final.");

    setCellsMessage("Carregando dados das celulas...", false);

    const [retention, recurring, history, insights, charts, visitors, assiduos, members, meetingsData, lostSheepRows] = await Promise.all([
      api(`/cells/${cellId}/dashboard/retention?start_date=${startDate}&end_date=${endDate}`),
      api(`/cells/${cellId}/dashboard/visitors-recurring?start_date=${startDate}&end_date=${endDate}`),
      api(`/cells/${cellId}/dashboard/history?start_date=${startDate}&end_date=${endDate}`),
      api(`/cells/${cellId}/dashboard/insights?start_date=${startDate}&end_date=${endDate}`),
      api(`/cells/${cellId}/dashboard/charts?start_date=${startDate}&end_date=${endDate}`),
      api(`/cells/${cellId}/people?stage=visitor`),
      api(`/cells/${cellId}/people?stage=assiduo`),
      api(`/cells/${cellId}/people?stage=member`),
      api(`/cells/${cellId}/meetings?start_date=${startDate}&end_date=${endDate}`),
      api(`/lost-sheep`),
    ]);

    state.peopleByStage = {
      visitor: Array.isArray(visitors) ? visitors : [],
      assiduo: Array.isArray(assiduos) ? assiduos : [],
      member: Array.isArray(members) ? members : [],
    };

    renderRetention(retention);
    renderVisitors(recurring);
    renderHistory(history);
    renderInsights(insights);
    renderVisitorsByDateChart(charts && Array.isArray(charts.visitors_by_date) ? charts.visitors_by_date : []);
    renderWeeklyPresenceChart(charts && Array.isArray(charts.weekly_presence) ? charts.weekly_presence : []);
    renderVisitorRetentionChart(charts && Array.isArray(charts.visitor_retention) ? charts.visitor_retention : []);
    renderCompositionPieChart(charts && Array.isArray(charts.composition) ? charts.composition : []);
    renderStageCountsChart(charts && Array.isArray(charts.stage_counts_by_date) ? charts.stage_counts_by_date : []);
    renderMissingMembers(Array.isArray(meetingsData) ? meetingsData : []);
    renderDashboardLostSheep(cellId, Array.isArray(lostSheepRows) ? lostSheepRows : []);
    renderCellInfoCard();
    setCellsMessage("Dados de celula atualizados.", false);
  }

  async function submitCreateCell(event) {
    event.preventDefault();
    const disciplerMemberId = toNumber(el.cellsCreateCellDisciplerId ? el.cellsCreateCellDisciplerId.value : 0, 0);
    const leaderMemberId = toNumber(el.cellsCreateCellLeaderId ? el.cellsCreateCellLeaderId.value : 0, 0);

    if (!disciplerMemberId) throw new Error("Selecione um discipulador para a celula.");
    if (!leaderMemberId) throw new Error("Selecione um lider para a celula.");
    if (disciplerMemberId === leaderMemberId) {
      throw new Error("Lider e discipulador devem ser pessoas diferentes.");
    }

    const payload = {
      name: el.cellsCreateCellName.value.trim(),
      weekday: el.cellsCreateCellWeekday.value,
      meeting_time: `${el.cellsCreateCellMeetingTime.value}:00`,
      address: el.cellsCreateCellAddress.value.trim() || null,
      status: "active",
    };

    const createdCell = await api("/cells/", { method: "POST", body: JSON.stringify(payload) });

    await api(`/cells/${createdCell.id}/members/${leaderMemberId}`, {
      method: "POST",
      body: JSON.stringify({}),
    });

    await api(`/cells/${createdCell.id}/leaders`, {
      method: "POST",
      body: JSON.stringify({ member_id: disciplerMemberId, role: "co_leader", is_primary: false }),
    });
    await api(`/cells/${createdCell.id}/leaders`, {
      method: "POST",
      body: JSON.stringify({
        member_id: leaderMemberId,
        discipler_member_id: disciplerMemberId,
        role: "leader",
        is_primary: false,
      }),
    });
    await ensureDisciplerIsSupervisorOnly(createdCell.id, disciplerMemberId, leaderMemberId);

    el.cellsCreateCellForm.reset();
    if (el.cellsCreateCellDisciplerId) el.cellsCreateCellDisciplerId.value = "";
    if (el.cellsCreateCellLeaderId) el.cellsCreateCellLeaderId.value = "";
    await Promise.all([loadCells(), loadMembers()]);
    await loadAvailableMembersForCellCreation();
    setCellsMessage("Celula cadastrada com lider vinculado e discipulador supervisor definido.", false);
  }

  async function submitCreateDiscipler(event) {
    event.preventDefault();
    const member = await createMemberOnly(
      el.cellsCreateDisciplerName.value.trim(),
      el.cellsCreateDisciplerContact.value.trim()
    );
    setMemberRoleTag(member.id, "discipler");

    el.cellsCreateDisciplerForm.reset();
    await loadMembers();
    await loadAvailableMembersForCellCreation();
    setCellsMessage("Discipulador cadastrado com sucesso. Vincule a uma celula no cadastro da celula.", false);
  }

  async function submitCreateLeader(event) {
    event.preventDefault();
    const member = await createMemberOnly(
      el.cellsCreateLeaderName.value.trim(),
      el.cellsCreateLeaderContact.value.trim()
    );
    setMemberRoleTag(member.id, "leader");

    el.cellsCreateLeaderForm.reset();
    await loadMembers();
    await loadAvailableMembersForCellCreation();
    setCellsMessage("Lider cadastrado com sucesso. Vincule a uma celula no cadastro da celula.", false);
  }

  async function ensureCellsInitialized() {
    if (state.initialized) return;
    await loadCurrentUserRole();
    applyRoleLayout();
    state.memberRoleTags = loadRoleTagsFromStorage();
    applyPreset(30);
    await Promise.all([loadCells(), loadMembers()]);
    await refreshLeadershipByCellMap();
    resetPeopleCountStartDateInputs();
    state.initialized = true;
  }

  async function createRoleMemberFromCell(roleTag) {
    const roleLabel = roleTag === "discipler" ? "discipulador" : "lider";
    const controls = getRoleControls(roleTag);
    const name = controls.input ? controls.input.value.trim() : "";
    if (!name || !name.trim()) return;

    const member = await createMemberOnly(name.trim(), "");
    setMemberRoleTag(member.id, roleTag);

    await loadMembers();
    await loadAvailableMembersForCellCreation();

    setRoleInputToMember(roleTag, member);
    if (roleTag === "discipler") syncCreateCellRoleOptions();
    hideRoleList(roleTag);

    setCellsMessage(`${roleLabel.charAt(0).toUpperCase() + roleLabel.slice(1)} adicionado com sucesso.`, false);
  }

  async function submitCellModal(event) {
    event.preventDefault();
    const cellId = toNumber(el.cellsCellModalId ? el.cellsCellModalId.value : 0, 0);
    const disciplerMemberId = toNumber(el.cellsCellModalDisciplerId ? el.cellsCellModalDisciplerId.value : 0, 0);
    const leaderMemberId = toNumber(el.cellsCellModalLeaderId ? el.cellsCellModalLeaderId.value : 0, 0);
    const payload = {
      name: el.cellsCellModalName ? el.cellsCellModalName.value.trim() : "",
      weekday: el.cellsCellModalWeekday ? el.cellsCellModalWeekday.value : "monday",
      meeting_time: `${el.cellsCellModalMeetingTime ? el.cellsCellModalMeetingTime.value : "19:00"}:00`,
      address: el.cellsCellModalAddress && el.cellsCellModalAddress.value.trim()
        ? el.cellsCellModalAddress.value.trim()
        : null,
      status: el.cellsCellModalStatus ? el.cellsCellModalStatus.value : "active",
    };

    if (!payload.name) throw new Error("Informe o nome da celula.");
    if (!disciplerMemberId) throw new Error("Selecione um discipulador para a celula.");
    if (!leaderMemberId) throw new Error("Selecione um lider para a celula.");
    if (disciplerMemberId === leaderMemberId) throw new Error("Lider e discipulador devem ser pessoas diferentes.");

    if (cellId) {
      await api(`/cells/${cellId}`, { method: "PUT", body: JSON.stringify(payload) });
      await ensureMembersLinkedToCell(cellId, [leaderMemberId]);
      await syncCellLeadershipAssignments(cellId, disciplerMemberId, leaderMemberId);
      await ensureDisciplerIsSupervisorOnly(cellId, disciplerMemberId, leaderMemberId);
      setCellsMessage("Celula atualizada com sucesso.", false);
    } else {
      const createdCell = await api("/cells/", { method: "POST", body: JSON.stringify(payload) });
      await ensureMembersLinkedToCell(createdCell.id, [leaderMemberId]);
      await syncCellLeadershipAssignments(createdCell.id, disciplerMemberId, leaderMemberId);
      await ensureDisciplerIsSupervisorOnly(createdCell.id, disciplerMemberId, leaderMemberId);
      setCellsMessage("Celula cadastrada com sucesso.", false);
    }

    closeCellModal();
    await refreshCellsAdminData();
  }

  async function submitMemberModal(event) {
    event.preventDefault();
    const memberId = toNumber(el.cellsMemberModalId ? el.cellsMemberModalId.value : 0, 0);
    const roleTag = valueOr(el.cellsMemberModalRoleTag ? el.cellsMemberModalRoleTag.value : "", "");
    const fullName = el.cellsMemberModalName ? el.cellsMemberModalName.value.trim() : "";
    const contact = el.cellsMemberModalContact ? el.cellsMemberModalContact.value.trim() : "";
    const status = el.cellsMemberModalStatus ? el.cellsMemberModalStatus.value : "active";
    const countStartDate = el.cellsMemberModalCountStartDate ? el.cellsMemberModalCountStartDate.value : "";

    if (!fullName) throw new Error("Informe o nome completo.");
    if (!roleTag) throw new Error("Perfil invalido para o registro.");
    if (!countStartDate) throw new Error("Informe a data de cadastrado.");

    if (memberId) {
      await api(`/cells/members/${memberId}`, {
        method: "PUT",
        body: JSON.stringify({
          full_name: fullName,
          contact: contact || null,
          status,
          count_start_date: countStartDate,
        }),
      });
      setMemberRoleTag(memberId, roleTag);
      setCellsMessage("Registro atualizado com sucesso.", false);
    } else {
      const member = await api("/cells/members/all", {
        method: "POST",
        body: JSON.stringify({
          full_name: fullName,
          contact: contact || null,
          status,
          count_start_date: countStartDate,
        }),
      });
      setMemberRoleTag(member.id, roleTag);
      setCellsMessage("Registro cadastrado com sucesso.", false);
    }

    closeMemberModal();
    await refreshCellsAdminData();
  }

  async function openCellsModule() {
    setActiveModule("cells");
    await ensureCellsInitialized();
    if (isLeaderMode()) {
      setCellsView("people");
      fillPeopleCellSelect();
      await loadPeopleViewData();
      fillMeetingsCellSelect();
      return;
    }
    setCellsView("dashboard");
    await loadCellsDashboard();
  }

  async function handleLoadError(fn, fallbackMessage) {
    try {
      await fn();
    } catch (error) {
      const message = error instanceof Error ? error.message : fallbackMessage;
      setCellsMessage(message, true);
    }
  }

  el.financeBtn.addEventListener("click", function () {
    setActiveModule("finance");
  });

  el.cellsBtn.addEventListener("click", function () {
    handleLoadError(openCellsModule, "Falha ao carregar modulo de celulas.");
  });

  if (valueOr(localStorage.getItem("currentUserRole"), "").toLowerCase() === "leader" && getToken()) {
    handleLoadError(openCellsModule, "Falha ao carregar modulo de celulas.");
  }

  if (el.cellsNavDashboardBtn) {
    el.cellsNavDashboardBtn.addEventListener("click", function () {
      setCellsView("dashboard");
      handleLoadError(loadCellsDashboard, "Falha ao carregar dashboard de celulas.");
    });
  }

  if (el.cellsNavCellsBtn) {
    el.cellsNavCellsBtn.addEventListener("click", function () {
      setCellsView("cells");
      handleLoadError(refreshCellsAdminData, "Falha ao carregar tabela de celulas.");
    });
  }

  if (el.cellsNavPeopleBtn) {
    el.cellsNavPeopleBtn.addEventListener("click", function () {
      setCellsView("people");
      handleLoadError(async function () {
        fillPeopleCellSelect();
        await loadPeopleViewData();
      }, "Falha ao carregar pessoas da celula.");
    });
  }

  if (el.cellsNavMeetingsBtn) {
    el.cellsNavMeetingsBtn.addEventListener("click", function () {
      setCellsView("meetings");
      handleLoadError(async function () {
        fillMeetingsCellSelect();
        await loadMeetingsViewData();
      }, "Falha ao carregar reunioes da celula.");
    });
  }

  if (el.cellsNavLeadersBtn) {
    el.cellsNavLeadersBtn.addEventListener("click", function () {
      setCellsView("leaders");
      handleLoadError(refreshCellsAdminData, "Falha ao carregar tabela de lideres.");
    });
  }

  if (el.cellsNavDisciplersBtn) {
    el.cellsNavDisciplersBtn.addEventListener("click", function () {
      setCellsView("disciplers");
      handleLoadError(refreshCellsAdminData, "Falha ao carregar tabela de discipuladores.");
    });
  }

  if (el.cellsNavLostSheepBtn) {
    el.cellsNavLostSheepBtn.addEventListener("click", function () {
      setCellsView("lost-sheep");
      handleLoadError(loadLostSheepData, "Falha ao carregar ovelhas perdidas.");
    });
  }

  if (el.cellsApplyFiltersBtn) {
    el.cellsApplyFiltersBtn.addEventListener("click", function () {
      handleLoadError(loadCellsDashboard, "Falha ao aplicar filtros.");
    });
  }

  if (el.cellsRefreshBtn) {
    el.cellsRefreshBtn.addEventListener("click", function () {
      handleLoadError(async function () {
        await Promise.all([loadCells(), loadMembers()]);
        await loadCellsDashboard();
      }, "Falha ao atualizar modulo de celulas.");
    });
  }

  if (el.cellsPeopleRefreshBtn) {
    el.cellsPeopleRefreshBtn.addEventListener("click", function () {
      handleLoadError(async function () {
        await loadCells();
        fillPeopleCellSelect();
        await loadPeopleViewData();
      }, "Falha ao atualizar pessoas da celula.");
    });
  }

  if (el.cellsMeetingsRefreshBtn) {
    el.cellsMeetingsRefreshBtn.addEventListener("click", function () {
      handleLoadError(async function () {
        await loadCells();
        fillMeetingsCellSelect();
        await loadMeetingsViewData();
      }, "Falha ao atualizar reunioes da celula.");
    });
  }

  if (el.cellsPeopleCellSelect) {
    el.cellsPeopleCellSelect.addEventListener("change", function () {
      handleLoadError(loadPeopleViewData, "Falha ao carregar pessoas da celula.");
    });
  }

  if (el.cellsMeetingsCellSelect) {
    el.cellsMeetingsCellSelect.addEventListener("change", function () {
      handleLoadError(loadMeetingsViewData, "Falha ao carregar reunioes da celula.");
    });
  }

  if (el.cellsMeetingsStartDate) {
    el.cellsMeetingsStartDate.addEventListener("change", function () {
      handleLoadError(loadMeetingsViewData, "Falha ao aplicar filtro de data.");
    });
  }

  if (el.cellsMeetingsEndDate) {
    el.cellsMeetingsEndDate.addEventListener("change", function () {
      handleLoadError(loadMeetingsViewData, "Falha ao aplicar filtro de data.");
    });
  }

  if (el.cellsMeetingsPrevBtn) {
    el.cellsMeetingsPrevBtn.addEventListener("click", function () {
      state.meetingsPagination.page -= 1;
      renderMeetingsTable();
    });
  }

  if (el.cellsMeetingsNextBtn) {
    el.cellsMeetingsNextBtn.addEventListener("click", function () {
      state.meetingsPagination.page += 1;
      renderMeetingsTable();
    });
  }

  if (el.cellsPeopleVisitorForm) {
    el.cellsPeopleVisitorForm.addEventListener("submit", function (event) {
      event.preventDefault();
      handleLoadError(async function () {
        await addPersonToSelectedCell(
          "visitor",
          el.cellsPeopleVisitorName ? el.cellsPeopleVisitorName.value.trim() : "",
          el.cellsPeopleVisitorContact ? el.cellsPeopleVisitorContact.value.trim() : "",
          el.cellsPeopleVisitorCountStartDate ? el.cellsPeopleVisitorCountStartDate.value : ""
        );
        if (el.cellsPeopleVisitorForm) el.cellsPeopleVisitorForm.reset();
        if (el.cellsPeopleVisitorCountStartDate) el.cellsPeopleVisitorCountStartDate.value = getTodayIsoDate();
        await loadPeopleViewData();
        setCellsMessage("Visitante cadastrado com sucesso.", false);
      }, "Falha ao cadastrar visitante.");
    });
  }

  if (el.cellsPeopleAssiduoForm) {
    el.cellsPeopleAssiduoForm.addEventListener("submit", function (event) {
      event.preventDefault();
      handleLoadError(async function () {
        await addPersonToSelectedCell(
          "assiduo",
          el.cellsPeopleAssiduoName ? el.cellsPeopleAssiduoName.value.trim() : "",
          el.cellsPeopleAssiduoContact ? el.cellsPeopleAssiduoContact.value.trim() : "",
          el.cellsPeopleAssiduoCountStartDate ? el.cellsPeopleAssiduoCountStartDate.value : ""
        );
        if (el.cellsPeopleAssiduoForm) el.cellsPeopleAssiduoForm.reset();
        if (el.cellsPeopleAssiduoCountStartDate) el.cellsPeopleAssiduoCountStartDate.value = getTodayIsoDate();
        await loadPeopleViewData();
        setCellsMessage("Assiduo cadastrado com sucesso.", false);
      }, "Falha ao cadastrar assiduo.");
    });
  }

  if (el.cellsPeopleMemberForm) {
    el.cellsPeopleMemberForm.addEventListener("submit", function (event) {
      event.preventDefault();
      handleLoadError(async function () {
        await addPersonToSelectedCell(
          "member",
          el.cellsPeopleMemberName ? el.cellsPeopleMemberName.value.trim() : "",
          el.cellsPeopleMemberContact ? el.cellsPeopleMemberContact.value.trim() : "",
          el.cellsPeopleMemberCountStartDate ? el.cellsPeopleMemberCountStartDate.value : ""
        );
        if (el.cellsPeopleMemberForm) el.cellsPeopleMemberForm.reset();
        if (el.cellsPeopleMemberCountStartDate) el.cellsPeopleMemberCountStartDate.value = getTodayIsoDate();
        await loadPeopleViewData();
        setCellsMessage("Membro cadastrado com sucesso.", false);
      }, "Falha ao cadastrar membro.");
    });
  }

  if (el.cellsMeetingsForm) {
    el.cellsMeetingsForm.addEventListener("submit", function (event) {
      event.preventDefault();
      handleLoadError(async function () {
        const cellId = toNumber(el.cellsMeetingsCellSelect ? el.cellsMeetingsCellSelect.value : 0, 0);
        const meetingDate = el.cellsMeetingDate ? el.cellsMeetingDate.value : "";
        const theme = el.cellsMeetingTheme ? el.cellsMeetingTheme.value.trim() : "";
        const notes = el.cellsMeetingNotes ? el.cellsMeetingNotes.value.trim() : "";

        if (!cellId) throw new Error("Selecione uma celula para criar reuniao.");
        if (!meetingDate) throw new Error("Informe a data da reuniao.");

        await api(`/cells/${cellId}/meetings`, {
          method: "POST",
          body: JSON.stringify({
            meeting_date: meetingDate,
            theme: theme || null,
            notes: notes || null,
          }),
        });

        if (el.cellsMeetingsForm) el.cellsMeetingsForm.reset();
        await loadMeetingsViewData();
        setCellsMessage("Reuniao criada com sucesso.", false);
      }, "Falha ao criar reuniao.");
    });
  }

  if (el.cellsMeetingsView) {
    el.cellsMeetingsView.addEventListener("click", function (event) {
      const target = event.target;
      if (!(target instanceof HTMLElement)) return;
      if (!target.classList.contains("cells-open-attendance-btn")) return;

      const meetingId = toNumber(target.getAttribute("data-meeting-id"), 0);
      const cellId = toNumber(target.getAttribute("data-cell-id"), 0);
      const meetingDate = valueOr(target.getAttribute("data-meeting-date"), "");
      if (!meetingId || !cellId) return;

      handleLoadError(function () {
        return openAttendanceModal(meetingId, cellId, meetingDate);
      }, "Falha ao carregar frequencia da reuniao.");
    });
  }

  if (el.cellsAttendanceModalCloseBtn) {
    el.cellsAttendanceModalCloseBtn.addEventListener("click", closeAttendanceModal);
  }

  if (el.cellsAttendanceModalCancelBtn) {
    el.cellsAttendanceModalCancelBtn.addEventListener("click", closeAttendanceModal);
  }

  if (el.cellsAttendanceModalSaveBtn) {
    el.cellsAttendanceModalSaveBtn.addEventListener("click", function () {
      handleLoadError(saveAttendanceFromModal, "Falha ao salvar frequencia.");
    });
  }

  if (el.cellsAttendanceModalSaveAndPeopleBtn) {
    el.cellsAttendanceModalSaveAndPeopleBtn.addEventListener("click", function () {
      handleLoadError(function () { return saveAttendanceFromModal(true); }, "Falha ao salvar frequencia.");
    });
  }

  if (el.cellsAttendanceModal) {
    el.cellsAttendanceModal.addEventListener("click", function (event) {
      if (event.target === el.cellsAttendanceModal) {
        closeAttendanceModal();
      }
    });
  }

  if (el.cellsCellsRefreshBtn) {
    el.cellsCellsRefreshBtn.addEventListener("click", function () {
      handleLoadError(refreshCellsAdminData, "Falha ao atualizar tabela de celulas.");
    });
  }

  if (el.cellsLeadersRefreshBtn) {
    el.cellsLeadersRefreshBtn.addEventListener("click", function () {
      handleLoadError(refreshCellsAdminData, "Falha ao atualizar tabela de lideres.");
    });
  }

  if (el.cellsDisciplersRefreshBtn) {
    el.cellsDisciplersRefreshBtn.addEventListener("click", function () {
      handleLoadError(refreshCellsAdminData, "Falha ao atualizar tabela de discipuladores.");
    });
  }

  if (el.cellsCellsAddBtn) {
    el.cellsCellsAddBtn.addEventListener("click", function () {
      handleLoadError(function () { return openCellModal(null); }, "Falha ao abrir cadastro de celula.");
    });
  }

  if (el.cellsLeadersAddBtn) {
    el.cellsLeadersAddBtn.addEventListener("click", function () {
      openMemberModal("leader", null);
    });
  }

  if (el.cellsDisciplersAddBtn) {
    el.cellsDisciplersAddBtn.addEventListener("click", function () {
      openMemberModal("discipler", null);
    });
  }

  if (el.cellsCellModalCloseBtn) {
    el.cellsCellModalCloseBtn.addEventListener("click", closeCellModal);
  }

  if (el.cellsCellModalDisciplerId) {
    el.cellsCellModalDisciplerId.addEventListener("change", function () {
      updateCellModalLeaderOptions();
    });
  }

  if (el.cellsMemberModalCloseBtn) {
    el.cellsMemberModalCloseBtn.addEventListener("click", closeMemberModal);
  }

  if (el.cellsCellModalForm) {
    el.cellsCellModalForm.addEventListener("submit", function (event) {
      handleLoadError(function () { return submitCellModal(event); }, "Falha ao salvar celula.");
    });
  }

  if (el.cellsMemberModalForm) {
    el.cellsMemberModalForm.addEventListener("submit", function (event) {
      handleLoadError(function () { return submitMemberModal(event); }, "Falha ao salvar registro.");
    });
  }

  if (el.cellsCellModalDisableBtn) {
    el.cellsCellModalDisableBtn.addEventListener("click", function () {
      const cellId = toNumber(el.cellsCellModalId ? el.cellsCellModalId.value : 0, 0);
      if (!cellId) return;
      handleLoadError(async function () {
        await disableCell(cellId);
        closeCellModal();
      }, "Falha ao desabilitar celula.");
    });
  }

  if (el.cellsCellModalDeleteBtn) {
    el.cellsCellModalDeleteBtn.addEventListener("click", function () {
      const cellId = toNumber(el.cellsCellModalId ? el.cellsCellModalId.value : 0, 0);
      if (!cellId) return;
      openConfirmModal(
        "Tem certeza que deseja excluir esta celula? Esta acao nao pode ser desfeita.",
        async function () {
          await deleteCell(cellId);
          closeCellModal();
        },
        "Falha ao excluir celula."
      );
    });
  }

  if (el.cellsMemberModalDisableBtn) {
    el.cellsMemberModalDisableBtn.addEventListener("click", function () {
      const memberId = toNumber(el.cellsMemberModalId ? el.cellsMemberModalId.value : 0, 0);
      const roleTag = valueOr(el.cellsMemberModalRoleTag ? el.cellsMemberModalRoleTag.value : "", "");
      if (!memberId) return;
      handleLoadError(async function () {
        await disableMember(memberId, roleTag, false);
        closeMemberModal();
      }, "Falha ao desabilitar registro.");
    });
  }

  if (el.cellsMemberModalDeleteBtn) {
    el.cellsMemberModalDeleteBtn.addEventListener("click", function () {
      const memberId = toNumber(el.cellsMemberModalId ? el.cellsMemberModalId.value : 0, 0);
      const roleTag = valueOr(el.cellsMemberModalRoleTag ? el.cellsMemberModalRoleTag.value : "", "");
      if (!memberId) return;
      openConfirmModal(
        "Tem certeza que deseja excluir este registro? Esta acao nao pode ser desfeita.",
        async function () {
          await disableMember(memberId, roleTag, true);
          closeMemberModal();
        },
        "Falha ao excluir registro."
      );
    });
  }

  if (el.cellsConfirmModalCloseBtn) {
    el.cellsConfirmModalCloseBtn.addEventListener("click", closeConfirmModal);
  }

  if (el.cellsConfirmModalCancelBtn) {
    el.cellsConfirmModalCancelBtn.addEventListener("click", closeConfirmModal);
  }

  if (el.cellsConfirmModalConfirmBtn) {
    el.cellsConfirmModalConfirmBtn.addEventListener("click", function () {
      confirmModalAction();
    });
  }

  if (el.cellsSelect) {
    el.cellsSelect.addEventListener("change", function () {
      handleLoadError(loadCellsDashboard, "Falha ao carregar dados da celula.");
    });
  }

  if (el.cellsCreateCellForm) {
    el.cellsCreateCellForm.addEventListener("submit", function (event) {
      handleLoadError(function () { return submitCreateCell(event); }, "Falha ao cadastrar celula.");
    });
  }

  if (el.cellsCreateCellDisciplerInput) {
    el.cellsCreateCellDisciplerInput.addEventListener("input", function () {
      resolveRoleSelection("discipler");
      resolveRoleSelection("leader");
      renderRoleList("discipler");
    });
    el.cellsCreateCellDisciplerInput.addEventListener("change", function () {
      resolveRoleSelection("discipler");
      resolveRoleSelection("leader");
      hideRoleList("discipler");
    });
    el.cellsCreateCellDisciplerInput.addEventListener("blur", function () {
      setTimeout(function () { hideRoleList("discipler"); }, 120);
    });
  }

  if (el.cellsCreateCellLeaderInput) {
    el.cellsCreateCellLeaderInput.addEventListener("input", function () {
      resolveRoleSelection("leader");
      renderRoleList("leader");
    });
    el.cellsCreateCellLeaderInput.addEventListener("change", function () {
      resolveRoleSelection("leader");
      hideRoleList("leader");
    });
    el.cellsCreateCellLeaderInput.addEventListener("blur", function () {
      setTimeout(function () { hideRoleList("leader"); }, 120);
    });
  }

  if (el.cellsModule) {
    el.cellsModule.addEventListener("mousedown", function (event) {
      const target = event.target;
      if (!(target instanceof HTMLElement)) return;
      if (!target.classList.contains("autocomplete-item")) return;

      const roleTag = target.getAttribute("data-role");
      const memberId = toNumber(target.getAttribute("data-member-id"), 0);
      const memberName = valueOr(target.getAttribute("data-member-name"), "");
      if (!roleTag || !memberId || !memberName) return;

      const controls = getRoleControls(roleTag);
      if (!controls.input || !controls.hidden) return;

      controls.input.value = memberName;
      controls.hidden.value = String(memberId);
      toggleRoleAddButton(roleTag);
      hideRoleList(roleTag);

      if (roleTag === "discipler") {
        resolveRoleSelection("leader");
        if (el.cellsCreateCellLeaderInput) {
          renderRoleList("leader");
        }
      }
    });
  }

  if (el.cellsCreateCellAddDisciplerBtn) {
    el.cellsCreateCellAddDisciplerBtn.addEventListener("click", function () {
      handleLoadError(function () { return createRoleMemberFromCell("discipler"); }, "Falha ao adicionar discipulador.");
    });
  }

  if (el.cellsCreateCellAddLeaderBtn) {
    el.cellsCreateCellAddLeaderBtn.addEventListener("click", function () {
      handleLoadError(function () { return createRoleMemberFromCell("leader"); }, "Falha ao adicionar lider.");
    });
  }

  if (el.cellsCreateDisciplerForm) {
    el.cellsCreateDisciplerForm.addEventListener("submit", function (event) {
      handleLoadError(function () { return submitCreateDiscipler(event); }, "Falha ao cadastrar discipulador.");
    });
  }

  if (el.cellsCreateLeaderForm) {
    el.cellsCreateLeaderForm.addEventListener("submit", function (event) {
      handleLoadError(function () { return submitCreateLeader(event); }, "Falha ao cadastrar lider.");
    });
  }

  if (el.cellsListView) {
    el.cellsListView.addEventListener("click", function (event) {
      const target = event.target;
      if (!(target instanceof HTMLElement)) return;
      if (!target.classList.contains("cells-edit-cell-btn")) return;

      const cellId = toNumber(target.getAttribute("data-cell-id"), 0);
      if (!cellId) return;
      const cell = state.cells.find((item) => item.id === cellId);
      if (!cell) return;
      handleLoadError(function () { return openCellModal(cell); }, "Falha ao abrir edicao da celula.");
    });
  }

  if (el.cellsLeadersView) {
    el.cellsLeadersView.addEventListener("click", function (event) {
      const target = event.target;
      if (!(target instanceof HTMLElement)) return;
      if (!target.classList.contains("cells-edit-member-btn")) return;

      const memberId = toNumber(target.getAttribute("data-member-id"), 0);
      if (!memberId) return;
      const member = state.members.find((item) => item.id === memberId);
      if (!member) return;
      openMemberModal("leader", member);
    });
  }

  if (el.cellsDisciplersView) {
    el.cellsDisciplersView.addEventListener("click", function (event) {
      const target = event.target;
      if (!(target instanceof HTMLElement)) return;
      if (!target.classList.contains("cells-edit-member-btn")) return;

      const memberId = toNumber(target.getAttribute("data-member-id"), 0);
      if (!memberId) return;
      const member = state.members.find((item) => item.id === memberId);
      if (!member) return;
      openMemberModal("discipler", member);
    });
  }

  if (el.cellsMemberModalTransferBtn) {
    el.cellsMemberModalTransferBtn.addEventListener("click", function () {
      const memberId = toNumber(el.cellsMemberModalId ? el.cellsMemberModalId.value : 0, 0);
      if (!memberId) return;
      closeMemberPeopleModal();
      openTransferMemberModal(memberId);
    });
  }

  if (el.cellsTransferMemberModalCloseBtn) {
    el.cellsTransferMemberModalCloseBtn.addEventListener("click", closeTransferMemberModal);
  }

  if (el.cellsTransferMemberModalCancelBtn) {
    el.cellsTransferMemberModalCancelBtn.addEventListener("click", closeTransferMemberModal);
  }

  if (el.cellsTransferMemberModalSaveBtn) {
    el.cellsTransferMemberModalSaveBtn.addEventListener("click", function () {
      handleLoadError(transferMemberToCell, "Falha ao transferir membro.");
    });
  }

  if (el.cellsLostSheepRefreshBtn) {
    el.cellsLostSheepRefreshBtn.addEventListener("click", function () {
      handleLoadError(loadLostSheepData, "Falha ao atualizar ovelhas perdidas.");
    });
  }

  if (el.cellsLostSheepModalCloseBtn) {
    el.cellsLostSheepModalCloseBtn.addEventListener("click", closeLostSheepModal);
  }

  if (el.cellsLostSheepModalCancelBtn) {
    el.cellsLostSheepModalCancelBtn.addEventListener("click", closeLostSheepModal);
  }

  if (el.cellsLostSheepModalConfirmBtn) {
    el.cellsLostSheepModalConfirmBtn.addEventListener("click", function () {
      handleLoadError(markMemberAsLostSheep, "Falha ao marcar como ovelha perdida.");
    });
  }

  if (el.cellsLostSheepVisitModalCloseBtn) {
    el.cellsLostSheepVisitModalCloseBtn.addEventListener("click", closeLostSheepVisitModal);
  }

  if (el.cellsLostSheepVisitModalCancelBtn) {
    el.cellsLostSheepVisitModalCancelBtn.addEventListener("click", closeLostSheepVisitModal);
  }

  if (el.cellsLostSheepVisitModalConfirmBtn) {
    el.cellsLostSheepVisitModalConfirmBtn.addEventListener("click", function () {
      handleLoadError(recordLostSheepVisit, "Falha ao registrar visita.");
    });
  }

  if (el.cellsPeopleView) {
    el.cellsPeopleView.addEventListener("click", function (event) {
      const target = event.target;
      if (!(target instanceof HTMLElement)) return;

      if (target.classList.contains("cells-edit-member-people-btn")) {
        const memberId = toNumber(target.getAttribute("data-member-id"), 0);
        if (!memberId) return;
        openMemberPeopleModal(memberId);
      }

      if (target.classList.contains("cells-transfer-member-btn")) {
        const memberId = toNumber(target.getAttribute("data-member-id"), 0);
        if (!memberId) return;
        openTransferMemberModal(memberId);
      }

      if (target.classList.contains("cells-mark-lost-sheep-btn")) {
        const memberId = toNumber(target.getAttribute("data-member-id"), 0);
        const cellId = toNumber(target.getAttribute("data-cell-id"), 0);
        const memberName = valueOr(target.getAttribute("data-member-name"), "");
        if (!memberId || !cellId) return;
        openLostSheepModal(memberId, cellId, memberName);
      }

      if (target.classList.contains("cells-promote-btn")) {
        const memberId = toNumber(target.getAttribute("data-member-id"), 0);
        const stage = valueOr(target.getAttribute("data-target-stage"), "");
        if (!memberId || !stage) return;
        handleLoadError(async function () {
          await promotePersonInSelectedCell(memberId, stage);
          await loadPeopleViewData();
        }, "Falha ao promover pessoa.");
      }
    });
  }

  if (el.cellsLostSheepView) {
    el.cellsLostSheepView.addEventListener("click", function (event) {
      const target = event.target;
      if (!(target instanceof HTMLElement)) return;

      if (target.classList.contains("cells-lost-sheep-visit-btn")) {
        const lostSheepId = toNumber(target.getAttribute("data-lost-sheep-id"), 0);
        if (!lostSheepId) return;
        openLostSheepVisitModal(lostSheepId);
      }
    });
  }

})();
