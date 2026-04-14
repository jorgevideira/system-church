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


def _upsert_permissions(db: Session, templates: list[PermissionTemplate]) -> dict[str, Permission]:
    names = [t.name for t in templates]
    existing = db.query(Permission).filter(Permission.name.in_(names)).all()
    by_name = {p.name: p for p in existing if p and p.name}

    for t in templates:
        current = by_name.get(t.name)
        if current:
            # Keep names stable, refresh metadata in case templates evolve.
            current.description = t.description
            current.category = t.category
            current.module = t.module
            current.active = True
            continue
        created = Permission(
            name=t.name,
            description=t.description,
            category=t.category,
            module=t.module,
            active=True,
        )
        db.add(created)
        by_name[t.name] = created

    db.commit()
    # Ensure objects are attached and have ids.
    for p in by_name.values():
        db.refresh(p)
    return by_name


def _upsert_role(
    db: Session,
    *,
    tenant_id: int,
    name: str,
    description: str,
    permission_names: list[str],
    permissions_by_name: dict[str, Permission],
) -> Role:
    role = db.query(Role).filter(Role.tenant_id == tenant_id, Role.name == name).first()
    if not role:
        role = Role(tenant_id=tenant_id, name=name)
        db.add(role)

    role.description = description
    role.active = True
    role.is_admin = False

    perms: list[Permission] = []
    for perm_name in permission_names:
        perm = permissions_by_name.get(perm_name)
        if perm:
            perms.append(perm)
    role.permissions = perms
    db.commit()
    db.refresh(role)
    return role


def install_cells_hierarchy_roles(db: Session, tenant_id: int) -> dict[str, int]:
    """Creates/updates permission templates and 3 default roles aligned with the org chart."""
    permission_templates = [
        # Views
        PermissionTemplate("cells_dashboard_view", "Visualizar dashboard de células", "view", "cells"),
        PermissionTemplate("cells_cells_view", "Visualizar lista de células", "view", "cells"),
        PermissionTemplate("cells_people_view", "Visualizar pessoas da célula", "view", "cells"),
        PermissionTemplate("cells_meetings_view", "Visualizar reuniões", "view", "cells"),
        PermissionTemplate("cells_leaders_view", "Visualizar líderes", "view", "cells"),
        PermissionTemplate("cells_disciplers_view", "Visualizar discipuladores", "view", "cells"),
        PermissionTemplate("cells_lost_sheep_view", "Visualizar ovelhas perdidas", "view", "cells"),
        PermissionTemplate("cells_network_pastors_view", "Visualizar pastores de rede", "view", "cells"),
        PermissionTemplate("cells_orgchart_view", "Visualizar organograma de rede", "view", "cells"),

        # Manage
        PermissionTemplate("cells_cells_create", "Criar células", "manage", "cells"),
        PermissionTemplate("cells_cells_edit", "Editar células", "manage", "cells"),
        PermissionTemplate("cells_cells_delete", "Excluir células", "manage", "cells"),
        PermissionTemplate("cells_people_add_visitor", "Cadastrar visitante", "manage", "cells"),
        PermissionTemplate("cells_people_add_assiduo", "Cadastrar assíduo", "manage", "cells"),
        PermissionTemplate("cells_people_add_member", "Cadastrar membro", "manage", "cells"),
        PermissionTemplate("cells_people_promote_member", "Promover membro", "manage", "cells"),
        PermissionTemplate("cells_people_transfer_member", "Transferir membro", "manage", "cells"),
        PermissionTemplate("cells_people_disable_member", "Desabilitar membro", "manage", "cells"),
        PermissionTemplate("cells_meetings_create", "Criar reuniões", "manage", "cells"),
        PermissionTemplate("cells_attendance_manage", "Gerenciar frequência", "manage", "cells"),
        PermissionTemplate("cells_leaders_create", "Cadastrar líderes", "manage", "cells"),
        PermissionTemplate("cells_leaders_edit", "Editar líderes", "manage", "cells"),
        PermissionTemplate("cells_leaders_delete", "Excluir líderes", "manage", "cells"),
        PermissionTemplate("cells_disciplers_create", "Cadastrar discipuladores", "manage", "cells"),
        PermissionTemplate("cells_disciplers_edit", "Editar discipuladores", "manage", "cells"),
        PermissionTemplate("cells_disciplers_delete", "Excluir discipuladores", "manage", "cells"),
        PermissionTemplate("cells_network_pastors_create", "Cadastrar pastores de rede", "manage", "cells"),
        PermissionTemplate("cells_network_pastors_edit", "Editar pastores de rede", "manage", "cells"),
        PermissionTemplate("cells_network_pastors_delete", "Excluir pastores de rede", "manage", "cells"),
        PermissionTemplate("cells_lost_sheep_manage", "Gerenciar ovelhas perdidas", "manage", "cells"),
    ]

    permissions_by_name = _upsert_permissions(db, permission_templates)

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

    discipler_permissions = sorted(set(leader_permissions + [
        "cells_cells_view",
        "cells_leaders_view",
        "cells_disciplers_view",
        "cells_network_pastors_view",
        "cells_leaders_create",
        "cells_leaders_edit",
        "cells_disciplers_create",
        "cells_disciplers_edit",
    ]))

    network_pastor_permissions = sorted(set(discipler_permissions + [
        "cells_network_pastors_view",
        "cells_network_pastors_create",
        "cells_network_pastors_edit",
        "cells_network_pastors_delete",
    ]))

    created_roles = {
        "leader": _upsert_role(
            db,
            tenant_id=tenant_id,
            name="Leader",
            description="Gerencia sua celula (pessoas, reunioes e frequencia).",
            permission_names=leader_permissions,
            permissions_by_name=permissions_by_name,
        ).id,
        "discipler": _upsert_role(
            db,
            tenant_id=tenant_id,
            name="Discipler",
            description="Supervisiona lideres e suas celulas (rede local).",
            permission_names=discipler_permissions,
            permissions_by_name=permissions_by_name,
        ).id,
        "network_pastor": _upsert_role(
            db,
            tenant_id=tenant_id,
            name="Network_Pastor",
            description="Supervisiona discipuladores e suas celulas (rede).",
            permission_names=network_pastor_permissions,
            permissions_by_name=permissions_by_name,
        ).id,
    }
    return created_roles
