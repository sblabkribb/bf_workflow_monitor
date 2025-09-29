from pathlib import Path
from src.parsers.readme_parser import ReadmeParser
from src.parsers.workflow_parser import WorkflowParser

def monitor_labnote_folder(folder_path: Path):
    # Find all experiment folders (numbered folders)
    experiment_folders = [
        f for f in folder_path.iterdir() 
        if f.is_dir() and f.name[0].isdigit()
    ]
    
    experiments = []
    for exp_folder in experiment_folders:
        # Parse README.md
        readme_path = exp_folder / "README.md"
        if not readme_path.exists():
            continue
            
        experiment = ReadmeParser(readme_path).parse()
        
        # Parse each workflow file
        for workflow_info in experiment.workflows:
            workflow_path = exp_folder / workflow_info["file"]
            if workflow_path.exists():
                workflow = WorkflowParser(workflow_path).parse()
                workflow_info["details"] = workflow
        
        experiments.append(experiment)
    
    return experiments

if __name__ == "__main__":
    labnote_path = Path("path/to/labnote/folder")
    experiments = monitor_labnote_folder(labnote_path)
    
    # Print summary
    for exp in experiments:
        print(f"\nExperiment: {exp.title}")
        print(f"Status: {exp.calculate_overall_status()}")
        
        for wf in exp.workflows:
            if "details" in wf:
                details = wf["details"]
                print(f"\n  Workflow: {details.title}")
                print(f"  Automation Level: {details.calculate_automation_level():.1f}")
                print(f"  Status: {details.status}")
                
                for uo in details.unit_operations:
                    print(f"\n    UO: {uo.id} - {uo.name}")
                    print(f"    Status: {uo.status}")
                    print(f"    Automation Score: {uo.automation_score}")
                    if uo.kpis:
                        print(f"    KPIs: {uo.kpis}")