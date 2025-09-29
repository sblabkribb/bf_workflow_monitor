
from typing import List, Optional
from ..models.experiment import Experiment

class WorkflowTemplateVisualizer:
    """
    실험 데이터를 기반으로 워크플로 템플릿의 전체 구조를 보여주는
    Mermaid.js 흐름도(flowchart) 마크다운을 생성합니다.
    """

    def generate_flowchart(self, experiments: List[Experiment]) -> str:
        """
        가장 복잡한 실험을 템플릿으로 간주하여 전체 워크플로 흐름도를 생성합니다.
        """
        if not experiments:
            return ""

        # 가장 많은 워크플로우를 가진 실험을 템플릿으로 선택
        template_experiment = max(experiments, key=lambda exp: len(exp.workflows), default=None)

        if not template_experiment or not template_experiment.workflows:
            return ""

        md = []
        md.append("## 🔬 워크플로 템플릿 흐름도")
        md.append(f"> 가장 상세한 워크플로를 가진 '{template_experiment.title}' 실험을 기준으로 생성되었습니다.")
        md.append("```mermaid")
        md.append("graph LR") # Left to Right (왼쪽에서 오른쪽으로)

        # 1. 각 워크플로우(subgraph)와 그 안의 Unit Operation 노드들을 정의
        for i, workflow in enumerate(template_experiment.workflows):
            # Mermaid에서 subgraph ID는 공백이 없어야 함
            subgraph_id = f"wf{i}"
            md.append(f"\n    subgraph {subgraph_id} [\"{workflow.title}\"]")
            
            if workflow.unit_operations:
                # UO들을 순서대로 연결
                node_ids = []
                for j, uo in enumerate(workflow.unit_operations):
                    # 노드 ID는 고유해야 함
                    node_id = f"uo_{i}_{j}"
                    # 노드 텍스트에는 UO의 ID와 이름을 표시
                    node_text = f'\"{uo.id}<br/>{uo.name}\"' 
                    md.append(f"        {node_id}[{node_text}]")
                    node_ids.append(node_id)
                
                # 같은 워크플로우 내의 UO들을 연결
                if len(node_ids) > 1:
                    md.append(f"        {' --> '.join(node_ids)}")

            md.append("    end")

        # 2. 워크플로우(subgraph)들을 순서대로 연결
        workflow_ids = [f"wf{i}" for i in range(len(template_experiment.workflows))]
        if len(workflow_ids) > 1:
            md.append("\n    " + " --> ".join(workflow_ids))

        md.append("```")
        return "\n".join(md)
