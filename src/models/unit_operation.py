from dataclasses import dataclass
from datetime import datetime
from typing import Dict, Optional

@dataclass
class UnitOperation:
    id: str
    name: str
    experimenter: str
    start_date: Optional[datetime]
    end_date: Optional[datetime]
    hw_automation: str
    sw_automation: str
    kpis: Dict[str, float]
    results: str
    
    @property
    def automation_score(self) -> int:
        score = 0
        if self.hw_automation and "Manual" not in self.hw_automation:
            score += 1
        if self.sw_automation and self.sw_automation != "None":
            score += 2
        return score

    @property
    def status(self) -> str:
        if self.end_date and self.results:
            return "Completed"
        elif self.start_date:
            return "In Progress"
        return "Planned"