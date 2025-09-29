from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import date
from .unit_operation import UnitOperation

class Workflow(BaseModel):
    """워크플로우 모델"""
    file_name: str
    title: str
    status: str = "Planned" # Planned, In Progress, Completed
    created_date: Optional[date] = None
    last_updated_date: Optional[date] = None
    unit_operations: List[UnitOperation] = Field(default_factory=list)