from datetime import date, datetime
from typing import List, Optional, TYPE_CHECKING

# 순환 참조 방지를 위한 TYPE_CHECKING
if TYPE_CHECKING:
    from ..models.unit_operation import UnitOperation
    from ..models.workflow import Workflow

class StatusCalculator:
    @staticmethod
    def calculate_uo_status(
        start_date: Optional[date],
        end_date: Optional[date],
        results: str,
        placeholder: str = "(여기에 결과가 기록되면 '완료' 상태가 됩니다)"
    ) -> str:
        """Unit Operation의 상태를 계산"""
        # 결과 섹션에 내용이 있고, 그 내용이 플레이스홀더가 아니면 완료로 간주
        has_results = results.strip() and results.strip() != placeholder

        if end_date and has_results:
            return "Completed"
        elif start_date:
            # start_date가 미래 날짜이면 'Planned'
            if start_date > date.today():
                return "Planned"
            return "In Progress"
        return "Planned"

    @staticmethod
    def calculate_workflow_status(unit_operations: List['UnitOperation']) -> str:
        """워크플로우의 전체 상태를 계산"""
        if not unit_operations:
            return "Planned"

        statuses = {uo.status for uo in unit_operations}
        
        if statuses == {"Completed"}:
            return "Completed"
        elif "In Progress" in statuses or ("Planned" in statuses and "Completed" in statuses):
            return "In Progress"
        return "Planned"

    @staticmethod
    def calculate_experiment_status(workflows: List['Workflow']) -> str:
        """실험 전체의 상태를 계산"""
        if not workflows:
            return "Planned"
            
        statuses = {w.status for w in workflows}
        
        if statuses == {"Completed"}:
            return "Completed"
        elif "In Progress" in statuses or ("Planned" in statuses and "Completed" in statuses):
            return "In Progress"
        return "Planned"

    @staticmethod
    def calculate_automation_level(hw_content: str, sw_content: str, uo_name: str) -> int:
        """자동화 수준 점수를 명세서에 따라 계산합니다."""
        if 'manual' in uo_name.lower():
            return 0

        hw_clean = hw_content.strip().lower()
        sw_clean = sw_content.strip().lower()

        has_hw = hw_clean not in ['', 'none', 'manual pipetting']
        has_sw = sw_clean not in ['', 'none']

        if has_hw and has_sw:
            return 3  # HW + SW
        elif has_sw:
            return 2  # SW only
        elif has_hw:
            return 1  # HW only
        return 0      # None or Manual