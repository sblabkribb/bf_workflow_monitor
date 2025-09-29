from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import date
from .kpi import KPI

class UnitOperation(BaseModel):
    """Unit Operation (UO) 모델"""
    id: str
    name: str
    experimenter: Optional[str] = None
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    status: str = "Planned"  # Planned, In Progress, Completed
    automation_level: int = 0
    kpis: List[KPI] = Field(default_factory=list)
    raw_content: str # 파싱된 원본 마크다운 텍스트