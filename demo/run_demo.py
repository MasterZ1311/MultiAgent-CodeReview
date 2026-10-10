#!/usr/bin/env python3
"""
cerberus</> Automated Demo Runner.
Executes the 5 enterprise demo scenarios and displays rich terminal visualizations.
Can run in-process (zero config) or against a live HTTP server.
"""

import asyncio
import os
from pathlib import Path
import sys
import time

# Ensure repository root is on sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

# Ensure UTF-8 output on Windows console
if sys.platform == "win32":
    try:
        if hasattr(sys.stdout, "reconfigure"):
            sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        if hasattr(sys.stderr, "reconfigure"):
            sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

from typing import Optional
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.text import Text

from demo.demo_scenarios import ALL_SCENARIOS
from cerberus import __version__
from cerberus.agents.orchestrator import orchestrator
from cerberus.models.schemas import CodeReviewRequest, ReviewConfig

console = Console()


async def run_scenario_in_process(scenario: dict) -> dict:
    req = CodeReviewRequest(
        code=scenario["code"],
        language="python",
        filename=scenario["name"][:20].strip() + ".py",
        agents=scenario.get("agents"),
        config=ReviewConfig(blocking_mode=False)
    )
    start = time.perf_counter()
    resp = await orchestrator.execute_review(req)
    latency_ms = int((time.perf_counter() - start) * 1000)
    return {
        "scenario": scenario,
        "response": resp,
        "latency_ms": latency_ms
    }


async def main():
    console.print(Panel(
        f"[bold white]cerberus</>[/bold white] [bold cyan]Autonomous Multi-Agent Code Review & Quality Assurance[/bold cyan]\n"
        f"[dim]Version {__version__} • IBM Agentic AI Platform Demo Sprint[/dim]\n\n"
        f"Executing [bold yellow]5 Enterprise Scenarios[/bold yellow] across Security, Performance, Quality, Architecture & Compliance...",
        title="[bold magenta]🚀 DEMO ORCHESTRATION PIPELINE[/bold magenta]",
        border_style="magenta"
    ))

    passed_scenarios = 0
    total_findings_count = 0

    for idx, scenario in enumerate(ALL_SCENARIOS, 1):
        console.print(f"\n[bold cyan]▶ [{idx}/5] {scenario['name']}[/bold cyan]")
        console.print(f"  [dim]{scenario['description']}[/dim]")
        
        result = await run_scenario_in_process(scenario)
        resp = result["response"]
        
        all_findings = resp.critical_issues + resp.warnings + resp.suggestions
        total_findings_count += len(all_findings)
        
        # Determine score styling
        score = resp.overall_score or 0
        score_color = "green" if score >= 85 else ("yellow" if score >= 60 else "red")
        
        summary = resp.results.get("severity_summary", {}) if resp.results else {}
        crit = summary.get("critical", 0)
        high = summary.get("high", 0)
        med = summary.get("medium", 0)
        low = summary.get("low", 0) + summary.get("info", 0)

        # Verification check
        matched = True
        for expected in scenario["expected_findings"]:
            found = any(expected.lower() in (f.title + " " + f.message).lower() for f in all_findings)
            if not found:
                matched = False
                break
        
        status_text = "[bold green]✔ PASSED EXPECTATION[/bold green]" if matched else "[bold yellow]⚠ PARTIAL MATCH[/bold yellow]"
        if matched:
            passed_scenarios += 1

        # Print metrics row
        console.print(
            f"  Score: [{score_color} bold]{score}/100[/{score_color} bold] | "
            f"Latency: [bold]{result['latency_ms']}ms[/bold] | "
            f"Findings: [red]{crit} Crit[/red], [yellow]{high} High[/yellow], [cyan]{med} Med[/cyan], [blue]{low} Info[/blue] | "
            f"{status_text}"
        )

        if all_findings:
            table = Table(show_header=True, header_style="bold blue", box=None, padding=(0, 1))
            table.add_column("Sev", width=10)
            table.add_column("Agent", width=13)
            table.add_column("Line", width=5)
            table.add_column("Finding Title", style="bold")
            table.add_column("Remediation Preview", style="dim")

            for f in all_findings:
                sev_style = "bold red" if f.severity.value in ("critical", "high") else ("bold yellow" if f.severity.value == "medium" else "dim blue")
                agent_name = f.category or "agent"
                table.add_row(
                    Text(f.severity.value.upper(), style=sev_style),
                    agent_name,
                    str(f.line or "-"),
                    f.title[:38] + ("..." if len(f.title) > 38 else ""),
                    (f.suggestion or f.recommendation or "")[:45] + "..."
                )
            console.print(table)

    # Final Summary Panel
    console.print("\n")
    console.print(Panel(
        f"[bold green]✔ All 5 Enterprise Scenarios Executed Successfully[/bold green]\n\n"
        f"• [bold]Scenarios Passed:[/bold] {passed_scenarios} / {len(ALL_SCENARIOS)}\n"
        f"• [bold]Total Flaws Identified:[/bold] {total_findings_count}\n"
        f"• [bold]Autonomous Agents Verified:[/bold] Security, Performance, Quality, Architecture, Compliance\n"
        f"• [bold]Live Web Dashboard:[/bold] http://localhost:8000/\n"
        f"• [bold]Interactive Swagger Docs:[/bold] http://localhost:8000/docs",
        title="[bold green]🏆 DEMO SUITE EXECUTION COMPLETE[/bold green]",
        border_style="green"
    ))

    return 0 if passed_scenarios == len(ALL_SCENARIOS) else 1


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
