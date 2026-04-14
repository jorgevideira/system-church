from __future__ import annotations

from typing import Optional

from pydantic import BaseModel


class OrgChartMember(BaseModel):
    id: int
    full_name: str
    user_id: Optional[int] = None

    model_config = {"from_attributes": True}


class OrgChartCell(BaseModel):
    id: int
    name: str
    weekday: Optional[str] = None
    meeting_time: Optional[str] = None
    address: Optional[str] = None
    status: Optional[str] = None

    model_config = {"from_attributes": True}


class OrgChartLeaderNode(BaseModel):
    leader: OrgChartMember
    cells: list[OrgChartCell]


class OrgChartDisciplerNode(BaseModel):
    discipler: OrgChartMember
    leaders: list[OrgChartLeaderNode]


class OrgChartNetworkPastorNode(BaseModel):
    network_pastor: Optional[OrgChartMember] = None
    disciplers: list[OrgChartDisciplerNode]


class OrgChartResponse(BaseModel):
    networks: list[OrgChartNetworkPastorNode]

