(function () {
  const apiPrefix = "/api/v1";

  const el = {
    financeBtn: document.getElementById("moduleFinanceBtn"),
    cellsBtn: document.getElementById("moduleCellsBtn"),
    financeModule: document.getElementById("financeModule"),
    cellsModule: document.getElementById("cellsModule"),
    cellsNavDashboardBtn: document.getElementById("cellsNavDashboardBtn"),
    cellsNavCreateCellBtn: document.getElementById("cellsNavCreateCellBtn"),
    cellsNavCreateDisciplerBtn: document.getElementById("cellsNavCreateDisciplerBtn"),
    cellsNavCreateLeaderBtn: document.getElementById("cellsNavCreateLeaderBtn"),
    cellsDashboardView: document.getElementById("cellsDashboardView"),
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
    cellsCreateDisciplerForm: document.getElementById("cellsCreateDisciplerForm"),
    cellsCreateDisciplerCell: document.getElementById("cellsCreateDisciplerCell"),
    cellsCreateDisciplerName: document.getElementById("cellsCreateDisciplerName"),
    cellsCreateDisciplerContact: document.getElementById("cellsCreateDisciplerContact"),
    cellsCreateLeaderForm: document.getElementById("cellsCreateLeaderForm"),
    cellsCreateLeaderCell: document.getElementById("cellsCreateLeaderCell"),
    cellsCreateLeaderDiscipler: document.getElementById("cellsCreateLeaderDiscipler"),
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
    currentView: "dashboard",
  };

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
    if (el.cellsCreateCellView) el.cellsCreateCellView.classList.toggle("hide", viewName !== "create-cell");
    if (el.cellsCreateDisciplerView) el.cellsCreateDisciplerView.classList.toggle("hide", viewName !== "create-discipler");
    if (el.cellsCreateLeaderView) el.cellsCreateLeaderView.classList.toggle("hide", viewName !== "create-leader");

    if (el.cellsNavDashboardBtn) el.cellsNavDashboardBtn.classList.toggle("active", viewName === "dashboard");
    if (el.cellsNavCreateCellBtn) el.cellsNavCreateCellBtn.classList.toggle("active", viewName === "create-cell");
    if (el.cellsNavCreateDisciplerBtn) el.cellsNavCreateDisciplerBtn.classList.toggle("active", viewName === "create-discipler");
    if (el.cellsNavCreateLeaderBtn) el.cellsNavCreateLeaderBtn.classList.toggle("active", viewName === "create-leader");
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

  async function loadCells() {
    const cells = await api("/cells/");
    state.cells = Array.isArray(cells) ? cells : [];

    fillCellOptions(el.cellsSelect, state.cells, "Selecione");
    fillCellOptions(el.cellsCreateDisciplerCell, state.cells, "Selecione");
    fillCellOptions(el.cellsCreateLeaderCell, state.cells, "Selecione");

    if (state.cells.length && !el.cellsSelect.value) {
      el.cellsSelect.value = String(state.cells[0].id);
    }
  }

  async function loadDisciplersForCell(cellId) {
    if (!el.cellsCreateLeaderDiscipler) return;
    if (!cellId) {
      el.cellsCreateLeaderDiscipler.innerHTML = '<option value="">Selecione a celula primeiro</option>';
      return;
    }

    const leaders = await api(`/cells/${cellId}/leaders`);
    const disciplers = Array.isArray(leaders)
      ? leaders.filter((item) => item.active && item.role === "co_leader")
      : [];

    if (!disciplers.length) {
      el.cellsCreateLeaderDiscipler.innerHTML = '<option value="">Nenhum discipulador cadastrado</option>';
      return;
    }

    el.cellsCreateLeaderDiscipler.innerHTML = '<option value="">Selecione</option>' + disciplers
      .map((item) => `<option value="${item.member_id}">Membro #${item.member_id}</option>`)
      .join("");
  }

  async function createMemberAndLink(cellId, fullName, contact) {
    const member = await api("/cells/members/all", {
      method: "POST",
      body: JSON.stringify({ full_name: fullName, contact: contact || null, status: "active" }),
    });

    await api(`/cells/${cellId}/members/${member.id}`, {
      method: "POST",
      body: JSON.stringify({}),
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
    const payload = {
      name: el.cellsCreateCellName.value.trim(),
      weekday: el.cellsCreateCellWeekday.value,
      meeting_time: `${el.cellsCreateCellMeetingTime.value}:00`,
      address: el.cellsCreateCellAddress.value.trim() || null,
      status: "active",
    };
    await api("/cells/", { method: "POST", body: JSON.stringify(payload) });
    el.cellsCreateCellForm.reset();
    await loadCells();
    setCellsMessage("Celula cadastrada com sucesso.", false);
  }

  async function submitCreateDiscipler(event) {
    event.preventDefault();
    const cellId = toNumber(el.cellsCreateDisciplerCell.value, 0);
    if (!cellId) throw new Error("Selecione a celula do discipulador.");

    const member = await createMemberAndLink(
      cellId,
      el.cellsCreateDisciplerName.value.trim(),
      el.cellsCreateDisciplerContact.value.trim()
    );

    await api(`/cells/${cellId}/leaders`, {
      method: "POST",
      body: JSON.stringify({ member_id: member.id, role: "co_leader", is_primary: false }),
    });

    el.cellsCreateDisciplerForm.reset();
    if (String(cellId) === el.cellsCreateLeaderCell.value) {
      await loadDisciplersForCell(cellId);
    }
    setCellsMessage("Discipulador cadastrado com sucesso.", false);
  }

  async function submitCreateLeader(event) {
    event.preventDefault();
    const cellId = toNumber(el.cellsCreateLeaderCell.value, 0);
    const disciplerMemberId = toNumber(el.cellsCreateLeaderDiscipler.value, 0);

    if (!cellId) throw new Error("Selecione a celula do lider.");
    if (!disciplerMemberId) throw new Error("Selecione um discipulador para o lider.");

    const member = await createMemberAndLink(
      cellId,
      el.cellsCreateLeaderName.value.trim(),
      el.cellsCreateLeaderContact.value.trim()
    );

    await api(`/cells/${cellId}/leaders`, {
      method: "POST",
      body: JSON.stringify({
        member_id: member.id,
        discipler_member_id: disciplerMemberId,
        role: "leader",
        is_primary: false,
      }),
    });

    el.cellsCreateLeaderForm.reset();
    setCellsMessage("Lider cadastrado com sucesso e vinculado ao discipulador.", false);
  }

  async function ensureCellsInitialized() {
    if (state.initialized) return;
    applyPreset(30);
    await loadCells();
    state.initialized = true;
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

  if (el.cellsNavCreateCellBtn) {
    el.cellsNavCreateCellBtn.addEventListener("click", function () {
      setCellsView("create-cell");
    });
  }

  if (el.cellsNavCreateDisciplerBtn) {
    el.cellsNavCreateDisciplerBtn.addEventListener("click", function () {
      setCellsView("create-discipler");
    });
  }

  if (el.cellsNavCreateLeaderBtn) {
    el.cellsNavCreateLeaderBtn.addEventListener("click", function () {
      setCellsView("create-leader");
      handleLoadError(function () {
        return loadDisciplersForCell(toNumber(el.cellsCreateLeaderCell.value, 0));
      }, "Falha ao carregar discipuladores da celula.");
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
        await loadCells();
        await loadCellsDashboard();
      }, "Falha ao atualizar modulo de celulas.");
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

  if (el.cellsCreateLeaderCell) {
    el.cellsCreateLeaderCell.addEventListener("change", function () {
      handleLoadError(function () {
        return loadDisciplersForCell(toNumber(el.cellsCreateLeaderCell.value, 0));
      }, "Falha ao carregar discipuladores da celula.");
    });
  }

  if (el.cellsCreateCellForm) {
    el.cellsCreateCellForm.addEventListener("submit", function (event) {
      handleLoadError(function () { return submitCreateCell(event); }, "Falha ao cadastrar celula.");
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
})();
