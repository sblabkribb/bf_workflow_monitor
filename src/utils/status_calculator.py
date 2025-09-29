from datetime import datetime
from typing import List, Optional
from ..models.unit_operation import UnitOperation
from ..models.workflow import Workflow

class StatusCalculator:
    @staticmethod
    def calculate_uo_status(
        start_date: Optional[datetime],
        end_date: Optional[datetime],
        results: str
    ) -> str:
        """Unit Operation의 상태를 계산"""
        if end_date and results:
            return "Completed"
        elif start_date:
            if start_date > datetime.now():
                return "Planned"
            return "In Progress"
        return "Planned"

    @staticmethod
    def calculate_workflow_status(unit_operations: List[UnitOperation]) -> str:
        """워크플로우의 전체 상태를 계산"""
        if not unit_operations:
            return "Planned"

        completed = sum(1 for uo in unit_operations if uo.status == "Completed")
        in_progress = sum(1 for uo in unit_operations if uo.status == "In Progress")
        
        if completed == len(unit_operations):
            return "Completed"
        elif in_progress > 0 or completed > 0:
            return "In Progress"
        return "Planned"

    @staticmethod
    def calculate_experiment_status(workflows: List[Workflow]) -> str:
        """실험 전체의 상태를 계산"""
        if not workflows:
            return "Planned"
            
        completed = sum(1 for w in workflows if w.status == "Completed")
        in_progress = sum(1 for w in workflows if w.status == "In Progress")
        
        if completed == len(workflows):
            return "Completed"
        elif in_progress > 0 or completed > 0:
            return "In Progress"
        return "Planned"

    @staticmethod
    def calculate_automation_score(hw_automation: str, sw_automation: str) -> int:
        """자동화 수준 점수 계산"""
        score = 0
        
        # HW 자동화 점수
        if hw_automation and hw_automation != "None":
            if "Manual" not in hw_automation:
                score += 1
                
        # SW 자동화 점수
        if sw_automation and sw_automation != "None":
            score += 2
            
        return score