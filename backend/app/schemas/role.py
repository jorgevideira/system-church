from datetime import datetime
from typing import Optional, List

from pydantic import BaseModel, Field


class PermissionBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    description: Optional[str] = Field(None, max_length=255)
    category: str = Field(..., min_length=1, max_length=50)  # "view", "edit", "delete"
    module: str = Field(..., min_length=1, max_length=50)  # "finance", "cells", "school", "users"
    active: bool = True


class PermissionCreate(PermissionBase):
    pass


class PermissionUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    description: Optional[str] = Field(None, max_length=255)
    category: Optional[str] = Field(None, min_length=1, max_length=50)
    module: Optional[str] = Field(None, min_length=1, max_length=50)
    active: Optional[bool] = None


class PermissionResponse(PermissionBase):
    id: int
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class RoleBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    description: Optional[str] = Field(None, max_length=255)
    is_admin: bool = False
    active: bool = True


class RoleCreate(RoleBase):
    permission_ids: List[int] = Field(default_factory=list)


class RoleUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    description: Optional[str] = Field(None, max_length=255)
    is_admin: Optional[bool] = None
    active: Optional[bool] = None
    permission_ids: Optional[List[int]] = None


class RoleResponse(RoleBase):
    id: int
    permissions: List[PermissionResponse]
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class RoleWithoutPermissions(RoleBase):
    id: int
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}
