import json
import sys
from pathlib import Path
from typing import List

from src.models.experiment import Experiment
from src.parsers.readme_parser import ReadmeParser
from src.parsers.workflow_parser import WorkflowParser
from src.utils.status_calculator import StatusCalculator
# visualizer 파일이 models 폴더에 있으므로 경로를 수정합니다. (이전 수정 유지)
from src.models.gantt_chart_visualizer import MermaidGanttChartVisualizer 

# 프로젝트 루트를 sys.path에 추가하여 모듈을 찾을 수 있도록 함
sys.path.append(str(Path(__file__).resolve().parent))

class LabnoteMonitor:
    def __init__(self, root_dir: Path):
        self.root_dir = root_dir

    def monitor(self) -> List[Experiment]:
        """지정된 폴더 내의 모든 실험 노트를 파싱하고 집계합니다."""
        experiment_folders = [
            f for f in self.root_dir.iterdir()
            if f.is_dir() and f.name and f.name[0].isdigit()
        ]

        experiments = []
        for exp_folder in experiment_folders:
            readme_path = exp_folder / "README.md"
            if not readme_path.exists():
                continue

            # 1. README.md 파싱하여 실험 기본 정보 및 워크플로우 목록 생성
            experiment = ReadmeParser(readme_path, exp_folder).parse()

            # 2. 각 워크플로우 파일 파싱 및 UO 정보 채우기
            for workflow in experiment.workflows:
                workflow_path = exp_folder / workflow.file_name
                if workflow_path.exists():
                    # 워크플로우 파서로부터 메타데이터와 UO 리스트를 받음
                    wf_metadata, parsed_uo_list = WorkflowParser(workflow_path).parse()
                    workflow.unit_operations = parsed_uo_list
                    # 파싱된 메타데이터로 워크플로우 정보 업데이트
                    workflow.title = wf_metadata.get("title", workflow.title)
                    workflow.created_date = wf_metadata.get("created_date")
                    workflow.last_updated_date = wf_metadata.get("last_updated_date")
                    # 워크플로우 상태 재계산
                    workflow.status = StatusCalculator.calculate_workflow_status(workflow.unit_operations)

            # 3. 실험 전체 상태 재계산
            experiment.status = StatusCalculator.calculate_experiment_status(experiment.workflows)
            experiments.append(experiment)

        return experiments

if __name__ == "__main__":
    # 실제 labnote 폴더 경로를 지정하세요.
    labnote_path = Path("./labnote")
    monitor = LabnoteMonitor(labnote_path)
    parsed_experiments = monitor.monitor()

    # 파싱된 결과를 JSON으로 변환하여 출력
    print("--- 1. Parsed JSON Data ---")
    try:
        # Pydantic v2+
        results = [exp.model_dump(exclude_none=True) for exp in parsed_experiments]
    except AttributeError:
        # Pydantic v1
        results = [exp.dict(exclude_none=True) for exp in parsed_experiments]

    print(json.dumps(results, indent=2, default=str, ensure_ascii=False))

    print("\n\n--- 2. Mermaid.js Gantt Chart Markdown ---")
    # 시각화 인스턴스 생성
    visualizer = MermaidGanttChartVisualizer()

    # 간트 차트 마크다운 생성
    gantt_chart_md = visualizer.generate_charts(parsed_experiments)

    # 결과 출력
    print(gantt_chart_md)

    # 생성된 마크다운을 파일로 저장
    output_md_path = Path("gantt_chart.md")
    output_md_path.write_text(gantt_chart_md, encoding="utf-8")
    print(f"\n--- Gantt chart markdown has been saved to: {output_md_path.resolve()} ---")