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
    cellsNavLeadersBtn: document.getElementById("cellsNavLeadersBtn"),
    cellsNavDisciplersBtn: document.getElementById("cellsNavDisciplersBtn"),
    cellsDashboardView: document.getElementById("cellsDashboardView"),
    cellsListView: document.getElementById("cellsListView"),
    cellsLeadersView: document.getElementById("cellsLeadersView"),
    cellsDisciplersView: document.getElementById("cellsDisciplersView"),
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
    cellsMemberModalDisableBtn: document.getElementById("cellsMemberModalDisableBtn"),
    cellsMemberModalDeleteBtn: document.getElementById("cellsMemberModalDeleteBtn"),
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
    cellsHistoryMonths: document.getElementById("cellsHistoryMonths"),
    cellsApplyFiltersBtn: document.getElementById("cellsApplyFiltersBtn"),
    cellsRefreshBtn: document.getElementById("cellsRefreshBtn"),
    cellsPreset30Btn: document.getElementById("cellsPreset30Btn"),
    cellsPreset90Btn: document.getElementById("cellsPreset90Btn"),
    cellsPreset180Btn: document.getElementById("cellsPreset180Btn"),
    cellsKpiActiveStart: document.getElementById("cellsKpiActiveStart"),
    cellsKpiRetained: document.getElementById("cellsKpiRetained"),
    cellsKpiRetentionRate: document.getElementById("cellsKpiRetentionRate"),
    cellsKpiRecurringTotal: document.getElementById("cellsKpiRecurringTotal"),
    cellsRecurringBody: document.getElementById("cellsRecurringBody"),
    cellsRetentionChart: document.getElementById("cellsRetentionChart"),
    cellsVisitorsChart: document.getElementById("cellsVisitorsChart"),
    cellsHistoryChart: document.getElementById("cellsHistoryChart"),
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
  };

  if (!el.financeBtn || !el.cellsBtn || !el.financeModule || !el.cellsModule) return;

  const state = {
    initialized: false,
    retentionChart: null,
    visitorsChart: null,
    historyChart: null,
    cells: [],
    members: [],
    availableMembersForCellCreation: [],
    memberRoleTags: {},
    leadershipByCellId: {},
    pendingConfirmAction: null,
    pendingConfirmErrorMessage: "Falha ao executar exclusao.",
    currentView: "dashboard",
  };

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
    if (el.cellsLeadersView) el.cellsLeadersView.classList.toggle("hide", viewName !== "leaders");
    if (el.cellsDisciplersView) el.cellsDisciplersView.classList.toggle("hide", viewName !== "disciplers");
    if (el.cellsCreateCellView) el.cellsCreateCellView.classList.add("hide");
    if (el.cellsCreateDisciplerView) el.cellsCreateDisciplerView.classList.add("hide");
    if (el.cellsCreateLeaderView) el.cellsCreateLeaderView.classList.add("hide");

    if (el.cellsNavDashboardBtn) el.cellsNavDashboardBtn.classList.toggle("active", viewName === "dashboard");
    if (el.cellsNavCellsBtn) el.cellsNavCellsBtn.classList.toggle("active", viewName === "cells");
    if (el.cellsNavLeadersBtn) el.cellsNavLeadersBtn.classList.toggle("active", viewName === "leaders");
    if (el.cellsNavDisciplersBtn) el.cellsNavDisciplersBtn.classList.toggle("active", viewName === "disciplers");
  }

  function formatDate(date) {
    return date.toISOString().slice(0, 10);
  }

  function applyPreset(days) {
    const end = new Date();
    const start = new Date();
    start.setDate(end.getDate() - days);
    el.cellsStartDate.value = formatDate(start);
    el.cellsEndDate.value = formatDate(end);
  }

  function createOrUpdateChart(currentChart, canvas, config) {
    if (!canvas || typeof Chart === "undefined") return currentChart;
    if (currentChart) currentChart.destroy();
    return new Chart(canvas.getContext("2d"), config);
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

    el.cellsKpiRecurringTotal.textContent = String(recurringTotal);
    renderRecurringVisitors(visitors);

    state.visitorsChart = createOrUpdateChart(state.visitorsChart, el.cellsVisitorsChart, {
      type: "bar",
      data: {
        labels: visitors.slice(0, 10).map((item) => valueOr(item.full_name, "-")),
        datasets: [{
          label: "Visitas",
          data: visitors.slice(0, 10).map((item) => toNumber(item.visits_count, 0)),
          backgroundColor: "#1565c0",
          borderRadius: 8,
        }],
      },
      options: { responsive: true, maintainAspectRatio: false, indexAxis: "y" },
    });
  }

  function renderHistory(history) {
    const data = Array.isArray(history) ? history : [];
    state.historyChart = createOrUpdateChart(state.historyChart, el.cellsHistoryChart, {
      type: "line",
      data: {
        labels: data.map((item) => valueOr(item.month, "-")),
        datasets: [
          {
            label: "Reunioes",
            data: data.map((item) => toNumber(item.meetings_count, 0)),
            borderColor: "#1565c0",
            backgroundColor: "rgba(21, 101, 192, 0.2)",
            tension: 0.35,
            fill: true,
          },
          {
            label: "Presencas",
            data: data.map((item) => toNumber(item.presents_count, 0)),
            borderColor: "#0a8f72",
            backgroundColor: "rgba(10, 143, 114, 0.2)",
            tension: 0.35,
            fill: true,
          },
          {
            label: "Visitantes",
            data: data.map((item) => toNumber(item.visitors_count, 0)),
            borderColor: "#f57c00",
            backgroundColor: "rgba(245, 124, 0, 0.18)",
            tension: 0.35,
            fill: true,
          },
        ],
      },
      options: { responsive: true, maintainAspectRatio: false },
    });
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
    const taggedCandidates = state.availableMembersForCellCreation
      .filter((member) => state.memberRoleTags[String(member.id)] === roleTag);
    const base = taggedCandidates.length ? taggedCandidates : state.availableMembersForCellCreation;

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
    const cells = await api("/cells/");
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
        return `<tr>
          <td>${escapeHtml(valueOr(cell.name, `Celula ${cell.id}`))}</td>
          <td>${escapeHtml(formatWeekday(cell.weekday))}</td>
          <td>${escapeHtml(meetingTime)}</td>
          <td>${escapeHtml(leadership.disciplerName)}</td>
          <td>${escapeHtml(leadership.leaderName)}</td>
          <td>${escapeHtml(valueOr(cell.status, "-"))}</td>
          <td><button class="btn ghost btn-inline cells-edit-cell-btn" type="button" data-cell-id="${cell.id}">Editar</button></td>
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

  async function refreshCellsAdminData() {
    await Promise.all([loadCells(), loadMembers()]);
    if (state.cells.length) {
      const assignmentsByCell = await Promise.all(state.cells.map((cell) => api(`/cells/${cell.id}/leaders`)));
      tagMembersFromAssignments(assignmentsByCell);
      state.leadershipByCellId = {};
      state.cells.forEach((cell, index) => {
        const selections = getCellActiveRoleSelections(assignmentsByCell[index]);
        state.leadershipByCellId[String(cell.id)] = selections;
      });
    } else {
      state.leadershipByCellId = {};
    }

    renderCellsListTable();
    renderRoleMembersTable("leader", el.cellsLeadersBody);
    renderRoleMembersTable("discipler", el.cellsDisciplersBody);
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

    const startDate = el.cellsStartDate.value;
    const endDate = el.cellsEndDate.value;
    const months = toNumber(el.cellsHistoryMonths.value, 6);

    if (!startDate || !endDate) throw new Error("Informe data inicial e final.");
    if (new Date(startDate) > new Date(endDate)) throw new Error("Data inicial nao pode ser maior que data final.");

    setCellsMessage("Carregando dados das celulas...", false);

    const [retention, recurring, history] = await Promise.all([
      api(`/cells/${cellId}/dashboard/retention?start_date=${startDate}&end_date=${endDate}`),
      api(`/cells/${cellId}/dashboard/visitors-recurring?start_date=${startDate}&end_date=${endDate}`),
      api(`/cells/${cellId}/dashboard/history?months=${months}`),
    ]);

    renderRetention(retention);
    renderVisitors(recurring);
    renderHistory(history);
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

    await api(`/cells/${createdCell.id}/members/${disciplerMemberId}`, {
      method: "POST",
      body: JSON.stringify({}),
    });
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

    el.cellsCreateCellForm.reset();
    if (el.cellsCreateCellDisciplerId) el.cellsCreateCellDisciplerId.value = "";
    if (el.cellsCreateCellLeaderId) el.cellsCreateCellLeaderId.value = "";
    await Promise.all([loadCells(), loadMembers()]);
    await loadAvailableMembersForCellCreation();
    setCellsMessage("Celula cadastrada com lider e discipulador vinculados com sucesso.", false);
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
    state.memberRoleTags = loadRoleTagsFromStorage();
    applyPreset(30);
    await Promise.all([loadCells(), loadMembers()]);
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
      await ensureMembersLinkedToCell(cellId, [disciplerMemberId, leaderMemberId]);
      await syncCellLeadershipAssignments(cellId, disciplerMemberId, leaderMemberId);
      setCellsMessage("Celula atualizada com sucesso.", false);
    } else {
      const createdCell = await api("/cells/", { method: "POST", body: JSON.stringify(payload) });
      await ensureMembersLinkedToCell(createdCell.id, [disciplerMemberId, leaderMemberId]);
      await syncCellLeadershipAssignments(createdCell.id, disciplerMemberId, leaderMemberId);
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

    if (!fullName) throw new Error("Informe o nome completo.");
    if (!roleTag) throw new Error("Perfil invalido para o registro.");

    if (memberId) {
      await api(`/cells/members/${memberId}`, {
        method: "PUT",
        body: JSON.stringify({
          full_name: fullName,
          contact: contact || null,
          status,
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

  if (el.cellsPreset30Btn) el.cellsPreset30Btn.addEventListener("click", function () { applyPreset(30); });
  if (el.cellsPreset90Btn) el.cellsPreset90Btn.addEventListener("click", function () { applyPreset(90); });
  if (el.cellsPreset180Btn) el.cellsPreset180Btn.addEventListener("click", function () { applyPreset(180); });

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
})();
