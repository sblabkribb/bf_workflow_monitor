import re
from datetime import datetime
from pathlib import Path
import yaml
from ..models.workflow import Workflow
from ..models.unit_operation import UnitOperation

class WorkflowParser:
    def __init__(self, filepath: Path):
        self.filepath = filepath
        
    def parse(self) -> Workflow:
        content = self.filepath.read_text()
        
        # Parse YAML front matter
        yaml_match = re.match(r"---\n(.*?)\n---", content, re.DOTALL)
        metadata = yaml.safe_load(yaml_match.group(1))
        
        # Parse Unit Operations
        uo_blocks = re.split(r"###\s+\[(.*?)\]", content)[1:]
        unit_operations = []
        
        for i in range(0, len(uo_blocks), 2):
            uo_id_name = uo_blocks[i].strip()
            uo_content = uo_blocks[i + 1]
            
            uo_id, uo_name = uo_id_name.split(" ", 1)
            
            # Parse Meta section
            meta = self._parse_section(uo_content, "Meta")
            # Parse Automation section
            automation = self._parse_section(uo_content, "Automation")
            # Parse KPI section
            kpis = self._parse_kpi_section(uo_content)
            # Parse Results section
            results = self._parse_section(uo_content, "Results & Discussions")
            
            unit_operations.append(
                UnitOperation(
                    id=uo_id,
                    name=uo_name,
                    experimenter=meta.get("Experimenter", ""),
                    start_date=self._parse_date(meta.get("Start_date")),
                    end_date=self._parse_date(meta.get("End_date")),
                    hw_automation=automation.get("HW", "None"),
                    sw_automation=automation.get("SW", "None"),
                    kpis=kpis,
                    results=results
                )
            )
        
        return Workflow(
            title=metadata["title"],
            experimenter=metadata["experimenter"],
            status=metadata["status"],
            created_date=datetime.strptime(metadata["created_date"], "%Y-%m-%d"),
            last_updated_date=datetime.strptime(metadata["last_updated_date"], "%Y-%m-%d"),
            unit_operations=unit_operations
        )
    
    def _parse_section(self, content: str, section_name: str) -> dict:
        section_match = re.search(
            rf"####\s+{section_name}\n(.*?)(?=####|\Z)", 
            content, 
            re.DOTALL
        )
        if not section_match:
            return {}
            
        result = {}
        for line in section_match.group(1).strip().split("\n"):
            if not line.startswith("- **"):
                continue
            key, value = re.match(r"-\s+\*\*(.*?)\*\*:\s+(.*)", line).groups()
            result[key] = value.strip()
        return result
    
    def _parse_kpi_section(self, content: str) -> dict:
        kpis = {}
        kpi_section = self._parse_section(content, "KPI")
        
        for key, value in kpi_section.items():
            # Extract numeric value and unit
            match = re.match(r"([\d.]+)\s*(\(.*?\))?", value)
            if match:
                kpis[key] = float(match.group(1))
        return kpis
    
    def _parse_date(self, date_str: str) -> datetime:
        if not date_str:
            return None
        return datetime.strptime(date_str, "%Y-%m-%d")