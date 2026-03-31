from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class LostSheepBase(BaseModel):
    member_id: int
    previous_cell_id: int
    phone_number: Optional[str] = None
    observation: Optional[str] = None


class LostSheepCreateRequest(BaseModel):
    member_id: int
    cell_id: int
    phone_number: Optional[str] = None
    observation: Optional[str] = None


class LostSheepCreate(LostSheepBase):
    pass


class LostSheepUpdate(BaseModel):
    visit_completed: Optional[bool] = None
    visit_date: Optional[datetime] = None
    visit_observation: Optional[str] = None
    current_cell_id: Optional[int] = None
    re_inserted_date: Optional[datetime] = None


class LostSheepResponse(LostSheepBase):
    id: int
    member_name: Optional[str] = None
    previous_cell_name: Optional[str] = None
    visit_completed: bool
    visit_date: Optional[datetime]
    visit_observation: Optional[str]
    marked_as_lost_date: datetime
    re_inserted_date: Optional[datetime]
    current_cell_id: Optional[int]

    class Config:
        from_attributes = True

    class Config:
        from_attributes = True
