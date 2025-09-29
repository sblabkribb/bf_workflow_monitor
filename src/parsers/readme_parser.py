import re
from datetime import datetime
from pathlib import Path
import yaml
from ..models.experiment import Experiment

class ReadmeParser:
    def __init__(self, filepath: Path):
        self.filepath = filepath
        
    def parse(self) -> Experiment:
        content = self.filepath.read_text()
        
        # Parse YAML front matter
        yaml_match = re.match(r"---\n(.*?)\n---", content, re.DOTALL)
        if not yaml_match:
            raise ValueError("No YAML front matter found")
            
        metadata = yaml.safe_load(yaml_match.group(1))
        
        # Parse workflow list
        workflow_lines = re.findall(r"- \[([ x])\] \[(.*?)\]", content)
        workflows = [
            {"file": wf[1], "completed": bool(wf[0].strip())}
            for wf in workflow_lines
        ]
        
        return Experiment(
            title=metadata["title"],
            author=metadata["author"],
            status=metadata["status"],
            created_date=datetime.strptime(metadata["created_date"], "%Y-%m-%d"),
            workflows=workflows
        )