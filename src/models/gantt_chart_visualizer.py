from datetime import date
from typing import List
from ..models.experiment import Experiment
from ..models.unit_operation import UnitOperation

class MermaidGanttChartVisualizer:
    """
    파싱된 실험 데이터를 기반으로 Mermaid.js 간트 차트 마크다운을 생성합니다.
    """

    def generate_charts(self, experiments: List[Experiment]) -> str:
        """
        여러 실험에 대한 간트 차트 마크다운을 생성하여 하나의 문자열로 반환합니다.
        """
        all_charts_md = []
        for exp in experiments:
            all_charts_md.append(self._generate_single_chart(exp))
        
        # 각 차트 사이에 두 줄을 띄어 렌더링 시 분리되도록 함
        return "\n\n".join(all_charts_md)

    def _generate_single_chart(self, experiment: Experiment) -> str:
        """단일 실험에 대한 간트 차트 마크다운을 생성합니다."""
        if not any(wf.unit_operations for wf in experiment.workflows):
            return f"## {experiment.title}\n\n(표시할 데이터가 없습니다.)"

        md = []
        md.append("```mermaid")
        md.append("gantt")
        md.append(f"    title {experiment.title} ({experiment.folder_name})")
        md.append("    dateFormat  YYYY-MM-DD")
        md.append("    axisFormat %m-%d") # 축에 월-일만 표시하여 간결하게

        for workflow in experiment.workflows:
            if not workflow.unit_operations:
                continue
            
            md.append(f"\n    section {workflow.title}")
            
            for uo in workflow.unit_operations:
                if not uo.start_date:
                    continue # 시작 날짜가 없는 UO는 간트 차트에 표시하지 않음

                # 상태에 따라 Mermaid 상태 키워드 결정
                status_keyword = ""
                if uo.status == "Completed":
                    status_keyword = "crit, " # crit은 강조 표시
                elif uo.status == "In Progress":
                    status_keyword = "active, "

                # 종료 날짜가 없으면 오늘 날짜로 설정하여 '진행 중'을 표현
                end_date = uo.end_date if uo.end_date else date.today()

                # Mermaid.js에서 오류를 유발할 수 있는 특수문자(콜론 등) 제거
                clean_name = uo.name.replace(":", "")

                # UO 이름이 길 경우를 대비해 잘라내기 (옵션)
                task_name = (clean_name[:25] + '...') if len(clean_name) > 28 else clean_name

                # Mermaid 간트 차트 태스크 라인 생성
                # 포맷: Task Name :[status], [id], startDate, endDate
                md.append(f"    {task_name} :{status_keyword}{uo.id}, {uo.start_date}, {end_date}")

        md.append("```")
        return "\n".join(md)