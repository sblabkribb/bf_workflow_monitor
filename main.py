import json
import sys
from pathlib import Path
from typing import List, Dict, Any
from flask import Flask, jsonify, render_template
from flask_cors import CORS

from src.models.experiment import Experiment
from src.parsers.readme_parser import ReadmeParser
from src.parsers.workflow_parser import WorkflowParser
from src.utils.status_calculator import StatusCalculator
from src.models.gantt_chart_visualizer import MermaidGanttChartVisualizer
from src.models.workflow_template_visualizer import WorkflowTemplateVisualizer

# 프로젝트 루트를 sys.path에 추가하여 모듈을 찾을 수 있도록 함
sys.path.append(str(Path(__file__).resolve().parent))

class LabnoteMonitor:
    """
    Labnote 디렉토리를 모니터링하고 파싱하는 클래스.
    웹 애플리케이션의 어느 곳에서나 재사용될 수 있도록 분리.
    """
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

app = Flask(__name__, template_folder='templates')
# CORS(Cross-Origin Resource Sharing) 설정
# '/api/'로 시작하는 모든 경로에 대해 모든 도메인에서의 요청을 허용합니다.
# React 개발 서버(보통 localhost:3000)에서 API를 호출하기 위해 필요합니다.
CORS(app, resources={r"/api/*": {"origins": "*"}})
labnote_path = Path("./labnote")
monitor = LabnoteMonitor(labnote_path)

def get_monitor_data() -> Dict[str, Any]:
    """Helper function to get parsed data and visualizations."""
    parsed_experiments = monitor.monitor()

    # 1. JSON 데이터 생성
    try:
        results = [exp.model_dump(exclude_none=True) for exp in parsed_experiments]
    except AttributeError:
        results = [exp.dict(exclude_none=True) for exp in parsed_experiments]
    json_output = json.dumps(results, indent=2, default=str, ensure_ascii=False)

    # 2. 시각화 마크다운 생성
    template_visualizer = WorkflowTemplateVisualizer()
    flowchart_md = template_visualizer.generate_flowchart(parsed_experiments)

    gantt_visualizer = MermaidGanttChartVisualizer()
    gantt_chart_md = gantt_visualizer.generate_charts(parsed_experiments)

    return {
        "json_data": json_output,
        "flowchart_md": flowchart_md,
        "gantt_chart_md": gantt_chart_md,
        "raw_json": results
    }

@app.route('/')
def index():
    """메인 대시보드 페이지를 렌더링합니다."""
    data = get_monitor_data()
    return render_template(
        'index.html',
        json_data=data["json_data"],
        flowchart_md=data["flowchart_md"],
        gantt_chart_md=data["gantt_chart_md"]
    )

@app.route('/api/experiments')
def get_experiments_api():
    """파싱된 실험 데이터를 JSON API로 제공합니다."""
    data = get_monitor_data()
    return jsonify(data["raw_json"])

if __name__ == "__main__":
    # host='0.0.0.0'으로 설정하면 외부에서도 접속 가능합니다.
    # debug=True 모드는 개발 중에 유용하며, 코드 변경 시 서버가 자동으로 재시작됩니다.
    app.run(host='127.0.0.1', port=5001, debug=True)