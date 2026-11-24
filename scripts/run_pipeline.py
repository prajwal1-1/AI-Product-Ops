"""
AI Product Ops Research Pipeline - End-to-End Unified Runner
Executes the full pipeline from raw input to verified dataset, patterns, and HTML case study.
"""

import os
import sys
import time
import subprocess
from rich.console import Console
from rich.panel import Panel

console = Console()
SCRIPTS_DIR = os.path.dirname(__file__)
VENV_PYTHON = os.path.join(os.path.dirname(SCRIPTS_DIR), ".venv", "Scripts", "python.exe")
if not os.path.exists(VENV_PYTHON):
    VENV_PYTHON = sys.executable

def run_step(step_num: int, title: str, script_name: str, args: list = None):
    args = args or []
    cmd = [VENV_PYTHON, os.path.join(SCRIPTS_DIR, script_name)] + args
    console.print(f"\n[bold cyan]============================================================[/bold cyan]")
    console.print(f"[bold yellow]STEP {step_num}: {title}[/bold yellow]")
    console.print(f"[dim]Executing: {' '.join(cmd)}[/dim]")
    console.print(f"[bold cyan]============================================================[/bold cyan]\n")
    
    start = time.time()
    res = subprocess.run(cmd)
    elapsed = time.time() - start
    
    if res.returncode != 0:
        console.print(f"[bold red]❌ Step {step_num} failed with exit code {res.returncode}[/bold red]")
        sys.exit(res.returncode)
    else:
        console.print(f"[bold green]✔ Step {step_num} completed in {elapsed:.2f}s[/bold green]")

def main():
    console.print(Panel(
        "[bold white]Composio AI Product Ops: 100 App Research & Verification Pipeline[/bold white]\n"
        "[dim]Automated Multi-Pass Agent Pipeline • Ground-Truth Registries • Executive Deliverable[/dim]",
        border_style="orange3",
        title="[bold orange3]PIPELINE ORCHESTRATOR[/bold orange3]"
    ))

    # Step 1: Pass 1 Research Agent
    run_step(1, "Pass 1 Research Agent (100 Apps)", "01_research_agent.py", ["--all"])

    # Step 2: Pass 2 Verification Loop
    run_step(2, "Pass 2 Verification Loop (Liveness + Registries + Auditor)", "02_verify_agent.py")

    # Step 3: Pass 3 Export Stratified Audit Sample
    run_step(3, "Pass 3 Export Stratified 26-App Audit Sample", "03_audit_and_analyze.py", ["--export-audit"])

    # Step 4: Pass 3 Finalize Patterns & Verified Dataset
    run_step(4, "Pass 3 Finalize Ground-Truth Dataset & Pattern Clustering", "03_audit_and_analyze.py", ["--finalize"])

    # Step 5: Compile Standalone Executive HTML Case Study
    run_step(5, "Compile Interactive HTML Case Study", "build_html_report.py")

    console.print("\n[bold green]🎉 FULL PIPELINE COMPLETED SUCCESSFULLY![/bold green]")
    console.print("[white]Deliverables ready:[/white]")
    console.print("  - [cyan]index.html[/cyan] (Executive Interactive Case Study)")
    console.print("  - [cyan]data/final_verified.json[/cyan] (100-App Verified Dataset)")
    console.print("  - [cyan]data/patterns_summary.json[/cyan] (Category Matrices & Blockers)")
    console.print("  - [cyan]data/human_audit_sample.csv[/cyan] (Stratified 26-App Human Audit)")
    console.print("\nTo view the interactive case study, run: [bold yellow]python scripts/serve.py[/bold yellow]\n")

if __name__ == "__main__":
    main()
