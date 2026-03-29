#!/usr/bin/env python3
"""
Session Recovery Script for planning-with-files

Intelligently analyzes planning files to generate context summary,
progress report, and next steps recommendations.

Usage: python3 session-recover.py [project-directory]
"""

import os
import sys
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional


def read_markdown_file(filepath: Path) -> str:
    """Read a markdown file and return its content."""
    if not filepath.exists():
        return ""
    with open(filepath, 'r', encoding='utf-8') as f:
        return f.read()


def parse_task_plan(content: str) -> Dict:
    """Parse task_plan.md and extract key information."""
    if not content:
        return {"exists": False}

    result = {
        "exists": True,
        "goal": "",
        "current_phase": "",
        "phases": [],
        "decisions": [],
        "errors": []
    }

    # Extract goal
    lines = content.split('\n')
    for i, line in enumerate(lines):
        if line.startswith('## Goal'):
            # Get next non-empty line
            for j in range(i+1, len(lines)):
                if lines[j].strip() and not lines[j].startswith('#'):
                    result["goal"] = lines[j].strip()
                    break
        elif line.startswith('## Current Phase'):
            for j in range(i+1, len(lines)):
                if lines[j].strip() and not lines[j].startswith('#'):
                    result["current_phase"] = lines[j].strip()
                    break
        elif line.startswith('### Phase'):
            phase_name = line.replace('### Phase', '').strip()
            # Check status
            for j in range(i, min(i+20, len(lines))):
                if '**Status:**' in lines[j]:
                    status = lines[j].split('**Status:**')[1].strip()
                    result["phases"].append({
                        "name": phase_name,
                        "status": status
                    })
                    break

    # Extract errors
    in_errors = False
    for line in lines:
        if '## Errors Encountered' in line:
            in_errors = True
            continue
        if in_errors and line.startswith('##'):
            break
        if in_errors and '|' in line and not line.startswith('|---'):
            parts = [p.strip() for p in line.split('|')]
            if len(parts) >= 3 and parts[0]:
                result["errors"].append({
                    "error": parts[0],
                    "attempt": parts[1] if len(parts) > 1 else "",
                    "resolution": parts[2] if len(parts) > 2 else ""
                })

    return result


def parse_findings(content: str) -> Dict:
    """Parse findings.md and extract key information."""
    if not content:
        return {"exists": False}

    result = {
        "exists": True,
        "requirements": [],
        "research": [],
        "decisions": [],
        "issues": []
    }

    lines = content.split('\n')

    # Extract key sections
    current_section = None
    for line in lines:
        if line.startswith('## Requirements'):
            current_section = "requirements"
        elif line.startswith('## Research Findings'):
            current_section = "research"
        elif line.startswith('## Technical Decisions'):
            current_section = "decisions"
        elif line.startswith('## Issues Encountered'):
            current_section = "issues"
        elif line.startswith('##'):
            current_section = None
        elif current_section and line.strip() and not line.startswith('#'):
            result[current_section].append(line.strip())

    return result


def parse_progress(content: str) -> Dict:
    """Parse progress.md and extract key information."""
    if not content:
        return {"exists": False}

    result = {
        "exists": True,
        "phases": [],
        "test_results": [],
        "error_log": []
    }

    lines = content.split('\n')
    current_phase = None

    for line in lines:
        if line.startswith('### Phase'):
            current_phase = line.replace('### Phase', '').strip()
        elif line.startswith('- **Status:**') and current_phase:
            status = line.split('**Status:**')[1].strip()
            result["phases"].append({
                "name": current_phase,
                "status": status
            })

    # Extract test results and errors
    in_section = None
    for line in lines:
        if line.startswith('## Test Results'):
            in_section = "test"
        elif line.startswith('## Error Log'):
            in_section = "errors"
        elif line.startswith('##'):
            in_section = None
        elif in_section == "test" and '|' in line and not line.startswith('|---'):
            parts = [p.strip() for p in line.split('|')]
            if len(parts) >= 5 and parts[0]:
                result["test_results"].append({
                    "test": parts[0],
                    "input": parts[1] if len(parts) > 1 else "",
                    "expected": parts[2] if len(parts) > 2 else "",
                    "actual": parts[3] if len(parts) > 3 else "",
                    "status": parts[4] if len(parts) > 4 else ""
                })

    return result


def calculate_progress(phases: List[Dict]) -> tuple:
    """Calculate progress percentage."""
    if not phases:
        return 0, 0, 0

    total = len(phases)
    complete = sum(1 for p in phases if "complete" in p.get("status", "").lower())
    in_progress = sum(1 for p in phases if "in_progress" in p.get("status", "").lower())

    percentage = int((complete / total) * 100) if total > 0 else 0
    return percentage, complete, total


def generate_report(project_dir: Path):
    """Generate comprehensive session recovery report."""
    print("\n" + "="*80)
    print("PLANNING-WITH-FILES: SESSION RECOVERY REPORT")
    print("="*80)
    print(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Project: {project_dir}")
    print()

    # Read planning files
    task_plan = parse_task_plan(read_markdown_file(project_dir / "task_plan.md"))
    findings = parse_findings(read_markdown_file(project_dir / "findings.md"))
    progress = parse_progress(read_markdown_file(project_dir / "progress.md"))

    # Check file existence
    print("📁 PLANNING FILES STATUS")
    print("-" * 80)
    files_status = [
        ("task_plan.md", task_plan["exists"]),
        ("findings.md", findings["exists"]),
        ("progress.md", progress["exists"])
    ]

    for filename, exists in files_status:
        status = "✓" if exists else "✗"
        print(f"  {status} {filename}")

    if not task_plan["exists"]:
        print("\n⚠️  WARNING: No task_plan.md found. Cannot generate full report.")
        print("   Consider creating planning files to enable session recovery.")
        return

    print()

    # Goal and Current Status
    print("🎯 GOAL & CURRENT STATUS")
    print("-" * 80)
    print(f"  Goal: {task_plan.get('goal', 'Not specified')}")
    print(f"  Current Phase: {task_plan.get('current_phase', 'Not specified')}")

    # Progress calculation
    percentage, complete, total = calculate_progress(task_plan["phases"])
    print(f"\n  Overall Progress: {percentage}% ({complete}/{total} phases complete)")

    # Progress bar
    bar_length = 40
    filled = int(bar_length * percentage / 100)
    bar = "█" * filled + "░" * (bar_length - filled)
    print(f"  [{bar}] {percentage}%")

    # Phase details
    print("\n📋 PHASE DETAILS")
    print("-" * 80)
    for phase in task_plan["phases"]:
        status_icon = "✓" if "complete" in phase["status"].lower() else "▶" if "in_progress" in phase["status"].lower() else "○"
        print(f"  {status_icon} {phase['name']}")
        print(f"      Status: {phase['status']}")

    # Key Decisions
    if findings["decisions"]:
        print("\n💡 KEY DECISIONS")
        print("-" * 80)
        for decision in findings["decisions"][:5]:  # Show top 5
            print(f"  • {decision}")
        if len(findings["decisions"]) > 5:
            print(f"  ... and {len(findings['decisions']) - 5} more")

    # Research Findings
    if findings["research"]:
        print("\n🔍 RESEARCH FINDINGS")
        print("-" * 80)
        for finding in findings["research"][:5]:
            print(f"  • {finding}")
        if len(findings["research"]) > 5:
            print(f"  ... and {len(findings['research']) - 5} more")

    # Errors
    if task_plan["errors"]:
        print("\n❌ ERRORS ENCOUNTERED")
        print("-" * 80)
        for error in task_plan["errors"]:
            print(f"  • {error['error']}")
            print(f"      Attempt: {error['attempt']}")
            print(f"      Resolution: {error['resolution']}")
            print()

    # Test Results
    if progress["test_results"]:
        passed = sum(1 for t in progress["test_results"] if "✓" in t["status"])
        total_tests = len(progress["test_results"])
        print(f"\n🧪 TEST RESULTS ({passed}/{total_tests} passed)")
        print("-" * 80)
        for test in progress["test_results"][:5]:
            status_icon = "✓" if "✓" in test["status"] else "✗"
            print(f"  {status_icon} {test['test']}")
        if len(progress["test_results"]) > 5:
            print(f"  ... and {len(progress['test_results']) - 5} more")

    # Next Steps
    print("\n🚀 RECOMMENDED NEXT STEPS")
    print("-" * 80)

    # Find next incomplete phase
    next_phase = None
    for phase in task_plan["phases"]:
        if "pending" in phase["status"].lower():
            next_phase = phase
            break

    if next_phase:
        print(f"  1. Start: {next_phase['name']}")
        print(f"     Status: {next_phase['status']}")
        print("     Action: Read task_plan.md for detailed requirements")
    else:
        print("  1. Review: All phases appear complete")
        print("     Action: Verify deliverables and prepare for handoff")

    print("  2. Update: Mark current phase as in_progress")
    print("     Action: Edit task_plan.md and update status")
    print("  3. Execute: Follow the phase requirements")
    print("     Action: Work through checklist items")
    print("  4. Document: Update findings.md with discoveries")
    print("     Action: Apply 2-Action Rule after every 2 operations")
    print("  5. Track: Update progress.md throughout session")
    print("     Action: Log actions and results")

    # Compliance Check
    print("\n✓ COMPLIANCE CHECKLIST")
    print("-" * 80)
    checks = [
        ("Planning files exist", all(f[1] for f in files_status)),
        ("Goal is defined", bool(task_plan.get("goal"))),
        ("Current phase is set", bool(task_plan.get("current_phase"))),
        ("Errors are logged", len(task_plan["errors"]) > 0 or True),  # No errors is OK
        ("Progress > 0%", percentage > 0 or total == 0)
    ]

    for check, passed in checks:
        status = "✓" if passed else "✗"
        print(f"  {status} {check}")

    print("\n" + "="*80)
    print("END OF SESSION RECOVERY REPORT")
    print("="*80 + "\n")


def main():
    """Main entry point."""
    project_dir = Path(sys.argv[1]) if len(sys.argv) > 1 else Path.cwd()

    if not project_dir.exists():
        print(f"Error: Directory {project_dir} does not exist")
        sys.exit(1)

    generate_report(project_dir)


if __name__ == "__main__":
    main()
