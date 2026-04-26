from datetime import date, timedelta
from calendar import monthrange
from typing import Optional

from sqlalchemy.orm import Session
from sqlalchemy import func
import sqlalchemy as sa

from app.db.models.cell import Cell
from app.db.models.cell_leader_assignment import CellLeaderAssignment
from app.db.models.cell_member import CellMember
from app.db.models.cell_member_link import CellMemberLink
from app.db.models.cell_meeting import CellMeeting
from app.db.models.cell_meeting_attendance import CellMeetingAttendance
from app.db.models.cell_visitor import CellVisitor
from app.db.models.cell_meeting_visitor import CellMeetingVisitor
from app.db.models.tenant import Tenant
from app.db.models.user import User
from app.schemas.cell import (
    CellCreate,
    CellLeaderAssignmentCreate,
    CellLeaderAssignmentUpdate,
    CellMemberCreate,
    CellMemberUpdate,
    CellMeetingAttendanceItem,
    CellMeetingCreate,
    CellMeetingUpdate,
    CellVisitorCreate,
    CellUpdate,
)
from app.schemas.cell_orgchart import OrgChartResponse, OrgChartNetworkPastorNode, OrgChartDisciplerNode, OrgChartLeaderNode, OrgChartMember, OrgChartCell


def list_cells(
    db: Session,
    tenant_id: int,
    status_filter: Optional[str] = None,
    allowed_cell_ids: Optional[list[int]] = None,
) -> list[Cell]:
    q = db.query(Cell).filter(Cell.tenant_id == tenant_id)
    if allowed_cell_ids is not None:
        if not allowed_cell_ids:
            return []
        q = q.filter(Cell.id.in_(allowed_cell_ids))
    if status_filter:
        q = q.filter(Cell.status == status_filter)
    return q.order_by(Cell.name.asc()).all()


def list_public_cells(db: Session, tenant_slug: str) -> tuple[Optional[Tenant], list[dict]]:
    tenant = db.query(Tenant).filter(Tenant.slug == tenant_slug, Tenant.is_active.is_(True)).first()
    if tenant is None:
        return None, []

    cells = (
        db.query(Cell)
        .filter(
            Cell.tenant_id == tenant.id,
            Cell.status == "active",
        )
        .order_by(Cell.name.asc(), Cell.id.asc())
        .all()
    )

    payload: list[dict] = []
    for cell in cells:
        leader_assignment = (
            db.query(CellLeaderAssignment, CellMember.full_name)
            .join(CellMember, CellMember.id == CellLeaderAssignment.member_id)
            .filter(
                CellLeaderAssignment.tenant_id == tenant.id,
                CellLeaderAssignment.cell_id == cell.id,
                CellLeaderAssignment.active.is_(True),
                CellMember.tenant_id == tenant.id,
                CellMember.is_active.is_(True),
            )
            .order_by(
                CellLeaderAssignment.is_primary.desc(),
                CellLeaderAssignment.start_date.desc(),
                CellLeaderAssignment.id.desc(),
            )
            .first()
        )

        leader_name = None
        if leader_assignment is not None:
            _assignment, leader_name = leader_assignment

        payload.append({
            "id": cell.id,
            "name": cell.name,
            "weekday": cell.weekday,
            "meeting_time": cell.meeting_time,
            "address": cell.address,
            "leader_name": leader_name,
        })

    return tenant, payload


def list_cell_ids_led_by_user(db: Session, user: User, tenant_id: int) -> list[int]:
    rows = (
        db.query(CellLeaderAssignment.cell_id)
        .join(CellMember, CellMember.id == CellLeaderAssignment.member_id)
        .filter(
            CellLeaderAssignment.tenant_id == tenant_id,
            CellMember.tenant_id == tenant_id,
            CellMember.user_id == user.id,
            CellLeaderAssignment.active.is_(True),
        )
        .distinct()
        .all()
    )
    return [row.cell_id for row in rows]

def _member_ids_for_user(db: Session, user: User, tenant_id: int) -> list[int]:
    rows = (
        db.query(CellMember.id)
        .filter(
            CellMember.tenant_id == tenant_id,
            CellMember.user_id == user.id,
            CellMember.is_active.is_(True),
        )
        .all()
    )
    return [row.id for row in rows]


def list_cell_ids_supervised_by_discipler_user(db: Session, user: User, tenant_id: int) -> list[int]:
    """Cells where the user acts as discipler/supervisor for leaders (and/or is the discipler row)."""
    member_ids = _member_ids_for_user(db, user, tenant_id)
    if not member_ids:
        return []

    rows = (
        db.query(CellLeaderAssignment.cell_id)
        .filter(
            CellLeaderAssignment.tenant_id == tenant_id,
            CellLeaderAssignment.active.is_(True),
            sa.or_(
                # Leader rows point to their discipler.
                sa.and_(CellLeaderAssignment.role == "leader", CellLeaderAssignment.discipler_member_id.in_(member_ids)),
                # Discipler row (co_leader) identifies the discipler supervising that cell.
                sa.and_(CellLeaderAssignment.role == "co_leader", CellLeaderAssignment.member_id.in_(member_ids)),
            ),
        )
        .distinct()
        .all()
    )
    return [row.cell_id for row in rows]


def list_cell_ids_supervised_by_network_pastor_user(db: Session, user: User, tenant_id: int) -> list[int]:
    """Cells where the user is set as network pastor for the discipler (co_leader row)."""
    member_ids = _member_ids_for_user(db, user, tenant_id)
    if not member_ids:
        return []

    rows = (
        db.query(CellLeaderAssignment.cell_id)
        .filter(
            CellLeaderAssignment.tenant_id == tenant_id,
            CellLeaderAssignment.active.is_(True),
            CellLeaderAssignment.role == "co_leader",
            CellLeaderAssignment.discipler_member_id.in_(member_ids),
        )
        .distinct()
        .all()
    )
    return [row.cell_id for row in rows]

def user_has_access_to_cell(db: Session, user: User, tenant_id: int, cell_id: int, *, mode: str = "leader") -> bool:
    """Check scoped access based on the caller mode (leader/discipler/network_pastor)."""
    if mode == "network_pastor":
        return cell_id in list_cell_ids_supervised_by_network_pastor_user(db, user, tenant_id)
    if mode == "discipler":
        return cell_id in list_cell_ids_supervised_by_discipler_user(db, user, tenant_id)
    return cell_id in list_cell_ids_led_by_user(db, user, tenant_id)


def get_cells_org_chart(db: Session, tenant_id: int, allowed_cell_ids: Optional[list[int]] = None) -> OrgChartResponse:
    """Return the org chart: Network Pastor -> Disciplers -> Leaders -> Cells."""
    cell_query = db.query(Cell).filter(Cell.tenant_id == tenant_id)
    if allowed_cell_ids is not None:
        if not allowed_cell_ids:
            return OrgChartResponse(networks=[])
        cell_query = cell_query.filter(Cell.id.in_(allowed_cell_ids))
    cells = cell_query.all()
    if not cells:
        return OrgChartResponse(networks=[])

    cell_ids = [c.id for c in cells]
    assignments = (
        db.query(CellLeaderAssignment)
        .filter(
            CellLeaderAssignment.tenant_id == tenant_id,
            CellLeaderAssignment.cell_id.in_(cell_ids),
            CellLeaderAssignment.active.is_(True),
            CellLeaderAssignment.role.in_(["leader", "co_leader"]),
        )
        .all()
    )

    co_by_cell: dict[int, CellLeaderAssignment] = {}
    leader_by_cell: dict[int, CellLeaderAssignment] = {}
    for row in assignments:
        if row.role == "co_leader" and row.cell_id not in co_by_cell:
            co_by_cell[row.cell_id] = row
        elif row.role == "leader" and row.cell_id not in leader_by_cell:
            leader_by_cell[row.cell_id] = row

    # Collect all member ids referenced by the chart.
    member_ids: set[int] = set()
    for cell_id in cell_ids:
        co = co_by_cell.get(cell_id)
        lead = leader_by_cell.get(cell_id)
        if co:
            member_ids.add(co.member_id)
            if co.discipler_member_id:
                member_ids.add(co.discipler_member_id)
        if lead:
            member_ids.add(lead.member_id)
            if lead.discipler_member_id:
                member_ids.add(lead.discipler_member_id)

    members = (
        db.query(CellMember)
        .filter(
            CellMember.tenant_id == tenant_id,
            CellMember.id.in_(list(member_ids) or [0]),
        )
        .all()
    )
    member_by_id = {m.id: m for m in members}

    # network_pastor_id -> discipler_id -> leader_id -> [cells]
    tree: dict[int | None, dict[int, dict[int, list[Cell]]]] = {}

    for cell in cells:
        co = co_by_cell.get(cell.id)
        lead = leader_by_cell.get(cell.id)
        discipler_id = co.member_id if co else (lead.discipler_member_id if lead else None)
        leader_id = lead.member_id if lead else None
        network_pastor_id = co.discipler_member_id if co else None

        if not discipler_id or not leader_id:
            # Without both discipler and leader this cell can't be placed cleanly in the chart.
            continue

        tree.setdefault(network_pastor_id, {}).setdefault(discipler_id, {}).setdefault(leader_id, []).append(cell)

    networks: list[OrgChartNetworkPastorNode] = []

    def _member_summary(member_id: int) -> OrgChartMember:
        m = member_by_id.get(member_id)
        if not m:
            return OrgChartMember(id=member_id, full_name=f"Membro {member_id}", user_id=None)
        return OrgChartMember(id=m.id, full_name=m.full_name, user_id=m.user_id)

    for network_pastor_id, discipler_map in sorted(tree.items(), key=lambda item: (item[0] is None, item[0] or 0)):
        disciplers: list[OrgChartDisciplerNode] = []
        for discipler_id, leader_map in sorted(discipler_map.items(), key=lambda item: item[0]):
            leaders: list[OrgChartLeaderNode] = []
            for leader_id, leader_cells in sorted(leader_map.items(), key=lambda item: item[0]):
                leaders.append(
                    OrgChartLeaderNode(
                        leader=_member_summary(leader_id),
                        cells=[
                            OrgChartCell(
                                id=c.id,
                                name=c.name,
                                weekday=c.weekday,
                                meeting_time=str(c.meeting_time) if c.meeting_time is not None else None,
                                address=c.address,
                                status=c.status,
                            )
                            for c in sorted(leader_cells, key=lambda cc: cc.name or "")
                        ],
                    )
                )
            disciplers.append(OrgChartDisciplerNode(discipler=_member_summary(discipler_id), leaders=leaders))

        networks.append(
            OrgChartNetworkPastorNode(
                network_pastor=_member_summary(network_pastor_id) if network_pastor_id else None,
                disciplers=disciplers,
            )
        )

    return OrgChartResponse(networks=networks)


def get_cell(db: Session, cell_id: int, tenant_id: int) -> Optional[Cell]:
    return db.query(Cell).filter(Cell.id == cell_id, Cell.tenant_id == tenant_id).first()


def create_cell(db: Session, payload: CellCreate, tenant_id: int) -> Cell:
    cell = Cell(**payload.model_dump(), tenant_id=tenant_id)
    db.add(cell)
    db.commit()
    db.refresh(cell)
    return cell


def update_cell(db: Session, cell: Cell, payload: CellUpdate) -> Cell:
    changes = payload.model_dump(exclude_unset=True)
    for field, value in changes.items():
        setattr(cell, field, value)
    db.commit()
    db.refresh(cell)
    return cell


def delete_cell(db: Session, cell: Cell) -> None:
    db.delete(cell)
    db.commit()


def create_member(db: Session, payload: CellMemberCreate, tenant_id: int) -> CellMember:
    data = payload.model_dump()
    data["count_start_date"] = data.get("count_start_date") or date.today()
    member = CellMember(**data, tenant_id=tenant_id, is_active=(data.get("status", "active") == "active"))
    db.add(member)
    db.commit()
    db.refresh(member)
    return member


def list_members(
    db: Session,
    tenant_id: int,
    status_filter: Optional[str] = None,
    allowed_cell_ids: Optional[list[int]] = None,
) -> list[CellMember]:
    q = db.query(CellMember).filter(CellMember.tenant_id == tenant_id)
    if allowed_cell_ids is not None:
        if not allowed_cell_ids:
            return []
        q = (
            q.join(CellMemberLink, CellMemberLink.member_id == CellMember.id)
            .filter(
                CellMemberLink.tenant_id == tenant_id,
                CellMemberLink.active.is_(True),
                CellMemberLink.cell_id.in_(allowed_cell_ids),
            )
            .distinct()
        )
    if status_filter:
        q = q.filter(CellMember.status == status_filter)
    return q.order_by(CellMember.full_name.asc()).all()


def member_is_in_cells(db: Session, member_id: int, tenant_id: int, allowed_cell_ids: list[int]) -> bool:
    if not allowed_cell_ids:
        return False
    link = (
        db.query(CellMemberLink)
        .filter(
            CellMemberLink.tenant_id == tenant_id,
            CellMemberLink.member_id == member_id,
            CellMemberLink.active.is_(True),
            CellMemberLink.cell_id.in_(allowed_cell_ids),
        )
        .first()
    )
    return link is not None


def get_member(db: Session, member_id: int, tenant_id: int) -> Optional[CellMember]:
    return db.query(CellMember).filter(CellMember.id == member_id, CellMember.tenant_id == tenant_id).first()


def update_member(db: Session, member: CellMember, payload: CellMemberUpdate) -> CellMember:
    changes = payload.model_dump(exclude_unset=True)
    if "status" in changes and "is_active" not in changes:
        changes["is_active"] = changes["status"] == "active"
    if (
        "stage" in changes
        and changes["stage"] != member.stage
        and "count_start_date" not in changes
    ):
        changes["count_start_date"] = date.today()
    for field, value in changes.items():
        setattr(member, field, value)
    db.commit()
    db.refresh(member)
    return member


def list_cell_members(db: Session, tenant_id: int, cell_id: int) -> list[CellMemberLink]:
    return (
        db.query(CellMemberLink)
        .filter(CellMemberLink.tenant_id == tenant_id, CellMemberLink.cell_id == cell_id, CellMemberLink.active.is_(True))
        .order_by(CellMemberLink.start_date.asc())
        .all()
    )


def list_cell_people(
    db: Session,
    tenant_id: int,
    cell_id: int,
    stage_filter: Optional[str] = None,
    on_date: Optional[date] = None,
) -> list[CellMember]:
    q = (
        db.query(CellMember)
        .join(CellMemberLink, CellMemberLink.member_id == CellMember.id)
        .filter(
            CellMember.tenant_id == tenant_id,
            CellMemberLink.tenant_id == tenant_id,
            CellMemberLink.cell_id == cell_id,
            CellMember.status == "active",
            CellMember.is_active.is_(True),
        )
    )

    if on_date:
        q = q.filter(
            CellMemberLink.start_date <= on_date,
            (CellMemberLink.end_date.is_(None)) | (CellMemberLink.end_date >= on_date),
        )
    else:
        q = q.filter(CellMemberLink.active.is_(True))

    if stage_filter:
        q = q.filter(CellMember.stage == stage_filter)
    return q.order_by(CellMember.full_name.asc()).all()


def promote_member_stage(
    db: Session,
    *,
    tenant_id: int,
    cell_id: int,
    member: CellMember,
    target_stage: str,
) -> CellMember:
    active_link = (
        db.query(CellMemberLink)
        .filter(
            CellMemberLink.tenant_id == tenant_id,
            CellMemberLink.cell_id == cell_id,
            CellMemberLink.member_id == member.id,
            CellMemberLink.active.is_(True),
        )
        .first()
    )
    if not active_link:
        raise ValueError("Member is not linked to this cell")

    current_stage = (member.stage or "member").strip().lower()
    allowed_transitions = {
        "visitor": {"assiduo", "member"},
        "assiduo": {"member"},
        "member": set(),
    }

    if target_stage == current_stage:
        return member
    if target_stage not in allowed_transitions.get(current_stage, set()):
        raise ValueError("Invalid promotion transition")

    member.stage = target_stage
    member.count_start_date = date.today()
    db.commit()
    db.refresh(member)
    return member


def assign_member_to_cell(
    db: Session,
    tenant_id: int,
    cell_id: int,
    member_id: int,
    start_date: Optional[date] = None,
) -> CellMemberLink:
    current_link = (
        db.query(CellMemberLink)
        .filter(CellMemberLink.tenant_id == tenant_id, CellMemberLink.member_id == member_id, CellMemberLink.active.is_(True))
        .first()
    )
    if current_link:
        raise ValueError("Member is already linked to an active cell")

    member = get_member(db, member_id, tenant_id)
    default_start_date = start_date or (member.count_start_date if member else None) or date.today()

    link = CellMemberLink(
        tenant_id=tenant_id,
        cell_id=cell_id,
        member_id=member_id,
        start_date=default_start_date,
        active=True,
    )
    db.add(link)
    db.commit()
    db.refresh(link)
    return link


def unassign_member_from_cell(
    db: Session,
    tenant_id: int,
    *,
    cell_id: int,
    member_id: int,
    end_date: Optional[date] = None,
) -> CellMemberLink:
    link = (
        db.query(CellMemberLink)
        .filter(
            CellMemberLink.tenant_id == tenant_id,
            CellMemberLink.cell_id == cell_id,
            CellMemberLink.member_id == member_id,
            CellMemberLink.active.is_(True),
        )
        .first()
    )
    if not link:
        raise ValueError("Member is not linked to this cell")

    link.active = False
    link.end_date = end_date or date.today()
    db.commit()
    db.refresh(link)
    return link


def update_member_link(
    db: Session,
    tenant_id: int,
    *,
    cell_id: int,
    member_id: int,
    start_date: Optional[date] = None,
) -> CellMemberLink:
    link = (
        db.query(CellMemberLink)
        .filter(
            CellMemberLink.tenant_id == tenant_id,
            CellMemberLink.cell_id == cell_id,
            CellMemberLink.member_id == member_id,
            CellMemberLink.active.is_(True),
        )
        .first()
    )
    if not link:
        raise ValueError("Member is not linked to this cell")
    if start_date is not None:
        link.start_date = start_date
    db.commit()
    db.refresh(link)
    return link


def transfer_member(
    db: Session,
    tenant_id: int,
    *,
    member_id: int,
    target_cell_id: int,
    transfer_date: Optional[date],
    transfer_reason: Optional[str],
) -> CellMemberLink:
    current_link = (
        db.query(CellMemberLink)
        .filter(CellMemberLink.tenant_id == tenant_id, CellMemberLink.member_id == member_id, CellMemberLink.active.is_(True))
        .first()
    )
    if not current_link:
        raise ValueError("Member has no active cell link")
    if current_link.cell_id == target_cell_id:
        raise ValueError("Target cell must be different from current cell")

    effective_date = transfer_date or date.today()
    current_link.active = False
    current_link.end_date = effective_date
    current_link.transfer_reason = transfer_reason

    new_link = CellMemberLink(
        tenant_id=tenant_id,
        cell_id=target_cell_id,
        member_id=member_id,
        start_date=effective_date,
        active=True,
        transfer_reason=transfer_reason,
    )
    db.add(new_link)
    db.commit()
    db.refresh(new_link)
    return new_link


def list_leader_assignments(db: Session, tenant_id: int, cell_id: int) -> list[CellLeaderAssignment]:
    return (
        db.query(CellLeaderAssignment)
        .filter(CellLeaderAssignment.tenant_id == tenant_id, CellLeaderAssignment.cell_id == cell_id)
        .order_by(CellLeaderAssignment.start_date.desc())
        .all()
    )


def assign_leader(
    db: Session,
    tenant_id: int,
    cell_id: int,
    payload: CellLeaderAssignmentCreate,
) -> CellLeaderAssignment:
    if payload.discipler_member_id is not None and payload.discipler_member_id == payload.member_id:
        raise ValueError("Leader cannot be linked to themselves as discipler")

    if payload.is_primary:
        _disable_other_primary_assignments(db, tenant_id, cell_id)

    assignment = CellLeaderAssignment(
        tenant_id=tenant_id,
        cell_id=cell_id,
        member_id=payload.member_id,
        discipler_member_id=payload.discipler_member_id,
        role=payload.role,
        is_primary=payload.is_primary,
        start_date=payload.start_date or date.today(),
        active=True,
    )
    db.add(assignment)

    # Leadership assignment must also exist as an active member link in the same cell.
    active_link = (
        db.query(CellMemberLink)
        .filter(
            CellMemberLink.tenant_id == tenant_id,
            CellMemberLink.cell_id == cell_id,
            CellMemberLink.member_id == payload.member_id,
            CellMemberLink.active.is_(True),
        )
        .first()
    )
    if active_link is None:
        member = get_member(db, payload.member_id, tenant_id)
        link_start_date = payload.start_date or (member.count_start_date if member else None) or date.today()
        db.add(
            CellMemberLink(
                tenant_id=tenant_id,
                cell_id=cell_id,
                member_id=payload.member_id,
                start_date=link_start_date,
                active=True,
            )
        )

    db.commit()
    db.refresh(assignment)
    return assignment


def update_leader_assignment(
    db: Session,
    assignment: CellLeaderAssignment,
    payload: CellLeaderAssignmentUpdate,
) -> CellLeaderAssignment:
    changes = payload.model_dump(exclude_unset=True)
    if "discipler_member_id" in changes:
        discipler_member_id = changes.get("discipler_member_id")
        if discipler_member_id is not None and discipler_member_id == assignment.member_id:
            raise ValueError("Leader cannot be linked to themselves as discipler")

    if changes.get("is_primary") is True:
        _disable_other_primary_assignments(db, assignment.tenant_id, assignment.cell_id, skip_assignment_id=assignment.id)

    for field, value in changes.items():
        setattr(assignment, field, value)

    db.commit()
    db.refresh(assignment)
    return assignment


def delete_leader_assignment(db: Session, assignment: CellLeaderAssignment) -> None:
    db.delete(assignment)
    db.commit()


def get_leader_assignment(db: Session, assignment_id: int, tenant_id: int) -> Optional[CellLeaderAssignment]:
    return (
        db.query(CellLeaderAssignment)
        .filter(CellLeaderAssignment.id == assignment_id, CellLeaderAssignment.tenant_id == tenant_id)
        .first()
    )


def _disable_other_primary_assignments(
    db: Session,
    tenant_id: int,
    cell_id: int,
    skip_assignment_id: Optional[int] = None,
) -> None:
    q = db.query(CellLeaderAssignment).filter(
        CellLeaderAssignment.tenant_id == tenant_id,
        CellLeaderAssignment.cell_id == cell_id,
        CellLeaderAssignment.active.is_(True),
        CellLeaderAssignment.is_primary.is_(True),
    )
    if skip_assignment_id is not None:
        q = q.filter(CellLeaderAssignment.id != skip_assignment_id)

    for row in q.all():
        row.is_primary = False


def list_meetings(
    db: Session,
    tenant_id: int,
    cell_id: int,
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
) -> list[CellMeeting]:
    q = db.query(CellMeeting).filter(CellMeeting.tenant_id == tenant_id, CellMeeting.cell_id == cell_id)
    if start_date:
        q = q.filter(CellMeeting.meeting_date >= start_date)
    if end_date:
        q = q.filter(CellMeeting.meeting_date <= end_date)
    return q.order_by(CellMeeting.meeting_date.desc(), CellMeeting.id.desc()).all()


def get_meeting(db: Session, meeting_id: int, tenant_id: int) -> Optional[CellMeeting]:
    return db.query(CellMeeting).filter(CellMeeting.id == meeting_id, CellMeeting.tenant_id == tenant_id).first()


def create_meeting(db: Session, tenant_id: int, cell_id: int, payload: CellMeetingCreate) -> CellMeeting:
    meeting = CellMeeting(cell_id=cell_id, tenant_id=tenant_id, **payload.model_dump())
    db.add(meeting)
    db.commit()
    db.refresh(meeting)
    return meeting


def update_meeting(db: Session, meeting: CellMeeting, payload: CellMeetingUpdate) -> CellMeeting:
    changes = payload.model_dump(exclude_unset=True)
    for field, value in changes.items():
        setattr(meeting, field, value)
    db.commit()
    db.refresh(meeting)
    return meeting


def upsert_meeting_attendances(
    db: Session,
    tenant_id: int,
    meeting_id: int,
    items: list[CellMeetingAttendanceItem],
) -> list[CellMeetingAttendance]:
    result: list[CellMeetingAttendance] = []
    for item in items:
        existing = (
            db.query(CellMeetingAttendance)
            .filter(
                CellMeetingAttendance.tenant_id == tenant_id,
                CellMeetingAttendance.meeting_id == meeting_id,
                CellMeetingAttendance.member_id == item.member_id,
            )
            .first()
        )
        if existing:
            existing.attendance_status = item.attendance_status
            existing.notes = item.notes
            result.append(existing)
            continue

        row = CellMeetingAttendance(
            tenant_id=tenant_id,
            meeting_id=meeting_id,
            member_id=item.member_id,
            attendance_status=item.attendance_status,
            notes=item.notes,
        )
        db.add(row)
        result.append(row)

    db.commit()
    for row in result:
        db.refresh(row)
    return result


def list_meeting_attendances(db: Session, tenant_id: int, meeting_id: int) -> list[CellMeetingAttendance]:
    return (
        db.query(CellMeetingAttendance)
        .filter(CellMeetingAttendance.tenant_id == tenant_id, CellMeetingAttendance.meeting_id == meeting_id)
        .order_by(CellMeetingAttendance.id.asc())
        .all()
    )


def add_meeting_visitor(
    db: Session,
    tenant_id: int,
    meeting_id: int,
    payload: CellVisitorCreate,
) -> CellMeetingVisitor:
    visitor = (
        db.query(CellVisitor)
        .filter(
            CellVisitor.tenant_id == tenant_id,
            CellVisitor.full_name == payload.full_name,
            CellVisitor.contact == payload.contact,
        )
        .first()
    )
    if visitor is None:
        visitor = CellVisitor(
            tenant_id=tenant_id,
            full_name=payload.full_name,
            contact=payload.contact,
            count_start_date=payload.count_start_date or date.today(),
        )
        db.add(visitor)
        db.flush()

    meeting_visitor = CellMeetingVisitor(
        tenant_id=tenant_id,
        meeting_id=meeting_id,
        visitor_id=visitor.id,
        is_first_time=payload.is_first_time,
        notes=payload.notes,
    )
    db.add(meeting_visitor)
    db.commit()
    db.refresh(meeting_visitor)
    return meeting_visitor


def list_meeting_visitors(db: Session, tenant_id: int, meeting_id: int) -> list[CellMeetingVisitor]:
    return (
        db.query(CellMeetingVisitor)
        .filter(CellMeetingVisitor.tenant_id == tenant_id, CellMeetingVisitor.meeting_id == meeting_id)
        .order_by(CellMeetingVisitor.id.asc())
        .all()
    )


def get_cells_summary(
    db: Session,
    tenant_id: int,
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
    allowed_cell_ids: Optional[list[int]] = None,
) -> list[dict]:
    cells = list_cells(db, tenant_id=tenant_id, allowed_cell_ids=allowed_cell_ids)
    rows: list[dict] = []
    for cell in cells:
        active_members = (
            db.query(CellMemberLink)
            .filter(CellMemberLink.cell_id == cell.id, CellMemberLink.active.is_(True))
            .count()
        )

        meetings_q = db.query(CellMeeting).filter(CellMeeting.cell_id == cell.id)
        if start_date:
            meetings_q = meetings_q.filter(CellMeeting.meeting_date >= start_date)
        if end_date:
            meetings_q = meetings_q.filter(CellMeeting.meeting_date <= end_date)
        meetings = meetings_q.all()
        meeting_ids = [m.id for m in meetings]

        present_total = 0
        visitors_count = 0
        if meeting_ids:
            present_total = (
                db.query(CellMeetingAttendance)
                .filter(
                    CellMeetingAttendance.meeting_id.in_(meeting_ids),
                    CellMeetingAttendance.attendance_status == "present",
                )
                .count()
            )
            visitors_count = (
                db.query(CellMeetingVisitor)
                .filter(CellMeetingVisitor.meeting_id.in_(meeting_ids))
                .count()
            )

        denominator = len(meetings) * active_members
        average_frequency_percent = round((present_total / denominator) * 100, 2) if denominator else 0.0

        rows.append(
            {
                "cell_id": cell.id,
                "cell_name": cell.name,
                "active_members": active_members,
                "meetings_count": len(meetings),
                "visitors_count": visitors_count,
                "average_frequency_percent": average_frequency_percent,
            }
        )
    return rows


def get_cell_frequency(
    db: Session,
    cell_id: int,
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
) -> list[dict]:
    tenant_id = db.query(Cell.tenant_id).filter(Cell.id == cell_id).scalar()
    meetings = list_meetings(db, tenant_id, cell_id, start_date=start_date, end_date=end_date) if tenant_id is not None else []
    active_members = (
        db.query(CellMemberLink)
        .filter(CellMemberLink.cell_id == cell_id, CellMemberLink.active.is_(True))
        .count()
    )
    rows: list[dict] = []
    for meeting in meetings:
        present = (
            db.query(CellMeetingAttendance)
            .filter(
                CellMeetingAttendance.meeting_id == meeting.id,
                CellMeetingAttendance.attendance_status == "present",
            )
            .count()
        )
        frequency_percent = round((present / active_members) * 100, 2) if active_members else 0.0
        rows.append(
            {
                "meeting_id": meeting.id,
                "meeting_date": meeting.meeting_date,
                "present": present,
                "active_members": active_members,
                "frequency_percent": frequency_percent,
            }
        )
    return rows


def get_cell_growth(
    db: Session,
    cell_id: int,
    start_date: date,
    end_date: date,
) -> dict:
    new_members = (
        db.query(CellMemberLink)
        .filter(
            CellMemberLink.cell_id == cell_id,
            CellMemberLink.start_date >= start_date,
            CellMemberLink.start_date <= end_date,
        )
        .count()
    )
    retained_members = (
        db.query(CellMemberLink)
        .filter(
            CellMemberLink.cell_id == cell_id,
            CellMemberLink.active.is_(True),
        )
        .count()
    )

    recurrent_visitors = (
        db.query(func.count())
        .select_from(
            db.query(CellMeetingVisitor.visitor_id)
            .join(CellMeeting, CellMeeting.id == CellMeetingVisitor.meeting_id)
            .filter(
                CellMeeting.cell_id == cell_id,
                CellMeeting.meeting_date >= start_date,
                CellMeeting.meeting_date <= end_date,
            )
            .group_by(CellMeetingVisitor.visitor_id)
            .having(func.count(CellMeetingVisitor.id) > 1)
            .subquery()
        )
        .scalar()
    )

    return {
        "cell_id": cell_id,
        "period_start": start_date,
        "period_end": end_date,
        "new_members": new_members,
        "retained_members": retained_members,
        "recurrent_visitors": int(recurrent_visitors or 0),
    }


def get_cell_retention(
    db: Session,
    cell_id: int,
    start_date: date,
    end_date: date,
) -> dict:
    active_start_rows = (
        db.query(CellMemberLink.member_id)
        .filter(
            CellMemberLink.cell_id == cell_id,
            CellMemberLink.start_date <= start_date,
            (CellMemberLink.end_date.is_(None)) | (CellMemberLink.end_date >= start_date),
        )
        .all()
    )
    active_end_rows = (
        db.query(CellMemberLink.member_id)
        .filter(
            CellMemberLink.cell_id == cell_id,
            CellMemberLink.start_date <= end_date,
            (CellMemberLink.end_date.is_(None)) | (CellMemberLink.end_date >= end_date),
        )
        .all()
    )

    active_start = {row.member_id for row in active_start_rows}
    active_end = {row.member_id for row in active_end_rows}
    retained = active_start.intersection(active_end)
    rate = round((len(retained) / len(active_start)) * 100, 2) if active_start else 0.0

    return {
        "cell_id": cell_id,
        "period_start": start_date,
        "period_end": end_date,
        "active_at_start": len(active_start),
        "active_at_end": len(active_end),
        "retained_members": len(retained),
        "retention_rate_percent": rate,
    }


def get_cell_recurring_visitors(
    db: Session,
    cell_id: int,
    start_date: date,
    end_date: date,
) -> dict:
    external_rows = (
        db.query(
            CellVisitor.id.label("visitor_id"),
            CellVisitor.full_name.label("full_name"),
            CellVisitor.contact.label("contact"),
            func.count(CellMeetingVisitor.id).label("visits_count"),
        )
        .join(CellMeetingVisitor, CellMeetingVisitor.visitor_id == CellVisitor.id)
        .join(CellMeeting, CellMeeting.id == CellMeetingVisitor.meeting_id)
        .filter(
            CellMeeting.cell_id == cell_id,
            CellMeeting.meeting_date >= start_date,
            CellMeeting.meeting_date <= end_date,
        )
        .group_by(CellVisitor.id, CellVisitor.full_name, CellVisitor.contact)
        .having(func.count(CellMeetingVisitor.id) > 1)
        .all()
    )

    stage_normalized = func.lower(func.trim(CellMember.stage))
    member_rows = (
        db.query(
            CellMember.id.label("member_id"),
            CellMember.full_name.label("full_name"),
            CellMember.contact.label("contact"),
            func.count(CellMeetingAttendance.id).label("visits_count"),
        )
        .join(CellMeetingAttendance, CellMeetingAttendance.member_id == CellMember.id)
        .join(CellMeeting, CellMeeting.id == CellMeetingAttendance.meeting_id)
        .filter(
            CellMeeting.cell_id == cell_id,
            CellMeeting.meeting_date >= start_date,
            CellMeeting.meeting_date <= end_date,
            CellMeetingAttendance.attendance_status == "present",
            stage_normalized.in_(["visitor", "visitante"]),
        )
        .group_by(CellMember.id, CellMember.full_name, CellMember.contact)
        .having(func.count(CellMeetingAttendance.id) > 1)
        .all()
    )

    external_visitors = [
        {
            "visitor_id": row.visitor_id,
            "full_name": row.full_name,
            "contact": row.contact,
            "visits_count": int(row.visits_count),
        }
        for row in external_rows
    ]

    member_visitors = [
        {
            # Keep IDs unique vs external visitors while preserving int schema.
            "visitor_id": -int(row.member_id),
            "full_name": row.full_name,
            "contact": row.contact,
            "visits_count": int(row.visits_count),
        }
        for row in member_rows
    ]

    visitors = sorted(
        external_visitors + member_visitors,
        key=lambda item: (-int(item["visits_count"]), str(item["full_name"] or "").lower()),
    )

    return {
        "cell_id": cell_id,
        "period_start": start_date,
        "period_end": end_date,
        "total_recurring_visitors": len(visitors),
        "visitors": visitors,
    }


def get_cell_history(
    db: Session,
    cell_id: int,
    months: int = 6,
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
) -> list[dict]:
    if start_date and end_date:
        start_anchor = date(start_date.year, start_date.month, 1)
        end_anchor = date(end_date.year, end_date.month, 1)
        span_months = ((end_anchor.year - start_anchor.year) * 12) + (end_anchor.month - start_anchor.month) + 1
        safe_months = max(1, min(span_months, 24))
        start_year = end_anchor.year
        start_month = end_anchor.month - (safe_months - 1)
        while start_month <= 0:
            start_month += 12
            start_year -= 1
    else:
        safe_months = max(1, min(months, 24))
        today = date.today()
        start_year = today.year
        start_month = today.month - (safe_months - 1)
        while start_month <= 0:
            start_month += 12
            start_year -= 1

    rows: list[dict] = []
    year = start_year
    month = start_month
    for _ in range(safe_months):
        first_day = date(year, month, 1)
        last_day = date(year, month, monthrange(year, month)[1])

        meetings = (
            db.query(CellMeeting)
            .filter(
                CellMeeting.cell_id == cell_id,
                CellMeeting.meeting_date >= first_day,
                CellMeeting.meeting_date <= last_day,
            )
            .all()
        )
        meeting_ids = [m.id for m in meetings]

        presents_count = 0
        visitors_count = 0
        if meeting_ids:
            presents_count = (
                db.query(CellMeetingAttendance)
                .filter(
                    CellMeetingAttendance.meeting_id.in_(meeting_ids),
                    CellMeetingAttendance.attendance_status == "present",
                )
                .count()
            )
            visitors_count = (
                db.query(CellMeetingVisitor)
                .filter(CellMeetingVisitor.meeting_id.in_(meeting_ids))
                .count()
            )

        new_members = (
            db.query(CellMemberLink)
            .filter(
                CellMemberLink.cell_id == cell_id,
                CellMemberLink.start_date >= first_day,
                CellMemberLink.start_date <= last_day,
            )
            .count()
        )
        active_members = (
            db.query(CellMemberLink)
            .filter(
                CellMemberLink.cell_id == cell_id,
                CellMemberLink.start_date <= last_day,
                (CellMemberLink.end_date.is_(None)) | (CellMemberLink.end_date >= first_day),
            )
            .count()
        )
        denominator = len(meetings) * active_members
        avg_freq = round((presents_count / denominator) * 100, 2) if denominator else 0.0

        rows.append(
            {
                "month": f"{year:04d}-{month:02d}",
                "meetings_count": len(meetings),
                "presents_count": presents_count,
                "visitors_count": visitors_count,
                "new_members_count": new_members,
                "average_frequency_percent": avg_freq,
            }
        )

        month += 1
        if month > 12:
            month = 1
            year += 1

    return rows


def get_cell_dashboard_insights(
    db: Session,
    cell_id: int,
    start_date: date,
    end_date: date,
) -> dict:
    stage_normalized = func.lower(func.trim(CellMember.stage))

    meetings = (
        db.query(CellMeeting)
        .filter(
            CellMeeting.cell_id == cell_id,
            CellMeeting.meeting_date >= start_date,
            CellMeeting.meeting_date <= end_date,
        )
        .order_by(CellMeeting.meeting_date.asc())
        .all()
    )

    meeting_ids = [meeting.id for meeting in meetings]
    meetings_count = len(meetings)

    total_visitors = 0
    present_total = 0
    low_frequency_meetings_count = 0
    if meeting_ids:
        external_visitors_total = (
            db.query(CellMeetingVisitor)
            .filter(CellMeetingVisitor.meeting_id.in_(meeting_ids))
            .count()
        )

        visitor_members_total = (
            db.query(CellMeetingAttendance)
            .join(CellMeeting, CellMeeting.id == CellMeetingAttendance.meeting_id)
            .join(CellMember, CellMember.id == CellMeetingAttendance.member_id)
            .filter(
                CellMeetingAttendance.meeting_id.in_(meeting_ids),
                CellMeetingAttendance.attendance_status == "present",
                stage_normalized.in_(["visitor", "visitante"]),
                CellMember.count_start_date <= CellMeeting.meeting_date,
            )
            .count()
        )
        total_visitors = external_visitors_total + visitor_members_total

        present_total = (
            db.query(CellMeetingAttendance)
            .filter(
                CellMeetingAttendance.meeting_id.in_(meeting_ids),
                CellMeetingAttendance.attendance_status == "present",
            )
            .count()
        )

    assiduous_members_count = (
        db.query(CellMember)
        .join(CellMemberLink, CellMemberLink.member_id == CellMember.id)
        .filter(
            CellMemberLink.cell_id == cell_id,
            CellMemberLink.active.is_(True),
            CellMember.stage == "assiduo",
            CellMember.count_start_date <= end_date,
        )
        .count()
    )

    active_members = (
        db.query(CellMemberLink)
        .filter(CellMemberLink.cell_id == cell_id, CellMemberLink.active.is_(True))
        .count()
    )

    denominator = meetings_count * active_members
    member_frequency_percent = round((present_total / denominator) * 100, 2) if denominator else 0.0
    visitors_average_per_meeting = round((total_visitors / meetings_count), 2) if meetings_count else 0.0

    if meetings_count and active_members:
        for meeting in meetings:
            present_for_meeting = (
                db.query(CellMeetingAttendance)
                .filter(
                    CellMeetingAttendance.meeting_id == meeting.id,
                    CellMeetingAttendance.attendance_status == "present",
                )
                .count()
            )
            frequency_percent = (present_for_meeting / active_members) * 100
            if frequency_percent < 70:
                low_frequency_meetings_count += 1

    weeks_without_reports: list[dict] = []
    week_start = start_date - timedelta(days=start_date.weekday())
    while week_start <= end_date:
        week_end = min(week_start + timedelta(days=6), end_date)
        has_meeting = any(week_start <= meeting.meeting_date <= week_end for meeting in meetings)
        if not has_meeting:
            weeks_without_reports.append({"week_start": week_start, "week_end": week_end})
        week_start += timedelta(days=7)

    return {
        "cell_id": cell_id,
        "period_start": start_date,
        "period_end": end_date,
        "meetings_count": meetings_count,
        "total_visitors": total_visitors,
        "member_frequency_percent": member_frequency_percent,
        "assiduous_members_count": assiduous_members_count,
        "visitors_average_per_meeting": visitors_average_per_meeting,
        "low_frequency_meetings_count": low_frequency_meetings_count,
        "weeks_without_reports_count": len(weeks_without_reports),
        "weeks_without_reports": weeks_without_reports,
    }


def get_cell_dashboard_charts(
    db: Session,
    cell_id: int,
    start_date: date,
    end_date: date,
) -> dict:
    meetings = (
        db.query(CellMeeting)
        .filter(
            CellMeeting.cell_id == cell_id,
            CellMeeting.meeting_date >= start_date,
            CellMeeting.meeting_date <= end_date,
        )
        .order_by(CellMeeting.meeting_date.asc())
        .all()
    )

    meeting_ids = [meeting.id for meeting in meetings]

    stage_normalized = func.lower(func.trim(CellMember.stage))

    visitors_count_by_meeting_id = {}
    if meeting_ids:
        external_visitors_rows = (
            db.query(
                CellMeetingVisitor.meeting_id,
                func.count(CellMeetingVisitor.id).label("visitors_count"),
            )
            .join(CellVisitor, CellVisitor.id == CellMeetingVisitor.visitor_id)
            .filter(CellMeetingVisitor.meeting_id.in_(meeting_ids))
            .join(CellMeeting, CellMeeting.id == CellMeetingVisitor.meeting_id)
            .filter(CellVisitor.count_start_date <= CellMeeting.meeting_date)
            .group_by(CellMeetingVisitor.meeting_id)
            .all()
        )
        visitors_count_by_meeting_id = {
            int(row.meeting_id): int(row.visitors_count)
            for row in external_visitors_rows
        }

        visitor_members_rows = (
            db.query(
                CellMeetingAttendance.meeting_id,
                func.count(func.distinct(CellMeetingAttendance.member_id)).label("visitors_count"),
            )
            .join(CellMeeting, CellMeeting.id == CellMeetingAttendance.meeting_id)
            .join(CellMember, CellMember.id == CellMeetingAttendance.member_id)
            .filter(
                CellMeetingAttendance.meeting_id.in_(meeting_ids),
                CellMeetingAttendance.attendance_status == "present",
                stage_normalized.in_(["visitor", "visitante"]),
                CellMember.count_start_date <= CellMeeting.meeting_date,
            )
            .group_by(CellMeetingAttendance.meeting_id)
            .all()
        )

        for row in visitor_members_rows:
            meeting_id = int(row.meeting_id)
            visitors_count_by_meeting_id[meeting_id] = visitors_count_by_meeting_id.get(meeting_id, 0) + int(row.visitors_count)

    visitors_by_date: list[dict] = []
    visitors_by_day_index: dict[date, int] = {}
    for meeting in meetings:
        visitors_for_meeting = visitors_count_by_meeting_id.get(int(meeting.id), 0)
        visitors_by_day_index[meeting.meeting_date] = visitors_by_day_index.get(meeting.meeting_date, 0) + visitors_for_meeting

    for meeting_date in sorted(visitors_by_day_index.keys()):
        visitors_by_date.append(
            {
                "date": meeting_date,
                "visitors_count": visitors_by_day_index[meeting_date],
            }
        )

    weekly_presence: list[dict] = []
    for meeting in meetings:
        present_total = (
            db.query(func.count(CellMeetingAttendance.id))
            .filter(
                CellMeetingAttendance.meeting_id == meeting.id,
                CellMeetingAttendance.attendance_status == "present",
            )
            .scalar()
        ) or 0

        absent_total = (
            db.query(func.count(CellMeetingAttendance.id))
            .filter(
                CellMeetingAttendance.meeting_id == meeting.id,
                CellMeetingAttendance.attendance_status == "absent",
            )
            .scalar()
        ) or 0

        justified_total = (
            db.query(func.count(CellMeetingAttendance.id))
            .filter(
                CellMeetingAttendance.meeting_id == meeting.id,
                CellMeetingAttendance.attendance_status == "justified",
            )
            .scalar()
        ) or 0

        expected_total = int(present_total) + int(absent_total) + int(justified_total)

        weekly_presence.append(
            {
                "week_start": meeting.meeting_date,
                "week_end": meeting.meeting_date,
                "present_total": int(present_total),
                "absent_total": int(absent_total),
                "justified_total": int(justified_total),
                "expected_total": expected_total,
            }
        )

    stage_counts_by_date: list[dict] = []
    for meeting in meetings:
        visitors_count = (
            db.query(func.count(func.distinct(CellMember.id)))
            .join(CellMemberLink, CellMemberLink.member_id == CellMember.id)
            .filter(
                CellMemberLink.cell_id == cell_id,
                CellMemberLink.start_date <= meeting.meeting_date,
                (CellMemberLink.end_date.is_(None)) | (CellMemberLink.end_date >= meeting.meeting_date),
                CellMember.status == "active",
                CellMember.is_active.is_(True),
                stage_normalized.in_(["visitor", "visitante"]),
                CellMember.count_start_date <= meeting.meeting_date,
            )
            .scalar()
        ) or 0

        members_count = (
            db.query(func.count(func.distinct(CellMember.id)))
            .join(CellMemberLink, CellMemberLink.member_id == CellMember.id)
            .filter(
                CellMemberLink.cell_id == cell_id,
                CellMemberLink.start_date <= meeting.meeting_date,
                (CellMemberLink.end_date.is_(None)) | (CellMemberLink.end_date >= meeting.meeting_date),
                CellMember.status == "active",
                CellMember.is_active.is_(True),
                stage_normalized.in_(["member", "membro"]),
                CellMember.count_start_date <= meeting.meeting_date,
            )
            .scalar()
        ) or 0

        assiduous_count = (
            db.query(func.count(func.distinct(CellMember.id)))
            .join(CellMemberLink, CellMemberLink.member_id == CellMember.id)
            .filter(
                CellMemberLink.cell_id == cell_id,
                CellMemberLink.start_date <= meeting.meeting_date,
                (CellMemberLink.end_date.is_(None)) | (CellMemberLink.end_date >= meeting.meeting_date),
                CellMember.status == "active",
                CellMember.is_active.is_(True),
                stage_normalized.in_(["assiduo", "assíduo", "assidua", "assídua"]),
                CellMember.count_start_date <= meeting.meeting_date,
            )
            .scalar()
        ) or 0

        stage_counts_by_date.append(
            {
                "date": meeting.meeting_date,
                "visitors_count": int(visitors_count),
                "members_count": int(members_count),
                "assiduous_count": int(assiduous_count),
            }
        )

    visitor_retention = [
        {"bucket_label": "1x", "visitors_count": 0},
        {"bucket_label": "2x", "visitors_count": 0},
        {"bucket_label": "3x", "visitors_count": 0},
        {"bucket_label": "4x+", "visitors_count": 0},
    ]
    if meeting_ids:
        visits_per_visitor = (
            db.query(
                CellMeetingVisitor.visitor_id,
                func.count(CellMeetingVisitor.id).label("visits_count"),
            )
            .join(CellVisitor, CellVisitor.id == CellMeetingVisitor.visitor_id)
            .join(CellMeeting, CellMeeting.id == CellMeetingVisitor.meeting_id)
            .filter(CellMeetingVisitor.meeting_id.in_(meeting_ids))
            .filter(CellVisitor.count_start_date <= CellMeeting.meeting_date)
            .group_by(CellMeetingVisitor.visitor_id)
            .all()
        )

        for row in visits_per_visitor:
            visits = int(row.visits_count)
            if visits <= 1:
                visitor_retention[0]["visitors_count"] += 1
            elif visits == 2:
                visitor_retention[1]["visitors_count"] += 1
            elif visits == 3:
                visitor_retention[2]["visitors_count"] += 1
            else:
                visitor_retention[3]["visitors_count"] += 1

        visits_per_visitor_member = (
            db.query(
                CellMeetingAttendance.member_id,
                func.count(CellMeetingAttendance.id).label("visits_count"),
            )
            .join(CellMeeting, CellMeeting.id == CellMeetingAttendance.meeting_id)
            .join(CellMember, CellMember.id == CellMeetingAttendance.member_id)
            .filter(
                CellMeetingAttendance.meeting_id.in_(meeting_ids),
                CellMeetingAttendance.attendance_status == "present",
                stage_normalized.in_(["visitor", "visitante"]),
                CellMember.count_start_date <= CellMeeting.meeting_date,
            )
            .group_by(CellMeetingAttendance.member_id)
            .all()
        )

        for row in visits_per_visitor_member:
            visits = int(row.visits_count)
            if visits <= 1:
                visitor_retention[0]["visitors_count"] += 1
            elif visits == 2:
                visitor_retention[1]["visitors_count"] += 1
            elif visits == 3:
                visitor_retention[2]["visitors_count"] += 1
            else:
                visitor_retention[3]["visitors_count"] += 1

    unique_external_visitors_count = 0
    if meeting_ids:
        unique_external_visitors_count = (
            db.query(func.count(func.distinct(CellMeetingVisitor.visitor_id)))
            .join(CellVisitor, CellVisitor.id == CellMeetingVisitor.visitor_id)
            .join(CellMeeting, CellMeeting.id == CellMeetingVisitor.meeting_id)
            .filter(CellMeetingVisitor.meeting_id.in_(meeting_ids))
            .filter(CellVisitor.count_start_date <= CellMeeting.meeting_date)
            .scalar()
        ) or 0

    unique_visitor_members_present_count = (
        db.query(func.count(func.distinct(CellMeetingAttendance.member_id)))
        .join(CellMeeting, CellMeeting.id == CellMeetingAttendance.meeting_id)
        .join(CellMember, CellMember.id == CellMeetingAttendance.member_id)
        .filter(
            CellMeeting.cell_id == cell_id,
            CellMeeting.meeting_date >= start_date,
            CellMeeting.meeting_date <= end_date,
            CellMeetingAttendance.attendance_status == "present",
            stage_normalized.in_(["visitor", "visitante"]),
            CellMember.count_start_date <= CellMeeting.meeting_date,
        )
        .scalar()
    ) or 0

    unique_members_present_count = (
        db.query(func.count(func.distinct(CellMeetingAttendance.member_id)))
        .join(CellMeeting, CellMeeting.id == CellMeetingAttendance.meeting_id)
        .join(CellMember, CellMember.id == CellMeetingAttendance.member_id)
        .filter(
            CellMeeting.cell_id == cell_id,
            CellMeeting.meeting_date >= start_date,
            CellMeeting.meeting_date <= end_date,
            CellMeetingAttendance.attendance_status == "present",
            stage_normalized.in_(["member", "membro"]),
            CellMember.count_start_date <= CellMeeting.meeting_date,
        )
        .scalar()
    ) or 0

    unique_assiduous_present_count = (
        db.query(func.count(func.distinct(CellMeetingAttendance.member_id)))
        .join(CellMeeting, CellMeeting.id == CellMeetingAttendance.meeting_id)
        .join(CellMember, CellMember.id == CellMeetingAttendance.member_id)
        .filter(
            CellMeeting.cell_id == cell_id,
            CellMeeting.meeting_date >= start_date,
            CellMeeting.meeting_date <= end_date,
            CellMeetingAttendance.attendance_status == "present",
            stage_normalized.in_(["assiduo", "assíduo", "assidua", "assídua"]),
            CellMember.count_start_date <= CellMeeting.meeting_date,
        )
        .scalar()
    ) or 0

    composition_raw = [
        ("Visitantes", int(unique_external_visitors_count) + int(unique_visitor_members_present_count)),
        ("Membros", int(unique_members_present_count)),
        ("Assiduos", int(unique_assiduous_present_count)),
    ]
    total_composition = sum(item[1] for item in composition_raw)
    composition = [
        {
            "label": label,
            "count": count,
            "percent": round((count / total_composition) * 100, 2) if total_composition else 0.0,
        }
        for label, count in composition_raw
    ]

    return {
        "cell_id": cell_id,
        "period_start": start_date,
        "period_end": end_date,
        "visitors_by_date": visitors_by_date,
        "weekly_presence": weekly_presence,
        "visitor_retention": visitor_retention,
        "composition": composition,
        "stage_counts_by_date": stage_counts_by_date,
    }
