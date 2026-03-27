from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class MinistryBase(BaseModel):
    name: str
    description: Optional[str] = None


class MinistryCreate(MinistryBase):
    pass


class MinistryUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    is_active: Optional[bool] = None


class MinistryResponse(MinistryBase):
    id: int
    is_active: bool
    created_at: datetime

    model_config = {"from_attributes": True}
