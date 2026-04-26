from datetime import datetime
from typing import Optional

from sqlalchemy.orm import Session

from app.db.models import LostSheep, CellMember, Cell, CellMemberLink


def mark_member_as_lost_sheep(
    db: Session,
    tenant_id: int,
    member_id: int,
    cell_id: int,
    phone_number: str = None,
    observation: str = None,
) -> dict:
    """Mark a member as lost sheep and remove from cell"""
    member = db.query(CellMember).filter(CellMember.id == member_id, CellMember.tenant_id == tenant_id).first()
    if not member:
        raise ValueError(f"Member {member_id} not found")

    cell = db.query(Cell).filter(Cell.id == cell_id, Cell.tenant_id == tenant_id).first()
    if not cell:
        raise ValueError(f"Cell {cell_id} not found")

    # Check if already marked as lost
    existing = db.query(LostSheep).filter(
        LostSheep.tenant_id == tenant_id,
        LostSheep.member_id == member_id,
        LostSheep.re_inserted_date.is_(None)
    ).first()
    if existing:
        raise ValueError(f"Member already marked as lost sheep")

    # Unlink from cell
    link = db.query(CellMemberLink).filter(
        CellMemberLink.tenant_id == tenant_id,
        CellMemberLink.member_id == member_id,
        CellMemberLink.cell_id == cell_id,
        CellMemberLink.active == True
    ).first()
    if link:
        link.active = False
        link.end_date = datetime.utcnow()
        db.add(link)

    # Create lost sheep record
    lost_sheep = LostSheep(
        tenant_id=tenant_id,
        member_id=member_id,
        previous_cell_id=cell_id,
        phone_number=phone_number,
        observation=observation,
        marked_as_lost_date=datetime.utcnow(),
    )
    db.add(lost_sheep)
    db.commit()
    db.refresh(lost_sheep)
    
    return {
        'id': lost_sheep.id,
        'member_id': lost_sheep.member_id,
        'member_name': member.full_name,
        'previous_cell_id': lost_sheep.previous_cell_id,
        'previous_cell_name': cell.name,
        'phone_number': lost_sheep.phone_number,
        'observation': lost_sheep.observation,
        'visit_completed': lost_sheep.visit_completed,
        'visit_date': lost_sheep.visit_date,
        'visit_observation': lost_sheep.visit_observation,
        'marked_as_lost_date': lost_sheep.marked_as_lost_date,
        're_inserted_date': lost_sheep.re_inserted_date,
        'current_cell_id': lost_sheep.current_cell_id,
    }


def list_lost_sheep(db: Session, tenant_id: int, allowed_cell_ids: Optional[list[int]] = None) -> list[dict]:
    """List all active lost sheep (not yet reinserted) with member and cell details"""
    query = db.query(
        LostSheep,
        CellMember.full_name,
        Cell.name.label('cell_name')
    ).join(
        CellMember, LostSheep.member_id == CellMember.id
    ).join(
        Cell, LostSheep.previous_cell_id == Cell.id
    ).filter(
        LostSheep.tenant_id == tenant_id,
        CellMember.tenant_id == tenant_id,
        Cell.tenant_id == tenant_id,
        LostSheep.re_inserted_date.is_(None)
    )
    if allowed_cell_ids is not None:
        if not allowed_cell_ids:
            return []
        query = query.filter(LostSheep.previous_cell_id.in_(allowed_cell_ids))
    results = query.all()
    
    return [
        {
            'id': lost_sheep.id,
            'member_id': lost_sheep.member_id,
            'member_name': member_name,
            'previous_cell_id': lost_sheep.previous_cell_id,
            'previous_cell_name': cell_name,
            'phone_number': lost_sheep.phone_number,
            'observation': lost_sheep.observation,
            'visit_completed': lost_sheep.visit_completed,
            'visit_date': lost_sheep.visit_date,
            'visit_observation': lost_sheep.visit_observation,
            'marked_as_lost_date': lost_sheep.marked_as_lost_date,
            're_inserted_date': lost_sheep.re_inserted_date,
            'current_cell_id': lost_sheep.current_cell_id,
        }
        for lost_sheep, member_name, cell_name in results
    ]


def get_lost_sheep(db: Session, tenant_id: int, lost_sheep_id: int, allowed_cell_ids: Optional[list[int]] = None) -> dict:
    """Get a specific lost sheep record with member and cell details"""
    query = db.query(
        LostSheep,
        CellMember.full_name,
        Cell.name.label('cell_name')
    ).join(
        CellMember, LostSheep.member_id == CellMember.id
    ).join(
        Cell, LostSheep.previous_cell_id == Cell.id
    ).filter(
        LostSheep.tenant_id == tenant_id,
        CellMember.tenant_id == tenant_id,
        Cell.tenant_id == tenant_id,
        LostSheep.id == lost_sheep_id
    )
    if allowed_cell_ids is not None:
        if not allowed_cell_ids:
            return None
        query = query.filter(LostSheep.previous_cell_id.in_(allowed_cell_ids))
    result = query.first()
    
    if not result:
        return None
    
    lost_sheep, member_name, cell_name = result
    return {
        'id': lost_sheep.id,
        'member_id': lost_sheep.member_id,
        'member_name': member_name,
        'previous_cell_id': lost_sheep.previous_cell_id,
        'previous_cell_name': cell_name,
        'phone_number': lost_sheep.phone_number,
        'observation': lost_sheep.observation,
        'visit_completed': lost_sheep.visit_completed,
        'visit_date': lost_sheep.visit_date,
        'visit_observation': lost_sheep.visit_observation,
        'marked_as_lost_date': lost_sheep.marked_as_lost_date,
        're_inserted_date': lost_sheep.re_inserted_date,
        'current_cell_id': lost_sheep.current_cell_id,
    }


def update_lost_sheep_visit(
    db: Session,
    tenant_id: int,
    lost_sheep_id: int,
    visit_date: datetime = None,
    visit_observation: str = None,
) -> dict:
    """Record visit to lost sheep"""
    lost_sheep = db.query(LostSheep).filter(LostSheep.id == lost_sheep_id, LostSheep.tenant_id == tenant_id).first()
    if not lost_sheep:
        raise ValueError(f"Lost sheep record {lost_sheep_id} not found")

    lost_sheep.visit_completed = True
    lost_sheep.visit_date = visit_date or datetime.utcnow()
    lost_sheep.visit_observation = visit_observation
    db.add(lost_sheep)
    db.commit()
    db.refresh(lost_sheep)
    return get_lost_sheep(db, tenant_id, lost_sheep_id)


def reinsert_lost_sheep_into_cell(
    db: Session,
    tenant_id: int,
    lost_sheep_id: int,
    target_cell_id: int,
) -> dict:
    """Reinsert lost sheep back into a cell"""
    lost_sheep = db.query(LostSheep).filter(LostSheep.id == lost_sheep_id, LostSheep.tenant_id == tenant_id).first()
    if not lost_sheep:
        raise ValueError(f"Lost sheep record {lost_sheep_id} not found")

    cell = db.query(Cell).filter(Cell.id == target_cell_id, Cell.tenant_id == tenant_id).first()
    if not cell:
        raise ValueError(f"Cell {target_cell_id} not found")

    # Create new link to cell
    link = CellMemberLink(
        tenant_id=tenant_id,
        member_id=lost_sheep.member_id,
        cell_id=target_cell_id,
        active=True,
    )
    db.add(link)

    # Update lost sheep record
    lost_sheep.re_inserted_date = datetime.utcnow()
    lost_sheep.current_cell_id = target_cell_id
    db.add(lost_sheep)
    db.commit()
    db.refresh(lost_sheep)
    return get_lost_sheep(db, tenant_id, lost_sheep_id)


def delete_lost_sheep(db: Session, tenant_id: int, lost_sheep_id: int) -> bool:
    """Delete a lost sheep record (hard delete)"""
    lost_sheep = db.query(LostSheep).filter(LostSheep.id == lost_sheep_id, LostSheep.tenant_id == tenant_id).first()
    if not lost_sheep:
        return False

    db.delete(lost_sheep)
    db.commit()
    return True
