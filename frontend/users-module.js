(function () {
  const apiPrefix = "/api/v1";
  const usersEndpoint = `${apiPrefix}/users/`;
  const rolesEndpoint = `${apiPrefix}/roles/roles`;
  const permissionsEndpoint = `${apiPrefix}/roles/permissions?skip=0&limit=200`;
  const createPermissionEndpoint = `${apiPrefix}/roles/permissions`;
  const permissionStorageKey = "currentUserPermissions";
  const isAdminStorageKey = "currentUserIsAdmin";

  const MODULE_LABELS = {
    finance: "Financeiro",
    cells: "Células",
    school: "Escola Bíblica",
    users: "Configurações",
  };

  const CATEGORY_LABELS = {
    view: "Visualizar",
    create: "Criar",
    edit: "Editar",
    delete: "Excluir",
    manage: "Gerenciar",
  };

  const MODULE_ORDER = ["finance", "cells", "school", "users"];
  const CATEGORY_ORDER = ["view", "create", "edit", "delete", "manage"];

  const PERMISSION_BLUEPRINT = [
    { module: "finance", groups: [
      { label: "Dashboard", permissions: [{ name: "finance_dashboard_view", category: "view", description: "Visualizar o painel financeiro." }] },
      { label: "Lancamentos", permissions: [
        { name: "finance_transactions_view", category: "view", description: "Visualizar lancamentos." },
        { name: "finance_transactions_create", category: "create", description: "Cadastrar lancamentos." },
        { name: "finance_transactions_edit", category: "edit", description: "Editar lancamentos." },
        { name: "finance_transactions_delete", category: "delete", description: "Excluir lancamentos." },
      ] },
      { label: "Categorias", permissions: [
        { name: "finance_categories_view", category: "view", description: "Visualizar categorias." },
        { name: "finance_categories_create", category: "create", description: "Cadastrar categorias." },
        { name: "finance_categories_edit", category: "edit", description: "Editar categorias." },
        { name: "finance_categories_delete", category: "delete", description: "Excluir categorias." },
      ] },
      { label: "Ministerios", permissions: [
        { name: "finance_ministries_view", category: "view", description: "Visualizar ministerios." },
        { name: "finance_ministries_create", category: "create", description: "Cadastrar ministerios." },
        { name: "finance_ministries_edit", category: "edit", description: "Editar ministerios." },
        { name: "finance_ministries_delete", category: "delete", description: "Excluir ministerios." },
      ] },
      { label: "Contas a pagar", permissions: [
        { name: "finance_payables_view", category: "view", description: "Visualizar contas a pagar." },
        { name: "finance_payables_create", category: "create", description: "Cadastrar contas a pagar." },
        { name: "finance_payables_edit", category: "edit", description: "Editar contas a pagar." },
        { name: "finance_payables_delete", category: "delete", description: "Excluir contas a pagar." },
      ] },
      { label: "Contas a receber", permissions: [
        { name: "finance_receivables_view", category: "view", description: "Visualizar contas a receber." },
        { name: "finance_receivables_create", category: "create", description: "Cadastrar contas a receber." },
        { name: "finance_receivables_edit", category: "edit", description: "Editar contas a receber." },
        { name: "finance_receivables_delete", category: "delete", description: "Excluir contas a receber." },
      ] },
      { label: "Importacao de extrato", permissions: [{ name: "finance_upload_manage", category: "manage", description: "Importar e processar extratos bancarios." }] },
      { label: "Relatorios", permissions: [{ name: "finance_reports_view", category: "view", description: "Visualizar relatorios financeiros." }] },
    ] },
    { module: "cells", groups: [
      { label: "Dashboard", permissions: [{ name: "cells_dashboard_view", category: "view", description: "Visualizar o dashboard de celulas." }] },
      { label: "Celulas", permissions: [
        { name: "cells_cells_view", category: "view", description: "Visualizar celulas." },
        { name: "cells_cells_create", category: "create", description: "Cadastrar celulas." },
        { name: "cells_cells_edit", category: "edit", description: "Editar celulas." },
        { name: "cells_cells_delete", category: "delete", description: "Excluir celulas." },
      ] },
      { label: "Pessoas", permissions: [
        { name: "cells_people_view", category: "view", description: "Visualizar pessoas vinculadas as celulas." },
        { name: "cells_people_add_visitor", category: "create", description: "Adicionar visitante." },
        { name: "cells_people_add_assiduo", category: "create", description: "Adicionar assiduo." },
        { name: "cells_people_add_member", category: "create", description: "Adicionar membro." },
        { name: "cells_people_promote_member", category: "manage", description: "Promover pessoas para membro." },
        { name: "cells_people_transfer_member", category: "manage", description: "Transferir membros entre celulas." },
        { name: "cells_people_disable_member", category: "manage", description: "Desativar membros." },
      ] },
      { label: "Frequencia", permissions: [
        { name: "cells_meetings_view", category: "view", description: "Visualizar reunioes da celula." },
        { name: "cells_meetings_create", category: "create", description: "Cadastrar reunioes da celula." },
        { name: "cells_attendance_manage", category: "manage", description: "Registrar e salvar frequencia." },
      ] },
      { label: "Liderancas", permissions: [
        { name: "cells_leaders_view", category: "view", description: "Visualizar lideres." },
        { name: "cells_leaders_create", category: "create", description: "Cadastrar lideres." },
        { name: "cells_leaders_edit", category: "edit", description: "Editar lideres." },
        { name: "cells_leaders_delete", category: "delete", description: "Excluir lideres." },
      ] },
      { label: "Discipuladores", permissions: [
        { name: "cells_disciplers_view", category: "view", description: "Visualizar discipuladores." },
        { name: "cells_disciplers_create", category: "create", description: "Cadastrar discipuladores." },
        { name: "cells_disciplers_edit", category: "edit", description: "Editar discipuladores." },
        { name: "cells_disciplers_delete", category: "delete", description: "Excluir discipuladores." },
      ] },
      { label: "Ovelhas perdidas", permissions: [
        { name: "cells_lost_sheep_view", category: "view", description: "Visualizar ovelhas perdidas." },
        { name: "cells_lost_sheep_manage", category: "manage", description: "Marcar, registrar visita e tratar ovelhas perdidas." },
      ] },
    ] },
    { module: "school", groups: [
      { label: "Dashboard", permissions: [{ name: "school_dashboard_view", category: "view", description: "Visualizar o dashboard da escola biblica." }] },
      { label: "Cursos", permissions: [
        { name: "school_courses_view", category: "view", description: "Visualizar cursos." },
        { name: "school_courses_create", category: "create", description: "Cadastrar cursos." },
        { name: "school_courses_edit", category: "edit", description: "Editar cursos." },
        { name: "school_courses_delete", category: "delete", description: "Excluir cursos." },
      ] },
      { label: "Turmas", permissions: [
        { name: "school_classes_view", category: "view", description: "Visualizar turmas." },
        { name: "school_classes_create", category: "create", description: "Cadastrar turmas." },
        { name: "school_classes_edit", category: "edit", description: "Editar turmas." },
        { name: "school_classes_delete", category: "delete", description: "Excluir turmas." },
      ] },
      { label: "Professores", permissions: [
        { name: "school_professors_view", category: "view", description: "Visualizar professores." },
        { name: "school_professors_create", category: "create", description: "Cadastrar professores." },
        { name: "school_professors_edit", category: "edit", description: "Editar professores." },
        { name: "school_professors_delete", category: "delete", description: "Excluir professores." },
      ] },
      { label: "Aulas", permissions: [
        { name: "school_lessons_view", category: "view", description: "Visualizar aulas." },
        { name: "school_lessons_create", category: "create", description: "Cadastrar aulas." },
        { name: "school_lessons_edit", category: "edit", description: "Editar aulas." },
        { name: "school_lessons_delete", category: "delete", description: "Excluir aulas." },
      ] },
      { label: "Alunos", permissions: [
        { name: "school_students_view", category: "view", description: "Visualizar alunos." },
        { name: "school_students_create", category: "create", description: "Cadastrar alunos." },
        { name: "school_students_edit", category: "edit", description: "Editar alunos." },
        { name: "school_students_delete", category: "delete", description: "Excluir alunos." },
      ] },
      { label: "Chamada", permissions: [
        { name: "school_attendance_view", category: "view", description: "Visualizar chamada." },
        { name: "school_attendance_manage", category: "manage", description: "Registrar e salvar chamada." },
      ] },
    ] },
    { module: "users", groups: [
      { label: "Usuarios", permissions: [
        { name: "users_users_view", category: "view", description: "Visualizar usuarios." },
        { name: "users_users_create", category: "create", description: "Cadastrar usuarios." },
        { name: "users_users_edit", category: "edit", description: "Editar usuarios." },
        { name: "users_users_delete", category: "delete", description: "Excluir usuarios." },
      ] },
      { label: "Roles", permissions: [
        { name: "users_roles_view", category: "view", description: "Visualizar roles." },
        { name: "users_roles_create", category: "create", description: "Cadastrar roles." },
        { name: "users_roles_edit", category: "edit", description: "Editar roles." },
        { name: "users_roles_delete", category: "delete", description: "Excluir roles." },
      ] },
      { label: "Permissoes", permissions: [
        { name: "users_permissions_view", category: "view", description: "Visualizar permissoes." },
        { name: "users_permissions_create", category: "create", description: "Cadastrar permissoes." },
        { name: "users_permissions_edit", category: "edit", description: "Editar permissoes." },
        { name: "users_permissions_delete", category: "delete", description: "Excluir permissoes." },
      ] },
      { label: "Sistema", permissions: [{ name: "users_system_permissions_manage", category: "manage", description: "Gerar permissoes do sistema." }] },
    ] },
  ];

  let eventsBound = false;

  const el = {
    financeBtn: document.getElementById("moduleFinanceBtn"),
    cellsBtn: document.getElementById("moduleCellsBtn"),
    schoolBtn: document.getElementById("moduleBibleSchoolBtn"),
    usersBtn: document.getElementById("moduleUsersBtn"),

    financeModule: document.getElementById("financeModule"),
    cellsModule: document.getElementById("cellsModule"),
    schoolModule: document.getElementById("bibleSchoolModule"),
    usersModule: document.getElementById("usersModule"),

    usersNavUsersBtn: document.getElementById("usersNavUsersBtn"),
    usersNavRolesBtn: document.getElementById("usersNavRolesBtn"),
    usersUsersView: document.getElementById("usersUsersView"),
    usersRolesView: document.getElementById("usersRolesView"),

    usersMessage: document.getElementById("usersMessage"),
    rolesMessage: document.getElementById("rolesMessage"),
    usersTableBody: document.getElementById("usersTableBody"),
    rolesTableBody: document.getElementById("rolesTableBody"),

    usersAddBtn: document.getElementById("usersAddBtn"),
    usersOpenRoleModalBtn: document.getElementById("usersOpenRoleModalBtn"),
    usersOpenPermissionModalBtn: document.getElementById("usersOpenPermissionModalBtn"),
    usersGeneratePermissionsBtn: document.getElementById("usersGeneratePermissionsBtn"),

    usersFormModal: document.getElementById("usersFormModal"),
    usersFormTitle: document.getElementById("usersFormTitle"),
    usersForm: document.getElementById("usersForm"),
    usersFormEmail: document.getElementById("usersFormEmail"),
    usersFormFullName: document.getElementById("usersFormFullName"),
    usersFormRoleId: document.getElementById("usersFormRoleId"),
    usersFormIsActive: document.getElementById("usersFormIsActive"),
    usersFormPassword: document.getElementById("usersFormPassword"),
    usersFormPasswordHint: document.getElementById("usersFormPasswordHint"),
    usersFormMessage: document.getElementById("usersFormMessage"),
    usersFormCloseBtn: document.getElementById("usersFormCloseBtn"),
    usersFormCancelBtn: document.getElementById("usersFormCancelBtn"),

    usersDeleteModal: document.getElementById("usersDeleteModal"),
    usersDeleteMessage: document.getElementById("usersDeleteMessage"),
    usersDeleteCloseBtn: document.getElementById("usersDeleteCloseBtn"),
    usersDeleteCancelBtn: document.getElementById("usersDeleteCancelBtn"),
    usersDeleteConfirmBtn: document.getElementById("usersDeleteConfirmBtn"),

    usersRoleModal: document.getElementById("usersRoleModal"),
    usersRoleForm: document.getElementById("usersRoleForm"),
    usersRoleName: document.getElementById("usersRoleName"),
    usersRoleDescription: document.getElementById("usersRoleDescription"),
    usersRoleIsAdmin: document.getElementById("usersRoleIsAdmin"),
    usersRoleActive: document.getElementById("usersRoleActive"),
    usersRolePermissions: document.getElementById("usersRolePermissions"),
    usersRoleMessage: document.getElementById("usersRoleMessage"),
    usersRoleCloseBtn: document.getElementById("usersRoleCloseBtn"),
    usersRoleCancelBtn: document.getElementById("usersRoleCancelBtn"),
    usersRoleSubmitBtn: document.getElementById("usersRoleSubmitBtn"),

    usersPermissionModal: document.getElementById("usersPermissionModal"),
    usersPermissionForm: document.getElementById("usersPermissionForm"),
    usersPermissionName: document.getElementById("usersPermissionName"),
    usersPermissionDescription: document.getElementById("usersPermissionDescription"),
    usersPermissionModule: document.getElementById("usersPermissionModule"),
    usersPermissionCategory: document.getElementById("usersPermissionCategory"),
    usersPermissionActive: document.getElementById("usersPermissionActive"),
    usersPermissionMessage: document.getElementById("usersPermissionMessage"),
    usersPermissionCloseBtn: document.getElementById("usersPermissionCloseBtn"),
    usersPermissionCancelBtn: document.getElementById("usersPermissionCancelBtn"),
    usersPermissionSubmitBtn: document.getElementById("usersPermissionSubmitBtn"),
  };

  const state = {
    users: [],
    roles: [],
    permissions: [],
    permissionSet: new Set(),
    isAdmin: false,
    mode: "create",
    currentView: "users",
    editingUserId: null,
    editingRoleId: null,
    deletingUserId: null,
  };

  function getToken() {
    return localStorage.getItem("accessToken") || "";
  }

  function buildHeaders(includeJson) {
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
    }

    if (response.status === 401) return "Sessão expirada. Faça login novamente.";
    return detail;
  }

  async function fetchJson(url, options, fallbackMessage) {
    const response = await fetch(url, options);
    if (!response.ok) throw new Error(await parseError(response, fallbackMessage));
    if (response.status === 204) return null;
    return response.json();
  }

  function toModuleLabel(moduleName) {
    return MODULE_LABELS[moduleName] || moduleName;
  }

  function toCategoryLabel(categoryName) {
    return CATEGORY_LABELS[categoryName] || categoryName;
  }

  function setMessage(message, isError) {
    if (!el.usersMessage) return;
    el.usersMessage.textContent = message || "";
    el.usersMessage.style.color = isError ? "#b42318" : "#5f6b6d";
  }

  function setRolesMessage(message, isError) {
    if (!el.rolesMessage) return;
    el.rolesMessage.textContent = message || "";
    el.rolesMessage.style.color = isError ? "#b42318" : "#5f6b6d";
  }

  function setFormMessage(message, isError) {
    if (!el.usersFormMessage) return;
    el.usersFormMessage.textContent = message || "";
    el.usersFormMessage.style.color = isError ? "#b42318" : "#5f6b6d";
  }

  function setRoleMessage(message, isError) {
    if (!el.usersRoleMessage) return;
    el.usersRoleMessage.textContent = message || "";
    el.usersRoleMessage.style.color = isError ? "#b42318" : "#5f6b6d";
  }

  function setPermissionMessage(message, isError) {
    if (!el.usersPermissionMessage) return;
    el.usersPermissionMessage.textContent = message || "";
    el.usersPermissionMessage.style.color = isError ? "#b42318" : "#5f6b6d";
  }

  function escapeHtml(value) {
    return String(value ?? "")
      .replace(/&/g, "&amp;")
      .replace(/</g, "&lt;")
      .replace(/>/g, "&gt;")
      .replace(/\"/g, "&quot;")
      .replace(/'/g, "&#39;");
  }

  function buildSystemPermissionBlueprint() {
    const permissions = [];

    PERMISSION_BLUEPRINT.forEach((moduleSpec) => {
      moduleSpec.groups.forEach((groupSpec) => {
        groupSpec.permissions.forEach((permissionSpec) => {
          permissions.push({
            module: moduleSpec.module,
            category: permissionSpec.category,
            name: permissionSpec.name,
            description: permissionSpec.description,
            groupLabel: groupSpec.label,
          });
        });
      });
    });

    return permissions;
  }

  function getBlueprintGroupsByModule() {
    return PERMISSION_BLUEPRINT.reduce((accumulator, moduleSpec) => {
      accumulator[moduleSpec.module] = moduleSpec.groups;
      return accumulator;
    }, {});
  }

  function permissionIdentity(permission) {
    return `${permission.module || ""}::${permission.name || ""}`;
  }

  async function generateMissingPermissions() {
    const blueprint = buildSystemPermissionBlueprint();
    const existingByIdentity = new Set(state.permissions.map(permissionIdentity));
    const missingPermissions = blueprint.filter((permission) => !existingByIdentity.has(permissionIdentity(permission)));

    if (!missingPermissions.length) {
      setRolesMessage("Todas as permissões do sistema já estão cadastradas.", false);
      return;
    }

    setRolesMessage(`Gerando ${missingPermissions.length} permissão(ões) do sistema...`, false);

    for (const permission of missingPermissions) {
      await fetchJson(
        createPermissionEndpoint,
        {
          method: "POST",
          headers: buildHeaders(true),
          body: JSON.stringify({
            name: permission.name,
            description: permission.description,
            module: permission.module,
            category: permission.category,
            active: true,
          }),
        },
        "Erro ao gerar permissao do sistema."
      );
    }

    await loadPermissions();
    renderRolePermissions(getSelectedPermissionIds());
    setRolesMessage(`Permissões geradas com sucesso (${missingPermissions.length}).`, false);
  }

  function setActiveModule(moduleName) {
    const isFinance = moduleName === "finance";
    const isCells = moduleName === "cells";
    const isSchool = moduleName === "school";
    const isUsers = moduleName === "users";

    if (el.financeBtn) el.financeBtn.classList.toggle("active", isFinance);
    if (el.cellsBtn) el.cellsBtn.classList.toggle("active", isCells);
    if (el.schoolBtn) el.schoolBtn.classList.toggle("active", isSchool);
    if (el.usersBtn) el.usersBtn.classList.toggle("active", isUsers);

    if (el.financeModule) el.financeModule.classList.toggle("hide", !isFinance);
    if (el.cellsModule) el.cellsModule.classList.toggle("hide", !isCells);
    if (el.schoolModule) el.schoolModule.classList.toggle("hide", !isSchool);
    if (el.usersModule) el.usersModule.classList.toggle("hide", !isUsers);
  }

  function setUsersView(viewName) {
    const viewPermissions = {
      users: "users_users_view",
      roles: "users_roles_view",
    };

    const requiredPermission = viewPermissions[viewName];
    if (requiredPermission && !hasPermission(requiredPermission)) {
      setMessage("Acesso negado: sua role nao permite esta tela.", true);
      const fallback = getFirstAllowedUsersView();
      if (!fallback || fallback === viewName) {
        return;
      }
      viewName = fallback;
    }

    state.currentView = viewName;
    const isUsersView = viewName === "users";
    const isRolesView = viewName === "roles";

    if (el.usersNavUsersBtn) el.usersNavUsersBtn.classList.toggle("active", isUsersView);
    if (el.usersNavRolesBtn) el.usersNavRolesBtn.classList.toggle("active", isRolesView);
    if (el.usersUsersView) el.usersUsersView.classList.toggle("hide", !isUsersView);
    if (el.usersRolesView) el.usersRolesView.classList.toggle("hide", !isRolesView);
  }

  function loadPermissionState() {
    try {
      const raw = localStorage.getItem(permissionStorageKey);
      const parsed = raw ? JSON.parse(raw) : [];
      const permissions = Array.isArray(parsed) ? parsed.filter((item) => typeof item === "string") : [];
      state.permissionSet = new Set(permissions);
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

  function hasUsersModuleAccess() {
    if (state.isAdmin) return true;
    for (const permissionName of state.permissionSet) {
      if (permissionName.indexOf("users_") === 0) return true;
    }
    return false;
  }

  function getFirstAllowedUsersView() {
    if (hasPermission("users_users_view")) return "users";
    if (hasPermission("users_roles_view")) return "roles";
    return null;
  }

  function applyUsersPermissionLayout() {
    const canOpenModule = hasUsersModuleAccess();
    if (el.usersBtn) {
      el.usersBtn.classList.toggle("hide", !canOpenModule);
      el.usersBtn.disabled = !canOpenModule;
    }

    if (el.usersNavUsersBtn) el.usersNavUsersBtn.classList.toggle("hide", !hasPermission("users_users_view"));
    if (el.usersNavRolesBtn) el.usersNavRolesBtn.classList.toggle("hide", !hasPermission("users_roles_view"));
    if (el.usersAddBtn) el.usersAddBtn.classList.toggle("hide", !hasPermission("users_users_create"));
    if (el.usersOpenRoleModalBtn) el.usersOpenRoleModalBtn.classList.toggle("hide", !hasPermission("users_roles_create"));
    if (el.usersOpenPermissionModalBtn) el.usersOpenPermissionModalBtn.classList.toggle("hide", !hasPermission("users_permissions_create"));
    if (el.usersGeneratePermissionsBtn) el.usersGeneratePermissionsBtn.classList.toggle("hide", !hasPermission("users_system_permissions_manage"));
  }

  async function loadUsers() {
    setMessage("Carregando usuários...", false);
    state.users = await fetchJson(usersEndpoint, { headers: buildHeaders(false) }, "Falha ao carregar usuários.");
    renderUsers();
    setMessage("", false);
  }

  async function loadRoles() {
    state.roles = await fetchJson(rolesEndpoint, { headers: buildHeaders(false) }, "Falha ao carregar roles.");
    renderRoles();
  }

  async function loadPermissions() {
    state.permissions = await fetchJson(permissionsEndpoint, { headers: buildHeaders(false) }, "Falha ao carregar permissões.");
  }

  function ensureRolesOptions(selectedRoleId) {
    if (!el.usersFormRoleId) return;

    if (!state.roles.length) {
      el.usersFormRoleId.innerHTML = '<option value="">Nenhuma role disponível</option>';
      el.usersFormRoleId.value = "";
      return;
    }

    el.usersFormRoleId.innerHTML = state.roles
      .map((role) => `<option value="${role.id}">${role.name}</option>`)
      .join("");

    el.usersFormRoleId.value = selectedRoleId != null ? String(selectedRoleId) : String(state.roles[0].id);
  }

  function renderRolePermissions(selectedIds = []) {
    if (!el.usersRolePermissions) return;

    const selectedSet = new Set((selectedIds || []).map((id) => String(id)));
    const activePermissions = state.permissions.filter((permission) => permission.active);

    const permissionsByIdentity = new Map();
    activePermissions.forEach((permission) => {
      permissionsByIdentity.set(permissionIdentity(permission), permission);
    });

    const blueprintGroupsByModule = getBlueprintGroupsByModule();

    const discoveredModules = [...new Set(activePermissions.map((permission) => permission.module).filter(Boolean))]
      .filter((name) => !MODULE_ORDER.includes(name));
    const moduleOrder = [...MODULE_ORDER, ...discoveredModules];

    const groupsHtml = moduleOrder
      .map((moduleName) => {
        const moduleGroups = blueprintGroupsByModule[moduleName] || [];
        const moduleGroupHtml = moduleGroups
          .map((groupSpec) => {
            const groupItems = groupSpec.permissions
              .map((permissionSpec) => {
                const existingPermission = permissionsByIdentity.get(`${moduleName}::${permissionSpec.name}`);

                if (!existingPermission) {
                  return `<label class="role-permission-item" style="opacity:0.55"><input type="checkbox" disabled> <span><strong>${escapeHtml(permissionSpec.description)}</strong><small>${escapeHtml(toCategoryLabel(permissionSpec.category))}</small></span></label>`;
                }

                const checked = selectedSet.has(String(existingPermission.id)) ? "checked" : "";
                return `<label class="role-permission-item"><input type="checkbox" value="${existingPermission.id}" data-role-permission ${checked}> <span><strong>${escapeHtml(existingPermission.description || permissionSpec.description)}</strong><small>${escapeHtml(toCategoryLabel(existingPermission.category))}</small></span></label>`;
              })
              .join("");

            return `<div class="role-permission-group"><p class="role-permission-group-title">${escapeHtml(groupSpec.label)}</p><div class="role-permission-items">${groupItems}</div></div>`;
          })
          .join("");

        const moduleExtras = activePermissions.filter((permission) => !moduleGroups.some((groupSpec) => groupSpec.permissions.some((permissionSpec) => permissionSpec.name === permission.name)));

        const extrasHtml = moduleExtras.length
          ? `<div class="role-permission-group"><p class="role-permission-group-title">Outras permissões</p><div class="role-permission-items">${moduleExtras
              .map((permission) => {
                const checked = selectedSet.has(String(permission.id)) ? "checked" : "";
                return `<label class="role-permission-item"><input type="checkbox" value="${permission.id}" data-role-permission ${checked}> <span><strong>${escapeHtml(permission.description || permission.name || "Permissão")}</strong><small>${escapeHtml(toCategoryLabel(permission.category))}</small></span></label>`;
              })
              .join("")}</div></div>`
          : "";

        if (!moduleGroupHtml && !extrasHtml) return "";

        return `<div class="role-permission-group"><p class="role-permission-group-title">${escapeHtml(toModuleLabel(moduleName))}</p>${moduleGroupHtml}${extrasHtml}</div>`;
      })
      .join("");

    el.usersRolePermissions.innerHTML = groupsHtml || '<p class="tiny">Nenhuma permissão cadastrada.</p>';
  }

  function getSelectedPermissionIds() {
    if (!el.usersRolePermissions) return [];

    return Array.from(el.usersRolePermissions.querySelectorAll("input[data-role-permission]:checked"))
      .map((node) => parseInt(node.value, 10))
      .filter((value) => Number.isInteger(value));
  }

  function renderUsers() {
    if (!el.usersTableBody) return;

    if (!state.users.length) {
      el.usersTableBody.innerHTML = '<tr><td colspan="5">Nenhum usuário encontrado.</td></tr>';
      return;
    }

    el.usersTableBody.innerHTML = state.users
      .map((user) => {
        const roleName = (user.role_obj && user.role_obj.name) || user.role || "N/A";
        const statusClass = user.is_active ? "bg-success" : "bg-secondary";
        const statusLabel = user.is_active ? "Ativo" : "Inativo";
        const canEdit = hasPermission("users_users_edit");
        const canDelete = hasPermission("users_users_delete");
        const editButton = canEdit
          ? `<button type="button" class="btn btn-sm btn-warning" data-user-edit="${user.id}" onclick="window.usersEditUser && window.usersEditUser(${user.id})">Editar</button>`
          : "";
        const deleteButton = canDelete
          ? `<button type="button" class="btn btn-sm btn-danger" data-user-delete="${user.id}" onclick="window.usersDeleteUser && window.usersDeleteUser(${user.id})">Excluir</button>`
          : "";
        return `<tr>
          <td><strong>${user.email}</strong></td>
          <td>${user.full_name || "-"}</td>
          <td><span class="badge bg-info">${roleName}</span></td>
          <td><span class="badge ${statusClass}">${statusLabel}</span></td>
          <td>
            ${editButton}
            ${deleteButton}
          </td>
        </tr>`;
      })
      .join("");

    el.usersTableBody.querySelectorAll("[data-user-edit]").forEach((button) => {
      button.addEventListener("click", () => openEditUser(parseInt(button.getAttribute("data-user-edit"), 10)));
    });

    el.usersTableBody.querySelectorAll("[data-user-delete]").forEach((button) => {
      button.addEventListener("click", () => openDeleteModal(parseInt(button.getAttribute("data-user-delete"), 10)));
    });
  }

  function renderRoles() {
    if (!el.rolesTableBody) return;

    if (!state.roles.length) {
      el.rolesTableBody.innerHTML = '<tr><td colspan="6">Nenhuma role encontrada.</td></tr>';
      return;
    }

    el.rolesTableBody.innerHTML = state.roles
      .map((role) => {
        const canEditRole = hasPermission("users_roles_edit");
        const canDeleteRole = hasPermission("users_roles_delete");
        const editRoleButton = canEditRole ? `<button class="btn btn-sm btn-warning" data-role-edit="${role.id}">Editar</button>` : "";
        const deleteRoleButton = canDeleteRole ? `<button class="btn btn-sm btn-danger" data-role-delete="${role.id}">Excluir</button>` : "";
        const permissionList = Array.isArray(role.permissions) ? role.permissions : [];
        const permissionCount = permissionList.length;

        const tooltip = permissionList
          .map((permission) => `${toModuleLabel(permission.module)} - ${toCategoryLabel(permission.category)}`)
          .join(", ");

        return `<tr>
          <td><strong>${role.name}</strong></td>
          <td>${role.description || "-"}</td>
          <td>${role.is_admin ? "Sim" : "Não"}</td>
          <td>${role.active ? "Ativa" : "Inativa"}</td>
          <td title="${tooltip || "Sem permissões"}">${permissionCount}</td>
          <td>
            ${editRoleButton}
            ${deleteRoleButton}
          </td>
        </tr>`;
      })
      .join("");

    el.rolesTableBody.querySelectorAll("[data-role-edit]").forEach((button) => {
      button.addEventListener("click", () => openEditRole(parseInt(button.getAttribute("data-role-edit"), 10)));
    });

    el.rolesTableBody.querySelectorAll("[data-role-delete]").forEach((button) => {
      button.addEventListener("click", () => deleteRole(parseInt(button.getAttribute("data-role-delete"), 10)).catch((error) => setRolesMessage(error.message, true)));
    });
  }

  function openUserForm(mode, user) {
    if (!el.usersFormModal) return;

    state.mode = mode;
    state.editingUserId = mode === "edit" && user ? user.id : null;

    if (el.usersFormTitle) el.usersFormTitle.textContent = mode === "edit" ? "Editar usuário" : "Novo usuário";
    if (el.usersFormEmail) el.usersFormEmail.value = user ? user.email || "" : "";
    if (el.usersFormFullName) el.usersFormFullName.value = user ? user.full_name || "" : "";
    if (el.usersFormIsActive) el.usersFormIsActive.value = String(user ? Boolean(user.is_active) : true);

    if (el.usersFormPassword) {
      el.usersFormPassword.value = "";
      el.usersFormPassword.required = mode === "create";
      el.usersFormPassword.placeholder = mode === "create" ? "Informe a senha" : "Opcional";
    }

    if (el.usersFormPasswordHint) {
      el.usersFormPasswordHint.textContent = mode === "create"
        ? "Obrigatória no cadastro."
        : "Opcional na edição. Deixe em branco para manter a senha atual.";
    }

    ensureRolesOptions(user ? user.role_id : null);
    setFormMessage("", false);
    el.usersFormModal.classList.remove("hide");
  }

  function closeUserForm() {
    if (el.usersFormModal) el.usersFormModal.classList.add("hide");
    setFormMessage("", false);
  }

  function openEditUser(userId) {
    const user = state.users.find((item) => item.id === userId);
    if (!user) return;
    openUserForm("edit", user);
  }

  function openDeleteModal(userId) {
    state.deletingUserId = userId;
    if (!el.usersDeleteModal) return;

    const user = state.users.find((item) => item.id === userId);
    if (el.usersDeleteMessage) {
      el.usersDeleteMessage.textContent = `Tem certeza que deseja excluir ${user ? user.email : "este usuário"}?`;
    }

    el.usersDeleteModal.classList.remove("hide");
  }

  function closeDeleteModal() {
    state.deletingUserId = null;
    if (el.usersDeleteModal) el.usersDeleteModal.classList.add("hide");
  }

  function openRoleModal() {
    state.mode = "create";
    state.editingRoleId = null;

    if (el.usersRoleForm) el.usersRoleForm.reset();
    if (el.usersRoleIsAdmin) el.usersRoleIsAdmin.value = "false";
    if (el.usersRoleActive) el.usersRoleActive.value = "true";
    if (el.usersRoleSubmitBtn) el.usersRoleSubmitBtn.textContent = "Criar role";

    renderRolePermissions([]);
    setRoleMessage("", false);
    if (el.usersRoleModal) el.usersRoleModal.classList.remove("hide");
  }

  function openEditRole(roleId) {
    const role = state.roles.find((item) => item.id === roleId);
    if (!role) return;

    state.mode = "edit";
    state.editingRoleId = role.id;

    if (el.usersRoleName) el.usersRoleName.value = role.name || "";
    if (el.usersRoleDescription) el.usersRoleDescription.value = role.description || "";
    if (el.usersRoleIsAdmin) el.usersRoleIsAdmin.value = String(Boolean(role.is_admin));
    if (el.usersRoleActive) el.usersRoleActive.value = String(Boolean(role.active));
    if (el.usersRoleSubmitBtn) el.usersRoleSubmitBtn.textContent = "Salvar alterações";

    const selectedIds = Array.isArray(role.permissions) ? role.permissions.map((permission) => permission.id) : [];
    renderRolePermissions(selectedIds);

    setRoleMessage("", false);
    if (el.usersRoleModal) el.usersRoleModal.classList.remove("hide");
  }

  function closeRoleModal() {
    if (el.usersRoleModal) el.usersRoleModal.classList.add("hide");
    setRoleMessage("", false);
  }

  function openPermissionModal() {
    if (el.usersPermissionForm) el.usersPermissionForm.reset();

    if (el.usersPermissionModule) el.usersPermissionModule.value = "finance";
    if (el.usersPermissionCategory) el.usersPermissionCategory.value = "view";
    if (el.usersPermissionActive) el.usersPermissionActive.value = "true";

    setPermissionMessage("", false);
    if (el.usersPermissionModal) el.usersPermissionModal.classList.remove("hide");
  }

  function closePermissionModal() {
    if (el.usersPermissionModal) el.usersPermissionModal.classList.add("hide");
    setPermissionMessage("", false);
  }

  async function submitUserForm(event) {
    event.preventDefault();

    if (!el.usersFormEmail || !el.usersFormFullName || !el.usersFormRoleId || !el.usersFormIsActive) return;

    const email = el.usersFormEmail.value.trim();
    const fullName = el.usersFormFullName.value.trim();
    const roleId = parseInt(el.usersFormRoleId.value || "0", 10);
    const isActive = el.usersFormIsActive.value === "true";
    const password = el.usersFormPassword ? el.usersFormPassword.value : "";

    if (!email || !fullName || !roleId) {
      setFormMessage("Preencha os campos obrigatórios.", true);
      return;
    }

    if (state.mode === "create" && !password) {
      setFormMessage("A senha é obrigatória para cadastro.", true);
      return;
    }

    const payload = { email, full_name: fullName, role_id: roleId, is_active: isActive };
    if (password) payload.password = password;

    const isCreate = state.mode === "create";
    const endpoint = isCreate ? usersEndpoint : `${usersEndpoint}${state.editingUserId}`;
    const method = isCreate ? "POST" : "PUT";

    try {
      setFormMessage(isCreate ? "Salvando usuário..." : "Atualizando usuário...", false);
      await fetchJson(endpoint, { method, headers: buildHeaders(true), body: JSON.stringify(payload) }, isCreate ? "Erro ao cadastrar usuário." : "Erro ao atualizar usuário.");
      closeUserForm();
      await loadUsers();
    } catch (error) {
      setFormMessage(error instanceof Error ? error.message : "Falha ao salvar usuário.", true);
    }
  }

  async function submitRoleForm(event) {
    event.preventDefault();

    if (!el.usersRoleName || !el.usersRoleDescription || !el.usersRoleIsAdmin || !el.usersRoleActive) return;

    const name = el.usersRoleName.value.trim();
    if (!name) {
      setRoleMessage("Informe o nome da role.", true);
      return;
    }

    const payload = {
      name,
      description: el.usersRoleDescription.value.trim() || null,
      is_admin: el.usersRoleIsAdmin.value === "true",
      active: el.usersRoleActive.value === "true",
      permission_ids: getSelectedPermissionIds(),
    };

    const isEdit = state.mode === "edit" && state.editingRoleId;
    const endpoint = isEdit ? `${rolesEndpoint}/${state.editingRoleId}` : rolesEndpoint;
    const method = isEdit ? "PUT" : "POST";

    try {
      setRoleMessage(isEdit ? "Atualizando role..." : "Criando role...", false);
      await fetchJson(endpoint, { method, headers: buildHeaders(true), body: JSON.stringify(payload) }, isEdit ? "Erro ao atualizar role." : "Erro ao criar role.");
      await loadRoles();
      ensureRolesOptions();
      closeRoleModal();
      setRolesMessage("", false);
    } catch (error) {
      setRoleMessage(error instanceof Error ? error.message : "Falha ao salvar role.", true);
    }
  }

  async function submitPermissionForm(event) {
    event.preventDefault();

    if (!el.usersPermissionName || !el.usersPermissionDescription || !el.usersPermissionModule || !el.usersPermissionCategory || !el.usersPermissionActive) return;

    const name = el.usersPermissionName.value.trim();
    if (!name) {
      setPermissionMessage("Informe o nome da permissão.", true);
      return;
    }

    const payload = {
      name,
      description: el.usersPermissionDescription.value.trim() || null,
      module: el.usersPermissionModule.value,
      category: el.usersPermissionCategory.value,
      active: el.usersPermissionActive.value === "true",
    };

    try {
      setPermissionMessage("Criando permissão...", false);
      await fetchJson(createPermissionEndpoint, { method: "POST", headers: buildHeaders(true), body: JSON.stringify(payload) }, "Erro ao criar permissão.");
      await loadPermissions();
      renderRolePermissions(getSelectedPermissionIds());
      closePermissionModal();
      setRoleMessage("Permissão criada com sucesso.", false);
    } catch (error) {
      setPermissionMessage(error instanceof Error ? error.message : "Falha ao criar permissão.", true);
    }
  }

  async function confirmDeleteUser() {
    if (!state.deletingUserId) return;

    await fetchJson(`${usersEndpoint}${state.deletingUserId}`, { method: "DELETE", headers: buildHeaders(false) }, "Erro ao excluir usuário.");
    closeDeleteModal();
    await loadUsers();
  }

  async function deleteRole(roleId) {
    await fetchJson(`${rolesEndpoint}/${roleId}`, { method: "DELETE", headers: buildHeaders(false) }, "Erro ao excluir role.");
    await loadRoles();
    ensureRolesOptions();
  }

  async function openUsersModule() {
    loadPermissionState();
    applyUsersPermissionLayout();

    if (!hasUsersModuleAccess()) {
      throw new Error("Acesso negado ao modulo Configuracoes.");
    }

    const fallbackView = getFirstAllowedUsersView();
    if (!fallbackView) {
      throw new Error("Sua role nao possui permissao de visualizacao no modulo Configuracoes.");
    }

    setActiveModule("users");
    setUsersView(fallbackView);
    if (hasPermission("users_roles_view") || hasPermission("users_users_view")) {
      await loadPermissions();
    }
    if (hasPermission("users_roles_view") || hasPermission("users_users_view")) {
      await loadRoles();
      ensureRolesOptions();
    }
    if (hasPermission("users_users_view")) {
      await loadUsers();
    }
  }

  async function openRolesView() {
    if (!hasPermission("users_roles_view")) {
      setRolesMessage("Acesso negado: sua role nao permite visualizar roles.", true);
      return;
    }

    setUsersView("roles");
    await loadPermissions();
    await loadRoles();
  }

  function bindEvents() {
    if (eventsBound) return;
    eventsBound = true;

    if (el.usersBtn) {
      el.usersBtn.addEventListener("click", () => {
        openUsersModule().catch((error) => setMessage(error.message, true));
      });
    }

    loadPermissionState();
    applyUsersPermissionLayout();

    if (el.financeBtn) el.financeBtn.addEventListener("click", () => setActiveModule("finance"));
    if (el.cellsBtn) el.cellsBtn.addEventListener("click", () => setActiveModule("cells"));
    if (el.schoolBtn) el.schoolBtn.addEventListener("click", () => setActiveModule("school"));

    if (el.usersNavUsersBtn) el.usersNavUsersBtn.addEventListener("click", () => setUsersView("users"));
    if (el.usersNavRolesBtn) el.usersNavRolesBtn.addEventListener("click", () => openRolesView().catch((error) => setRolesMessage(error.message, true)));

    if (el.usersAddBtn) el.usersAddBtn.addEventListener("click", () => openUserForm("create", null));
    if (el.usersOpenRoleModalBtn) el.usersOpenRoleModalBtn.addEventListener("click", openRoleModal);
    if (el.usersOpenPermissionModalBtn) el.usersOpenPermissionModalBtn.addEventListener("click", openPermissionModal);
    if (el.usersGeneratePermissionsBtn) el.usersGeneratePermissionsBtn.addEventListener("click", () => generateMissingPermissions().catch((error) => setRolesMessage(error.message, true)));

    if (el.usersForm) el.usersForm.addEventListener("submit", submitUserForm);
    if (el.usersRoleForm) el.usersRoleForm.addEventListener("submit", submitRoleForm);
    if (el.usersPermissionForm) el.usersPermissionForm.addEventListener("submit", submitPermissionForm);

    if (el.usersFormCloseBtn) el.usersFormCloseBtn.addEventListener("click", closeUserForm);
    if (el.usersFormCancelBtn) el.usersFormCancelBtn.addEventListener("click", closeUserForm);

    if (el.usersRoleCloseBtn) el.usersRoleCloseBtn.addEventListener("click", closeRoleModal);
    if (el.usersRoleCancelBtn) el.usersRoleCancelBtn.addEventListener("click", closeRoleModal);

    if (el.usersPermissionCloseBtn) el.usersPermissionCloseBtn.addEventListener("click", closePermissionModal);
    if (el.usersPermissionCancelBtn) el.usersPermissionCancelBtn.addEventListener("click", closePermissionModal);

    if (el.usersDeleteCloseBtn) el.usersDeleteCloseBtn.addEventListener("click", closeDeleteModal);
    if (el.usersDeleteCancelBtn) el.usersDeleteCancelBtn.addEventListener("click", closeDeleteModal);
    if (el.usersDeleteConfirmBtn) el.usersDeleteConfirmBtn.addEventListener("click", () => confirmDeleteUser().catch((error) => setMessage(error.message, true)));

    if (el.usersFormModal) {
      el.usersFormModal.addEventListener("click", (event) => {
        if (event.target === el.usersFormModal) closeUserForm();
      });
    }

    if (el.usersRoleModal) {
      el.usersRoleModal.addEventListener("click", (event) => {
        if (event.target === el.usersRoleModal) closeRoleModal();
      });
    }

    if (el.usersPermissionModal) {
      el.usersPermissionModal.addEventListener("click", (event) => {
        if (event.target === el.usersPermissionModal) closePermissionModal();
      });
    }

    if (el.usersDeleteModal) {
      el.usersDeleteModal.addEventListener("click", (event) => {
        if (event.target === el.usersDeleteModal) closeDeleteModal();
      });
    }

    document.addEventListener("click", (event) => {
      const addButton = event.target.closest && event.target.closest("#usersAddBtn");
      if (addButton) {
        openUserForm("create", null);
        return;
      }

      const editButton = event.target.closest && event.target.closest("[data-user-edit]");
      if (editButton) {
        openEditUser(parseInt(editButton.getAttribute("data-user-edit"), 10));
        return;
      }

      const deleteButton = event.target.closest && event.target.closest("[data-user-delete]");
      if (deleteButton) {
        openDeleteModal(parseInt(deleteButton.getAttribute("data-user-delete"), 10));
      }
    });

    if (el.usersAddBtn) {
      el.usersAddBtn.setAttribute("onclick", "window.usersOpenCreateUserModal && window.usersOpenCreateUserModal()");
    }
  }

  window.openUsersModule = () => openUsersModule().catch((error) => setMessage(error.message, true));
  window.usersOpenCreateUserModal = () => openUserForm("create", null);
  window.usersEditUser = (userId) => openEditUser(Number(userId));
  window.usersDeleteUser = (userId) => openDeleteModal(Number(userId));

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", bindEvents);
  } else {
    bindEvents();
  }
})();
