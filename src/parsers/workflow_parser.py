import re
from datetime import date, datetime
from pathlib import Path
from typing import List, Optional, Tuple, Dict, Any
import frontmatter
from ..models.unit_operation import UnitOperation
from ..models.kpi import KPI
from ..utils.status_calculator import StatusCalculator

class WorkflowParser:
    def __init__(self, filepath: Path):
        self.filepath = filepath

    def parse(self) -> Tuple[Dict[str, Any], List[UnitOperation]]:
        """워크플로우 파일을 파싱하여 메타데이터와 UnitOperation 리스트를 반환합니다."""
        content = self.filepath.read_text(encoding="utf-8")
        post = frontmatter.loads(content)

        # Parse Unit Operations
        # 실제 파일 형식에 맞게 긴 하이픈 라인을 기준으로 UO 블록 분리
        uo_blocks = re.split(r'\n-{10,}\n', post.content.strip())
        unit_operations = []

        for block in uo_blocks:
            # 블록이 비어있지 않고, UO 헤더 형식을 포함하는 경우에만 파싱
            if block.strip() and '### [' in block:
                unit_operations.append(self._parse_unit_operation(block))

        return post.metadata, unit_operations

    def _parse_unit_operation(self, block: str) -> UnitOperation:
        """하나의 Unit Operation 텍스트 블록을 파싱합니다."""
        # ### 헤더만 UO로 인식하고, ID와 이름을 더 정확하게 추출하도록 수정
        # 이름(name)은 닫는 대괄호 `]` 앞까지의 모든 문자를 포함
        header_match = re.search(r'### \s*\\?\[(.*?)\s([^\]]*)\]', block)

        uo_id, uo_name = (header_match.groups() if header_match else ("UNKNOWN", "Unnamed"))

        meta_content = self._get_section_content(block, "Meta")
        automation_content = self._get_section_content(block, "Automation")
        kpi_content = self._get_section_content(block, "KPI")
        results_content = self._get_section_content(block, "Results & Discussions")

        # Meta 정보 파싱
        exp_match = re.search(r'Experimenter:\s*(.*)', meta_content, re.I)
        start_match = re.search(r'Start_date:\s*(\S*)', meta_content, re.I)
        end_match = re.search(r'End_date:\s*(\S*)', meta_content, re.I)

        start_date = self._to_date(start_match.group(1) if start_match else None)
        end_date = self._to_date(end_match.group(1) if end_match else None)

        # Automation 정보 파싱
        hw_match = re.search(r'HW:\s*(.*)', automation_content, re.I)
        sw_match = re.search(r'SW:\s*(.*)', automation_content, re.I)
        hw_content = hw_match.group(1).strip() if hw_match else ""
        sw_content = sw_match.group(1).strip() if sw_match else ""

        # 상태 및 자동화 수준 계산
        status = StatusCalculator.calculate_uo_status(start_date, end_date, results_content)
        automation_level = StatusCalculator.calculate_automation_level(hw_content, sw_content, uo_name)

        # KPI 파싱
        kpis = self._parse_kpis(kpi_content)

        return UnitOperation(
            id=uo_id,
            name=uo_name,
            experimenter=exp_match.group(1).strip() if exp_match else None,
            start_date=start_date,
            end_date=end_date,
            status=status,
            automation_level=automation_level,
            kpis=kpis,
            raw_content=block
        )

    def _get_section_content(self, block: str, section_name: str) -> str:
        """UO 블록에서 특정 섹션(####)의 내용을 추출합니다."""
        pattern = re.compile(r'####\s+' + re.escape(section_name) + r'\n(.*?)(?=\n####|\Z)', re.DOTALL | re.IGNORECASE)
        match = pattern.search(block)
        return match.group(1).strip() if match else ""

    def _parse_kpis(self, kpi_content: str) -> List[KPI]:
        """KPI 섹션 내용을 파싱하여 KPI 리스트를 반환합니다."""
        kpis = []
        lines = kpi_content.split('\n')
        for line in lines:
            if ':' in line:
                key, value_str = line.split(':', 1)
                key = key.strip('-* ').strip()
                value_str = value_str.strip()

                unit_match = re.search(r'\((.*?)\)', key)
                unit = unit_match.group(1) if unit_match else None
                name = re.sub(r'\s*\(.*?\)\s*', '', key).strip()

                try:
                    value = float(re.match(r'[\d.]+', value_str).group())
                    kpis.append(KPI(name=name, value=value, unit=unit))
                except (ValueError, TypeError, AttributeError):
                    continue
        return kpis

    def _to_date(self, date_str: Optional[str]) -> Optional[date]:
        """문자열을 date 객체로 변환합니다."""
        if not date_str:
            return None
        
        # 작은따옴표 제거 및 시간 정보 제거
        clean_date_str = date_str.strip().strip("'").split(" ")[0]

        try:
            return datetime.strptime(clean_date_str, "%Y-%m-%d").date()
        except ValueError:
            return None