from __future__ import annotations

from dataclasses import dataclass

from sqlalchemy.orm import Session

from app.db.models.role import Permission, Role


@dataclass(frozen=True)
class PermissionTemplate:
    name: str
    description: str
    category: str
    module: str


@dataclass(frozen=True)
class RoleTemplate:
    key: str
    name: str
    description: str
    permission_names: list[str]
    is_admin: bool = False


SYSTEM_PERMISSION_TEMPLATES: list[PermissionTemplate] = [
    PermissionTemplate("finance_dashboard_view", "Visualizar o painel financeiro.", "view", "finance"),
    PermissionTemplate("finance_transactions_view", "Visualizar lancamentos.", "view", "finance"),
    PermissionTemplate("finance_transactions_create", "Cadastrar lancamentos.", "create", "finance"),
    PermissionTemplate("finance_transactions_edit", "Editar lancamentos.", "edit", "finance"),
    PermissionTemplate("finance_transactions_delete", "Excluir lancamentos.", "delete", "finance"),
    PermissionTemplate("finance_categories_view", "Visualizar categorias.", "view", "finance"),
    PermissionTemplate("finance_categories_create", "Cadastrar categorias.", "create", "finance"),
    PermissionTemplate("finance_categories_edit", "Editar categorias.", "edit", "finance"),
    PermissionTemplate("finance_categories_delete", "Excluir categorias.", "delete", "finance"),
    PermissionTemplate("finance_ministries_view", "Visualizar ministerios.", "view", "finance"),
    PermissionTemplate("finance_ministries_create", "Cadastrar ministerios.", "create", "finance"),
    PermissionTemplate("finance_ministries_edit", "Editar ministerios.", "edit", "finance"),
    PermissionTemplate("finance_ministries_delete", "Excluir ministerios.", "delete", "finance"),
    PermissionTemplate("finance_payables_view", "Visualizar contas a pagar.", "view", "finance"),
    PermissionTemplate("finance_payables_create", "Cadastrar contas a pagar.", "create", "finance"),
    PermissionTemplate("finance_payables_edit", "Editar contas a pagar.", "edit", "finance"),
    PermissionTemplate("finance_payables_delete", "Excluir contas a pagar.", "delete", "finance"),
    PermissionTemplate("finance_receivables_view", "Visualizar contas a receber.", "view", "finance"),
    PermissionTemplate("finance_receivables_create", "Cadastrar contas a receber.", "create", "finance"),
    PermissionTemplate("finance_receivables_edit", "Editar contas a receber.", "edit", "finance"),
    PermissionTemplate("finance_receivables_delete", "Excluir contas a receber.", "delete", "finance"),
    PermissionTemplate("finance_upload_manage", "Importar e processar extratos bancarios.", "manage", "finance"),
    PermissionTemplate("finance_reports_view", "Visualizar relatorios financeiros.", "view", "finance"),

    PermissionTemplate("cells_dashboard_view", "Visualizar dashboard de celulas.", "view", "cells"),
    PermissionTemplate("cells_cells_view", "Visualizar lista de celulas.", "view", "cells"),
    PermissionTemplate("cells_people_view", "Visualizar pessoas da celula.", "view", "cells"),
    PermissionTemplate("cells_meetings_view", "Visualizar reunioes.", "view", "cells"),
    PermissionTemplate("cells_leaders_view", "Visualizar lideres.", "view", "cells"),
    PermissionTemplate("cells_disciplers_view", "Visualizar discipuladores.", "view", "cells"),
    PermissionTemplate("cells_lost_sheep_view", "Visualizar ovelhas perdidas.", "view", "cells"),
    PermissionTemplate("cells_network_pastors_view", "Visualizar pastores de rede.", "view", "cells"),
    PermissionTemplate("cells_orgchart_view", "Visualizar organograma de rede.", "view", "cells"),
    PermissionTemplate("cells_cells_create", "Criar celulas.", "create", "cells"),
    PermissionTemplate("cells_cells_edit", "Editar celulas.", "edit", "cells"),
    PermissionTemplate("cells_cells_delete", "Excluir celulas.", "delete", "cells"),
    PermissionTemplate("cells_people_add_visitor", "Cadastrar visitante.", "create", "cells"),
    PermissionTemplate("cells_people_add_assiduo", "Cadastrar assiduo.", "create", "cells"),
    PermissionTemplate("cells_people_add_member", "Cadastrar membro.", "create", "cells"),
    PermissionTemplate("cells_people_promote_member", "Promover membro.", "manage", "cells"),
    PermissionTemplate("cells_people_transfer_member", "Transferir membro.", "manage", "cells"),
    PermissionTemplate("cells_people_disable_member", "Desabilitar membro.", "manage", "cells"),
    PermissionTemplate("cells_meetings_create", "Criar reunioes.", "create", "cells"),
    PermissionTemplate("cells_attendance_manage", "Gerenciar frequencia.", "manage", "cells"),
    PermissionTemplate("cells_leaders_create", "Cadastrar lideres.", "create", "cells"),
    PermissionTemplate("cells_leaders_edit", "Editar lideres.", "edit", "cells"),
    PermissionTemplate("cells_leaders_delete", "Excluir lideres.", "delete", "cells"),
    PermissionTemplate("cells_disciplers_create", "Cadastrar discipuladores.", "create", "cells"),
    PermissionTemplate("cells_disciplers_edit", "Editar discipuladores.", "edit", "cells"),
    PermissionTemplate("cells_disciplers_delete", "Excluir discipuladores.", "delete", "cells"),
    PermissionTemplate("cells_network_pastors_create", "Cadastrar pastores de rede.", "create", "cells"),
    PermissionTemplate("cells_network_pastors_edit", "Editar pastores de rede.", "edit", "cells"),
    PermissionTemplate("cells_network_pastors_delete", "Excluir pastores de rede.", "delete", "cells"),
    PermissionTemplate("cells_lost_sheep_manage", "Gerenciar ovelhas perdidas.", "manage", "cells"),
    PermissionTemplate("cells_kids_view", "Visualizar o modulo infantil.", "view", "cells"),
    PermissionTemplate("cells_kids_create", "Cadastrar familias, criancas e responsaveis.", "create", "cells"),
    PermissionTemplate("cells_kids_edit", "Editar cadastros infantis.", "edit", "cells"),
    PermissionTemplate("cells_kids_manage", "Gerenciar operacao geral do modulo infantil.", "manage", "cells"),
    PermissionTemplate("cells_kids_checkin", "Realizar check-in infantil.", "manage", "cells"),
    PermissionTemplate("cells_kids_checkout", "Realizar check-out infantil.", "manage", "cells"),
    PermissionTemplate("cells_kids_manual_override", "Liberar retirada por excecao.", "manage", "cells"),
    PermissionTemplate("cells_kids_reports", "Visualizar relatorios infantis.", "view", "cells"),

    PermissionTemplate("school_dashboard_view", "Visualizar o dashboard da escola biblica.", "view", "school"),
    PermissionTemplate("school_courses_view", "Visualizar cursos.", "view", "school"),
    PermissionTemplate("school_courses_create", "Cadastrar cursos.", "create", "school"),
    PermissionTemplate("school_courses_edit", "Editar cursos.", "edit", "school"),
    PermissionTemplate("school_courses_delete", "Excluir cursos.", "delete", "school"),
    PermissionTemplate("school_classes_view", "Visualizar turmas.", "view", "school"),
    PermissionTemplate("school_classes_create", "Cadastrar turmas.", "create", "school"),
    PermissionTemplate("school_classes_edit", "Editar turmas.", "edit", "school"),
    PermissionTemplate("school_classes_delete", "Excluir turmas.", "delete", "school"),
    PermissionTemplate("school_professors_view", "Visualizar professores.", "view", "school"),
    PermissionTemplate("school_professors_create", "Cadastrar professores.", "create", "school"),
    PermissionTemplate("school_professors_edit", "Editar professores.", "edit", "school"),
    PermissionTemplate("school_professors_delete", "Excluir professores.", "delete", "school"),
    PermissionTemplate("school_lessons_view", "Visualizar aulas.", "view", "school"),
    PermissionTemplate("school_lessons_create", "Cadastrar aulas.", "create", "school"),
    PermissionTemplate("school_lessons_edit", "Editar aulas.", "edit", "school"),
    PermissionTemplate("school_lessons_delete", "Excluir aulas.", "delete", "school"),
    PermissionTemplate("school_students_view", "Visualizar alunos.", "view", "school"),
    PermissionTemplate("school_students_create", "Cadastrar alunos.", "create", "school"),
    PermissionTemplate("school_students_edit", "Editar alunos.", "edit", "school"),
    PermissionTemplate("school_students_delete", "Excluir alunos.", "delete", "school"),
    PermissionTemplate("school_attendance_view", "Visualizar chamada.", "view", "school"),
    PermissionTemplate("school_attendance_manage", "Registrar e salvar chamada.", "manage", "school"),

    PermissionTemplate("events_events_view", "Visualizar agenda de eventos.", "view", "events"),
    PermissionTemplate("events_events_create", "Cadastrar eventos.", "create", "events"),
    PermissionTemplate("events_events_edit", "Editar eventos.", "edit", "events"),
    PermissionTemplate("events_events_delete", "Excluir eventos.", "delete", "events"),
    PermissionTemplate("events_registrations_view", "Visualizar inscricoes dos eventos.", "view", "events"),
    PermissionTemplate("events_payments_view", "Visualizar pagamentos dos eventos.", "view", "events"),
    PermissionTemplate("events_payments_manage", "Confirmar e acompanhar pagamentos dos eventos.", "manage", "events"),
    PermissionTemplate("events_analytics_view", "Visualizar analytics dos eventos.", "view", "events"),
    PermissionTemplate("events_notifications_view", "Visualizar notificacoes dos eventos.", "view", "events"),

    PermissionTemplate("users_users_view", "Visualizar usuarios.", "view", "users"),
    PermissionTemplate("users_users_create", "Cadastrar usuarios.", "create", "users"),
    PermissionTemplate("users_users_edit", "Editar usuarios.", "edit", "users"),
    PermissionTemplate("users_users_delete", "Excluir usuarios.", "delete", "users"),
    PermissionTemplate("users_roles_view", "Visualizar roles.", "view", "users"),
    PermissionTemplate("users_roles_create", "Cadastrar roles.", "create", "users"),
    PermissionTemplate("users_roles_edit", "Editar roles.", "edit", "users"),
    PermissionTemplate("users_roles_delete", "Excluir roles.", "delete", "users"),
    PermissionTemplate("users_permissions_view", "Visualizar permissoes.", "view", "users"),
    PermissionTemplate("users_permissions_create", "Cadastrar permissoes.", "create", "users"),
    PermissionTemplate("users_permissions_edit", "Editar permissoes.", "edit", "users"),
    PermissionTemplate("users_permissions_delete", "Excluir permissoes.", "delete", "users"),
    PermissionTemplate("users_system_permissions_manage", "Gerar permissoes do sistema.", "manage", "users"),
]


DEFAULT_ROLE_TEMPLATES: list[RoleTemplate] = [
    RoleTemplate(
        key="super_admin",
        name="Super_Admin",
        description="Acesso total a todos os modulos e configuracoes do tenant.",
        permission_names=[template.name for template in SYSTEM_PERMISSION_TEMPLATES],
        is_admin=True,
    ),
    RoleTemplate(
        key="finance_read",
        name="Finance_Read",
        description="Acesso de leitura ao modulo Financeiro.",
        permission_names=[
            "finance_dashboard_view",
            "finance_transactions_view",
            "finance_categories_view",
            "finance_ministries_view",
            "finance_payables_view",
            "finance_receivables_view",
            "finance_reports_view",
        ],
    ),
    RoleTemplate(
        key="finance_write",
        name="Finance_Write",
        description="Acesso de leitura e escrita ao modulo Financeiro.",
        permission_names=[
            template.name
            for template in SYSTEM_PERMISSION_TEMPLATES
            if template.module == "finance"
        ],
    ),
    RoleTemplate(
        key="kids_read",
        name="Kids_Read",
        description="Acesso de leitura ao modulo Infantil.",
        permission_names=[
            "cells_kids_view",
            "cells_kids_reports",
        ],
    ),
    RoleTemplate(
        key="kids_write",
        name="Kids_Write",
        description="Acesso de leitura e escrita ao modulo Infantil.",
        permission_names=[
            "cells_kids_view",
            "cells_kids_create",
            "cells_kids_edit",
            "cells_kids_manage",
            "cells_kids_checkin",
            "cells_kids_checkout",
            "cells_kids_manual_override",
            "cells_kids_reports",
        ],
    ),
    RoleTemplate(
        key="school_read",
        name="School_Read",
        description="Acesso de leitura ao modulo Escola Biblica.",
        permission_names=[
            "school_dashboard_view",
            "school_courses_view",
            "school_classes_view",
            "school_professors_view",
            "school_lessons_view",
            "school_students_view",
            "school_attendance_view",
        ],
    ),
    RoleTemplate(
        key="school_write",
        name="School_Write",
        description="Acesso de leitura e escrita ao modulo Escola Biblica.",
        permission_names=[
            template.name
            for template in SYSTEM_PERMISSION_TEMPLATES
            if template.module == "school"
        ],
    ),
    RoleTemplate(
        key="events_read",
        name="Events_Read",
        description="Acesso de leitura ao modulo Eventos.",
        permission_names=[
            "events_events_view",
            "events_registrations_view",
            "events_payments_view",
            "events_analytics_view",
            "events_notifications_view",
        ],
    ),
    RoleTemplate(
        key="events_write",
        name="Events_Write",
        description="Acesso de leitura e escrita ao modulo Eventos.",
        permission_names=[
            template.name
            for template in SYSTEM_PERMISSION_TEMPLATES
            if template.module == "events"
        ],
    ),
    RoleTemplate(
        key="users_read",
        name="Users_Read",
        description="Acesso de leitura ao modulo Usuarios.",
        permission_names=[
            "users_users_view",
            "users_roles_view",
            "users_permissions_view",
        ],
    ),
    RoleTemplate(
        key="users_write",
        name="Users_Write",
        description="Acesso de leitura e escrita ao modulo Usuarios.",
        permission_names=[
            template.name
            for template in SYSTEM_PERMISSION_TEMPLATES
            if template.module == "users"
        ],
    ),
]


def _upsert_permissions(db: Session, templates: list[PermissionTemplate]) -> dict[str, Permission]:
    names = [template.name for template in templates]
    existing = db.query(Permission).filter(Permission.name.in_(names)).all()
    by_name = {row.name: row for row in existing if row and row.name}

    for template in templates:
        current = by_name.get(template.name)
        if current:
            current.description = template.description
            current.category = template.category
            current.module = template.module
            current.active = True
            continue

        created = Permission(
            name=template.name,
            description=template.description,
            category=template.category,
            module=template.module,
            active=True,
        )
        db.add(created)
        by_name[template.name] = created

    db.commit()
    for row in by_name.values():
        db.refresh(row)
    return by_name


def _upsert_role(
    db: Session,
    *,
    tenant_id: int,
    name: str,
    description: str,
    permission_names: list[str],
    permissions_by_name: dict[str, Permission],
    is_admin: bool = False,
) -> Role:
    role = db.query(Role).filter(Role.tenant_id == tenant_id, Role.name == name).first()
    if not role:
        role = Role(tenant_id=tenant_id, name=name)
        db.add(role)

    role.description = description
    role.active = True
    role.is_admin = is_admin
    role.permissions = [
        permissions_by_name[permission_name]
        for permission_name in permission_names
        if permission_name in permissions_by_name
    ]
    db.commit()
    db.refresh(role)
    return role


def _cells_hierarchy_role_templates() -> list[RoleTemplate]:
    leader_permissions = [
        "cells_dashboard_view",
        "cells_orgchart_view",
        "cells_people_view",
        "cells_meetings_view",
        "cells_people_add_visitor",
        "cells_people_add_assiduo",
        "cells_people_add_member",
        "cells_people_promote_member",
        "cells_people_transfer_member",
        "cells_people_disable_member",
        "cells_meetings_create",
        "cells_attendance_manage",
        "cells_lost_sheep_view",
        "cells_lost_sheep_manage",
    ]

    discipler_permissions = sorted(
        set(
            leader_permissions
            + [
                "cells_cells_view",
                "cells_leaders_view",
                "cells_disciplers_view",
                "cells_network_pastors_view",
                "cells_leaders_create",
                "cells_leaders_edit",
                "cells_disciplers_create",
                "cells_disciplers_edit",
            ]
        )
    )

    network_pastor_permissions = sorted(
        set(
            discipler_permissions
            + [
                "cells_network_pastors_create",
                "cells_network_pastors_edit",
                "cells_network_pastors_delete",
            ]
        )
    )

    return [
        RoleTemplate(
            key="leader",
            name="Leader",
            description="Gerencia sua celula (pessoas, reunioes e frequencia).",
            permission_names=leader_permissions,
        ),
        RoleTemplate(
            key="discipler",
            name="Discipler",
            description="Supervisiona lideres e suas celulas (rede local).",
            permission_names=discipler_permissions,
        ),
        RoleTemplate(
            key="network_pastor",
            name="Network_Pastor",
            description="Supervisiona discipuladores e suas celulas (rede).",
            permission_names=network_pastor_permissions,
        ),
    ]


def _install_role_templates(
    db: Session,
    *,
    tenant_id: int,
    templates: list[RoleTemplate],
    permissions_by_name: dict[str, Permission],
) -> dict[str, int]:
    installed: dict[str, int] = {}
    for template in templates:
        installed[template.key] = _upsert_role(
            db,
            tenant_id=tenant_id,
            name=template.name,
            description=template.description,
            permission_names=template.permission_names,
            permissions_by_name=permissions_by_name,
            is_admin=template.is_admin,
        ).id
    return installed


def install_default_roles_for_tenant(db: Session, tenant_id: int) -> dict[str, int]:
    permissions_by_name = _upsert_permissions(db, SYSTEM_PERMISSION_TEMPLATES)
    installed = _install_role_templates(
        db,
        tenant_id=tenant_id,
        templates=DEFAULT_ROLE_TEMPLATES,
        permissions_by_name=permissions_by_name,
    )
    installed.update(
        _install_role_templates(
            db,
            tenant_id=tenant_id,
            templates=_cells_hierarchy_role_templates(),
            permissions_by_name=permissions_by_name,
        )
    )
    return installed


def install_cells_hierarchy_roles(db: Session, tenant_id: int) -> dict[str, int]:
    permissions_by_name = _upsert_permissions(db, SYSTEM_PERMISSION_TEMPLATES)
    return _install_role_templates(
        db,
        tenant_id=tenant_id,
        templates=_cells_hierarchy_role_templates(),
        permissions_by_name=permissions_by_name,
    )
