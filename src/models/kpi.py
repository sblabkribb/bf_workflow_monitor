from pydantic import BaseModel
from typing import Optional

class KPI(BaseModel):
    """Key Performance Indicator 모델"""
    name: str
    value: float
    unit: Optional[str] = None