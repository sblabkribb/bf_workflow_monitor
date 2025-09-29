import re
from pathlib import Path
import frontmatter
from ..models.experiment import Experiment
from ..models.workflow import Workflow

class ReadmeParser:
    def __init__(self, filepath: Path, exp_folder: Path):
        self.filepath = filepath
        self.exp_folder = exp_folder

    def parse(self) -> Experiment:
        content = self.filepath.read_text(encoding="utf-8")
        post = frontmatter.loads(content)

        # Parse workflow list
        # 정규표현식 수정: `- `가 없는 형식도 지원하도록 `(- )?` 추가
        workflow_lines = re.findall(r'(- )?\[.\]\s\[(.*?)\]\((.*?)\)', post.content)

        workflows = []
        for _, _, file_path in workflow_lines: # 캡처 그룹이 3개로 늘어남
            # 워크플로우 파일의 title은 나중에 workflow_parser가 채움
            workflows.append(Workflow(
                file_name=file_path,
                title=Path(file_path).stem # 임시 제목
            ))

        return Experiment(
            folder_name=self.exp_folder.name,
            title=post.metadata.get("title", "Untitled Experiment"),
            author=post.metadata.get("author"),
            created_date=post.metadata.get("created_date"),
            workflows=workflows
        )