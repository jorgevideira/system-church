(function () {
  const apiPrefix = "/api/v1";
  const usersEndpoint = `${apiPrefix}/users/`;
  const rolesEndpoint = `${apiPrefix}/roles/roles`;
  const permissionsEndpoint = `${apiPrefix}/roles/permissions?skip=0&limit=200`;
  const createPermissionEndpoint = `${apiPrefix}/roles/permissions`;
  const tenantEndpoint = `${apiPrefix}/tenants/current`;
  const tenantLogoUploadEndpoint = `${apiPrefix}/tenants/current/logo`;
  const tenantPaymentsEndpoint = `${apiPrefix}/tenants/current/payments`;
  const paymentAccountsEndpoint = `${apiPrefix}/payment-accounts/`;
  const usersLinkExistingEndpoint = `${apiPrefix}/users/link-existing`;
  const tenantInvitationsEndpoint = `${apiPrefix}/tenant-invitations/`;
  const publicEventsEndpoint = `${apiPrefix}/events/public/tenants/`;
  const permissionStorageKey = "currentUserPermissions";
  const isAdminStorageKey = "currentUserIsAdmin";

  const MODULE_LABELS = {
    finance: "Financeiro",
    cells: "Células",
    school: "Escola Bíblica",
    events: "Eventos",
    users: "Configurações",
  };

  const CATEGORY_LABELS = {
    view: "Visualizar",
    create: "Criar",
    edit: "Editar",
    delete: "Excluir",
    manage: "Gerenciar",
  };

  const MODULE_ORDER = ["finance", "cells", "school", "events", "users"];
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
    { module: "events", groups: [
      { label: "Agenda", permissions: [
        { name: "events_events_view", category: "view", description: "Visualizar agenda de eventos." },
        { name: "events_events_create", category: "create", description: "Cadastrar eventos." },
        { name: "events_events_edit", category: "edit", description: "Editar eventos." },
        { name: "events_events_delete", category: "delete", description: "Excluir eventos." },
      ] },
      { label: "Inscricoes", permissions: [
        { name: "events_registrations_view", category: "view", description: "Visualizar inscricoes dos eventos." },
      ] },
      { label: "Pagamentos", permissions: [
        { name: "events_payments_view", category: "view", description: "Visualizar pagamentos dos eventos." },
        { name: "events_payments_manage", category: "manage", description: "Confirmar e acompanhar pagamentos dos eventos." },
      ] },
      { label: "Analytics", permissions: [
        { name: "events_analytics_view", category: "view", description: "Visualizar analytics dos eventos." },
      ] },
      { label: "Notificacoes", permissions: [
        { name: "events_notifications_view", category: "view", description: "Visualizar notificacoes dos eventos." },
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

  const WHATSAPP_COUNTRIES = {
    BR: { dialCode: "+55", placeholder: "+55 11 99999-9999" },
    PT: { dialCode: "+351", placeholder: "+351 912 345 678" },
    US: { dialCode: "+1", placeholder: "+1 (415) 555-2671" },
    AR: { dialCode: "+54", placeholder: "+54 11 1234-5678" },
    PY: { dialCode: "+595", placeholder: "+595 981 234 567" },
  };

  const el = {
    financeBtn: document.getElementById("moduleFinanceBtn"),
    cellsBtn: document.getElementById("moduleCellsBtn"),
    schoolBtn: document.getElementById("moduleBibleSchoolBtn"),
    eventsBtn: document.getElementById("moduleEventsBtn"),
    usersBtn: document.getElementById("moduleUsersBtn"),

    financeModule: document.getElementById("financeModule"),
    cellsModule: document.getElementById("cellsModule"),
    schoolModule: document.getElementById("bibleSchoolModule"),
    eventsModule: document.getElementById("eventsModule"),
    usersModule: document.getElementById("usersModule"),

    usersNavUsersBtn: document.getElementById("usersNavUsersBtn"),
    usersNavRolesBtn: document.getElementById("usersNavRolesBtn"),
    usersNavChurchBtn: document.getElementById("usersNavChurchBtn"),
    usersUsersView: document.getElementById("usersUsersView"),
    usersRolesView: document.getElementById("usersRolesView"),
    usersChurchView: document.getElementById("usersChurchView"),

    usersMessage: document.getElementById("usersMessage"),
    rolesMessage: document.getElementById("rolesMessage"),
    usersChurchMessage: document.getElementById("usersChurchMessage"),
    usersTableBody: document.getElementById("usersTableBody"),
    usersInvitationsBody: document.getElementById("usersInvitationsBody"),
    rolesTableBody: document.getElementById("rolesTableBody"),

    usersAddBtn: document.getElementById("usersAddBtn"),
    usersInviteBtn: document.getElementById("usersInviteBtn"),
    usersOpenLinkInviteModalBtn: document.getElementById("usersOpenLinkInviteModalBtn"),
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

    usersInviteModal: document.getElementById("usersInviteModal"),
    usersInviteForm: document.getElementById("usersInviteForm"),
    usersInviteEmail: document.getElementById("usersInviteEmail"),
    usersInviteRoleId: document.getElementById("usersInviteRoleId"),
    usersInviteIsDefault: document.getElementById("usersInviteIsDefault"),
    usersInviteMessage: document.getElementById("usersInviteMessage"),
    usersInviteCloseBtn: document.getElementById("usersInviteCloseBtn"),
    usersInviteCancelBtn: document.getElementById("usersInviteCancelBtn"),

    usersLinkInviteModal: document.getElementById("usersLinkInviteModal"),
    usersLinkInviteForm: document.getElementById("usersLinkInviteForm"),
    usersLinkInviteEmail: document.getElementById("usersLinkInviteEmail"),
    usersLinkInviteRoleId: document.getElementById("usersLinkInviteRoleId"),
    usersLinkInviteExpiryDays: document.getElementById("usersLinkInviteExpiryDays"),
    usersLinkInviteIsDefault: document.getElementById("usersLinkInviteIsDefault"),
    usersLinkInviteMessage: document.getElementById("usersLinkInviteMessage"),
    usersLinkInviteResult: document.getElementById("usersLinkInviteResult"),
    usersLinkInviteCopyBtn: document.getElementById("usersLinkInviteCopyBtn"),
    usersLinkInviteCloseBtn: document.getElementById("usersLinkInviteCloseBtn"),
    usersLinkInviteCancelBtn: document.getElementById("usersLinkInviteCancelBtn"),

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

    usersChurchRefreshBtn: document.getElementById("usersChurchRefreshBtn"),
    usersChurchCreateBtn: document.getElementById("usersChurchCreateBtn"),
    usersChurchForm: document.getElementById("usersChurchForm"),
    usersChurchName: document.getElementById("usersChurchName"),
    usersChurchSlug: document.getElementById("usersChurchSlug"),
    usersChurchPublicDisplayName: document.getElementById("usersChurchPublicDisplayName"),
    usersChurchPublicDescription: document.getElementById("usersChurchPublicDescription"),
    usersChurchPrimaryColor: document.getElementById("usersChurchPrimaryColor"),
    usersChurchPrimaryColorPicker: document.getElementById("usersChurchPrimaryColorPicker"),
    usersChurchPrimaryEyedropperBtn: document.getElementById("usersChurchPrimaryEyedropperBtn"),
    usersChurchSecondaryColor: document.getElementById("usersChurchSecondaryColor"),
    usersChurchSecondaryColorPicker: document.getElementById("usersChurchSecondaryColorPicker"),
    usersChurchSecondaryEyedropperBtn: document.getElementById("usersChurchSecondaryEyedropperBtn"),
    usersChurchLogoUrl: document.getElementById("usersChurchLogoUrl"),
    usersChurchLogoFile: document.getElementById("usersChurchLogoFile"),
    usersChurchLogoUploadBtn: document.getElementById("usersChurchLogoUploadBtn"),
    usersChurchInlineLogoPreview: document.getElementById("usersChurchInlineLogoPreview"),
    usersChurchSupportEmail: document.getElementById("usersChurchSupportEmail"),
    usersChurchWhatsappCountry: document.getElementById("usersChurchWhatsappCountry"),
    usersChurchSupportWhatsapp: document.getElementById("usersChurchSupportWhatsapp"),
    usersChurchIsActive: document.getElementById("usersChurchIsActive"),
    usersChurchPaymentsMessage: document.getElementById("usersChurchPaymentsMessage"),
    usersChurchPaymentsForm: document.getElementById("usersChurchPaymentsForm"),
    usersChurchPaymentProvider: document.getElementById("usersChurchPaymentProvider"),
    usersChurchPaymentModeStatus: document.getElementById("usersChurchPaymentModeStatus"),
    usersChurchPaymentPixEnabled: document.getElementById("usersChurchPaymentPixEnabled"),
    usersChurchPaymentCardEnabled: document.getElementById("usersChurchPaymentCardEnabled"),
    usersChurchMercadoPagoPublicKey: document.getElementById("usersChurchMercadoPagoPublicKey"),
    usersChurchMercadoPagoAccessToken: document.getElementById("usersChurchMercadoPagoAccessToken"),
    usersChurchMercadoPagoClearAccessToken: document.getElementById("usersChurchMercadoPagoClearAccessToken"),
    usersChurchMercadoPagoWebhookSecret: document.getElementById("usersChurchMercadoPagoWebhookSecret"),
    usersChurchMercadoPagoClearWebhookSecret: document.getElementById("usersChurchMercadoPagoClearWebhookSecret"),
    usersChurchMercadoPagoIntegratorId: document.getElementById("usersChurchMercadoPagoIntegratorId"),
    usersChurchPaymentTokenStatus: document.getElementById("usersChurchPaymentTokenStatus"),
    usersChurchPaymentWebhookStatus: document.getElementById("usersChurchPaymentWebhookStatus"),
    usersChurchPaymentLiveStatus: document.getElementById("usersChurchPaymentLiveStatus"),
    usersPaymentAccountsMessage: document.getElementById("usersPaymentAccountsMessage"),
    usersPaymentAccountGuide: document.getElementById("usersPaymentAccountGuide"),
    usersPaymentAccountForm: document.getElementById("usersPaymentAccountForm"),
    usersPaymentAccountId: document.getElementById("usersPaymentAccountId"),
    usersPaymentAccountLabel: document.getElementById("usersPaymentAccountLabel"),
    usersPaymentAccountProvider: document.getElementById("usersPaymentAccountProvider"),
    usersPaymentAccountEnvironment: document.getElementById("usersPaymentAccountEnvironment"),
    usersPaymentAccountDescription: document.getElementById("usersPaymentAccountDescription"),
    usersPaymentAccountReadiness: document.getElementById("usersPaymentAccountReadiness"),
    usersPaymentAccountOAuthBox: document.getElementById("usersPaymentAccountOAuthBox"),
    usersPaymentAccountSupportsPix: document.getElementById("usersPaymentAccountSupportsPix"),
    usersPaymentAccountSupportsCard: document.getElementById("usersPaymentAccountSupportsCard"),
    usersPaymentAccountIsDefault: document.getElementById("usersPaymentAccountIsDefault"),
    usersPaymentAccountIsActive: document.getElementById("usersPaymentAccountIsActive"),
    usersPaymentAccountPublicKeyLabel: document.getElementById("usersPaymentAccountPublicKeyLabel"),
    usersPaymentAccountPublicKey: document.getElementById("usersPaymentAccountPublicKey"),
    usersPaymentAccountAccessTokenLabel: document.getElementById("usersPaymentAccountAccessTokenLabel"),
    usersPaymentAccountAccessToken: document.getElementById("usersPaymentAccountAccessToken"),
    usersPaymentAccountWebhookSecretLabel: document.getElementById("usersPaymentAccountWebhookSecretLabel"),
    usersPaymentAccountWebhookSecret: document.getElementById("usersPaymentAccountWebhookSecret"),
    usersPaymentAccountIntegratorIdLabel: document.getElementById("usersPaymentAccountIntegratorIdLabel"),
    usersPaymentAccountIntegratorId: document.getElementById("usersPaymentAccountIntegratorId"),
    usersPaymentAccountOAuthBtn: document.getElementById("usersPaymentAccountOAuthBtn"),
    usersPaymentAccountResetBtn: document.getElementById("usersPaymentAccountResetBtn"),
    usersPaymentAccountsBody: document.getElementById("usersPaymentAccountsBody"),
    usersChurchPreviewBtn: document.getElementById("usersChurchPreviewBtn"),
    usersChurchOpenLandingBtn: document.getElementById("usersChurchOpenLandingBtn"),
    usersChurchLandingUrl: document.getElementById("usersChurchLandingUrl"),
    usersChurchCatalogUrl: document.getElementById("usersChurchCatalogUrl"),
    usersChurchLoginUrl: document.getElementById("usersChurchLoginUrl"),
    usersChurchCopyLandingBtn: document.getElementById("usersChurchCopyLandingBtn"),
    usersChurchCopyCatalogBtn: document.getElementById("usersChurchCopyCatalogBtn"),
    usersChurchCopyLoginBtn: document.getElementById("usersChurchCopyLoginBtn"),
    usersChurchPreviewLogo: document.getElementById("usersChurchPreviewLogo"),
    usersChurchPreviewTitle: document.getElementById("usersChurchPreviewTitle"),
    usersChurchPreviewSummary: document.getElementById("usersChurchPreviewSummary"),
    usersChurchPreviewSupport: document.getElementById("usersChurchPreviewSupport"),
    usersChurchPreviewSlug: document.getElementById("usersChurchPreviewSlug"),
    usersChurchPreviewCard: document.getElementById("usersChurchPreviewCard"),
    usersChurchActivationScore: document.getElementById("usersChurchActivationScore"),
    usersChurchActivationChecklist: document.getElementById("usersChurchActivationChecklist"),

    usersChurchCreateModal: document.getElementById("usersChurchCreateModal"),
    usersChurchCreateForm: document.getElementById("usersChurchCreateForm"),
    usersChurchCreateName: document.getElementById("usersChurchCreateName"),
    usersChurchCreateSlug: document.getElementById("usersChurchCreateSlug"),
    usersChurchCreatePublicDisplayName: document.getElementById("usersChurchCreatePublicDisplayName"),
    usersChurchCreateSupportEmail: document.getElementById("usersChurchCreateSupportEmail"),
    usersChurchCreateSupportWhatsapp: document.getElementById("usersChurchCreateSupportWhatsapp"),
    usersChurchCreatePublicDescription: document.getElementById("usersChurchCreatePublicDescription"),
    usersChurchCreateMessage: document.getElementById("usersChurchCreateMessage"),
    usersChurchCreateCloseBtn: document.getElementById("usersChurchCreateCloseBtn"),
    usersChurchCreateCancelBtn: document.getElementById("usersChurchCreateCancelBtn"),
  };

  const state = {
    users: [],
    roles: [],
    permissions: [],
    invitations: [],
    publicEvents: [],
    tenantProfile: null,
    tenantPaymentSettings: null,
    paymentAccounts: [],
    permissionSet: new Set(),
    isAdmin: false,
    mode: "create",
    currentView: "users",
    editingUserId: null,
    editingRoleId: null,
    deletingUserId: null,
    churchDraftLogoPreviewUrl: "",
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

  function setInviteMessage(message, isError) {
    if (!el.usersInviteMessage) return;
    el.usersInviteMessage.textContent = message || "";
    el.usersInviteMessage.style.color = isError ? "#b42318" : "#5f6b6d";
  }

  function setLinkInviteMessage(message, isError) {
    if (!el.usersLinkInviteMessage) return;
    el.usersLinkInviteMessage.textContent = message || "";
    el.usersLinkInviteMessage.style.color = isError ? "#b42318" : "#5f6b6d";
  }

  function setPermissionMessage(message, isError) {
    if (!el.usersPermissionMessage) return;
    el.usersPermissionMessage.textContent = message || "";
    el.usersPermissionMessage.style.color = isError ? "#b42318" : "#5f6b6d";
  }

  function setChurchMessage(message, isError) {
    if (!el.usersChurchMessage) return;
    el.usersChurchMessage.textContent = message || "";
    el.usersChurchMessage.style.color = isError ? "#b42318" : "#5f6b6d";
  }

  function setChurchCreateMessage(message, isError) {
    if (!el.usersChurchCreateMessage) return;
    el.usersChurchCreateMessage.textContent = message || "";
    el.usersChurchCreateMessage.style.color = isError ? "#b42318" : "#5f6b6d";
  }

  function setChurchPaymentsMessage(message, isError) {
    if (!el.usersChurchPaymentsMessage) return;
    el.usersChurchPaymentsMessage.textContent = message || "";
    el.usersChurchPaymentsMessage.style.color = isError ? "#b42318" : "#5f6b6d";
  }

  function setPaymentAccountsMessage(message, isError) {
    if (!el.usersPaymentAccountsMessage) return;
    el.usersPaymentAccountsMessage.textContent = message || "";
    el.usersPaymentAccountsMessage.style.color = isError ? "#b42318" : "#5f6b6d";
  }

  function normalizeHexColor(value, fallback) {
    const raw = String(value || "").trim();
    if (/^#[0-9a-fA-F]{6}$/.test(raw)) return raw.toUpperCase();
    return fallback;
  }

  function syncChurchColorInputs(source) {
    if (source === "primary-picker") {
      if (el.usersChurchPrimaryColor) el.usersChurchPrimaryColor.value = normalizeHexColor(el.usersChurchPrimaryColorPicker.value, "#1565C0");
    } else if (source === "primary-text") {
      const normalized = normalizeHexColor(el.usersChurchPrimaryColor.value, "#1565C0");
      el.usersChurchPrimaryColor.value = normalized;
      if (el.usersChurchPrimaryColorPicker) el.usersChurchPrimaryColorPicker.value = normalized;
    } else if (source === "secondary-picker") {
      if (el.usersChurchSecondaryColor) el.usersChurchSecondaryColor.value = normalizeHexColor(el.usersChurchSecondaryColorPicker.value, "#0A8F72");
    } else if (source === "secondary-text") {
      const normalized = normalizeHexColor(el.usersChurchSecondaryColor.value, "#0A8F72");
      el.usersChurchSecondaryColor.value = normalized;
      if (el.usersChurchSecondaryColorPicker) el.usersChurchSecondaryColorPicker.value = normalized;
    }
    updateChurchPreview();
  }

  async function pickColorWithEyedropper(target) {
    if (!window.EyeDropper) {
      setChurchMessage("Seu navegador não suporta conta-gotas nativo. Use o seletor de cor.", true);
      return;
    }
    try {
      const eyeDropper = new window.EyeDropper();
      const result = await eyeDropper.open();
      if (target === "primary") {
        if (el.usersChurchPrimaryColor) el.usersChurchPrimaryColor.value = normalizeHexColor(result.sRGBHex, "#1565C0");
        if (el.usersChurchPrimaryColorPicker) el.usersChurchPrimaryColorPicker.value = normalizeHexColor(result.sRGBHex, "#1565C0");
      } else {
        if (el.usersChurchSecondaryColor) el.usersChurchSecondaryColor.value = normalizeHexColor(result.sRGBHex, "#0A8F72");
        if (el.usersChurchSecondaryColorPicker) el.usersChurchSecondaryColorPicker.value = normalizeHexColor(result.sRGBHex, "#0A8F72");
      }
      updateChurchPreview();
    } catch (_error) {
    }
  }

  function detectWhatsappCountry(value) {
    const normalized = String(value || "").replace(/\s+/g, "");
    const entries = Object.entries(WHATSAPP_COUNTRIES).sort((a, b) => b[1].dialCode.length - a[1].dialCode.length);
    for (const [countryCode, config] of entries) {
      if (normalized.startsWith(config.dialCode)) return countryCode;
    }
    return "BR";
  }

  function formatWhatsappByCountry(countryCode, rawDigits) {
    const config = WHATSAPP_COUNTRIES[countryCode] || WHATSAPP_COUNTRIES.BR;
    const allDigits = String(rawDigits || "").replace(/\D/g, "");
    const dialDigits = config.dialCode.replace(/\D/g, "");
    let localDigits = allDigits;
    if (localDigits.startsWith(dialDigits)) {
      localDigits = localDigits.slice(dialDigits.length);
    }

    const take = (start, end) => localDigits.slice(start, end);

    if (countryCode === "BR") {
      const area = take(0, 2);
      const first = localDigits.length > 10 ? take(2, 7) : take(2, 6);
      const second = localDigits.length > 10 ? take(7, 11) : take(6, 10);
      return `${config.dialCode}${area ? ` ${area}` : ""}${first ? ` ${first}` : ""}${second ? `-${second}` : ""}`.trim();
    }

    if (countryCode === "US") {
      const area = take(0, 3);
      const first = take(3, 6);
      const second = take(6, 10);
      return `${config.dialCode}${area ? ` (${area}` : ""}${area && area.length === 3 ? ")" : ""}${first ? ` ${first}` : ""}${second ? `-${second}` : ""}`.trim();
    }

    if (countryCode === "AR") {
      const area = take(0, 2);
      const first = take(2, 6);
      const second = take(6, 10);
      return `${config.dialCode}${area ? ` ${area}` : ""}${first ? ` ${first}` : ""}${second ? `-${second}` : ""}`.trim();
    }

    if (countryCode === "PT") {
      const first = take(0, 3);
      const second = take(3, 6);
      const third = take(6, 9);
      return `${config.dialCode}${first ? ` ${first}` : ""}${second ? ` ${second}` : ""}${third ? ` ${third}` : ""}`.trim();
    }

    if (countryCode === "PY") {
      const first = take(0, 3);
      const second = take(3, 6);
      const third = take(6, 9);
      return `${config.dialCode}${first ? ` ${first}` : ""}${second ? ` ${second}` : ""}${third ? ` ${third}` : ""}`.trim();
    }

    return `${config.dialCode}${localDigits ? ` ${localDigits}` : ""}`.trim();
  }

  function syncWhatsappField({ fromCountry = false } = {}) {
    if (!el.usersChurchSupportWhatsapp || !el.usersChurchWhatsappCountry) return;
    const selectedCountry = el.usersChurchWhatsappCountry.value || "BR";
    const digits = el.usersChurchSupportWhatsapp.value;
    if (!fromCountry && digits.trim().startsWith("+")) {
      el.usersChurchWhatsappCountry.value = detectWhatsappCountry(digits);
    }
    const countryCode = el.usersChurchWhatsappCountry.value || selectedCountry;
    el.usersChurchSupportWhatsapp.value = formatWhatsappByCountry(countryCode, digits);
    el.usersChurchSupportWhatsapp.placeholder = (WHATSAPP_COUNTRIES[countryCode] || WHATSAPP_COUNTRIES.BR).placeholder;
    updateChurchPreview();
  }

  function resolveAssetUrl(value) {
    const raw = String(value || "").trim();
    if (!raw) return "";
    try {
      return new URL(raw, window.location.origin).toString();
    } catch (_error) {
      return raw;
    }
  }

  function clearDraftLogoPreview() {
    if (state.churchDraftLogoPreviewUrl) {
      URL.revokeObjectURL(state.churchDraftLogoPreviewUrl);
      state.churchDraftLogoPreviewUrl = "";
    }
  }

  function syncSelectedLogoPreview() {
    if (!el.usersChurchLogoFile || !el.usersChurchLogoFile.files || !el.usersChurchLogoFile.files[0]) {
      clearDraftLogoPreview();
      updateChurchPreview();
      return;
    }
    clearDraftLogoPreview();
    state.churchDraftLogoPreviewUrl = URL.createObjectURL(el.usersChurchLogoFile.files[0]);
    updateChurchPreview();
  }

  async function resizeLogoFile(file) {
    const dataUrl = await new Promise((resolve, reject) => {
      const reader = new FileReader();
      reader.onload = () => resolve(reader.result);
      reader.onerror = () => reject(new Error("Falha ao ler a imagem selecionada."));
      reader.readAsDataURL(file);
    });

    const image = await new Promise((resolve, reject) => {
      const img = new Image();
      img.onload = () => resolve(img);
      img.onerror = () => reject(new Error("Falha ao processar a imagem selecionada."));
      img.src = dataUrl;
    });

    const canvas = document.createElement("canvas");
    canvas.width = 512;
    canvas.height = 512;
    const context = canvas.getContext("2d");
    context.clearRect(0, 0, 512, 512);

    const ratio = Math.min(512 / image.width, 512 / image.height);
    const width = Math.round(image.width * ratio);
    const height = Math.round(image.height * ratio);
    const x = Math.round((512 - width) / 2);
    const y = Math.round((512 - height) / 2);
    context.drawImage(image, x, y, width, height);

    return await new Promise((resolve, reject) => {
      canvas.toBlob((blob) => {
        if (!blob) {
          reject(new Error("Falha ao gerar a imagem ajustada."));
          return;
        }
        resolve(blob);
      }, "image/png", 0.92);
    });
  }

  async function uploadChurchLogo() {
    if (!el.usersChurchLogoFile || !el.usersChurchLogoFile.files || !el.usersChurchLogoFile.files[0]) {
      setChurchMessage("Selecione uma imagem antes de enviar a logo.", true);
      return;
    }

    try {
      setChurchMessage("Enviando logo da igreja...", false);
      const file = el.usersChurchLogoFile.files[0];
      const resizedBlob = await resizeLogoFile(file);
      const formData = new FormData();
      formData.append("file", resizedBlob, `${file.name.replace(/\.[^.]+$/, "") || "logo"}.png`);

      const response = await fetch(tenantLogoUploadEndpoint, {
        method: "POST",
        headers: buildHeaders(false),
        body: formData,
      });
      if (!response.ok) {
        throw new Error(await parseError(response, "Falha ao enviar logo da igreja."));
      }
      const tenant = await response.json();
      state.tenantProfile = tenant;
      if (el.usersChurchLogoUrl) el.usersChurchLogoUrl.value = tenant.logo_url || "";
      clearDraftLogoPreview();
      if (window.applyTenantBranding) {
        window.applyTenantBranding(tenant);
      }
      updateChurchPreview();
      setChurchMessage("Logo enviada com sucesso.", false);
      el.usersChurchLogoFile.value = "";
    } catch (error) {
      setChurchMessage(error instanceof Error ? error.message : "Falha ao enviar logo da igreja.", true);
    }
  }

  function getCurrentChurchSlug() {
    return (el.usersChurchSlug && el.usersChurchSlug.value.trim()) || localStorage.getItem("activeTenantSlug") || "default";
  }

  function buildChurchPublicUrls() {
    const slug = getCurrentChurchSlug();
    const origin = window.location.origin || "";
    return {
      landing: `${origin}/t/${encodeURIComponent(slug)}`,
      catalog: `${origin}/events/${encodeURIComponent(slug)}`,
      login: `${origin}/?tenant=${encodeURIComponent(slug)}`,
    };
  }

  function updateChurchPreview() {
    const displayName = (el.usersChurchPublicDisplayName && el.usersChurchPublicDisplayName.value.trim())
      || (el.usersChurchName && el.usersChurchName.value.trim())
      || "Sua igreja";
    const description = (el.usersChurchPublicDescription && el.usersChurchPublicDescription.value.trim())
      || "A descrição pública aparecerá aqui para visitantes e equipe.";
    const supportEmail = (el.usersChurchSupportEmail && el.usersChurchSupportEmail.value.trim()) || "";
    const supportWhatsapp = (el.usersChurchSupportWhatsapp && el.usersChurchSupportWhatsapp.value.trim()) || "";
    const logoUrl = state.churchDraftLogoPreviewUrl || ((el.usersChurchLogoUrl && el.usersChurchLogoUrl.value.trim()) || "");
    const resolvedLogoUrl = resolveAssetUrl(logoUrl);
    const primaryColor = normalizeHexColor(el.usersChurchPrimaryColor && el.usersChurchPrimaryColor.value, "#1565C0");
    const secondaryColor = normalizeHexColor(el.usersChurchSecondaryColor && el.usersChurchSecondaryColor.value, "#0A8F72");
    const supportParts = [supportEmail, supportWhatsapp].filter(Boolean);
    const urls = buildChurchPublicUrls();

    if (el.usersChurchLandingUrl) el.usersChurchLandingUrl.value = urls.landing;
    if (el.usersChurchCatalogUrl) el.usersChurchCatalogUrl.value = urls.catalog;
    if (el.usersChurchLoginUrl) el.usersChurchLoginUrl.value = urls.login;
    if (el.usersChurchPreviewTitle) el.usersChurchPreviewTitle.textContent = displayName;
    if (el.usersChurchPreviewSummary) el.usersChurchPreviewSummary.textContent = description;
    if (el.usersChurchPreviewSupport) el.usersChurchPreviewSupport.textContent = supportParts.length ? `Contato: ${supportParts.join(" | ")}` : "Contato da igreja ainda não configurado";
    if (el.usersChurchPreviewSlug) el.usersChurchPreviewSlug.textContent = `Landing: /t/${getCurrentChurchSlug()}`;
    if (el.usersChurchPreviewCard) {
      el.usersChurchPreviewCard.style.background = `linear-gradient(145deg, ${primaryColor}, ${secondaryColor})`;
    }
    if (el.usersChurchPreviewLogo) {
      el.usersChurchPreviewLogo.classList.toggle("hide", !resolvedLogoUrl);
      if (resolvedLogoUrl) {
        el.usersChurchPreviewLogo.src = resolvedLogoUrl;
      } else {
        el.usersChurchPreviewLogo.removeAttribute("src");
      }
    }
    if (el.usersChurchInlineLogoPreview) {
      el.usersChurchInlineLogoPreview.classList.toggle("hide", !resolvedLogoUrl);
      if (resolvedLogoUrl) {
        el.usersChurchInlineLogoPreview.src = resolvedLogoUrl;
      } else {
        el.usersChurchInlineLogoPreview.removeAttribute("src");
      }
    }
    renderChurchActivationChecklist();
  }

  function renderChurchActivationChecklist() {
    if (!el.usersChurchActivationChecklist || !el.usersChurchActivationScore) return;

    const items = [
      {
        done: Boolean(el.usersChurchPublicDisplayName && el.usersChurchPublicDisplayName.value.trim()),
        title: "Nome público",
        description: "Defina o nome exibido no login branded e na landing.",
      },
      {
        done: Boolean(el.usersChurchPublicDescription && el.usersChurchPublicDescription.value.trim()),
        title: "Descrição pública",
        description: "Apresente a proposta da igreja para visitantes.",
      },
      {
        done: Boolean(el.usersChurchPrimaryColor && el.usersChurchPrimaryColor.value.trim()) && Boolean(el.usersChurchSecondaryColor && el.usersChurchSecondaryColor.value.trim()),
        title: "Identidade visual",
        description: "Configure cores para a igreja ter presença própria.",
      },
      {
        done: Boolean(el.usersChurchLogoUrl && el.usersChurchLogoUrl.value.trim()),
        title: "Logo",
        description: "Exiba a marca nas páginas públicas e no acesso.",
      },
      {
        done: Boolean((el.usersChurchSupportEmail && el.usersChurchSupportEmail.value.trim()) || (el.usersChurchSupportWhatsapp && el.usersChurchSupportWhatsapp.value.trim())),
        title: "Contato",
        description: "Mostre um canal para inscrições e suporte.",
      },
      {
        done: Array.isArray(state.publicEvents) && state.publicEvents.length > 0,
        title: "Evento público",
        description: "Publique ao menos um evento para ativar a vitrine.",
      },
      {
        done: Array.isArray(state.invitations) && state.invitations.some((item) => item.status === "pending" || item.status === "accepted"),
        title: "Equipe convidada",
        description: "Convide pelo menos uma pessoa para começar a operação.",
      },
    ];

    const completed = items.filter((item) => item.done).length;
    el.usersChurchActivationScore.textContent = `${completed}/${items.length} concluído`;
    el.usersChurchActivationChecklist.innerHTML = items
      .map((item) => `<div class="tenant-onboarding-item ${item.done ? "done" : ""}"><strong>${item.done ? "Concluído" : "Pendente"} · ${escapeHtml(item.title)}</strong>${escapeHtml(item.description)}</div>`)
      .join("");
  }

  async function copyChurchUrl(kind) {
    const urls = buildChurchPublicUrls();
    const value = urls[kind];
    if (!value) {
      setChurchMessage("Link público indisponível para copiar.", true);
      return;
    }
    try {
      await navigator.clipboard.writeText(value);
      setChurchMessage("Link copiado com sucesso.", false);
    } catch (_error) {
      setChurchMessage("Não foi possível copiar o link automaticamente.", true);
    }
  }

  function escapeHtml(value) {
    return String(value ?? "")
      .replace(/&/g, "&amp;")
      .replace(/</g, "&lt;")
      .replace(/>/g, "&gt;")
      .replace(/\"/g, "&quot;")
      .replace(/'/g, "&#39;");
  }

  function formatInvitationDelivery(invitation) {
    const status = String(invitation && invitation.delivery_status ? invitation.delivery_status : "manual_share");
    const labels = {
      sent: "E-mail enviado",
      manual_share: "Compartilhar manualmente",
      failed: "Falhou",
    };
    const base = labels[status] || status;
    if (status === "sent" && invitation.last_sent_at) {
      return `${base} em ${new Date(invitation.last_sent_at).toLocaleString("pt-BR")}`;
    }
    if (status === "failed" && invitation.delivery_error) {
      return `${base}: ${invitation.delivery_error}`;
    }
    return base;
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
    const isEvents = moduleName === "events";
    const isUsers = moduleName === "users";

    if (el.financeBtn) el.financeBtn.classList.toggle("active", isFinance);
    if (el.cellsBtn) el.cellsBtn.classList.toggle("active", isCells);
    if (el.schoolBtn) el.schoolBtn.classList.toggle("active", isSchool);
    if (el.eventsBtn) el.eventsBtn.classList.toggle("active", isEvents);
    if (el.usersBtn) el.usersBtn.classList.toggle("active", isUsers);

    if (el.financeModule) el.financeModule.classList.toggle("hide", !isFinance);
    if (el.cellsModule) el.cellsModule.classList.toggle("hide", !isCells);
    if (el.schoolModule) el.schoolModule.classList.toggle("hide", !isSchool);
    if (el.eventsModule) el.eventsModule.classList.toggle("hide", !isEvents);
    if (el.usersModule) el.usersModule.classList.toggle("hide", !isUsers);
  }

  function setUsersView(viewName) {
    const viewPermissions = {
      users: "users_users_view",
      roles: "users_roles_view",
      church: "users_roles_view",
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
    const isChurchView = viewName === "church";

    if (el.usersNavUsersBtn) el.usersNavUsersBtn.classList.toggle("active", isUsersView);
    if (el.usersNavRolesBtn) el.usersNavRolesBtn.classList.toggle("active", isRolesView);
    if (el.usersNavChurchBtn) el.usersNavChurchBtn.classList.toggle("active", isChurchView);
    if (el.usersUsersView) el.usersUsersView.classList.toggle("hide", !isUsersView);
    if (el.usersRolesView) el.usersRolesView.classList.toggle("hide", !isRolesView);
    if (el.usersChurchView) el.usersChurchView.classList.toggle("hide", !isChurchView);
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
    if (state.isAdmin) return "church";
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
    if (el.usersNavChurchBtn) el.usersNavChurchBtn.classList.toggle("hide", !state.isAdmin);
    if (el.usersAddBtn) el.usersAddBtn.classList.toggle("hide", !hasPermission("users_users_create"));
    if (el.usersInviteBtn) el.usersInviteBtn.classList.toggle("hide", !hasPermission("users_users_create"));
    if (el.usersOpenLinkInviteModalBtn) el.usersOpenLinkInviteModalBtn.classList.toggle("hide", !hasPermission("users_users_create"));
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

  async function loadTenantProfile() {
    state.tenantProfile = await fetchJson(tenantEndpoint, { headers: buildHeaders(false) }, "Falha ao carregar perfil da igreja.");
    const tenant = state.tenantProfile || {};
    if (el.usersChurchName) el.usersChurchName.value = tenant.name || "";
    if (el.usersChurchSlug) el.usersChurchSlug.value = tenant.slug || "";
    if (el.usersChurchPublicDisplayName) el.usersChurchPublicDisplayName.value = tenant.public_display_name || "";
    if (el.usersChurchPublicDescription) el.usersChurchPublicDescription.value = tenant.public_description || "";
    if (el.usersChurchPrimaryColor) el.usersChurchPrimaryColor.value = tenant.primary_color || "";
    if (el.usersChurchSecondaryColor) el.usersChurchSecondaryColor.value = tenant.secondary_color || "";
    if (el.usersChurchPrimaryColorPicker) el.usersChurchPrimaryColorPicker.value = normalizeHexColor(tenant.primary_color, "#1565C0");
    if (el.usersChurchSecondaryColorPicker) el.usersChurchSecondaryColorPicker.value = normalizeHexColor(tenant.secondary_color, "#0A8F72");
    if (el.usersChurchLogoUrl) el.usersChurchLogoUrl.value = tenant.logo_url || "";
    if (el.usersChurchSupportEmail) el.usersChurchSupportEmail.value = tenant.support_email || "";
    if (el.usersChurchSupportWhatsapp) el.usersChurchSupportWhatsapp.value = tenant.support_whatsapp || "";
    if (el.usersChurchWhatsappCountry) el.usersChurchWhatsappCountry.value = detectWhatsappCountry(tenant.support_whatsapp || "");
    clearDraftLogoPreview();
    syncWhatsappField({ fromCountry: true });
    if (el.usersChurchIsActive) el.usersChurchIsActive.checked = tenant.is_active !== false;
    updateChurchPreview();
  }

  function renderTenantPaymentSettings() {
    const paymentSettings = state.tenantPaymentSettings || {};
    if (el.usersChurchPaymentProvider) el.usersChurchPaymentProvider.value = paymentSettings.payment_provider || "internal";
    if (el.usersChurchPaymentPixEnabled) el.usersChurchPaymentPixEnabled.checked = paymentSettings.payment_pix_enabled !== false;
    if (el.usersChurchPaymentCardEnabled) el.usersChurchPaymentCardEnabled.checked = paymentSettings.payment_card_enabled !== false;
    if (el.usersChurchMercadoPagoPublicKey) el.usersChurchMercadoPagoPublicKey.value = paymentSettings.mercadopago_public_key || "";
    if (el.usersChurchMercadoPagoAccessToken) el.usersChurchMercadoPagoAccessToken.value = "";
    if (el.usersChurchMercadoPagoClearAccessToken) el.usersChurchMercadoPagoClearAccessToken.checked = false;
    if (el.usersChurchMercadoPagoWebhookSecret) el.usersChurchMercadoPagoWebhookSecret.value = "";
    if (el.usersChurchMercadoPagoClearWebhookSecret) el.usersChurchMercadoPagoClearWebhookSecret.checked = false;
    if (el.usersChurchMercadoPagoIntegratorId) el.usersChurchMercadoPagoIntegratorId.value = paymentSettings.mercadopago_integrator_id || "";
    if (el.usersChurchPaymentTokenStatus) el.usersChurchPaymentTokenStatus.textContent = paymentSettings.mercadopago_access_token_configured ? "Sim" : "Não";
    if (el.usersChurchPaymentWebhookStatus) el.usersChurchPaymentWebhookStatus.textContent = paymentSettings.mercadopago_webhook_secret_configured ? "Sim" : "Não";
    if (el.usersChurchPaymentLiveStatus) el.usersChurchPaymentLiveStatus.textContent = paymentSettings.mercadopago_live_ready ? "Ativo" : "Desligado";
    if (el.usersChurchPaymentModeStatus) {
      el.usersChurchPaymentModeStatus.value = paymentSettings.checkout_mode === "live" ? "Checkout real ativo" : "Checkout interno";
    }
  }

  async function loadTenantPaymentSettings() {
    state.tenantPaymentSettings = await fetchJson(tenantPaymentsEndpoint, { headers: buildHeaders(false) }, "Falha ao carregar pagamentos da igreja.");
    renderTenantPaymentSettings();
  }

  function resetPaymentAccountForm() {
    if (!el.usersPaymentAccountForm) return;
    el.usersPaymentAccountForm.reset();
    if (el.usersPaymentAccountId) el.usersPaymentAccountId.value = "";
    if (el.usersPaymentAccountProvider) el.usersPaymentAccountProvider.value = "mercadopago";
    if (el.usersPaymentAccountEnvironment) el.usersPaymentAccountEnvironment.value = "production";
    if (el.usersPaymentAccountSupportsPix) el.usersPaymentAccountSupportsPix.checked = true;
    if (el.usersPaymentAccountSupportsCard) el.usersPaymentAccountSupportsCard.checked = true;
    if (el.usersPaymentAccountIsActive) el.usersPaymentAccountIsActive.checked = true;
    syncPaymentAccountProviderFields();
    setPaymentAccountsMessage("", false);
  }

  function getPaymentAccountDraft() {
    const editingId = Number((el.usersPaymentAccountId && el.usersPaymentAccountId.value) || 0);
    const existingAccount = editingId > 0 ? state.paymentAccounts.find((account) => account.id === editingId) : null;
    return {
      provider: el.usersPaymentAccountProvider ? el.usersPaymentAccountProvider.value : "mercadopago",
      environment: el.usersPaymentAccountEnvironment ? el.usersPaymentAccountEnvironment.value : "production",
      publicKey: el.usersPaymentAccountPublicKey ? el.usersPaymentAccountPublicKey.value.trim() : "",
      accessToken: el.usersPaymentAccountAccessToken && el.usersPaymentAccountAccessToken.value.trim()
        ? el.usersPaymentAccountAccessToken.value.trim()
        : (existingAccount && existingAccount.access_token_configured ? "__configured__" : ""),
      webhookSecret: el.usersPaymentAccountWebhookSecret && el.usersPaymentAccountWebhookSecret.value.trim()
        ? el.usersPaymentAccountWebhookSecret.value.trim()
        : (existingAccount && existingAccount.webhook_secret_configured ? "__configured__" : ""),
      integratorId: el.usersPaymentAccountIntegratorId ? el.usersPaymentAccountIntegratorId.value.trim() : "",
    };
  }

  function renderPaymentAccountGuide() {
    if (!el.usersPaymentAccountGuide) return;
    const draft = getPaymentAccountDraft();
    const providerLabel = draft.provider === "mercadopago"
      ? "Mercado Pago"
      : draft.provider === "pagbank"
        ? "PagBank"
        : "Interno";
    let title = `${providerLabel} pronto para configurar`;
    let summary = "Use esta conta quando quiser receber de forma real no evento.";
    let requirements = [];

    if (draft.provider === "mercadopago") {
      requirements = [
        "Preencha Public key e Access token da conta recebedora.",
        "Use Sandbox para testes e Produção para checkout real.",
        "Em produção, configure também o Webhook secret.",
      ];
    } else if (draft.provider === "pagbank") {
      title = "PagBank com checkout por link";
      summary = "A conta usa Access token como credencial principal e pode operar em sandbox ou produção.";
      requirements = [
        "Preencha o Access token da conta PagBank.",
        "Escolha o ambiente correto antes de publicar.",
        "Deixe o webhook público acessível para confirmação automática.",
      ];
    } else {
      title = "Conta interna de teste";
      summary = "Use este modo para validar o fluxo sem gateway real.";
      requirements = [
        "Gera checkout interno com PIX simulado.",
        "Ideal para testes locais e demonstrações.",
      ];
    }

    el.usersPaymentAccountGuide.innerHTML = `
      <div class="payment-account-guide-card">
        <strong>${escapeHtml(title)}</strong>
        <p>${escapeHtml(summary)}</p>
        <p class="payment-account-security-note">OAuth é a opção mais segura para produto SaaS; o modo por token manual continua disponível como fallback operacional.</p>
        <div class="payment-account-guide-meta">
          <span class="payment-guide-chip">${escapeHtml(providerLabel)}</span>
          <span class="payment-guide-chip">${draft.environment === "sandbox" ? "Sandbox" : "Produção"}</span>
        </div>
        <ul class="payment-guide-list">
          ${requirements.map((item) => `<li>${escapeHtml(item)}</li>`).join("")}
        </ul>
      </div>
    `;
  }

  function renderPaymentAccountReadiness() {
    if (!el.usersPaymentAccountReadiness) return;
    const draft = getPaymentAccountDraft();
    let checks = [];
    if (draft.provider === "mercadopago") {
      checks = [
        { label: "Public key", ok: Boolean(draft.publicKey) },
        { label: "Access token", ok: Boolean(draft.accessToken) },
        { label: "Webhook secret", ok: draft.environment === "sandbox" || Boolean(draft.webhookSecret) },
      ];
    } else if (draft.provider === "pagbank") {
      checks = [
        { label: "Access token", ok: Boolean(draft.accessToken) },
        { label: "Ambiente", ok: Boolean(draft.environment) },
      ];
    } else {
      checks = [{ label: "Conta interna pronta", ok: true }];
    }
    const ready = checks.every((item) => item.ok);
    el.usersPaymentAccountReadiness.innerHTML = `
      <div class="payment-readiness-head">
        <strong>${ready ? "Conta pronta para uso" : "Faltam dados para checkout real"}</strong>
        <span class="payment-readiness-status ${ready ? "is-ready" : "is-pending"}">${ready ? "Pronta" : "Pendente"}</span>
      </div>
      <div class="payment-readiness-list">
        ${checks.map((item) => `
          <span class="payment-readiness-item ${item.ok ? "is-ok" : "is-missing"}">
            ${item.ok ? "OK" : "Pendente"} · ${escapeHtml(item.label)}
          </span>
        `).join("")}
      </div>
    `;
  }

  async function startMercadoPagoOAuth() {
    const accountId = Number((el.usersPaymentAccountId && el.usersPaymentAccountId.value) || 0);
    if (!accountId) {
      setPaymentAccountsMessage("Salve a conta antes de conectar por OAuth.", true);
      return;
    }
    const account = state.paymentAccounts.find((item) => item.id === accountId);
    if (!account || account.provider !== "mercadopago") {
      setPaymentAccountsMessage("OAuth está disponível apenas para contas Mercado Pago.", true);
      return;
    }
    const response = await fetchJson(
      `${paymentAccountsEndpoint}${accountId}/oauth/mercadopago/start`,
      { method: "POST", headers: buildHeaders(false) },
      "Falha ao iniciar OAuth do Mercado Pago."
    );
    const popup = window.open(response.authorize_url, "mercadopago-oauth", "width=640,height=820");
    if (!popup) {
      setPaymentAccountsMessage("O navegador bloqueou a janela de autorização. Libere popups e tente novamente.", true);
      return;
    }
    setPaymentAccountsMessage("Janela de autorização aberta. Conclua a conexão no Mercado Pago.", false);
    const watcher = window.setInterval(async () => {
      if (!popup.closed) return;
      window.clearInterval(watcher);
      await loadPaymentAccounts();
      const refreshed = state.paymentAccounts.find((item) => item.id === accountId);
      setPaymentAccountsMessage(
        refreshed && refreshed.oauth_connected
          ? "Conta Mercado Pago conectada com sucesso por OAuth."
          : "A conexão OAuth foi encerrada. Confira o status da conta.",
        false,
      );
    }, 1200);
  }

  function syncPaymentAccountProviderFields() {
    const provider = el.usersPaymentAccountProvider ? el.usersPaymentAccountProvider.value : "mercadopago";
    const isMercadoPago = provider === "mercadopago";
    const isPagBank = provider === "pagbank";
    const isInternal = provider === "internal";

    if (el.usersPaymentAccountEnvironment) el.usersPaymentAccountEnvironment.disabled = isInternal;
    if (el.usersPaymentAccountPublicKeyLabel) el.usersPaymentAccountPublicKeyLabel.classList.toggle("hide", !isMercadoPago);
    if (el.usersPaymentAccountWebhookSecretLabel) el.usersPaymentAccountWebhookSecretLabel.classList.toggle("hide", !isMercadoPago);
    if (el.usersPaymentAccountIntegratorIdLabel) {
      el.usersPaymentAccountIntegratorIdLabel.classList.toggle("hide", isInternal);
      el.usersPaymentAccountIntegratorIdLabel.firstChild.textContent = isMercadoPago ? "Integrator ID" : "App ID / referência interna";
    }
    if (el.usersPaymentAccountAccessTokenLabel) {
      el.usersPaymentAccountAccessTokenLabel.firstChild.textContent = isPagBank ? "Access token PagBank" : "Access token";
    }
    if (el.usersPaymentAccountPublicKey) {
      el.usersPaymentAccountPublicKey.placeholder = isMercadoPago ? "APP_USR-... ou TEST-..." : "Não necessário para este provider";
    }
    if (el.usersPaymentAccountWebhookSecret) {
      el.usersPaymentAccountWebhookSecret.placeholder = isMercadoPago ? "Opcional, recomendado em produção" : "Não necessário para este provider";
    }
    if (el.usersPaymentAccountIntegratorId) {
      el.usersPaymentAccountIntegratorId.placeholder = isInternal ? "Não utilizado" : "Opcional";
    }
    if (el.usersPaymentAccountOAuthBox) {
      el.usersPaymentAccountOAuthBox.classList.toggle("hide", !isMercadoPago);
    }
    if (el.usersPaymentAccountOAuthBtn) {
      el.usersPaymentAccountOAuthBtn.disabled = !isMercadoPago;
    }
    if (isInternal) {
      if (el.usersPaymentAccountSupportsPix) el.usersPaymentAccountSupportsPix.checked = true;
      if (el.usersPaymentAccountSupportsCard) el.usersPaymentAccountSupportsCard.checked = false;
    }
    renderPaymentAccountGuide();
    renderPaymentAccountReadiness();
  }

  function renderPaymentAccounts() {
    if (!el.usersPaymentAccountsBody) return;
    if (!state.paymentAccounts.length) {
      el.usersPaymentAccountsBody.innerHTML = '<tr><td colspan="6">Nenhuma conta cadastrada.</td></tr>';
      return;
    }
    el.usersPaymentAccountsBody.innerHTML = state.paymentAccounts.map((account) => `
      <tr>
        <td><strong>${escapeHtml(account.label)}</strong><br><span class="tiny">${escapeHtml(account.description || "-")}</span></td>
        <td>${escapeHtml(account.provider)}<br><span class="tiny">${escapeHtml(account.environment || "production")}</span></td>
        <td>${account.supports_pix ? "PIX" : ""}${account.supports_pix && account.supports_card ? " / " : ""}${account.supports_card ? "Cartão" : ""}</td>
        <td>${account.is_active ? "Ativa" : "Inativa"}${account.is_default ? " · Padrão" : ""}</td>
        <td>${account.live_ready ? "Sim" : "Não"}${account.oauth_connected ? '<br><span class="tiny">OAuth conectado</span>' : ""}</td>
        <td>
          <button class="btn ghost btn-mini" type="button" data-payment-account-edit="${account.id}">Editar</button>
          <button class="btn ghost btn-mini" type="button" data-payment-account-delete="${account.id}">Excluir</button>
        </td>
      </tr>
    `).join("");
  }

  async function loadPaymentAccounts() {
    state.paymentAccounts = await fetchJson(paymentAccountsEndpoint, { headers: buildHeaders(false) }, "Falha ao carregar contas de pagamento.");
    renderPaymentAccounts();
    renderPaymentAccountGuide();
    renderPaymentAccountReadiness();
  }

  function editPaymentAccount(accountId) {
    const account = state.paymentAccounts.find((item) => item.id === accountId);
    if (!account) return;
    if (el.usersPaymentAccountId) el.usersPaymentAccountId.value = String(account.id);
    if (el.usersPaymentAccountLabel) el.usersPaymentAccountLabel.value = account.label || "";
    if (el.usersPaymentAccountProvider) el.usersPaymentAccountProvider.value = account.provider || "mercadopago";
    if (el.usersPaymentAccountEnvironment) el.usersPaymentAccountEnvironment.value = account.environment || "production";
    if (el.usersPaymentAccountDescription) el.usersPaymentAccountDescription.value = account.description || "";
    if (el.usersPaymentAccountSupportsPix) el.usersPaymentAccountSupportsPix.checked = Boolean(account.supports_pix);
    if (el.usersPaymentAccountSupportsCard) el.usersPaymentAccountSupportsCard.checked = Boolean(account.supports_card);
    if (el.usersPaymentAccountIsDefault) el.usersPaymentAccountIsDefault.checked = Boolean(account.is_default);
    if (el.usersPaymentAccountIsActive) el.usersPaymentAccountIsActive.checked = Boolean(account.is_active);
    if (el.usersPaymentAccountPublicKey) el.usersPaymentAccountPublicKey.value = account.public_key || "";
    if (el.usersPaymentAccountAccessToken) el.usersPaymentAccountAccessToken.value = "";
    if (el.usersPaymentAccountWebhookSecret) el.usersPaymentAccountWebhookSecret.value = "";
    if (el.usersPaymentAccountIntegratorId) el.usersPaymentAccountIntegratorId.value = account.integrator_id || account.app_id || "";
    syncPaymentAccountProviderFields();
    setPaymentAccountsMessage(`Editando conta: ${account.label}`, false);
  }

  async function submitPaymentAccountForm(event) {
    event.preventDefault();
    const accountId = Number((el.usersPaymentAccountId && el.usersPaymentAccountId.value) || 0);
    const isEdit = accountId > 0;
    const payload = {
      label: el.usersPaymentAccountLabel.value.trim(),
      provider: el.usersPaymentAccountProvider.value,
      environment: el.usersPaymentAccountEnvironment ? el.usersPaymentAccountEnvironment.value : "production",
      description: el.usersPaymentAccountDescription.value.trim() || null,
      supports_pix: Boolean(el.usersPaymentAccountSupportsPix.checked),
      supports_card: Boolean(el.usersPaymentAccountSupportsCard.checked),
      is_default: Boolean(el.usersPaymentAccountIsDefault.checked),
      is_active: Boolean(el.usersPaymentAccountIsActive.checked),
      public_key: el.usersPaymentAccountPublicKey.value.trim() || null,
      access_token: el.usersPaymentAccountAccessToken.value.trim() || null,
      webhook_secret: el.usersPaymentAccountWebhookSecret.value.trim() || null,
      integrator_id: el.usersPaymentAccountIntegratorId.value.trim() || null,
    };
    try {
      setPaymentAccountsMessage(isEdit ? "Salvando conta..." : "Criando conta...", false);
      await fetchJson(
        isEdit ? `${paymentAccountsEndpoint}${accountId}` : paymentAccountsEndpoint,
        { method: isEdit ? "PUT" : "POST", headers: buildHeaders(true), body: JSON.stringify(payload) },
        isEdit ? "Falha ao salvar conta de pagamento." : "Falha ao criar conta de pagamento."
      );
      await loadPaymentAccounts();
      resetPaymentAccountForm();
      setPaymentAccountsMessage("Conta de pagamento salva com sucesso.", false);
    } catch (error) {
      setPaymentAccountsMessage(error instanceof Error ? error.message : "Falha ao salvar conta de pagamento.", true);
    }
  }

  async function deletePaymentAccount(accountId) {
    await fetchJson(`${paymentAccountsEndpoint}${accountId}`, { method: "DELETE", headers: buildHeaders(false) }, "Falha ao excluir conta de pagamento.");
    await loadPaymentAccounts();
    resetPaymentAccountForm();
    setPaymentAccountsMessage("Conta de pagamento excluída com sucesso.", false);
  }

  async function loadInvitations() {
    state.invitations = await fetchJson(tenantInvitationsEndpoint, { headers: buildHeaders(false) }, "Falha ao carregar convites.");
    renderInvitations();
    renderChurchActivationChecklist();
  }

  async function loadPublicEventsForChurch() {
    const slug = getCurrentChurchSlug();
    if (!slug) {
      state.publicEvents = [];
      renderChurchActivationChecklist();
      return;
    }
    try {
      state.publicEvents = await fetchJson(`${publicEventsEndpoint}${encodeURIComponent(slug)}/events`, {}, "Falha ao carregar eventos públicos.");
    } catch (_error) {
      state.publicEvents = [];
    }
    renderChurchActivationChecklist();
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

  function ensureInviteRoleOptions(selectedRoleId) {
    if (!el.usersInviteRoleId) return;

    if (!state.roles.length) {
      el.usersInviteRoleId.innerHTML = '<option value="">Nenhuma role disponível</option>';
      el.usersInviteRoleId.value = "";
      return;
    }

    el.usersInviteRoleId.innerHTML = state.roles
      .map((role) => `<option value="${role.id}">${role.name}</option>`)
      .join("");

    el.usersInviteRoleId.value = selectedRoleId != null ? String(selectedRoleId) : String(state.roles[0].id);
  }

  function ensureLinkInviteRoleOptions(selectedRoleId) {
    if (!el.usersLinkInviteRoleId) return;

    if (!state.roles.length) {
      el.usersLinkInviteRoleId.innerHTML = '<option value="">Nenhuma role disponível</option>';
      el.usersLinkInviteRoleId.value = "";
      return;
    }

    el.usersLinkInviteRoleId.innerHTML = state.roles
      .map((role) => `<option value="${role.id}">${role.name}</option>`)
      .join("");

    el.usersLinkInviteRoleId.value = selectedRoleId != null ? String(selectedRoleId) : String(state.roles[0].id);
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

  function renderInvitations() {
    if (!el.usersInvitationsBody) return;

    if (!state.invitations.length) {
      el.usersInvitationsBody.innerHTML = '<tr><td colspan="6">Nenhum convite gerado.</td></tr>';
      return;
    }

    el.usersInvitationsBody.innerHTML = state.invitations
      .map((invitation) => {
        const roleName = (invitation.role_obj && invitation.role_obj.name) || invitation.role || "-";
        const statusLabel = invitation.status || "-";
        const deliveryLabel = formatInvitationDelivery(invitation);
        const revokeButton = invitation.status === "pending"
          ? `<button type="button" class="btn btn-sm btn-danger" data-invitation-revoke="${invitation.id}">Revogar</button>`
          : "";
        const resendButton = invitation.status === "pending"
          ? `<button type="button" class="btn btn-sm btn-warning" data-invitation-resend="${invitation.id}">Reenviar</button>`
          : "";
        const copyButton = invitation.status === "pending"
          ? `<button type="button" class="btn btn-sm btn-warning" data-invitation-copy="${invitation.id}">Copiar link</button>`
          : "";
        return `<tr>
          <td><strong>${escapeHtml(invitation.email)}</strong></td>
          <td>${escapeHtml(roleName)}</td>
          <td><span class="badge bg-info">${escapeHtml(statusLabel)}</span></td>
          <td>${escapeHtml(deliveryLabel)}</td>
          <td>${escapeHtml(new Date(invitation.expires_at).toLocaleString("pt-BR"))}</td>
          <td>${copyButton} ${resendButton} ${revokeButton}</td>
        </tr>`;
      })
      .join("");

    el.usersInvitationsBody.querySelectorAll("[data-invitation-copy]").forEach((button) => {
      button.addEventListener("click", async () => {
        const invitationId = parseInt(button.getAttribute("data-invitation-copy"), 10);
        const invitation = state.invitations.find((item) => item.id === invitationId);
        if (!invitation || !invitation.invite_url) return;
        try {
          await navigator.clipboard.writeText(invitation.invite_url);
          setMessage(`Link copiado para ${invitation.email}.`, false);
        } catch (_error) {
          setMessage("Nao foi possivel copiar o link automaticamente.", true);
        }
      });
    });

    el.usersInvitationsBody.querySelectorAll("[data-invitation-revoke]").forEach((button) => {
      button.addEventListener("click", () => revokeInvitation(parseInt(button.getAttribute("data-invitation-revoke"), 10)).catch((error) => setMessage(error.message, true)));
    });

    el.usersInvitationsBody.querySelectorAll("[data-invitation-resend]").forEach((button) => {
      button.addEventListener("click", () => resendInvitation(parseInt(button.getAttribute("data-invitation-resend"), 10)).catch((error) => setMessage(error.message, true)));
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

  function openInviteModal() {
    if (!el.usersInviteModal || !el.usersInviteForm) return;
    el.usersInviteForm.reset();
    ensureInviteRoleOptions();
    setInviteMessage("", false);
    el.usersInviteModal.classList.remove("hide");
  }

  function closeInviteModal() {
    if (!el.usersInviteModal) return;
    el.usersInviteModal.classList.add("hide");
  }

  function openLinkInviteModal() {
    if (!el.usersLinkInviteModal || !el.usersLinkInviteForm) return;
    el.usersLinkInviteForm.reset();
    ensureLinkInviteRoleOptions();
    if (el.usersLinkInviteResult) el.usersLinkInviteResult.value = "";
    setLinkInviteMessage("", false);
    el.usersLinkInviteModal.classList.remove("hide");
  }

  function closeLinkInviteModal() {
    if (!el.usersLinkInviteModal) return;
    el.usersLinkInviteModal.classList.add("hide");
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

  async function submitInviteForm(event) {
    event.preventDefault();

    if (!el.usersInviteEmail || !el.usersInviteRoleId || !el.usersInviteIsDefault) return;

    const email = el.usersInviteEmail.value.trim().toLowerCase();
    const roleId = parseInt(el.usersInviteRoleId.value || "0", 10);
    const isDefault = Boolean(el.usersInviteIsDefault.checked);

    if (!email || !roleId) {
      setInviteMessage("Informe email e role para o convite.", true);
      return;
    }

    try {
      setInviteMessage("Vinculando usuário existente a esta igreja...", false);
      await fetchJson(
        usersLinkExistingEndpoint,
        {
          method: "POST",
          headers: buildHeaders(true),
          body: JSON.stringify({
            email,
            role_id: roleId,
            is_default: isDefault,
          }),
        },
        "Erro ao convidar usuário existente."
      );
      closeInviteModal();
      await loadUsers();
      setMessage(`Usuário ${email} vinculado com sucesso a esta igreja.`, false);
    } catch (error) {
      setInviteMessage(error instanceof Error ? error.message : "Falha ao convidar usuário existente.", true);
    }
  }

  async function submitLinkInviteForm(event) {
    event.preventDefault();

    if (!el.usersLinkInviteEmail || !el.usersLinkInviteRoleId || !el.usersLinkInviteExpiryDays || !el.usersLinkInviteIsDefault) return;

    const email = el.usersLinkInviteEmail.value.trim().toLowerCase();
    const roleId = parseInt(el.usersLinkInviteRoleId.value || "0", 10);
    const expiresInDays = parseInt(el.usersLinkInviteExpiryDays.value || "7", 10);
    const isDefault = Boolean(el.usersLinkInviteIsDefault.checked);

    if (!email || !roleId) {
      setLinkInviteMessage("Informe email e role para gerar o convite.", true);
      return;
    }

    try {
      setLinkInviteMessage("Gerando link de convite...", false);
      const invitation = await fetchJson(
        tenantInvitationsEndpoint,
        {
          method: "POST",
          headers: buildHeaders(true),
          body: JSON.stringify({
            email,
            role_id: roleId,
            expires_in_days: expiresInDays,
            is_default: isDefault,
          }),
        },
        "Erro ao gerar convite."
      );
      if (el.usersLinkInviteResult) {
        el.usersLinkInviteResult.value = invitation.invite_url || "";
      }
      setLinkInviteMessage("Convite gerado com sucesso. Compartilhe o link abaixo.", false);
      await loadInvitations();
    } catch (error) {
      setLinkInviteMessage(error instanceof Error ? error.message : "Falha ao gerar convite.", true);
    }
  }

  async function revokeInvitation(invitationId) {
    await fetchJson(`${tenantInvitationsEndpoint}${invitationId}`, { method: "DELETE", headers: buildHeaders(false) }, "Erro ao revogar convite.");
    await loadInvitations();
    setMessage("Convite revogado com sucesso.", false);
  }

  async function resendInvitation(invitationId) {
    await fetchJson(`${tenantInvitationsEndpoint}${invitationId}/resend`, { method: "POST", headers: buildHeaders(false) }, "Erro ao reenviar convite.");
    await loadInvitations();
    setMessage("Convite reenviado com sucesso.", false);
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
      ensureInviteRoleOptions();
      ensureLinkInviteRoleOptions();
    }
    if (hasPermission("users_users_view")) {
      await loadUsers();
      await loadInvitations();
    }
    if (state.isAdmin) {
      await loadTenantProfile();
      await loadTenantPaymentSettings();
      await loadPaymentAccounts();
      await loadPublicEventsForChurch();
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

  async function openChurchView() {
    if (!state.isAdmin) {
      setChurchMessage("Acesso negado: somente administradores podem editar a igreja.", true);
      return;
    }

    setUsersView("church");
    await loadTenantProfile();
    await loadTenantPaymentSettings();
    await loadPaymentAccounts();
    resetPaymentAccountForm();
    await loadPublicEventsForChurch();
    setChurchMessage("", false);
    setChurchPaymentsMessage("", false);
  }

  async function submitChurchForm(event) {
    event.preventDefault();
    if (!state.isAdmin) {
      setChurchMessage("Acesso negado para editar a igreja.", true);
      return;
    }

    syncChurchColorInputs("primary-text");
    syncChurchColorInputs("secondary-text");
    syncWhatsappField({ fromCountry: true });

    const payload = {
      name: el.usersChurchName.value.trim(),
      slug: el.usersChurchSlug.value.trim(),
      public_display_name: el.usersChurchPublicDisplayName.value.trim() || null,
      public_description: el.usersChurchPublicDescription.value.trim() || null,
      primary_color: el.usersChurchPrimaryColor.value.trim() || null,
      secondary_color: el.usersChurchSecondaryColor.value.trim() || null,
      logo_url: el.usersChurchLogoUrl.value.trim() || null,
      support_email: el.usersChurchSupportEmail.value.trim() || null,
      support_whatsapp: el.usersChurchSupportWhatsapp.value.trim() || null,
      is_active: el.usersChurchIsActive.checked,
    };

    try {
      setChurchMessage("Salvando perfil da igreja...", false);
      const tenant = await fetchJson(
        tenantEndpoint,
        { method: "PUT", headers: buildHeaders(true), body: JSON.stringify(payload) },
        "Falha ao salvar perfil da igreja."
      );
      state.tenantProfile = tenant;
      localStorage.setItem("activeTenantSlug", tenant.slug || "");
      if (window.applyTenantBranding) {
        window.applyTenantBranding(tenant);
      }
      await loadPublicEventsForChurch();
      updateChurchPreview();
      setChurchMessage("Perfil da igreja atualizado com sucesso.", false);
    } catch (error) {
      setChurchMessage(error instanceof Error ? error.message : "Falha ao salvar perfil da igreja.", true);
    }
  }

  async function submitChurchPaymentsForm(event) {
    event.preventDefault();
    if (!state.isAdmin) {
      setChurchPaymentsMessage("Acesso negado para editar pagamentos da igreja.", true);
      return;
    }

    const payload = {
      payment_provider: el.usersChurchPaymentProvider.value,
      payment_pix_enabled: Boolean(el.usersChurchPaymentPixEnabled.checked),
      payment_card_enabled: Boolean(el.usersChurchPaymentCardEnabled.checked),
      mercadopago_public_key: el.usersChurchMercadoPagoPublicKey.value.trim() || null,
      mercadopago_access_token: el.usersChurchMercadoPagoAccessToken.value.trim() || null,
      mercadopago_webhook_secret: el.usersChurchMercadoPagoWebhookSecret.value.trim() || null,
      mercadopago_integrator_id: el.usersChurchMercadoPagoIntegratorId.value.trim() || null,
      clear_mercadopago_access_token: Boolean(el.usersChurchMercadoPagoClearAccessToken.checked),
      clear_mercadopago_webhook_secret: Boolean(el.usersChurchMercadoPagoClearWebhookSecret.checked),
    };

    try {
      setChurchPaymentsMessage("Salvando pagamentos da igreja...", false);
      state.tenantPaymentSettings = await fetchJson(
        tenantPaymentsEndpoint,
        { method: "PUT", headers: buildHeaders(true), body: JSON.stringify(payload) },
        "Falha ao salvar pagamentos da igreja."
      );
      renderTenantPaymentSettings();
      setChurchPaymentsMessage("Configurações de pagamento atualizadas com sucesso.", false);
    } catch (error) {
      setChurchPaymentsMessage(error instanceof Error ? error.message : "Falha ao salvar pagamentos da igreja.", true);
    }
  }

  function openChurchCreateModal() {
    if (!el.usersChurchCreateModal) return;
    el.usersChurchCreateForm.reset();
    setChurchCreateMessage("", false);
    el.usersChurchCreateModal.classList.remove("hide");
  }

  function closeChurchCreateModal() {
    if (!el.usersChurchCreateModal) return;
    el.usersChurchCreateModal.classList.add("hide");
  }

  async function submitChurchCreateForm(event) {
    event.preventDefault();
    if (!state.isAdmin) {
      setChurchCreateMessage("Acesso negado para criar igreja.", true);
      return;
    }

    const payload = {
      name: el.usersChurchCreateName.value.trim(),
      slug: el.usersChurchCreateSlug.value.trim(),
      public_display_name: el.usersChurchCreatePublicDisplayName.value.trim() || null,
      public_description: el.usersChurchCreatePublicDescription.value.trim() || null,
      support_email: el.usersChurchCreateSupportEmail.value.trim() || null,
      support_whatsapp: el.usersChurchCreateSupportWhatsapp.value.trim() || null,
    };

    try {
      setChurchCreateMessage("Criando igreja...", false);
      const tenant = await fetchJson(
        `${apiPrefix}/tenants/`,
        { method: "POST", headers: buildHeaders(true), body: JSON.stringify(payload) },
        "Falha ao criar igreja."
      );
      closeChurchCreateModal();
      setChurchMessage(`Igreja criada com sucesso: ${tenant.name}. Use o seletor no topo para trocar.`, false);
      if (window.initializeApp) {
        await window.initializeApp();
      }
      await loadTenantProfile();
    } catch (error) {
      setChurchCreateMessage(error instanceof Error ? error.message : "Falha ao criar igreja.", true);
    }
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
    if (el.usersNavChurchBtn) el.usersNavChurchBtn.addEventListener("click", () => openChurchView().catch((error) => setChurchMessage(error.message, true)));

    if (el.usersAddBtn) el.usersAddBtn.addEventListener("click", () => openUserForm("create", null));
    if (el.usersInviteBtn) el.usersInviteBtn.addEventListener("click", openInviteModal);
    if (el.usersOpenLinkInviteModalBtn) el.usersOpenLinkInviteModalBtn.addEventListener("click", openLinkInviteModal);
    if (el.usersOpenRoleModalBtn) el.usersOpenRoleModalBtn.addEventListener("click", openRoleModal);
    if (el.usersOpenPermissionModalBtn) el.usersOpenPermissionModalBtn.addEventListener("click", openPermissionModal);
    if (el.usersGeneratePermissionsBtn) el.usersGeneratePermissionsBtn.addEventListener("click", () => generateMissingPermissions().catch((error) => setRolesMessage(error.message, true)));

    if (el.usersForm) el.usersForm.addEventListener("submit", submitUserForm);
    if (el.usersInviteForm) el.usersInviteForm.addEventListener("submit", submitInviteForm);
    if (el.usersLinkInviteForm) el.usersLinkInviteForm.addEventListener("submit", submitLinkInviteForm);
    if (el.usersRoleForm) el.usersRoleForm.addEventListener("submit", submitRoleForm);
    if (el.usersPermissionForm) el.usersPermissionForm.addEventListener("submit", submitPermissionForm);
    if (el.usersChurchForm) el.usersChurchForm.addEventListener("submit", submitChurchForm);
    if (el.usersChurchPaymentsForm) el.usersChurchPaymentsForm.addEventListener("submit", submitChurchPaymentsForm);
    if (el.usersPaymentAccountForm) el.usersPaymentAccountForm.addEventListener("submit", submitPaymentAccountForm);
    if (el.usersPaymentAccountResetBtn) el.usersPaymentAccountResetBtn.addEventListener("click", resetPaymentAccountForm);
    if (el.usersChurchRefreshBtn) {
      el.usersChurchRefreshBtn.addEventListener("click", () => {
        Promise.all([loadTenantProfile(), loadTenantPaymentSettings(), loadPublicEventsForChurch()])
          .catch((error) => setChurchMessage(error.message, true));
      });
    }
    if (el.usersChurchCreateBtn) el.usersChurchCreateBtn.addEventListener("click", openChurchCreateModal);
    if (el.usersChurchLogoUploadBtn) el.usersChurchLogoUploadBtn.addEventListener("click", () => uploadChurchLogo().catch((error) => setChurchMessage(error.message, true)));
    if (el.usersChurchLogoFile) el.usersChurchLogoFile.addEventListener("change", syncSelectedLogoPreview);
    if (el.usersChurchPrimaryColorPicker) el.usersChurchPrimaryColorPicker.addEventListener("input", () => syncChurchColorInputs("primary-picker"));
    if (el.usersChurchSecondaryColorPicker) el.usersChurchSecondaryColorPicker.addEventListener("input", () => syncChurchColorInputs("secondary-picker"));
    if (el.usersChurchPrimaryColor) el.usersChurchPrimaryColor.addEventListener("change", () => syncChurchColorInputs("primary-text"));
    if (el.usersChurchSecondaryColor) el.usersChurchSecondaryColor.addEventListener("change", () => syncChurchColorInputs("secondary-text"));
    if (el.usersChurchPrimaryEyedropperBtn) el.usersChurchPrimaryEyedropperBtn.addEventListener("click", () => pickColorWithEyedropper("primary"));
    if (el.usersChurchSecondaryEyedropperBtn) el.usersChurchSecondaryEyedropperBtn.addEventListener("click", () => pickColorWithEyedropper("secondary"));
    if (el.usersChurchWhatsappCountry) el.usersChurchWhatsappCountry.addEventListener("change", () => syncWhatsappField({ fromCountry: true }));
    if (el.usersChurchSupportWhatsapp) el.usersChurchSupportWhatsapp.addEventListener("input", () => syncWhatsappField());
    if (el.usersChurchOpenLandingBtn) {
      el.usersChurchOpenLandingBtn.addEventListener("click", () => {
        window.open(buildChurchPublicUrls().landing, "_blank", "noopener,noreferrer");
      });
    }
    if (el.usersChurchPreviewBtn) {
      el.usersChurchPreviewBtn.addEventListener("click", () => {
        window.open(buildChurchPublicUrls().catalog, "_blank", "noopener,noreferrer");
      });
    }
    if (el.usersChurchCopyLandingBtn) el.usersChurchCopyLandingBtn.addEventListener("click", () => copyChurchUrl("landing"));
    if (el.usersChurchCopyCatalogBtn) el.usersChurchCopyCatalogBtn.addEventListener("click", () => copyChurchUrl("catalog"));
    if (el.usersChurchCopyLoginBtn) el.usersChurchCopyLoginBtn.addEventListener("click", () => copyChurchUrl("login"));
    [
      el.usersChurchName,
      el.usersChurchSlug,
      el.usersChurchPublicDisplayName,
      el.usersChurchPublicDescription,
      el.usersChurchPrimaryColor,
      el.usersChurchSecondaryColor,
      el.usersChurchLogoUrl,
      el.usersChurchSupportEmail,
    ].forEach((field) => {
      if (field) {
        field.addEventListener("input", updateChurchPreview);
      }
    });
    if (el.usersChurchCreateForm) el.usersChurchCreateForm.addEventListener("submit", submitChurchCreateForm);
    if (el.usersChurchCreateCloseBtn) el.usersChurchCreateCloseBtn.addEventListener("click", closeChurchCreateModal);
    if (el.usersChurchCreateCancelBtn) el.usersChurchCreateCancelBtn.addEventListener("click", closeChurchCreateModal);
    if (el.usersChurchCreateModal) {
      el.usersChurchCreateModal.addEventListener("click", (event) => {
        if (event.target === el.usersChurchCreateModal) closeChurchCreateModal();
      });
    }

    if (el.usersFormCloseBtn) el.usersFormCloseBtn.addEventListener("click", closeUserForm);
    if (el.usersFormCancelBtn) el.usersFormCancelBtn.addEventListener("click", closeUserForm);

    if (el.usersInviteCloseBtn) el.usersInviteCloseBtn.addEventListener("click", closeInviteModal);
    if (el.usersInviteCancelBtn) el.usersInviteCancelBtn.addEventListener("click", closeInviteModal);
    if (el.usersLinkInviteCloseBtn) el.usersLinkInviteCloseBtn.addEventListener("click", closeLinkInviteModal);
    if (el.usersLinkInviteCancelBtn) el.usersLinkInviteCancelBtn.addEventListener("click", closeLinkInviteModal);
    if (el.usersLinkInviteCopyBtn) {
      el.usersLinkInviteCopyBtn.addEventListener("click", async () => {
        try {
          const value = (el.usersLinkInviteResult && el.usersLinkInviteResult.value) || "";
          if (!value) {
            setLinkInviteMessage("Gere um link antes de copiar.", true);
            return;
          }
          await navigator.clipboard.writeText(value);
          setLinkInviteMessage("Link copiado com sucesso.", false);
        } catch (_error) {
          setLinkInviteMessage("Nao foi possivel copiar o link automaticamente.", true);
        }
      });
    }

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

    if (el.usersInviteModal) {
      el.usersInviteModal.addEventListener("click", (event) => {
        if (event.target === el.usersInviteModal) closeInviteModal();
      });
    }

    if (el.usersLinkInviteModal) {
      el.usersLinkInviteModal.addEventListener("click", (event) => {
        if (event.target === el.usersLinkInviteModal) closeLinkInviteModal();
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

    document.addEventListener("click", (event) => {
      const editButton = event.target.closest && event.target.closest("[data-payment-account-edit]");
      if (editButton) {
        editPaymentAccount(Number(editButton.getAttribute("data-payment-account-edit")));
        return;
      }
      const deleteButton = event.target.closest && event.target.closest("[data-payment-account-delete]");
      if (deleteButton) {
        deletePaymentAccount(Number(deleteButton.getAttribute("data-payment-account-delete"))).catch((error) => setPaymentAccountsMessage(error.message, true));
      }
    });

    if (el.usersPaymentAccountProvider) {
      el.usersPaymentAccountProvider.addEventListener("change", syncPaymentAccountProviderFields);
    }
    if (el.usersPaymentAccountEnvironment) {
      el.usersPaymentAccountEnvironment.addEventListener("change", syncPaymentAccountProviderFields);
    }
    if (el.usersPaymentAccountPublicKey) {
      el.usersPaymentAccountPublicKey.addEventListener("input", renderPaymentAccountReadiness);
    }
    if (el.usersPaymentAccountAccessToken) {
      el.usersPaymentAccountAccessToken.addEventListener("input", renderPaymentAccountReadiness);
    }
    if (el.usersPaymentAccountWebhookSecret) {
      el.usersPaymentAccountWebhookSecret.addEventListener("input", renderPaymentAccountReadiness);
    }
    if (el.usersPaymentAccountIntegratorId) {
      el.usersPaymentAccountIntegratorId.addEventListener("input", renderPaymentAccountGuide);
    }
    if (el.usersPaymentAccountOAuthBtn) {
      el.usersPaymentAccountOAuthBtn.addEventListener("click", () => {
        startMercadoPagoOAuth().catch((error) => setPaymentAccountsMessage(error.message, true));
      });
    }

    window.addEventListener("message", (event) => {
      if (!event.data || event.data.type !== "mercadopago-oauth") return;
      loadPaymentAccounts()
        .then(() => setPaymentAccountsMessage("Retorno do OAuth recebido. Status da conta atualizado.", false))
        .catch((error) => setPaymentAccountsMessage(error.message, true));
    });

    if (el.usersAddBtn) {
      el.usersAddBtn.setAttribute("onclick", "window.usersOpenCreateUserModal && window.usersOpenCreateUserModal()");
    }
  }

  window.openUsersModule = () => openUsersModule().catch((error) => setMessage(error.message, true));
  window.openUsersInviteModal = () => openUsersModule()
    .then(() => openInviteModal())
    .catch((error) => setMessage(error.message, true));
  window.openUsersLinkInviteModal = () => openUsersModule()
    .then(() => openLinkInviteModal())
    .catch((error) => setMessage(error.message, true));
  window.openChurchSettings = () => openUsersModule()
    .then(() => openChurchView())
    .catch((error) => setChurchMessage(error.message, true));
  window.setTopModule = setActiveModule;
  window.usersOpenCreateUserModal = () => openUserForm("create", null);
  window.usersEditUser = (userId) => openEditUser(Number(userId));
  window.usersDeleteUser = (userId) => openDeleteModal(Number(userId));

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", bindEvents);
  } else {
    bindEvents();
  }
})();
