from datetime import date
from calendar import monthrange
from typing import Optional

from sqlalchemy.orm import Session
from sqlalchemy import func

from app.db.models.cell import Cell
from app.db.models.cell_leader_assignment import CellLeaderAssignment
from app.db.models.cell_member import CellMember
from app.db.models.cell_member_link import CellMemberLink
from app.db.models.cell_meeting import CellMeeting
from app.db.models.cell_meeting_attendance import CellMeetingAttendance
from app.db.models.cell_visitor import CellVisitor
from app.db.models.cell_meeting_visitor import CellMeetingVisitor
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


def list_cells(db: Session, status_filter: Optional[str] = None) -> list[Cell]:
    q = db.query(Cell)
    if status_filter:
        q = q.filter(Cell.status == status_filter)
    return q.order_by(Cell.name.asc()).all()


def get_cell(db: Session, cell_id: int) -> Optional[Cell]:
    return db.query(Cell).filter(Cell.id == cell_id).first()


def create_cell(db: Session, payload: CellCreate) -> Cell:
    cell = Cell(**payload.model_dump())
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


def create_member(db: Session, payload: CellMemberCreate) -> CellMember:
    data = payload.model_dump()
    member = CellMember(**data, is_active=(data.get("status", "active") == "active"))
    db.add(member)
    db.commit()
    db.refresh(member)
    return member


def list_members(db: Session, status_filter: Optional[str] = None) -> list[CellMember]:
    q = db.query(CellMember)
    if status_filter:
        q = q.filter(CellMember.status == status_filter)
    return q.order_by(CellMember.full_name.asc()).all()


def get_member(db: Session, member_id: int) -> Optional[CellMember]:
    return db.query(CellMember).filter(CellMember.id == member_id).first()


def update_member(db: Session, member: CellMember, payload: CellMemberUpdate) -> CellMember:
    changes = payload.model_dump(exclude_unset=True)
    if "status" in changes and "is_active" not in changes:
        changes["is_active"] = changes["status"] == "active"
    for field, value in changes.items():
        setattr(member, field, value)
    db.commit()
    db.refresh(member)
    return member


def list_cell_members(db: Session, cell_id: int) -> list[CellMemberLink]:
    return (
        db.query(CellMemberLink)
        .filter(CellMemberLink.cell_id == cell_id, CellMemberLink.active.is_(True))
        .order_by(CellMemberLink.start_date.asc())
        .all()
    )


def assign_member_to_cell(
    db: Session,
    cell_id: int,
    member_id: int,
    start_date: Optional[date] = None,
) -> CellMemberLink:
    current_link = (
        db.query(CellMemberLink)
        .filter(CellMemberLink.member_id == member_id, CellMemberLink.active.is_(True))
        .first()
    )
    if current_link:
        raise ValueError("Member is already linked to an active cell")

    link = CellMemberLink(
        cell_id=cell_id,
        member_id=member_id,
        start_date=start_date or date.today(),
        active=True,
    )
    db.add(link)
    db.commit()
    db.refresh(link)
    return link


def transfer_member(
    db: Session,
    *,
    member_id: int,
    target_cell_id: int,
    transfer_date: Optional[date],
    transfer_reason: Optional[str],
) -> CellMemberLink:
    current_link = (
        db.query(CellMemberLink)
        .filter(CellMemberLink.member_id == member_id, CellMemberLink.active.is_(True))
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


def list_leader_assignments(db: Session, cell_id: int) -> list[CellLeaderAssignment]:
    return (
        db.query(CellLeaderAssignment)
        .filter(CellLeaderAssignment.cell_id == cell_id)
        .order_by(CellLeaderAssignment.start_date.desc())
        .all()
    )


def assign_leader(
    db: Session,
    cell_id: int,
    payload: CellLeaderAssignmentCreate,
) -> CellLeaderAssignment:
    if payload.discipler_member_id is not None and payload.discipler_member_id == payload.member_id:
        raise ValueError("Leader cannot be linked to themselves as discipler")

    if payload.is_primary:
        _disable_other_primary_assignments(db, cell_id)

    assignment = CellLeaderAssignment(
        cell_id=cell_id,
        member_id=payload.member_id,
        discipler_member_id=payload.discipler_member_id,
        role=payload.role,
        is_primary=payload.is_primary,
        start_date=payload.start_date or date.today(),
        active=True,
    )
    db.add(assignment)
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
        _disable_other_primary_assignments(db, assignment.cell_id, skip_assignment_id=assignment.id)

    for field, value in changes.items():
        setattr(assignment, field, value)

    db.commit()
    db.refresh(assignment)
    return assignment



def delete_leader_assignment(db: Session, assignment: CellLeaderAssignment) -> None:
    db.delete(assignment)
    db.commit()


def get_leader_assignment(db: Session, assignment_id: int) -> Optional[CellLeaderAssignment]:
    return db.query(CellLeaderAssignment).filter(CellLeaderAssignment.id == assignment_id).first()


def _disable_other_primary_assignments(
    db: Session,
    cell_id: int,
    skip_assignment_id: Optional[int] = None,
) -> None:
    q = db.query(CellLeaderAssignment).filter(
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
    cell_id: int,
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
) -> list[CellMeeting]:
    q = db.query(CellMeeting).filter(CellMeeting.cell_id == cell_id)
    if start_date:
        q = q.filter(CellMeeting.meeting_date >= start_date)
    if end_date:
        q = q.filter(CellMeeting.meeting_date <= end_date)
    return q.order_by(CellMeeting.meeting_date.desc(), CellMeeting.id.desc()).all()


def get_meeting(db: Session, meeting_id: int) -> Optional[CellMeeting]:
    return db.query(CellMeeting).filter(CellMeeting.id == meeting_id).first()


def create_meeting(db: Session, cell_id: int, payload: CellMeetingCreate) -> CellMeeting:
    meeting = CellMeeting(cell_id=cell_id, **payload.model_dump())
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
    meeting_id: int,
    items: list[CellMeetingAttendanceItem],
) -> list[CellMeetingAttendance]:
    result: list[CellMeetingAttendance] = []
    for item in items:
        existing = (
            db.query(CellMeetingAttendance)
            .filter(
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


def list_meeting_attendances(db: Session, meeting_id: int) -> list[CellMeetingAttendance]:
    return (
        db.query(CellMeetingAttendance)
        .filter(CellMeetingAttendance.meeting_id == meeting_id)
        .order_by(CellMeetingAttendance.id.asc())
        .all()
    )


def add_meeting_visitor(
    db: Session,
    meeting_id: int,
    payload: CellVisitorCreate,
) -> CellMeetingVisitor:
    visitor = (
        db.query(CellVisitor)
        .filter(
            CellVisitor.full_name == payload.full_name,
            CellVisitor.contact == payload.contact,
        )
        .first()
    )
    if visitor is None:
        visitor = CellVisitor(full_name=payload.full_name, contact=payload.contact)
        db.add(visitor)
        db.flush()

    meeting_visitor = CellMeetingVisitor(
        meeting_id=meeting_id,
        visitor_id=visitor.id,
        is_first_time=payload.is_first_time,
        notes=payload.notes,
    )
    db.add(meeting_visitor)
    db.commit()
    db.refresh(meeting_visitor)
    return meeting_visitor


def list_meeting_visitors(db: Session, meeting_id: int) -> list[CellMeetingVisitor]:
    return (
        db.query(CellMeetingVisitor)
        .filter(CellMeetingVisitor.meeting_id == meeting_id)
        .order_by(CellMeetingVisitor.id.asc())
        .all()
    )


def get_cells_summary(
    db: Session,
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
) -> list[dict]:
    cells = list_cells(db)
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
    meetings = list_meetings(db, cell_id, start_date=start_date, end_date=end_date)
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
    rows = (
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
        .order_by(func.count(CellMeetingVisitor.id).desc(), CellVisitor.full_name.asc())
        .all()
    )

    visitors = [
        {
            "visitor_id": row.visitor_id,
            "full_name": row.full_name,
            "contact": row.contact,
            "visits_count": int(row.visits_count),
        }
        for row in rows
    ]
    return {
        "cell_id": cell_id,
        "period_start": start_date,
        "period_end": end_date,
        "total_recurring_visitors": len(visitors),
        "visitors": visitors,
    }


def get_cell_history(db: Session, cell_id: int, months: int = 6) -> list[dict]:
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
