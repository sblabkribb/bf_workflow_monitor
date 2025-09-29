from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import date
from .workflow import Workflow

class Experiment(BaseModel):
    """최상위 실험 모델"""
    folder_name: str
    title: str
    author: Optional[str] = None
    created_date: Optional[date] = None
    status: str = "Planned" # Planned, In Progress, Completed
    workflows: List[Workflow] = Field(default_factory=list)