from dataclasses import dataclass
from datetime import datetime
from typing import List
from .unit_operation import UnitOperation

@dataclass
class Workflow:
    title: str
    experimenter: str
    status: str
    created_date: datetime
    last_updated_date: datetime
    unit_operations: List[UnitOperation]
    
    def calculate_automation_level(self) -> float:
        total_score = 0
        for uo in self.unit_operations:
            total_score += uo.automation_score
        return total_score / len(self.unit_operations) if self.unit_operations else 0