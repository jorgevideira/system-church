from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from datetime import datetime
from app.db.base_class import Base


class LostSheep(Base):
    __tablename__ = "lost_sheep"

    id = Column(Integer, primary_key=True, index=True)
    member_id = Column(Integer, ForeignKey("cell_members.id"), nullable=False, index=True)
    previous_cell_id = Column(Integer, ForeignKey("cells.id"), nullable=False, index=True)
    phone_number = Column(String(20), nullable=True)
    observation = Column(Text, nullable=True)
    visit_completed = Column(Boolean, default=False, nullable=False)
    visit_date = Column(DateTime, nullable=True)
    visit_observation = Column(Text, nullable=True)
    marked_as_lost_date = Column(DateTime, default=datetime.utcnow, nullable=False)
    re_inserted_date = Column(DateTime, nullable=True)
    current_cell_id = Column(Integer, ForeignKey("cells.id"), nullable=True, index=True)

    # Relationships
    member = relationship("CellMember", foreign_keys=[member_id])
    previous_cell = relationship("Cell", foreign_keys=[previous_cell_id])
    current_cell = relationship("Cell", foreign_keys=[current_cell_id])

    def __repr__(self):
        return f"<LostSheep(id={self.id}, member_id={self.member_id}, marked_date={self.marked_as_lost_date})>"
