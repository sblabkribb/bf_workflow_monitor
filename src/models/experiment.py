from dataclasses import dataclass
from datetime import datetime
from typing import List
from .workflow import Workflow

@dataclass
class Experiment:
    title: str
    author: str
    status: str
    created_date: datetime
    workflows: List[Workflow]
    
    def calculate_overall_status(self) -> str:
        completed = sum(1 for w in self.workflows if w.status == "Completed")
        if completed == len(self.workflows):
            return "Completed"
        elif completed > 0:
            return "In Progress"
        return "Planned"